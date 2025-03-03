import pandas as pd

def get_company_code(company_name: str) -> str:
    """Retrieve company code from the corp_list.csv file."""
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
    company_code = corp_info["corp_code"]
    found_company = corp_info["corp_name"]
    print(f"검색된 기업: {found_company} (고유번호: {company_code})")
    return company_code
