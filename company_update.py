import os
import requests
import pandas as pd
import asyncio
from company_code import get_company_code
from dart_api import (
    fetch_company_info, fetch_financial_info,
    fetch_financial_indicator, fetch_bz_stp, fetch_df_ocr, fetch_lwst_lg, fetch_rhsc_proc,
    fetch_mrgr_decsn, fetch_dvsn_decsn, fetch_bns_acqs_decsn, fetch_bns_trf_decsn,
    fetch_cap_incrs_sttus, fetch_alot_matter, fetch_tesstk_acqs_dsps_sttus,
    fetch_hyslr_sttus, fetch_hyslr_chg_sttus, fetch_mrhl_sttus, fetch_exctv_sttus, fetch_emp_sttus
)

# API 호출 구성을 모듈화한 함수
def build_api_calls(company_code, start_date, end_date, bsns_year, report_code):
    # 사용 플래그 정의
    USE_COMPANY_INFO       = True
    USE_FINANCIAL_INFO     = True
    USE_FIN_INDICATOR      = True
    USE_BZ_STP             = True
    USE_DF_OCR             = True
    USE_LWST_LG            = True
    USE_RHSC_PROC          = True
    USE_MRGR_DECSN         = True
    USE_DVSN_DECSN         = True
    USE_BNS_ACQS_DECSN     = True
    USE_BNS_TRF_DECSN      = True
    USE_EXTRA_INFO         = True
    USE_DOCUMENT           = True
    USE_CAP_INCRS_STTUS    = True
    USE_ALOT_MATTER        = True
    USE_TESSTK_ACQS_DSPS_STTUS = True
    USE_HYSLR_STTUS        = True
    USE_HYSLR_CHG_STTUS    = True
    USE_MRHL_STTUS         = True
    USE_EXCTV_STTUS        = True
    USE_EMP_STTUS          = True

    # 수동 Dart API 순서대로 API 호출 구성
    return [
        { "flag": USE_COMPANY_INFO, "func": fetch_company_info, "args": [company_code], "label": "기업정보", 
          "comment": "회사 API 사용" },
        { "flag": USE_FINANCIAL_INFO, "func": fetch_financial_info, "args": [company_code, bsns_year, report_code, "CFS"], "label": "재무정보",
          "comment": "FNLLT_SINGL_ACNT API 사용" },
        { "flag": USE_FIN_INDICATOR, "func": fetch_financial_indicator, "args": [company_code, bsns_year, report_code, "001"], "label": "재무지표",
          "comment": "FNLLT_SINGL_IND API 사용" },
        { "flag": USE_BZ_STP, "func": fetch_bz_stp, "args": [company_code, start_date, end_date], "label": "영업정지",
          "comment": "BZ_STP API 사용" },
        { "flag": USE_DF_OCR, "func": fetch_df_ocr, "args": [company_code, start_date, end_date], "label": "부도발생",
          "comment": "DF_OCR API 사용" },
        { "flag": USE_LWST_LG, "func": fetch_lwst_lg, "args": [company_code, start_date, end_date], "label": "소송제기",
          "comment": "LWST_LG API 사용" },
        { "flag": USE_RHSC_PROC, "func": fetch_rhsc_proc, "args": [company_code, start_date, end_date], "label": "회생절차",
          "comment": "RHSC_PROC_START_APP API 사용" },
        { "flag": USE_MRGR_DECSN, "func": fetch_mrgr_decsn, "args": [company_code, start_date, end_date], "label": "회사합병",
          "comment": "MRGR_DECSN API 사용" },
        { "flag": USE_DVSN_DECSN, "func": fetch_dvsn_decsn, "args": [company_code, start_date, end_date], "label": "회사분할",
          "comment": "DVSN_DECSN API 사용" },
        { "flag": USE_BNS_ACQS_DECSN, "func": fetch_bns_acqs_decsn, "args": [company_code, start_date, end_date], "label": "영업양수",
          "comment": "BNS_ACQS_DECSN API 사용" },
        { "flag": USE_BNS_TRF_DECSN, "func": fetch_bns_trf_decsn, "args": [company_code, start_date, end_date], "label": "영업양도",
          "comment": "BNS_TRF_DECSN API 사용" },
        { "flag": USE_CAP_INCRS_STTUS, "func": fetch_cap_incrs_sttus, "args": [company_code, bsns_year, report_code], "label": "증자감자현황",
          "comment": "CAP_INCRS_STTUS API 사용" },
        { "flag": USE_ALOT_MATTER, "func": fetch_alot_matter, "args": [company_code, bsns_year, report_code], "label": "배당사항",
          "comment": "ALOT_MATTER API 사용" },
        { "flag": USE_TESSTK_ACQS_DSPS_STTUS, "func": fetch_tesstk_acqs_dsps_sttus, "args": [company_code, bsns_year, report_code], "label": "자기주식현황",
          "comment": "TESSTK_ACQS_DSPS_STTUS API 사용" },
        { "flag": USE_HYSLR_STTUS, "func": fetch_hyslr_sttus, "args": [company_code, bsns_year, report_code], "label": "최대주주현황",
          "comment": "HYSLR_STTUS API 사용" },
        { "flag": USE_HYSLR_CHG_STTUS, "func": fetch_hyslr_chg_sttus, "args": [company_code, bsns_year, report_code], "label": "최대주주변동",
          "comment": "HYSLR_CHG_STTUS API 사용" },
        { "flag": USE_MRHL_STTUS, "func": fetch_mrhl_sttus, "args": [company_code, bsns_year, report_code], "label": "소액주주현황",
          "comment": "MRHL_STTUS API 사용" },
        { "flag": USE_EXCTV_STTUS, "func": fetch_exctv_sttus, "args": [company_code, bsns_year, report_code], "label": "임원현황",
          "comment": "EXCTV_STTUS API 사용" },
        { "flag": USE_EMP_STTUS, "func": fetch_emp_sttus, "args": [company_code, bsns_year, report_code], "label": "직원현황",
          "comment": "EMP_STTUS API 사용" },
    ]

# 데이터 프레임 저장을 모듈화한 함수
def save_dataframes(report_dir, company_name, labels, results, debug):
    combined = pd.concat(results, ignore_index=True)
    combined_file = os.path.join(report_dir, f"{company_name}_merged.csv")
    combined.to_csv(combined_file, index=False, encoding="utf-8-sig")
    print(f"모든 데이터가 합쳐져 {combined_file} 에 저장됨")
    
    if debug:
        # 개별 데이터 프레임 저장 (디버그 모드)
        for label, df in zip(labels, results):
            debug_file = os.path.join(report_dir, f"{company_name}_{label}.csv")
            df.to_csv(debug_file, index=False, encoding="utf-8-sig")
        print("디버그 모드: 개별 파일 저장됨")
    else:
        print("live 모드: 개발 중")

async def update_all_company_data(
    company_name: str,
    company_code: str,
    start_date: str,
    end_date: str,
    bsns_year: str = "",
    report_code: str = "",
    debug: bool = False
):
    report_dir = f"dart_data/{company_code}"
    os.makedirs(report_dir, exist_ok=True)

    # API 호출 구성 함수 호출
    api_calls = build_api_calls(company_code, start_date, end_date, bsns_year, report_code)

    tasks = []
    labels = []
    for call in api_calls:
        if call["flag"]:
            # API 함수 호출 (주석: 해당 API 사용)
            tasks.append(call["func"](*call["args"]))
            labels.append(call["label"])

    results = await asyncio.gather(*tasks)

    # 각 결과의 레코드 수 출력 (검증용)
    for label, df in zip(labels, results):
        print(f"{label}: {len(df)} 레코드")

    # 데이터 저장 함수 호출
    save_dataframes(report_dir, company_name, labels, results, debug)

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: (기본값: 현대오토에버)") or "현대오토에버"
    company_code = get_company_code(company_name)
    start_date = input("시작일(YYYYMMDD)을 입력하세요: (기본값: 20230101)") or "20230101"
    end_date = input("종료일(YYYYMMDD)을 입력하세요: (기본값: 20241231)") or "20241231"
    bsns_year = input("사업연도(YYYY)를 입력하세요 (기본값: 2023): ") or "2023"
    report_code = input("보고서 종류를 입력하세요 (기본값: 11011): ") or "11011"
    asyncio.run(update_all_company_data(company_name, company_code, start_date, end_date, bsns_year, report_code, debug=True))
