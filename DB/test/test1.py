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

print("MongoDB에 성공적으로 연결되었습니다.")