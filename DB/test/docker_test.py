import pymongo
print(pymongo.__version__) # 3.10.1

#// 몽고클라이언트를 만든다
conn = pymongo.MongoClient(
    host='host.docker.internal', 
    port=9017, 
    username='root',
    password='changeme',
    )

#// 데이터베이스 정보를 가져온다

evaluation_database = 'evaluation_database'
user_collection = "user_collection"
datasets_collection = "datasets_collection"
sessions_collection = "sessions_collection"
logs_collection = "logs_collection"
scores_collection = "scores_collection"



str_database_name = 'testdb'
db = conn.get_database(evaluation_database)

#// 콜렉션 정보를 가져온다
str_collection_name = 'test_table'
db.drop_collection(str_collection_name) #// 작업 전 콜렉션 초기화
collection = db.get_collection(str_collection_name)

collection.insert_one({'name': 'Trump', 'age': 70}) #// 도큐먼트를 추가한다
collection.insert_one({'name': 'Obama', 'age': 60}) #// 도큐먼트를 추가한다

#// Who is over 70 years old? (70세 이상 조회)
results = collection.find({"age": {"$gte": 70}})
for result in results:
    print(result)
#// {'_id': ObjectId('5ec7166de54cb8384dc8893f'), 'name': 'Trump', 'age': 70}    

#// Who is over 60 years old? (60세 이상 조회)
results = collection.find({"age": {"$gte": 60}})
for result in results:
    print(result)