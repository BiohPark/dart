import os
import requests
import pandas as pd
import asyncio

API_KEY = os.getenv("OPEN_DART_API_KEY")

async def fetch_financial_info(
    corp_code: str, # 고유번호
    bsns_year: str, # 사업연도
    reprt_code: str # 사업보고서
) -> pd.DataFrame:
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
    params = {
        "crtfc_key": API_KEY,
        "corp_code": corp_code,
        "bsns_year": bsns_year,
        "reprt_code": reprt_code
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return pd.json_normalize(data.get("list")) if data.get("status") == "000" else pd.DataFrame()

async def fetch_disclosure_info(
    corp_code: str,
    bgn_de: str,
    end_de: str
) -> pd.DataFrame:
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": API_KEY,
        "corp_code": corp_code,
        "bgn_de": bgn_de,
        "end_de": end_de
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return pd.json_normalize(data.get("list")) if data.get("status") == "000" else pd.DataFrame()

async def fetch_company_info(corp_code: str) -> pd.DataFrame:
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": API_KEY,
        "corp_code": corp_code
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return pd.DataFrame([data]) if data.get("status") == "000" else pd.DataFrame()