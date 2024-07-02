from pymongo import MongoClient
from collections import Counter

def find_representative_movement_pattern(database_uri, database_name, source_collection_name, target_collection_name):
    # MongoDB 클라이언트 생성하여 서버에 연결
    client = MongoClient(database_uri)

    # 데이터베이스 선택
    db = client[database_name]

    # 원본 컬렉션 선택
    source_collection = db[source_collection_name]

    # 집계 쿼리 정의
    pipeline = [
        {
            "$match": {
                "total_visits": {"$gte": 5}
            }
        }
    ]

    # 집계 쿼리 실행 및 결과 가져오기
    results = list(source_collection.aggregate(pipeline))

    # 유저별, 날짜별, TL별 이동 패턴 분석
    user_date_tl_patterns = {}
    for result in results:
        user_id = result["User Id"]
        date = result["LocalTime"]  # 날짜 필드 추가
        tl = result["TL"]
        venues = tuple(result["visited_venues"])

        if user_id not in user_date_tl_patterns:
            user_date_tl_patterns[user_id] = {}
        if date not in user_date_tl_patterns[user_id]:
            user_date_tl_patterns[user_id][date] = {}
        if tl not in user_date_tl_patterns[user_id][date]:
            user_date_tl_patterns[user_id][date][tl] = []
        user_date_tl_patterns[user_id][date][tl].append(venues)

    # 대표 이동 패턴 및 빈도 계산
    representative_patterns = []
    for user_id, date_tl_patterns in user_date_tl_patterns.items():
        for date, tl_patterns in date_tl_patterns.items():
            for tl, patterns in tl_patterns.items():
                pattern_counter = Counter(patterns)
                most_common_pattern, frequency = pattern_counter.most_common(1)[0]
                representative_patterns.append({
                    "User Id": user_id,
                    "date": date,
                    "TL": tl,
                    "representative_pattern": list(most_common_pattern),
                    "pattern_frequency": frequency,
                    "pattern_length": len(most_common_pattern)
                })

    # 결과를 대상 컬렉션에 삽입
    target_collection = db[target_collection_name]

    # 이전에 삽입된 문서가 있다면 삭제
    target_collection.delete_many({})

    # 새로운 결과 삽입
    if representative_patterns:
        target_collection.insert_many(representative_patterns)

    # 연결 종료
    client.close()

    print("대표 이동 패턴이 {} 컬렉션에 성공적으로 삽입되었습니다.".format(target_collection_name))

# 예시 실행
find_representative_movement_pattern("mongodb://localhost:27017/", "PolarBear_Pirates", "time-interval-stat", "RMP")
