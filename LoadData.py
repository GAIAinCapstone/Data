import pymysql
import csv
import os
import glob
from datetime import datetime

def safe_float(val):
    try:
        return float(val) if val not in ('', 'NaN', None) else None
    except ValueError:
        return None

def log_write(log_path, message):
    print(message)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {message}\n")

# 📄 로그 파일 경로
log_path = "upload.log"

# ✅ DB 연결
connection = pymysql.connect(
    host='127.0.0.1',
    port=3307,
    user='ksw',
    password='capstone',
    db='weatherCenter',
    charset='utf8mb4'
)
cursor = connection.cursor()

# ✅ 대시보드용 로그 테이블 생성 (upload_log)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS upload_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        site VARCHAR(50),
        year VARCHAR(10),
        item VARCHAR(100),
        filename VARCHAR(200),
        inserted_rows INT,
        upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# ✅ CSV 탐색 경로
base_dir = "./processed"
sites = os.listdir(base_dir)

for site in sites:
    site_path = os.path.join(base_dir, site)
    years = os.listdir(site_path)

    for year in years:
        year_path = os.path.join(site_path, year)
        csv_files = glob.glob(os.path.join(year_path, "*.csv"))

        for file_path in csv_files:
            file_name = os.path.basename(file_path)
            try:
                year_part, item = file_name.replace(".csv", "").split("_", 1)
            except ValueError:
                log_write(log_path, f"⚠️ 파일명 오류: {file_name} → 건너뜀")
                continue

            # 테이블 이름 설정 (ex: tms_보령_nox)
            table_name = f"tms_{site}_{item}".lower()

            # ✅ 테이블 생성 (중복 방지 위해 측정일시에 PRIMARY KEY)
            create_sql = f"""
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    측정일시 DATETIME PRIMARY KEY,
                    값 FLOAT
                )
            """
            cursor.execute(create_sql)

            # ✅ 데이터 삽입 (중복 방지: INSERT IGNORE)
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 헤더 스킵

                count = 0
                for row in reader:
                    measure_time = row[0]
                    value = safe_float(row[1])
                    if not measure_time or value is None:
                        continue
                    insert_sql = f"""
                        INSERT IGNORE INTO `{table_name}` (측정일시, 값)
                        VALUES (%s, %s)
                    """
                    cursor.execute(insert_sql, (measure_time, value))
                    count += 1

                # ✅ DB 기록 (upload_log 테이블)
                log_sql = """
                    INSERT INTO upload_log (site, year, item, filename, inserted_rows)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(log_sql, (site, year, item, file_name, count))

                # ✅ 로그 기록 (파일 + 콘솔)
                log_write(log_path, f"✅ [{site}/{year}] {item}: {count}건 → `{table_name}` 삽입 완료")

# 마무리
connection.commit()
cursor.close()
connection.close()
log_write(log_path, "🎉 전체 자동 업로드 + 테이블 생성 + 로그 기록 완료")
