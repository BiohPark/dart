import os
import requests
import pandas as pd
import asyncio

API_KEY = os.getenv("OPEN_DART_API_KEY")

# Added constants for DART_API_LIST and DART_API_DOCUMENT
DART_API_LIST = "https://opendart.fss.or.kr/api/list.json"
# 개발 참조: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001
# 설명: 공시 검색 API - 공시 유형별, 회사별, 날짜별 등 다양한 조건으로 검색.

DART_API_DOCUMENT = "https://opendart.fss.or.kr/api/document.xml"
# 개발 참조: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019003
# 설명: 공시서류원본파일 API - 공시보고서 원본 파일 제공.

# Define all endpoint URLs and reference guides from Manual_DartAPI.xlsx
ENDPOINTS = {
    # [기업 기본 정보]
    "COMPANY": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002
        "url": "https://opendart.fss.or.kr/api/company.json"
    },
    "CORPCODE": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019018
        "url": "https://opendart.fss.or.kr/api/corpCode.xml"
    },
    # [재무 정보]
    "FNLLT_SINGL_ACNT": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019016
        "url": "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
    },
    "FNLLT_SINGL_IND": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2022001
        "url": "https://opendart.fss.or.kr/api/fnlttSinglIndx.json"
    },
    # [최신 이슈 정보]
    "BZ_STP": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020020
        "url": "https://opendart.fss.or.kr/api/bzStp.json"
    },
    "DF_OCR": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020019
        "url": "https://opendart.fss.or.kr/api/dfOcr.json"
    },
    "LWST_LG": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020028
        "url": "https://opendart.fss.or.kr/api/lwstLg.json"
    },
    "RHSC_PROC_START_APP": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020021
        "url": "https://opendart.fss.or.kr/api/rhscProcStartApp.json"
    },
    "MRGR_DECSN": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020050
        "url": "https://opendart.fss.or.kr/api/mrgrDecsn.json"
    },
    "DVSN_DECSN": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020051
        "url": "https://opendart.fss.or.kr/api/dvsnDecsn.json"
    },
    "BNS_ACQS_DECSN": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020042
        "url": "https://opendart.fss.or.kr/api/bnsAcqsDecsn.json"
    },
    "BNS_TRF_DECSN": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020043
        "url": "https://opendart.fss.or.kr/api/bnsTrfDecsn.json"
    },
    # [정기보고서 주요정보]
    "CAP_INCRS_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019004
        "url": "https://opendart.fss.or.kr/api/capIncrsSttus.json"
    },
    "ALOT_MATTER": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019005
        "url": "https://opendart.fss.or.kr/api/alotMatter.json"
    },
    "TESSTK_ACQS_DSPS_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019006
        "url": "https://opendart.fss.or.kr/api/tesstkAcqsDspsSttus.json"
    },
    "HYSLR_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019007
        "url": "https://opendart.fss.or.kr/api/hyslrSttus.json"
    },
    "HYSLR_CHG_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019008
        "url": "https://opendart.fss.or.kr/api/hyslrChgSttus.json"
    },
    "MRHL_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019009
        "url": "https://opendart.fss.or.kr/api/mrhlSttus.json"
    },
    "EXCTV_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019010
        "url": "https://opendart.fss.or.kr/api/exctvSttus.json"
    },
    "EMP_STTUS": {
        # 개발 참조용: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019011
        "url": "https://opendart.fss.or.kr/api/empSttus.json"
    },
    "EXTRA": {
        # 개발 참조용: 별도 개발 가이드 참고
        "url": "https://opendart.fss.or.kr/api/extra.json"
    }
}

# Unified API call function replacing _fetch_data, _fetch_issue_info, _fetch_periodic_info
def _call_api(endpoint_key: str, params: dict, list_key: str = "list", xml: bool = False) -> pd.DataFrame:
    endpoint = ENDPOINTS.get(endpoint_key)
    if not endpoint:
        raise ValueError(f"Unknown endpoint key: {endpoint_key}")
    url = endpoint["url"]
    params["crtfc_key"] = API_KEY
    resp = requests.get(url, params=params)
    if xml:
        if resp.status_code == 200:
            df = pd.DataFrame([{"rcept_no": params.get("rcept_no"), "document": resp.text}])
        else:
            df = pd.DataFrame()
    else:
        try:
            data = resp.json()
        except Exception:
            data = {}
        if data.get("status") == "000":
            items = data.get(list_key) if list_key is not None else data
            df = pd.json_normalize(items) if items else pd.DataFrame()
        else:
            df = pd.DataFrame()
    print(f"{endpoint_key}: fetched {len(df)} records")
    return df

# Updated API functions using the unified _call_api

# DS003: 단일회사 주요계정 - now requires fs_div parameter
async def fetch_financial_info(company_code: str, bsns_year: str, report_code: str, fs_div: str) -> pd.DataFrame:
    params = {
        "corp_code": company_code,
        "bsns_year": bsns_year,
        "reprt_code": report_code,
        "fs_div": fs_div
    }
    return _call_api("FNLLT_SINGL_ACNT", params)
    
# DS001: 기업개황 now sends only required parameters (corp_code)
async def fetch_company_info(company_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code}  # corp_cls removed as per spec
    return _call_api("COMPANY", params, list_key=None)

# DS003: 단일회사 주요 재무지표 - now requires idx_cl_code parameter
async def fetch_financial_indicator(company_code: str, bsns_year: str, report_code: str, idx_cl_code: str) -> pd.DataFrame:
    params = {
        "corp_code": company_code,
        "bsns_year": bsns_year,
        "reprt_code": report_code,
        "idx_cl_code": idx_cl_code
    }
    return _call_api("FNLLT_SINGL_IND", params)

# DS005: 각 주요사항보고서 API now require bgn_de and end_de instead of page_count
async def fetch_bz_stp(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("BZ_STP", params)

async def fetch_df_ocr(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("DF_OCR", params)

async def fetch_lwst_lg(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("LWST_LG", params)

async def fetch_rhsc_proc(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("RHSC_PROC_START_APP", params)

async def fetch_mrgr_decsn(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("MRGR_DECSN", params)

async def fetch_dvsn_decsn(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("DVSN_DECSN", params)

async def fetch_bns_acqs_decsn(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("BNS_ACQS_DECSN", params)

async def fetch_bns_trf_decsn(company_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bgn_de": start_date, "end_de": end_date}
    return _call_api("BNS_TRF_DECSN", params)

# DS002: 증자(감자) 현황 - now requires bsns_year and report_code
async def fetch_cap_incrs_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("CAP_INCRS_STTUS", params)

# DS002: 배당에 관한 사항 - now requires bsns_year and report_code
async def fetch_alot_matter(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("ALOT_MATTER", params)

# DS002: 자기주식 취득 및 처분 현황 - now requires bsns_year and report_code
async def fetch_tesstk_acqs_dsps_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("TESSTK_ACQS_DSPS_STTUS", params)

# DS002: 최대주주 현황 - now requires bsns_year and report_code
async def fetch_hyslr_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("HYSLR_STTUS", params)

# DS002: 최대주주 변동현황 - now requires bsns_year and report_code
async def fetch_hyslr_chg_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("HYSLR_CHG_STTUS", params)

# DS002: 소액주주 현황 - now requires bsns_year and report_code
async def fetch_mrhl_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("MRHL_STTUS", params)

# DS002: 임원 현황 - now requires bsns_year and report_code
async def fetch_exctv_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("EXCTV_STTUS", params)

# DS002: 직원 현황 remains with bsns_year and report_code
async def fetch_emp_sttus(company_code: str, bsns_year: str, report_code: str) -> pd.DataFrame:
    params = {"corp_code": company_code, "bsns_year": bsns_year, "reprt_code": report_code}
    return _call_api("EMP_STTUS", params)

if __name__ == "__main__":
    import asyncio
    # Test one sample API call
    company_code = "00362441"
    bsns_year = "2024"
    report_code = "11011"
    result = asyncio.run(fetch_emp_sttus(company_code, bsns_year, report_code))
    print(result)