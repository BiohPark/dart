import os
import requests
import zipfile
import xml.etree.ElementTree as ET
from company_code import get_company_code
from dart_api import DART_API_LIST, DART_API_DOCUMENT

# New helper function to sanitize filenames
def sanitize_filename(filename: str) -> str:
    # 파일 이름에서 특수 문자와 슬래시를 제거
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

API_KEY = os.getenv("OPEN_DART_API_KEY")
if not API_KEY:
    print("환경 변수 OPEN_DART_API_KEY를 설정해야 합니다.")

def download_reports(company_name: str, company_code: str, bgn_de: str, end_de: str, download_all: bool = False) -> (str, dict):
    # 고유번호(company_code)를 직접 사용
    print(f"입력된 고유번호: {company_code}")

    # 폴더명은 고유번호로 생성
    download_folder = f"dart_reports/{company_code}"
    os.makedirs(download_folder, exist_ok=True)

    # Step 2: 최신 공시 목록 검색
    params = {
        "crtfc_key": API_KEY,
        "corp_code": company_code,
        "bgn_de": bgn_de,
        "end_de": end_de,
        "page_no": "1",
        "page_count": "100"
    }
    response = requests.get(DART_API_LIST, params=params)
    data = response.json()

    if download_all:
        report_contents = {}
        if "list" in data:
            print("\n📄 보고서 원본 파일 다운로드 및 압축 해제:")
            for report in data["list"]:
                rcp_no = report["rcept_no"]
                report_nm = report["report_nm"]
                report_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
                document_params = {
                    "crtfc_key": API_KEY,
                    "rcept_no": rcp_no
                }
                doc_response = requests.get(DART_API_DOCUMENT, params=document_params)
                if doc_response.status_code == 200:
                    zip_path = os.path.join(download_folder, f"{sanitize_filename(report_nm)}_{rcp_no}.zip")
                    with open(zip_path, "wb") as f:
                        f.write(doc_response.content)
                    # Extract XML file from zip directly into download_folder with new file name
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for file in zip_ref.namelist():
                            if file.endswith(".xml"):
                                data_bytes = zip_ref.read(file)
                                new_filename = sanitize_filename(f"{company_name}_{report_nm}")
                                xml_path = os.path.join(download_folder, new_filename + ".xml")
                                with open(xml_path, "wb") as f:
                                    f.write(data_bytes)
                                report_contents[rcp_no] = xml_path
                                break
                    print(f"✅ {report_nm} 다운로드 완료")
                    print(f"   📂 저장 폴더: {download_folder}")
                    print(f"         파일 이름: {new_filename}")
                    print(f"   🔗 원본 확인: {report_url}")
                else:
                    print(f"❌ {report_nm} 다운로드 실패")
        else:
            print("공시 목록을 불러오지 못했습니다.")
            return download_folder, {}
    else:
        # 기존 고정 4종 보고서 다운로드 로직
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
                report_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"   # 바로가기 URL 생성
                document_params = {
                    "crtfc_key": API_KEY,
                    "rcept_no": rcp_no
                }
                doc_response = requests.get(DART_API_DOCUMENT, params=document_params)
                if doc_response.status_code == 200:
                    zip_path = os.path.join(download_folder, f"{sanitize_filename(report_nm)}_{rcp_no}.zip")
                    with open(zip_path, "wb") as f:
                        f.write(doc_response.content)
                    # Extract XML file directly into download_folder with new file name
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for file in zip_ref.namelist():
                            if file.endswith(".xml"):
                                data_bytes = zip_ref.read(file)
                                new_filename = sanitize_filename(f"{company_name}_{report_nm}")
                                xml_path = os.path.join(download_folder, new_filename + ".xml")
                                with open(xml_path, "wb") as f:
                                    f.write(data_bytes)
                                report_contents[report_type] = xml_path
                                break
                    print(f"✅ {report_nm} 다운로드 완료")
                    print(f"   📂 저장 폴더: {download_folder}")
                    print(f"         파일 이름: {new_filename}")
                    print(f"   🔗 원본 확인: {report_url}")
                else:
                    print(f"❌ {report_nm} 다운로드 실패")
    return download_folder, report_contents

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: (기본값: 현대오토에버)") or "현대오토에버"
    company_code = get_company_code(company_name)
    bgn_de = input("시작일(YYYYMMDD)을 입력하세요: (기본값: 20240101)") or "20240101"
    end_de = input("종료일(YYYYMMDD)을 입력하세요: (기본값: 20241231)") or "20241231"
    download_all = input("모든 보고서를 다운로드 하시겠습니까? (y/n): ").lower() == 'y'
    download_folder, report_contents = download_reports(company_name, company_code, bgn_de, end_de, download_all)
    print("\n📢 보고서 내용 미리보기 (앞 100자):")
    for report_type, path in report_contents.items():
        if path:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                print(f"\n🔹 {report_type}:")
                print(content[:100])
            except Exception as e:
                print(f"\n🔹 {report_type}: 파일 읽기 실패: {e}")
        else:
            print(f"\n🔹 {report_type}: 내용 없음")

