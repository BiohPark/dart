import pandas as pd

def map_to_rdms(company_info):
    """
    RDMS 매핑 함수
    - 기업 정보를 바탕으로 RDBMS에 데이터를 입력할 SQL 코드를 생성하는 프레임입니다.
    - 실제 데이터베이스 연동은 이후 구현 예정입니다.
    """
    # 전달받은 기업 정보가 DataFrame이면 첫 번째 레코드를 사용, dict이면 그대로 사용
    if isinstance(company_info, pd.DataFrame):
        record = company_info.iloc[0].to_dict()
    elif isinstance(company_info, dict):
        record = company_info
    else:
        print("유효한 기업 정보가 제공되지 않았습니다.")
        return

    # 예시 SQL 코드 생성 (실제 테이블, 컬럼명에 따라 조정 필요)
    corp_code = record.get('corp_code', '')
    company_name = record.get('company_name', '')
    sql = f"INSERT INTO companies (corp_code, company_name) VALUES ('{corp_code}', '{company_name}');"
    
    print("생성된 SQL 코드 (RDBMS 매핑 예시):")
    print(sql)
    # TODO: 실제 DB 연결 및 SQL 실행 로직 구현
