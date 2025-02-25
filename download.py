import os
import requests
import zipfile
import xml.etree.ElementTree as ET

API_KEY = os.getenv("OPEN_DART_API_KEY")
if not API_KEY:
    print("환경 변수 OPEN_DART_API_KEY를 설정해야 합니다.")

def download_reports(company_name: str, corp_code: str) -> (str, dict):
    # 고유번호(corp_code)를 직접 사용
    print(f"입력된 고유번호: {corp_code}")

    # 폴더명은 고유번호로 생성
    download_folder = f"dart_reports/{corp_code}"
    os.makedirs(download_folder, exist_ok=True)

    # Step 2: 최신 공시 목록 검색
    disclosure_url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": API_KEY,
        "corp_code": corp_code,
        "bgn_de": "20230101",
        "page_no": "1",
        "page_count": "100"
    }
    response = requests.get(disclosure_url, params=params)
    data = response.json()

    # Step 3: 최신 공시 중 보고서 유형당 최신 1개 선택
    target_reports = {"사업보고서": None, "반기보고서": None, "분기보고서": None, "감사보고서": None}
    if "list" in data:
        for report in data["list"]:
            report_nm = report["report_nm"]
            for target in target_reports.keys():
                if target in report_nm and target_reports[target] is None:
                    target_reports[target] = report
    else:
        print("공시 목록을 불러오지 못했습니다.")
        return download_folder, {}

    print("\n📄 보고서 원본 파일 다운로드 및 압축 해제:")

    report_contents = {"사업보고서": "", "반기보고서": "", "분기보고서": "", "감사보고서": ""}
    for report_type, report in target_reports.items():
        if report:
            rcp_no = report["rcept_no"]
            report_nm = report["report_nm"]
            report_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
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
                extract_path = os.path.join(download_folder, report_type)
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"✅ {report_nm} 다운로드 완료")
                print(f"   📂 저장 폴더: {extract_path}")
                print(f"   🔗 원본 확인: {report_url}")
                xml_files = [f for f in os.listdir(extract_path) if f.endswith(".xml")]
                if xml_files:
                    xml_path = os.path.join(extract_path, xml_files[0])
                    try:
                        with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                            text_content = f.read()
                        text_content = text_content.replace("\n", " ").strip()
                        report_contents[report_type] = text_content
                    except Exception as e:
                        print(f"❌ {report_nm} XML 파일 읽기 실패: {e}")
            else:
                print(f"❌ {report_nm} 다운로드 실패")
    return download_folder, report_contents

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: ")
    corp_code = input("🔍 고유번호를 입력하세요: ")
    download_folder, report_contents = download_reports(company_name, corp_code)
    print("\n📢 보고서 내용 미리보기 (앞 100자):")
    for report_type, content in report_contents.items():
        if content:
            print(f"\n🔹 {report_type}:")
            print(content[:100])
        else:
            print(f"\n🔹 {report_type}: 내용 없음")

