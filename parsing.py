import os
import openai
import xml.etree.ElementTree as ET

def load_xml_files(base_dir: str, report_category: str):
    """Load XML file contents from the specified report directory."""
    xml_contents = []
    report_folder = os.path.join(base_dir, report_category)
    if os.path.exists(report_folder):
        for file_name in os.listdir(report_folder):
            if file_name.endswith(".xml"):
                xml_path = os.path.join(report_folder, file_name)
                with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
                    xml_contents.append(f.read())
    return xml_contents

def summarize_reports(company_name: str, company_code: str, use_openai: bool = False):
    """Generate summaries for reports using either the OpenAI API or direct XML parsing."""
    report_summaries = []
    base_dir = f"dart_reports/{company_code}"

    if use_openai:
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            print("환경 변수 OPENAI_API_KEY를 설정해야 합니다.")
            return report_summaries
        for report_category in ["사업보고서", "분기보고서", "반기보고서", "감사보고서"]:
            xml_contents = load_xml_files(base_dir, report_category)
            for content in xml_contents:
                try:
                    client = openai.OpenAI(api_key=API_KEY)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
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
                    report_summaries.append(response['choices'][0]['message']['content'].strip())
                except Exception as e:
                    report_summaries.append(f"Error: {e}")
    else:
        for report_category in ["사업보고서", "분기보고서", "반기보고서", "감사보고서"]:
            xml_contents = load_xml_files(base_dir, report_category)
            for content in xml_contents:
                try:
                    root = ET.fromstring(content)
                    customer = root.findtext(".//고객사")
                    website = root.findtext(".//홈페이지")
                    revenue = root.findtext(".//매출액")
                    products = root.findtext(".//제품")
                    summary = f"고객사: {customer}, 홈페이지: {website}, 매출액: {revenue}, 제품: {products}"
                    report_summaries.append(summary)
                except Exception as e:
                    report_summaries.append(f"Error: {e}")
    return report_summaries

def run_report_parsing(company_name: str, company_code: str, use_openai: bool = False):
    """Parse and print report summaries."""
    summaries = summarize_reports(company_name, company_code, use_openai)
    for summary in summaries:
        print(summary)

if __name__ == "__main__":
    company_name = input("🔍 기업명을 입력하세요: ")
    company_code = input("🔍 고유번호를 입력하세요: ")
    run_report_parsing(company_name, company_code)
