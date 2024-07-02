import pandas as pd
from pymongo import MongoClient

# 텍스트 파일 경로
file_path = "C:\\Users\\11\\OneDrive - 충북대학교\\바탕 화면\\연구실 자료\\북극곰해적단\\Checkins_merge.txt"

# 텍스트 파일 읽기
data = pd.read_csv(file_path, delimiter='\t')

# 데이터 확인
print(data.head())

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['PolarBear_Pirates']
collection = db['Place_Recommendation']

# 데이터 프레임을 딕셔너리로 변환 후 MongoDB에 삽입
data_dict = data.to_dict("records")
collection.insert_many(data_dict)

print("데이터가 성공적으로 MongoDB에 삽입되었습니다.")