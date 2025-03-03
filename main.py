import os
import sys
import pandas as pd
import io
import xml.etree.ElementTree as ET
import zipfile
import requests
from corpcode import fetch_corp_codes
from download import download_reports
from parsing import run_report_parsing   # renamed function
from company_update import update_all_company_data  # renamed function
from company_code import get_company_code  # imported from the new module

#################### main 함수 시작 ####################
def main():
    USE_CORP_CODE = True          # Step 1
    USE_DOWNLOAD_REPORTS = False  # Step 2
    USE_UPDATE_INFO = True        # Step 3
    USE_PARSING = False           # Step 4
    USE_RDMS_MAPPING = False      # Step 5

    print("====== 코드 사용 매뉴얼 ======")
    print("1. 기업코드 가져오기 (USE_CORP_CODE)" + " -----------------------------------> " + str(USE_CORP_CODE))
    print("2. 4종 보고서 다운로드 (USE_DOWNLOAD_REPORTS)" + " --------------------------> " + str(USE_DOWNLOAD_REPORTS))
    print("3. 고객사 정보 및 4종 보고서 업데이트 (USE_UPDATE_INFO)" + " -----------------> " + str(USE_UPDATE_INFO))
    print("4. 정보 parsing하기 (USE_PARSING)" + " -------------------------------------> " + str(USE_PARSING))
    print("5. 기존 DB 매핑 (USE_RDMS_MAPPING)" + " ------------------------------------> " + str(USE_RDMS_MAPPING))
    print("===================================")

    company_name = input("기업명을 입력하세요 (기본값: 현대오토에버):") or "현대오토에버"
    start_date = input("시작일(YYYYMMDD)을 입력하세요 (기본값: 20240101): ") or "20240101"
    end_date = input("종료일(YYYYMMDD)을 입력하세요 (기본값: 20241231): ") or "20241231"
    bsns_year = input("사업연도(YYYY)를 입력하세요 (기본값: 2024): ") or "2024"
    report_code = input("보고서 종류를 입력하세요 (기본값: 11011): ") or "11011"

    # 보고서 다운로드 옵션
    dynamic_option = input("전체 보고서 다운로드 옵션 사용 (y/n, 기본값: n): ") or "n"
    download_all = True if dynamic_option.lower() == "y" else False

    # --------------------- Step 1: 기업코드 가져오기 --------------------- 
    if USE_CORP_CODE:
        company_code = get_company_code(company_name)
        if not company_code:
            print("기업 정보를 찾지 못했습니다.")
            return
    else:
        company_code = "default_corp_code"

    # --------------------- Step 2: 4종 보고서 다운로드 --------------------- 
    if USE_DOWNLOAD_REPORTS:
        download_folder, report_contents = download_reports(company_name, company_code, start_date, end_date, download_all)
    else:
        download_folder = f"dart_reports/{company_code}"

    # --------------------- Step 3: 고객사 정보 업데이트 ---------------------
    if USE_UPDATE_INFO:
        import asyncio
        asyncio.run(
            update_all_company_data(
                company_name,
                company_code,
                start_date,
                end_date,
                bsns_year,
                report_code,
                debug=True
            )
        )
        company_info = {}  # 결과는 파일 저장으로 대체
    else:
        company_info = {}

    # --------------------- Step 4: 정보 parsing하기 ---------------------
    if USE_PARSING:
        use_openai = False  
        run_report_parsing(company_name, company_code, use_openai=use_openai)

    # --------------------- Step 5: 기존 DB 매핑 ---------------------
    if USE_RDMS_MAPPING:
        from rdms_mapper import map_to_rdms
        map_to_rdms(company_info)

    print("All tasks completed.")

if __name__ == "__main__":
    main()