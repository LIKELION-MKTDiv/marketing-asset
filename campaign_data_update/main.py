import os
import time, json, base64, hmac, hashlib, requests
import pandas as pd
from datetime import datetime, timedelta, date, timezone

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. 통합 설정 (한국 시간 기준)
# ==========================================
kst = timezone(timedelta(hours=9))
now_kst = datetime.now(kst)
today = now_kst.date()

SINCE = today.replace(day=1).strftime("%Y/%m/%d")
UNTIL = today.strftime("%Y/%m/%d")

SPREADSHEET_ID = "1Nqsc6xvHu-V1u7jyAgPvS1il0jIs9LK6cGRs4f98Qro"
TARGET_SHEET_NAME = "[RAW] 매체 데이터"

# 슬랙 웹훅 URL
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

KEYS = {
    "NAVER": {
        "CUSTOMER_ID": os.environ["NAVER_CUSTOMER_ID"],
        "API_KEY": os.environ["NAVER_API_KEY"],
        "SECRET": os.environ["NAVER_SECRET"]
    },
    "GOOGLE": {
        "developer_token": os.environ["GOOGLE_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_LOGIN_CUSTOMER_ID"],
        "customer_id": os.environ["GOOGLE_CUSTOMER_ID"]
    },
    "META": {
        "TOKEN": os.environ["META_TOKEN"],
        "AD_ACCOUNT_ID": os.environ["META_AD_ACCOUNT_ID"],
        "API_VER": os.environ.get("META_API_VER", "v19.0")
    },
    "TIKTOK": {
        "TOKEN": os.environ["TIKTOK_TOKEN"],
        "AD_ACCOUNT_ID": os.environ["TIKTOK_AD_ACCOUNT_ID"]
    }
}

def send_slack_message(message):
    payload = {"text": message}
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json=payload)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ 슬랙 알림 실패: {e}")

# ==========================================
# 2. 매체별 수집 함수
# ==========================================

def fetch_naver():
    print(f"🚀 네이버 SA 수집 중... ({SINCE} ~ {UNTIL})")

    BASE_URL = "https://api.searchad.naver.com"
    CHUNK_SIZE = 500

    def make_sig(ts, method, uri, secret):
        msg = f"{ts}.{method}.{uri}"
        digest = hmac.new(
            secret.encode(),
            msg.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(digest).decode()

    def sa_get(uri, params=None, max_retry=3):
        for attempt in range(1, max_retry + 1):
            try:
                ts = str(int(time.time() * 1000))
                headers = {
                    "X-Timestamp": ts,
                    "X-API-KEY": KEYS["NAVER"]["API_KEY"],
                    "X-Customer": KEYS["NAVER"]["CUSTOMER_ID"],
                    "X-Signature": make_sig(
                        ts,
                        "GET",
                        uri,
                        KEYS["NAVER"]["SECRET"]
                    ),
                    "Content-Type": "application/json"
                }

                r = requests.get(
                    BASE_URL + uri,
                    headers=headers,
                    params=params,
                    timeout=60
                )

                if r.status_code in [429, 500, 502, 503, 504]:
                    print(f"⚠️ 네이버 API 재시도 {attempt}/{max_retry}: {r.status_code}")
                    time.sleep(2 * attempt)
                    continue

                r.raise_for_status()
                return r.json()

            except Exception as e:
                print(f"⚠️ 네이버 API 오류 {attempt}/{max_retry}: {uri}, {e}")
                if attempt == max_retry:
                    raise
                time.sleep(2 * attempt)

    def chunks(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]

    def parse_stats(res):
        if isinstance(res, dict):
            return res.get("data", [])
        if isinstance(res, list):
            return res
        return []

    def get_stats(ids, fields, since, until):
        result = []

        if not ids:
            return result

        for chunk_ids in chunks(ids, CHUNK_SIZE):
            params = {
                "ids": ",".join(chunk_ids),
                "fields": json.dumps(fields),
                "timeRange": json.dumps({
                    "since": since,
                    "until": until
                })
            }

            res = sa_get("/stats", params)
            result.extend(parse_stats(res))
            time.sleep(0.05)

        return result

    try:
        camps = sa_get("/ncc/campaigns")

        target_camps = [
            c for c in camps
            if "kdtbc" in c.get("name", "").lower()
        ]

        if not target_camps:
            print("⚠️ 네이버 kdtbc 캠페인 없음")
            return pd.DataFrame(
                columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
            )

        target_camp_ids = [c["nccCampaignId"] for c in target_camps]

        adgroup_map = {}
        for cid in target_camp_ids:
            ags = sa_get("/ncc/adgroups", {"nccCampaignId": cid})
            for ag in ags:
                agid = ag["nccAdgroupId"]
                adgroup_map[agid] = ag.get("name", "")
            time.sleep(0.05)

        ag_ids = list(adgroup_map.keys())

        if not ag_ids:
            print("⚠️ 네이버 광고그룹 없음")
            return pd.DataFrame(
                columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
            )

        print(f"✅ 네이버 전체 광고그룹 수: {len(ag_ids)}개")

        full_since = SINCE.replace("/", "-")
        full_until = UNTIL.replace("/", "-")

        ag_total_stats = get_stats(
            ag_ids,
            ["salesAmt"],
            full_since,
            full_until
        )

        active_ag_ids = set()
        for s in ag_total_stats:
            if float(s.get("salesAmt", 0) or 0) > 0:
                sid = s.get("id")
                if sid:
                    active_ag_ids.add(sid)

        active_ag_ids = sorted(active_ag_ids)

        if not active_ag_ids:
            print("⚠️ 네이버 비용 발생 광고그룹 없음")
            return pd.DataFrame(
                columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
            )

        print(f"✅ 네이버 활성 광고그룹 수: {len(active_ag_ids)}개")

        kw_map = {}
        for agid in active_ag_ids:
            kws = sa_get("/ncc/keywords", {"nccAdgroupId": agid})
            for kw in kws:
                kwid = kw.get("nccKeywordId")
                if not kwid:
                    continue
                kw_map[kwid] = {
                    "keyword": kw.get("keyword", ""),
                    "agid": agid
                }
            time.sleep(0.05)

        kw_ids = list(kw_map.keys())

        if not kw_ids:
            print("⚠️ 네이버 현재 키워드 없음")
            return pd.DataFrame(
                columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
            )

        print(f"✅ 네이버 현재 키워드 수: {len(kw_ids)}개")

        rows = []
        kw_sum_by_day_ag = {}

        for d in pd.date_range(SINCE, UNTIL):
            d_api = d.strftime("%Y-%m-%d")
            d_sheet = d.strftime("%Y/%m/%d")

            stats = get_stats(
                kw_ids,
                ["impCnt", "clkCnt", "salesAmt"],
                d_api,
                d_api
            )

            for s in stats:
                cost = float(s.get("salesAmt", 0) or 0)
                if cost <= 0:
                    continue

                kwid = s.get("id")
                kw_info = kw_map.get(kwid)
                if not kw_info:
                    continue

                agid = kw_info["agid"]
                imp = int(float(s.get("impCnt", 0) or 0))
                clk = int(float(s.get("clkCnt", 0) or 0))

                rows.append([
                    d_sheet,
                    adgroup_map.get(agid, ""),
                    "" if "kdtbc" in adgroup_map.get(agid, "").lower() else "",
                    kw_info["keyword"],
                    imp,
                    clk,
                    cost
                ])

                key = (d_sheet, agid)
                if key not in kw_sum_by_day_ag:
                    kw_sum_by_day_ag[key] = {
                        "impCnt": 0,
                        "clkCnt": 0,
                        "salesAmt": 0
                    }

                kw_sum_by_day_ag[key]["impCnt"] += imp
                kw_sum_by_day_ag[key]["clkCnt"] += clk
                kw_sum_by_day_ag[key]["salesAmt"] += cost

        base_df = pd.DataFrame(
            rows,
            columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
        )

        print(f"✅ 네이버 기본 키워드 수집 완료: {len(base_df)}행")
        print(f"✅ 네이버 기본 키워드 비용 합계: {base_df['비용'].sum():,.0f}")

        recon_rows = []
        print(f"🔎 네이버 전체 기간 정합성 보정 시작: {full_since} ~ {full_until}")

        for d in pd.date_range(SINCE, UNTIL):
            d_api = d.strftime("%Y-%m-%d")
            d_sheet = d.strftime("%Y/%m/%d")

            ag_daily_stats = get_stats(
                active_ag_ids,
                ["impCnt", "clkCnt", "salesAmt"],
                d_api,
                d_api
            )

            for s in ag_daily_stats:
                agid = s.get("id")
                if not agid:
                    continue

                ag_cost = float(s.get("salesAmt", 0) or 0)
                if ag_cost <= 0:
                    continue

                ag_imp = int(float(s.get("impCnt", 0) or 0))
                ag_clk = int(float(s.get("clkCnt", 0) or 0))

                kw_sum = kw_sum_by_day_ag.get(
                    (d_sheet, agid),
                    {
                        "impCnt": 0,
                        "clkCnt": 0,
                        "salesAmt": 0
                    }
                )

                diff_cost = round(ag_cost - kw_sum["salesAmt"], 0)
                diff_imp = max(ag_imp - kw_sum["impCnt"], 0)
                diff_clk = max(ag_clk - kw_sum["clkCnt"], 0)

                if abs(diff_cost) >= 1:
                    recon_rows.append([
                        d_sheet,
                        adgroup_map.get(agid, ""),
                        "",
                        "[삭제키워드_보정]",
                        diff_imp,
                        diff_clk,
                        diff_cost
                    ])

        if recon_rows:
            recon_df = pd.DataFrame(
                recon_rows,
                columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"]
            )
            final_df = pd.concat([base_df, recon_df], ignore_index=True)
            print(f"✅ 네이버 삭제키워드 보정 추가: {len(recon_df)}행")
            print(f"✅ 네이버 삭제키워드 보정 비용 합계: {recon_df['비용'].sum():,.0f}")
        else:
            final_df = base_df
            print("⚠️ 네이버 삭제키워드 보정행 없음")

        if final_df.empty:
            print("⚠️ 네이버 최종 DataFrame 비어 있음")
            return final_df

        final_df["비용"] = final_df["비용"].round(0)

        ag_expected_total = 0
        for d in pd.date_range(SINCE, UNTIL):
            d_api = d.strftime("%Y-%m-%d")
            ag_daily_stats = get_stats(
                active_ag_ids,
                ["salesAmt"],
                d_api,
                d_api
            )
            for s in ag_daily_stats:
                ag_expected_total += float(s.get("salesAmt", 0) or 0)

        ag_expected_total = round(ag_expected_total, 0)
        final_total = round(final_df["비용"].sum(), 0)
        diff_total = ag_expected_total - final_total

        print("✅ 네이버 SA 최종 수집 완료")
        print(f" - 차이: {diff_total:,.0f}")

        if abs(diff_total) >= 1:
            print(f"⚠️ 네이버 비용 정합성 차이 발생: {diff_total:,.0f}")
            send_slack_message(
                f"⚠️ 네이버 SA 비용 정합성 차이 발생\n"
                f"차이: {diff_total:,.0f}"
            )

        # 🌟 네이버 SA 데이터는 어떤 필터링도 거치지 않고 온전하게 보존되어 반환됩니다.
        return final_df

    except Exception as e:
        print(f"❌ 네이버 수집 실패: {e}")
        send_slack_message(f"❌ 네이버 SA 수집 실패\n에러: {e}")
        return pd.DataFrame(columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"])

def fetch_google():
    print("🚀 구글 Ads 수집 중 (gm 수집 허용, bejv26 및 cld08 제외)...")
    try:
        VAT = 1.1; config = {"developer_token": KEYS["GOOGLE"]["developer_token"], "client_id": KEYS["GOOGLE"]["client_id"], "client_secret": KEYS["GOOGLE"]["client_secret"], "refresh_token": KEYS["GOOGLE"]["refresh_token"], "login_customer_id": KEYS["GOOGLE"]["login_customer_id"], "use_proto_plus": True}
        client = GoogleAdsClient.load_from_dict(config); ga_service = client.get_service("GoogleAdsService")
        def run_gaql(query):
            out = []; stream = ga_service.search_stream(customer_id=KEYS["GOOGLE"]["customer_id"], query=query)
            for batch in stream: out.extend(batch.results)
            return out
        rows = []
        q_since, q_until = SINCE.replace("/","-"), UNTIL.replace("/","-")

        # 💡 1. 검색 광고 수집 - NOT LIKE 조건에 cld08 추가
        q_kw = f"SELECT segments.date, campaign.name, ad_group.name, ad_group_criterion.keyword.text, metrics.impressions, metrics.clicks, metrics.cost_micros FROM keyword_view WHERE segments.date BETWEEN '{q_since}' AND '{q_until}' AND metrics.cost_micros > 0 AND campaign.advertising_channel_type = 'SEARCH' AND campaign.name NOT LIKE '%kdtall%' AND campaign.name NOT LIKE '%bejv26%' AND campaign.name NOT LIKE '%cld08%'"
        for r in run_gaql(q_kw):
            camp_name, group_name = r.campaign.name, r.ad_group.name
            if camp_name == "kdtbejv23_google_search_2601_new_v2" and group_name == "new_v2_1834_pcmo":
                group_name = "new_v2_4_developer_1834_pcmo"
            rows.append([str(r.segments.date).replace("-","/"), camp_name, group_name, r.ad_group_criterion.keyword.text, int(r.metrics.impressions), int(r.metrics.clicks), (r.metrics.cost_micros/1000000.0)*VAT])

        # 💡 2. 디스플레이/동영상 광고 수집 - NOT LIKE 조건에 cld08 추가
        q_ad = f"SELECT segments.date, campaign.name, ad_group.name, ad_group_ad.ad.name, ad_group_ad.ad.id, metrics.impressions, metrics.clicks, metrics.cost_micros FROM ad_group_ad WHERE segments.date BETWEEN '{q_since}' AND '{q_until}' AND metrics.cost_micros > 0 AND campaign.advertising_channel_type NOT IN ('SEARCH', 'PERFORMANCE_MAX') AND campaign.name NOT LIKE '%bejv26%' AND campaign.name NOT LIKE '%cld08%'"
        for r in run_gaql(q_ad):
            content = r.ad_group_ad.ad.name.strip() if getattr(r.ad_group_ad.ad, "name", None) else f"ad_{r.ad_group_ad.ad.id}"
            rows.append([str(r.segments.date).replace("-","/"), r.campaign.name, r.ad_group.name, content, int(r.metrics.impressions), int(r.metrics.clicks), (r.metrics.cost_micros/1000000.0)*VAT])

        # 💡 3. 실적 최대화 광고 수집 - NOT LIKE 조건에 cld08 추가
        q_pmax = f"SELECT segments.date, campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE segments.date BETWEEN '{q_since}' AND '{q_until}' AND metrics.cost_micros > 0 AND campaign.advertising_channel_type = 'PERFORMANCE_MAX' AND campaign.name NOT LIKE '%bejv26%' AND campaign.name NOT LIKE '%cld08%'"
        for r in run_gaql(q_pmax):
            rows.append([str(r.segments.date).replace("-","/"), r.campaign.name, "PMax", "PMax", int(r.metrics.impressions), int(r.metrics.clicks), (r.metrics.cost_micros/1000000.0)*VAT])

        return pd.DataFrame(rows, columns=["날짜","캠페인","그룹","콘텐츠","노출","클릭","비용"])
    except: return pd.DataFrame()

def fetch_meta():
    print("🚀 메타 Ads 수집 중 (소재명 보정 및 bejv26/cld08 필터링)...")
    try:
        url = f"https://graph.facebook.com/{KEYS['META']['API_VER']}/{KEYS['META']['AD_ACCOUNT_ID']}/insights"
        params = {"access_token": KEYS["META"]["TOKEN"], "level": "ad", "time_increment": 1, "time_range": json.dumps({"since": SINCE.replace("/","-"), "until": UNTIL.replace("/","-")}), "fields": "date_start,campaign_name,adset_name,ad_name,impressions,clicks,spend", "limit": 5000}
        r = requests.get(url, params=params).json()
        data = []
        for x in r.get("data", []):
            camp_name, ad_name = x.get("campaign_name", ""), x.get("ad_name", "")
            if camp_name == "kdtcld06_meta_da_conversion_2602_new" and ad_name in ["ad13_v_human_c3_jobcare", "ad14_v_human_c1_bootcamp"]:
                ad_name = "'+" + ad_name
            data.append([x["date_start"].replace("-","/"), camp_name, x.get("adset_name", ""), ad_name, int(x.get("impressions", 0)), int(x.get("clicks", 0)), float(x.get("spend", 0))])

        df = pd.DataFrame(data, columns=["날짜","캠페인","그룹","콘텐츠","노출","클릭","비용"])
        # 💡 메타 캠페인명에서 bejv26 또는 cld08이 포함된 행 필터링 제거
        df = df[~df["캠페인"].str.lower().str.contains("bejv26|cld08", na=False)]
        return df
    except: return pd.DataFrame()

def fetch_tiktok():
    print(f"🚀 틱톡 Ads 수집 및 소재명 매핑 중 (bejv26/cld08 필터링)... ({SINCE} ~ {UNTIL})")
    try:
        headers = {"Access-Token": KEYS["TIKTOK"]["TOKEN"]}
        adv_id = KEYS["TIKTOK"]["AD_ACCOUNT_ID"]

        map_url = "https://business-api.tiktok.com/open_api/v1.3/ad/get/"
        map_params = {"advertiser_id": adv_id, "page_size": 1000, "fields": json.dumps(["ad_id", "ad_name", "campaign_name", "adgroup_name"])}
        map_res = requests.get(map_url, headers=headers, params=map_params).json()

        ad_map = {}
        for item in map_res.get("data", {}).get("list", []):
            ad_id = str(item["ad_id"])
            ad_map[ad_id] = {"campaign_name": item.get("campaign_name", "N/A"), "adgroup_name": item.get("adgroup_name", "N/A"), "ad_name": item.get("ad_name", "N/A")}

        report_url = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"
        report_params = {"advertiser_id": adv_id, "report_type": "BASIC", "data_level": "AUCTION_AD", "dimensions": json.dumps(["ad_id", "stat_time_day"]), "metrics": json.dumps(["spend", "impressions", "clicks"]), "start_date": SINCE.replace("/","-"), "end_date": UNTIL.replace("/","-"), "page_size": 1000}
        r = requests.get(report_url, headers=headers, params=report_params).json()

        rows = []
        for item in r.get("data", {}).get("list", []):
            m = item.get("metrics", {})
            d = item.get("dimensions", {})
            impressions = int(m.get("impressions", 0))
            if impressions <= 0:
                continue

            ad_id = str(d.get("ad_id"))
            raw_date = d.get("stat_time_day", "")
            try:
                clean_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").strftime("%Y/%m/%d")
            except:
                clean_date = raw_date.replace("-", "/")

            names = ad_map.get(ad_id, {"campaign_name": "N/A", "adgroup_name": "N/A", "ad_name": ad_id})
            rows.append([clean_date, names["campaign_name"], names["adgroup_name"], names["ad_name"], impressions, int(m.get("clicks", 0)), float(m.get("spend", 0))])

        df = pd.DataFrame(rows, columns=["날짜", "캠페인", "그룹", "콘텐츠", "노출", "클릭", "비용"])
        # 💡 틱톡 캠페인명에서 bejv26 또는 cld08이 포함된 행 필터링 제거
        df = df[~df["캠페인"].str.lower().str.contains("bejv26|cld08", na=False)]
        return df
    except: return pd.DataFrame()

# ==========================================
# 3. 메인 실행부
# ==========================================
def main():
    all_dfs = []
    for f in [fetch_naver, fetch_google, fetch_meta, fetch_tiktok]:
        try:
            df = f()
            if not df.empty: all_dfs.append(df)
        except Exception as e: print(f"⚠️ 매체 수집 실패: {e}")

    if not all_dfs: return print("❌ 수집된 데이터 없음.")

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df["비용"] = final_df["비용"].round(0).astype(int)

    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(creds)

    try:
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(TARGET_SHEET_NAME)
        LIMIT_ROW = 5000
        ws.batch_clear([f"E2:K{LIMIT_ROW}"])

        data_to_write = final_df.values.tolist()
        if len(data_to_write) > (LIMIT_ROW - 1):
            data_to_write = data_to_write[:LIMIT_ROW - 1]

        if data_to_write:
            ws.update(range_name="E2", values=data_to_write, value_input_option='USER_ENTERED')
            print(f"✅ 안전 업데이트 완료! {len(data_to_write)}행 반영.")

            if now_kst.hour in [8, 9]:
                now_str = now_kst.strftime('%Y-%m-%d %H:%M')
                msg = (
                    f"*[마케팅 대시보드 업데이트 알림]*\n"
                    f"안녕하세요, 금일 KDT 부트캠프 대시보드 업데이트 완료되었습니다.\n"
                    f"4개 매체 통합 데이터 확인 및 오류 체크 부탁드립니다! @황성진\n\n"
                    f"좋은 하루 되세요! ☀️\n\n"
                    f"• *성공여부*: 정상 ✅ (대행사 데이터 제외)\n"
                    f"• *완료시간*: {now_str}\n"
                    f"• *반영행수*: {len(data_to_write)}행\n\n"
                    f"👉 <https://lookerstudio.google.com/u/0/reporting/ddd5366d-25fa-4aea-93ff-82b0f0c24450/page/p_wxro0jirzd|NEW DASHBOARD 2026 1.5ver>"
                )
                send_slack_message(msg)
            else:
                print(f"ℹ️ {now_kst.hour}시는 정기 알림 시간이 아니므로 슬랙은 생략합니다.")

    except Exception as e:
        send_slack_message(f"❌ 대시보드 업데이트 실패\n에러: {e}")

if __name__ == "__main__":
    main()
