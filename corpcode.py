import os
import requests
import zipfile
import xml.etree.ElementTree as ET
import io
import pandas as pd

API_KEY = os.getenv("OPEN_DART_API_KEY")
if not API_KEY:
    print("환경 변수 OPEN_DART_API_KEY를 설정해야 합니다.")
    
def fetch_corp_codes():
    # API 요청 URL
    url = "https://opendart.fss.or.kr/api/corpCode.xml"

    # 요청 파라미터
    params = {
        "crtfc_key": API_KEY
    }

    # API 요청
    response = requests.get(url, params=params)

    # 정상 응답 확인
    if response.status_code == 200:
        # 메모리에서 ZIP 파일 읽기
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open("CORPCODE.xml") as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()

        # XML 데이터 파싱
        corp_list = []
        for corp in root.findall("list"):
            corp_code = corp.find("corp_code").text.strip()
            corp_name = corp.find("corp_name").text.strip()
            stock_code = corp.find("stock_code").text.strip()
            modify_date = corp.find("modify_date").text.strip()
            corp_list.append([corp_code, corp_name, stock_code, modify_date])

        # DataFrame으로 변환
        df = pd.DataFrame(corp_list, columns=["corp_code", "corp_name", "stock_code", "modify_date"])

        # CSV 파일로 저장 (필요 시)
        df.to_csv("corp_list.csv", index=False, encoding="utf-8-sig")

        # 상위 10개 데이터 출력
        # print(df.head(10))

    else:
        # 오류 메시지 출력
        print("Error:", response.status_code)
