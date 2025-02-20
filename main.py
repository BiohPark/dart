import os
import sys
import pandas as pd
import io
import xml.etree.ElementTree as ET
import zipfile
import requests
import corpcode
import download
import parsing
from corpcode import fetch_corp_codes
from download import download_reports
from parsing import parse_reports

def main():
    # 1. 기업코드(회사 목록) 가져오기
    # fetch_corp_codes()

    # 2. 보고서 다운로드 (사업보고서, 분기보고서, 반기보고서, 감사보고서)
    # download_reports(company_name)

    # 3. 보고서 파싱 및 요약
    parse_reports(company_name, use_openai=False) # use_openai=False: 직접 파싱, True: OpenAI 사용

    # 모든 작업 완료 메시지 출력
    print("All tasks completed.")

if __name__ == "__main__":
    company_name = "현대오토에버"
    main()