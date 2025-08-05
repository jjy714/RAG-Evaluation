
from pymongo import MongoClient

# MongoDB 서버에 연결 (기본 포트: 27017)
# client = MongoClient('mongodb://localhost:27017/') 와 동일합니다.
client = MongoClient('localhost', 27017)

# 'mydatabase'라는 이름의 데이터베이스에 연결합니다.
# 만약 'mydatabase'가 존재하지 않으면, 첫 데이터가 추가될 때 자동으로 생성됩니다.
db = client['mydatabase']

# 'users'라는 이름의 컬렉션에 연결합니다.
# 컬렉션도 마찬가지로 첫 데이터 추가 시 자동 생성됩니다.
collection = db['users']


# 추가할 데이터 리스트
user_list = [
    {'name': 'Bob', 'age': 25, 'city': 'Paris'},
    {'name': 'Charlie', 'age': 35, 'city': 'London'}
]

# insert_many() 메소드로 여러 도큐먼트를 한 번에 추가합니다.
result = collection.insert_many(user_list)
print(f"추가된 문서들의 ID: {result.inserted_ids}")