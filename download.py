import requests
import pandas as pd
import os
import zipfile
import xml.etree.ElementTree as ET

# OpenDART API 키
API_KEY = "cc2aad92b1dd4414c0f3a66e9e1bc39263e3c77a"

# Step 1: 조회할 회사명 설정 (여기에 직접 입력)
company_name = "현대오토에버"  # 원하는 회사명 입력

# corp_list.csv 파일에서 회사명을 검색하여 회사 코드 찾기
corp_list_file = "corp_list.csv"

# dtype=str을 사용하여 고유번호 앞의 "00"이 유지되도록 함
df = pd.read_csv(corp_list_file, encoding="utf-8-sig", dtype=str)

# 1. 회사명이 완전히 일치하는 경우 우선 선택
exact_match = df[df["corp_name"] == company_name]

if not exact_match.empty:
    corp_info = exact_match.iloc[0]
else:
    # 2. 포함된 회사명을 찾음 (대소문자 무시)
    contains_match = df[df["corp_name"].str.contains(company_name, case=False, na=False)]

    if contains_match.empty:
        print(f"{company_name}에 대한 기업 정보가 없습니다.")
        exit()

    corp_info = contains_match.iloc[0]

corp_code = corp_info["corp_code"]
found_company = corp_info["corp_name"]
print(f"검색된 기업: {found_company} (고유번호: {corp_code})")

# Step 2: 최신 공시 목록 검색 (2023년 이후)
disclosure_url = "https://opendart.fss.or.kr/api/list.json"

params = {
    "crtfc_key": API_KEY,
    "corp_code": corp_code,
    "bgn_de": "20230101",  # 시작일 (2023년 1월 1일)
    "page_no": "1",
    "page_count": "100"  # 최근 100개 공시 검색
}

response = requests.get(disclosure_url, params=params)
data = response.json()

# Step 3: 최신 공시 중 사업보고서, 반기보고서, 분기보고서 각 1개만 선택
target_reports = {"사업보고서": None, "반기보고서": None, "분기보고서": None}

if "list" in data:
    for report in data["list"]:
        report_nm = report["report_nm"]
        for target in target_reports.keys():
            if target in report_nm and target_reports[target] is None:
                target_reports[target] = report  # 가장 최신 보고서만 저장
else:
    print("공시 목록을 불러오지 못했습니다.")
    exit()

# Step 4: 원본 파일(ZIP) 다운로드 및 압축 해제
download_folder = f"dart_reports/{found_company}"
os.makedirs(download_folder, exist_ok=True)

print("\n📄 보고서 원본 파일 다운로드 및 압축 해제:")

# 보고서 내용 저장 변수
report_contents = {"사업보고서": "", "반기보고서": "", "분기보고서": ""}

for report_type, report in target_reports.items():
    if report:
        rcp_no = report["rcept_no"]
        report_nm = report["report_nm"]
        report_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"  # 원본 확인 URL

        # 공시 원본 파일 다운로드 API
        document_url = "https://opendart.fss.or.kr/api/document.xml"
        document_params = {
            "crtfc_key": API_KEY,
            "rcept_no": rcp_no
        }

        doc_response = requests.get(document_url, params=document_params)

        if doc_response.status_code == 200:
            zip_path = os.path.join(download_folder, f"{report_nm}_{rcp_no}.zip")
            with open(zip_path, "wb") as f:
                f.write(doc_response.content)

            # ZIP 압축 해제
            extract_path = os.path.join(download_folder, f"{report_nm}_{rcp_no}")
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            print(f"✅ {report_nm} 다운로드 완료")
            print(f"   📂 저장 폴더: {extract_path}")
            print(f"   🔗 원본 확인: {report_url}")

            # Step 5: XML 파일 읽기 및 내용 추출 (파싱 없이 단순 Read)
            xml_files = [f for f in os.listdir(extract_path) if f.endswith(".xml")]
            if xml_files:
                xml_path = os.path.join(extract_path, xml_files[0])
                try:
                    # XML을 직접 텍스트로 읽기
                    with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                        text_content = f.read()

                    # 필요 없는 공백 및 개행 제거
                    text_content = text_content.replace("\n", " ").strip()

                    # 해당 보고서 유형의 변수에 저장
                    report_contents[report_type] = text_content

                except Exception as e:
                    print(f"❌ {report_nm} XML 파일 읽기 실패: {e}")

        else:
            print(f"❌ {report_nm} 다운로드 실패")

# Step 6: 각 보고서의 앞 100자 출력
print("\n📢 보고서 내용 미리보기 (앞 50자):")
for report_type, content in report_contents.items():
    if content:
        print(f"\n🔹 {report_type}:")
        print(content[:50])  # 앞 50자 출력
    else:
        print(f"\n🔹 {report_type}: 내용 없음")

