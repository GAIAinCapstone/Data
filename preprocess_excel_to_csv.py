import os
import pandas as pd
from glob import glob
from collections import defaultdict

def preprocess_excel_to_csv(filepath, intermediate_root):
    """
    엑셀 파일을 시트별 전처리 → CSV 저장 (대체값 → 측정값, 결측 보간)
    """
    if not os.path.exists(filepath):
        print(f"❌ 파일 없음: {filepath}")
        return

    xls = pd.ExcelFile(filepath)
    filename = os.path.splitext(os.path.basename(filepath))[0]
    output_dir = os.path.join(intermediate_root, filename.replace(" ", "_"))
    os.makedirs(output_dir, exist_ok=True)

    for sheet_name in xls.sheet_names:
        try:
            df = xls.parse(sheet_name)
        except Exception as e:
            print(f"⚠️ 시트 '{sheet_name}' 파싱 실패: {e}")
            continue

        for col in df.columns:
            if '측정값' in col:
                alt_col = col.replace('측정값', '대체값')
                if alt_col in df.columns:
                    if not df[alt_col].dropna().empty:
                        df[col] = df[alt_col].combine_first(df[col])
                    df.drop(columns=[alt_col], inplace=True)

        numeric_cols = df.select_dtypes(include='number').columns
        df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='both')

        save_name = f"{filename}_{sheet_name}.csv".replace(" ", "_")
        save_path = os.path.join(output_dir, save_name)
        df.to_csv(save_path, index=False)

    print(f"✅ {filename}: {len(xls.sheet_names)}개 시트 → CSV 전처리 완료")

def extract_year(filename):
    for part in filename.split("_"):
        if "년" in part:
            return part.replace("년", "")
    return None

def process_all_years(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_files = glob(os.path.join(input_dir, "*.csv"))
    files_by_year = defaultdict(list)

    for f in csv_files:
        year = extract_year(os.path.basename(f))
        if year:
            files_by_year[year].append(f)

    for year, file_list in files_by_year.items():
        df_all = pd.concat([pd.read_csv(f) for f in sorted(file_list)], ignore_index=True)
        df_all.columns = df_all.columns.str.strip().str.replace("\n", "").str.replace(" ", "")
        df_all.rename(columns={"측정항목": "항목", "측정값": "값", "측정일시": "일시"}, inplace=True)
        df_all["일시"] = pd.to_datetime(df_all["일시"])

        pivot_df = df_all.pivot_table(index="일시", columns="항목", values="값", aggfunc="mean").reset_index()
        pivot_df = pivot_df.sort_values("일시")

        pollutant_cols = pivot_df.columns.drop("일시")
        pivot_df[pollutant_cols] = pivot_df[pollutant_cols].apply(pd.to_numeric, errors="coerce")
        pivot_df[pollutant_cols] = pivot_df[pollutant_cols].interpolate(method="linear", limit_direction="both")

        for col in pollutant_cols:
            save_path = os.path.join(output_dir, f"{col}_{year}.csv")
            pivot_df[["일시", col]].dropna().to_csv(save_path, index=False)

        print(f"✅ {year}년 오염물질별 전처리 완료: {', '.join(pollutant_cols)}")

# 전체 실행
if __name__ == "__main__":
    excel_files = [
        "보령 오염물질(TSP, SOx, NOx).xlsx",
        "보령 추가 데이터(O₂, FL1).xlsx"
    ]

    intermediate_root = "전처리결과/_시트CSV"
    final_output = "전처리결과/_오염물질별"

    # 1단계: 엑셀 파일마다 시트별 CSV로 전처리
    for f in excel_files:
        preprocess_excel_to_csv(filepath=f, intermediate_root=intermediate_root)

    # 2단계: 각 하위 폴더에서 연도별 그룹 → 오염물질별 저장
    for folder in os.listdir(intermediate_root):
        folder_path = os.path.join(intermediate_root, folder)
        if os.path.isdir(folder_path):
            yearwise_out = os.path.join(final_output, folder)
            process_all_years(input_dir=folder_path, output_dir=yearwise_out)
