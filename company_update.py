import os
import requests
import pandas as pd
import asyncio
from dart_api import fetch_company_info, fetch_disclosure_info, fetch_financial_info

def update_company_info(company_name: str, corp_code: str):
    API_KEY = os.getenv("OPEN_DART_API_KEY")
    if not API_KEY:
        print("환경 변수 OPEN_DART_API_KEY를 설정해야 합니다.")
        return
    # Ensure the report directory exists
    report_dir = f"dart_reports/{corp_code}"
    os.makedirs(report_dir, exist_ok=True)
    
    api_url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        'crtfc_key': API_KEY,
        'corp_code': corp_code
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == '000':
            df = pd.DataFrame([data])
            csv_filename = os.path.join(report_dir, f"{company_name}_info.csv")
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"Company information saved to {csv_filename}")
        else:
            print(f"Error fetching company information: {data.get('message', 'No message')}")
    else:
        print(f"HTTP request failed with status code {response.status_code}")

async def update_all_info(
    company_name: str,
    corp_code: str,
    bgn_de: str,
    end_de: str,
    bsns_year: str = "",      # optional, if needed
    reprt_code: str = "",     # optional, if needed
    debug: bool = False
):
    # Ensure the report directory exists
    report_dir = f"dart_reports/{corp_code}"
    os.makedirs(report_dir, exist_ok=True)
    
    tasks = [
        fetch_company_info(corp_code),
        fetch_disclosure_info(corp_code, bgn_de, end_de),
        fetch_financial_info(corp_code, bsns_year, reprt_code)
    ]
    results = await asyncio.gather(*tasks)
    # 합치기
    combined = pd.concat(results, ignore_index=True)
    combined_file = os.path.join(report_dir, f"{company_name}_merged.csv")
    combined.to_csv(combined_file, index=False, encoding="utf-8-sig")
    print(f"All data combined and saved to {combined_file}")

    if debug:
        for df, name in zip(results, ["기업정보.csv", "공시정보.csv", "재무정보.csv"]):
            debug_file = os.path.join(report_dir, name)
            df.to_csv(debug_file, index=False, encoding="utf-8-sig")
        print("Debug mode: individual files saved.")

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: ")
    corp_code = input("🔍 고유번호를 입력하세요: ")
    bgn_de = input("시작일(YYYYMMDD)을 입력하세요: ")
    end_de = input("종료일(YYYYMMDD)을 입력하세요: ")
    # 필요한 경우 년도와 보고서 코드 등도 입력받을 수 있습니다.
    asyncio.run(update_all_info(company_name, corp_code, bgn_de, end_de, debug=True))
