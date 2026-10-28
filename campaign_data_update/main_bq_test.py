"""
[테스트] 매체 데이터 → BigQuery 적재

- main.py의 수집 함수를 그대로 불러와서 사용 (main.py는 수정하지 않음)
- 구글 시트에는 쓰지 않고, BigQuery 테스트 테이블에만 저장
- 매체별로 "이번 달 기존 행 삭제 → 새로 수집한 행 넣기"를 한 번에 처리
- 수집 결과가 비어 있는 매체는 삭제하지 않음 (기존 데이터 유지)
- 테스트 중에는 슬랙 알림을 보내지 않음 (로그에만 출력)
"""
import json
import os
from datetime import datetime, timezone

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

import main as m  # 기존 수집 스크립트 (main() 은 실행되지 않음)

# ------------------------------------------
# 테스트 중 슬랙 알림 끄기 (팀 채널에 알림 가지 않도록)
# ------------------------------------------
m.send_slack_message = lambda msg: print(f"[슬랙 생략] {msg}")

# ------------------------------------------
# 설정
# ------------------------------------------
PROJECT_ID = "ga4-bigquery-377201"
DATASET_ID = "mkt_dashboard_test"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.raw_media_api"
STAGE_ID = f"{PROJECT_ID}.{DATASET_ID}._stage_media_api"  # 임시 보관용 테이블

SCHEMA = [
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("campaign", "STRING"),
    bigquery.SchemaField("ad_group", "STRING"),
    bigquery.SchemaField("content", "STRING"),
    bigquery.SchemaField("impressions", "INT64"),
    bigquery.SchemaField("clicks", "INT64"),
    bigquery.SchemaField("cost", "INT64"),
    bigquery.SchemaField("collected_at", "TIMESTAMP"),
]
COLUMNS = [f.name for f in SCHEMA]

SOURCES = [
    ("naver_sa", m.fetch_naver),
    ("google", m.fetch_google),
    ("meta", m.fetch_meta),
    ("tiktok", m.fetch_tiktok),
]
if m.ENABLE_KAKAO:
    SOURCES.append(("kakao", m.fetch_kakao))


def get_client():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(info)
    print(f"🔑 실행 계정: {info.get('client_email')}")
    return bigquery.Client(project=PROJECT_ID, credentials=creds)


def to_bq_frame(df, source, collected_at):
    """main.py 결과(한글 컬럼)를 BigQuery 테이블 형식(영문 컬럼)으로 변환"""
    out = pd.DataFrame(index=df.index)
    out["date"] = pd.to_datetime(
        df["날짜"].astype(str), format="%Y/%m/%d", errors="coerce"
    ).dt.date
    out["source"] = source
    out["campaign"] = df["캠페인"].fillna("").astype(str)
    out["ad_group"] = df["그룹"].fillna("").astype(str)
    # 시트 수식 방지용으로 붙인 맨 앞 작은따옴표(')만 제거  예: '+ad13 → +ad13
    out["content"] = (
        df["콘텐츠"].fillna("").astype(str).str.replace(r"^'", "", regex=True)
    )
    for src, dst in [("노출", "impressions"), ("클릭", "clicks"), ("비용", "cost")]:
        out[dst] = (
            pd.to_numeric(df[src], errors="coerce").fillna(0).round(0).astype("int64")
        )
    out["collected_at"] = collected_at

    bad = out["date"].isna()
    if bad.any():
        print(f"⚠️ {source}: 날짜를 읽지 못한 {int(bad.sum())}행 제외")
    return out[~bad][COLUMNS]


def replace_source(client, frame, source, since, until):
    """임시 테이블에 올린 뒤, 해당 매체·기간 행을 한 번에 교체"""
    load_cfg = bigquery.LoadJobConfig(schema=SCHEMA, write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(frame, STAGE_ID, job_config=load_cfg).result()

    cols = ", ".join(COLUMNS)
    sql = f"""
    BEGIN TRANSACTION;

    DELETE FROM `{TABLE_ID}`
    WHERE source = '{source}'
      AND date BETWEEN DATE '{since.isoformat()}' AND DATE '{until.isoformat()}';

    INSERT INTO `{TABLE_ID}` ({cols})
    SELECT {cols} FROM `{STAGE_ID}`;

    COMMIT TRANSACTION;
    """
    client.query(sql).result()


def main():
    client = get_client()
    since = datetime.strptime(m.SINCE, "%Y/%m/%d").date()
    until = datetime.strptime(m.UNTIL, "%Y/%m/%d").date()
    collected_at = datetime.now(timezone.utc)
    print(f"📅 적재 기간: {since} ~ {until}")

    results = []
    for source, fetch in SOURCES:
        try:
            df = fetch()
        except Exception as e:
            print(f"❌ {source} 수집 오류: {e}")
            results.append((source, "수집 실패", 0, 0))
            continue

        if df is None or df.empty:
            print(f"⚠️ {source}: 수집 결과 없음 → BigQuery 기존 데이터 유지")
            results.append((source, "건너뜀(빈 결과)", 0, 0))
            continue

        frame = to_bq_frame(df, source, collected_at)
        try:
            replace_source(client, frame, source, since, until)
            results.append((source, "적재 완료", len(frame), int(frame["cost"].sum())))
        except Exception as e:
            print(f"❌ {source} 적재 오류: {e}")
            results.append((source, "적재 실패", len(frame), 0))

    print("\n========== 결과 요약 ==========")
    for source, status, rows, cost in results:
        print(f"{source:10s} | {status:12s} | {rows:6,d}행 | 비용 {cost:,d}")


if __name__ == "__main__":
    main()
