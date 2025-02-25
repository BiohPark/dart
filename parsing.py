import os
import openai
import xml.etree.ElementTree as ET

def read_xml_files(base_folder_path: str, report_type: str):
    # XML 파일 읽기
    xml_contents = []
    report_folder_path = os.path.join(base_folder_path, report_type)
    if os.path.exists(report_folder_path):
        for file_name in os.listdir(report_folder_path):
            if file_name.endswith(".xml"):
                xml_path = os.path.join(report_folder_path, file_name)
                with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                    xml_contents.append(f.read())
    return xml_contents

def parse_and_summarize(company_name: str, corp_code: str, use_openai: bool = False):
    summaries = []
    base_folder_path = f"dart_reports/{corp_code}"

    # OpenAI를 사용하는 경우 (chatGPT API), ChatGPT를 사용하여 요약
    if use_openai:
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            print("환경 변수 OPENAI_API_KEY를 설정해야 합니다.")
            return summaries

        for report_type in ["사업보고서", "분기보고서", "반기보고서", "감사보고서"]:
            xml_contents = read_xml_files(base_folder_path, report_type)
            for content in xml_contents: # xml_contents: xml 파일 내용
                try:
                    client = openai.OpenAI(api_key=API_KEY)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo", # gpt-4o-mini
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "당신은 판매하는 회사의 품질 담당자입니다. "
                                    "이 문서들을 read해서 고객사, 홈페이지, 매출액, 제품을 뽑아 줘."
                                )
                            },
                            {"role": "user", "content": content}
                        ]
                    )
                    summaries.append(response['choices'][0]['message']['content'].strip())
                except Exception as e:
                    summaries.append(f"Error: {e}")

    # OpenAI를 사용하지 않는 경우 (직접 파싱), XML 파일을 직접 읽어서 요약
    else:
        for report_type in ["사업보고서", "분기보고서", "반기보고서", "감사보고서"]:
            xml_contents = read_xml_files(base_folder_path, report_type)
            for content in xml_contents:
                try:
                    root = ET.fromstring(content)
                    customer = root.findtext(".//고객사")
                    website = root.findtext(".//홈페이지")
                    revenue = root.findtext(".//매출액")
                    products = root.findtext(".//제품")

                    summary = f"고객사: {customer}, 홈페이지: {website}, 매출액: {revenue}, 제품: {products}"
                    summaries.append(summary)
                except Exception as e:
                    summaries.append(f"Error: {e}")

    return summaries

def parse_reports(company_name: str, corp_code: str, use_openai: bool = False):
    # 보고서 파싱 및 요약
    summaries = parse_and_summarize(company_name, corp_code, use_openai)

    # 요약 출력
    for summary in summaries:
        print(summary)

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: ")
    corp_code = input("🔍 고유번호를 입력하세요: ")
    parse_reports(company_name, corp_code)
