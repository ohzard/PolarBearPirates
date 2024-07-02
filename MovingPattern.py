from pymongo import MongoClient

def aggregate_time_interval_stat(database_uri, database_name, source_collection_name, target_collection_name):
    # MongoDB 클라이언트 생성하여 서버에 연결
    client = MongoClient(database_uri)

    # 데이터베이스 선택
    db = client[database_name]

    # 원본 컬렉션 선택
    source_collection = db[source_collection_name]

    # 집계 쿼리 정의
    pipeline = [
        # LocalTime 필드가 문자열인 문서만 필터링
        {
            "$match": {
                "LocalTime": {"$type": "string"}
            }
        },
        # LocalTime의 년-월-일 부분만 추출하여 새로운 필드로 변환
        {
            "$addFields": {
                "CleanedLocalTime": {
                    "$substr": ["$LocalTime", 0, 10]
                },
                "ConvertedTL": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$TL", 1]}, "then": "M"},
                            {"case": {"$eq": ["$TL", 2]}, "then": "A"},
                            {"case": {"$eq": ["$TL", 3]}, "then": "E"},
                            {"case": {"$eq": ["$TL", 4]}, "then": "N"}
                        ],
                        "default": "$TL"
                    }
                }
            }
        },
        # User Id, ConvertedTL, CleanedLocalTime으로 그룹화하여 각 시간별 방문 장소 배열 생성
        {
            "$group": {
                "_id": {"User Id": "$User Id", "TL": "$ConvertedTL", "CleanedLocalTime": "$CleanedLocalTime"},
                "visited_venues": {"$push": "$VenueID"}
            }
        },
        # 최종 결과 정리 및 total_visits 추가
        {
            "$project": {
                "_id": 0,
                "User Id": "$_id.User Id",
                "TL": "$_id.TL",
                "LocalTime": "$_id.CleanedLocalTime",
                "visited_venues": 1,
                "total_visits": {"$size": "$visited_venues"}
            }
        }
    ]

    # 집계 쿼리 실행 및 결과 가져오기
    results = list(source_collection.aggregate(pipeline))

    # 결과를 대상 컬렉션에 삽입
    target_collection = db[target_collection_name]

    # 이전에 삽입된 문서가 있다면 삭제
    target_collection.delete_many({})

    # 새로운 결과 삽입
    if results:
        target_collection.insert_many(results)

    # 연결 종료
    client.close()

    print("결과가 {} 컬렉션에 성공적으로 삽입되었습니다.".format(target_collection_name))

# 예시 실행
aggregate_time_interval_stat("mongodb://localhost:27017/", "PolarBear_Pirates", "Place_Recommendation", "time-interval-stat")
