import os
import sys
import pandas as pd
import io
import xml.etree.ElementTree as ET
import zipfile
import requests
from corpcode import fetch_corp_codes
from download import download_reports
from parsing import parse_reports
from company_update import update_company_info

def get_corp_code(company_name: str) -> str:
    # corp_list.csv 파일에서 회사명을 검색하여 회사 코드 찾기
    corp_list_file = "corp_list.csv"
    df = pd.read_csv(corp_list_file, encoding="utf-8-sig", dtype=str)
    exact_match = df[df["corp_name"] == company_name]
    if not exact_match.empty:
        corp_info = exact_match.iloc[0]
    else:
        contains_match = df[df["corp_name"].str.contains(company_name, case=False, na=False)]
        if contains_match.empty:
            print(f"{company_name}에 대한 기업 정보가 없습니다.")
            return None
        corp_info = contains_match.iloc[0]
    corp_code = corp_info["corp_code"]
    found_company = corp_info["corp_name"]
    print(f"검색된 기업: {found_company} (고유번호: {corp_code})")
    return corp_code

def main():
    company_name = "현대오토에버" # input("기업명을 입력하세요: ")
    corp_code = get_corp_code(company_name)
    if not corp_code:
        print("기업 정보를 찾을 수 없습니다.")
        return

    bgn_de = input("시작일(YYYYMMDD)을 입력하세요 (기본값: 20230101): ") or "20230101"
    end_de = input("종료일(YYYYMMDD)을 입력하세요 (기본값: 20231231): ") or "20231231"
    bsns_year = input("사업연도(YYYY)를 입력하세요 (기본값: 2023): ") or "2023"
    reprt_code = input("보고서 종류를 입력하세요 (기본값: 11011): ") or "11011" # 11011: 사업보고서

    update_company_info(company_name, corp_code)

    import asyncio
    from company_update import update_all_info
    asyncio.run(
        update_all_info(
            company_name,
            corp_code,
            bgn_de,
            end_de,
            bsns_year=bsns_year,
            reprt_code=reprt_code,
            debug=True
        )
    )
    print("All tasks completed.")

if __name__ == "__main__":
    main()