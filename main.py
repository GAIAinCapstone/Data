# main.py
import os
from preprocess.preprocess_all_files import preprocess_all_files

def run_pipeline():
    print("🚀 GAIAinCapstone Data 전처리 파이프라인 시작합니다...")
    
    raw_folder = os.path.join('data', 'raw')
    output_file = os.path.join('data', 'processed', 'all_processed.csv')

    # 전처리 실행
    df = preprocess_all_files(input_folder=raw_folder, output_path=output_file)

    # 확인 출력
    print("\n✅ 데이터 미리보기:")
    print(df.head())
    print(f"\n📁 저장 완료: {output_file}")

if __name__ == '__main__':
    run_pipeline()
