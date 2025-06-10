import pandas as pd
import os
import numpy as np

def preprocess_sheet_long_format(df):
    """
    [단일 시트 전처리] - Long Format
    1. 불필요한 열 제거
    2. 대체값이 존재하면 측정값 보완
    3. 측정일시, 측정항목 기준으로 pivot (Wide-format 변환)
    4. 시간단위 평균으로 변환
    5. 결측값 보간
    """
    # 열 이름 통일
    df.columns = df.columns.str.strip().str.replace('\n', '').str.replace(' ', '')

    # 유효 열만 선택
    df = df[['측정일시', '측정항목', '측정값', '대체값']]

    # datetime 변환
    df['측정일시'] = pd.to_datetime(df['측정일시'], errors='coerce')
    df = df.dropna(subset=['측정일시', '측정항목'])

    # 대체값 우선 반영
    df['값'] = df['대체값'].combine_first(df['측정값'])

    # 시간 내림 (30분 → 시간 단위)
    df['측정일시'] = df['측정일시'].dt.floor('H')

    # 피벗 (항목별 열 생성)
    pivoted = df.pivot_table(index='측정일시', columns='측정항목', values='값', aggfunc='mean')

    # 결측값 선형 보간 + 앞뒤 채움
    pivoted = pivoted.interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')

    pivoted.reset_index(inplace=True)
    return pivoted


def filter_abnormal_data(df):
    """
    [비정상 데이터 필터링]
    - 산소농도 > 10 제거
    - 배기온도 - 대기온도 차이 < 20 제거
    """
    df_filtered = df.copy()

    # 산소농도 조건
    for col in df.columns:
        if '산소' in col:
            df_filtered = df_filtered[df_filtered[col] <= 10]

    # 온도 차이 조건
    exhaust_temp = None
    air_temp = None
    for col in df.columns:
        if '배기' in col and '온도' in col:
            exhaust_temp = col
        if ('대기' in col or '외기' in col) and '온도' in col:
            air_temp = col

    if exhaust_temp and air_temp:
        temp_diff = np.abs(df_filtered[exhaust_temp] - df_filtered[air_temp])
        df_filtered = df_filtered[temp_diff >= 20]

    return df_filtered


def save_by_item(df, save_dir, year):
    """
    [CSV 저장] - 측정 항목별 저장
    """
    os.makedirs(save_dir, exist_ok=True)
    for col in df.columns:
        if col == '측정일시':
            continue
        item_df = df[['측정일시', col]].copy()
        item_df.rename(columns={col: '값'}, inplace=True)
        item_df.to_csv(os.path.join(save_dir, f"{year}_{col}.csv"), index=False)


def process_excel_long_format(file_path, site_name):
    """
    [전체 엑셀 처리]
    - 시트별로 전처리
    - 연도별 통합 및 저장
    """
    xls = pd.ExcelFile(file_path)
    sheet_by_year = {}

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        clean_df = preprocess_sheet_long_format(df)

        # 연도 추출 (앞 2자리 기준)
        year_prefix = sheet[:2]
        if not year_prefix.isnumeric():
            continue
        year_full = '20' + year_prefix
        sheet_by_year.setdefault(year_full, []).append(clean_df)

    for year, dfs in sheet_by_year.items():
        merged = pd.concat(dfs, ignore_index=True)
        filtered = filter_abnormal_data(merged)
        save_by_item(filtered, f"./processed/{site_name}/{year}", year)


# ✅ 실제 실행 예시
process_excel_long_format("신보령.xlsx", "신보령")
process_excel_long_format("보령.xlsx", "보령")
process_excel_long_format("신서천.xlsx", "신서천")
