import requests
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

# API key for DART Open API
API_KEY = "cc2aad92b1dd4414c0f3a66e9e1bc39263e3c77a"
# Base URL for fetching company information
BASE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"

def get_company_info(company_name):
    # Parameters for the API request
    params = {
        'crtfc_key': API_KEY
    }
    # Make the API request
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        # Unzip the response content
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            with z.open(z.namelist()[0]) as f:
                # Parse the XML content
                tree = ET.parse(f)
                root = tree.getroot()
                # Search for the company by name
                for company in root.findall('list'):
                    if company.find('corp_name').text == company_name:
                        return company.find('corp_code').text
                return "Company not found"
    else:
        return f"HTTP Error: {response.status_code}"

if __name__ == "__main__":
    # Example company name
    company_name = "세아제강"
    # Get the company code
    corp_code = get_company_info(company_name)
    # Print the result
    print(f"Company: {company_name}, Corp Code: {corp_code}")
