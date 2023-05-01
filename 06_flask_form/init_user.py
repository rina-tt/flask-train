from app import db, User

#db.drop_all() # 削除
db.create_all() # 構築

user1 = User("admin_user1@test.com", "Admin User1", "111", "1")
user2 = User("test_user1@test.com", "Test User1", "111", "0")
# 複数のオブジェクトを一括で追加
db.session.add_all([user1, user2])

# 1つずつ追加
# db.session.add(user1)
# db.session.add(user2)

db.session.commit()

print(user1.id)
print(user2.id)