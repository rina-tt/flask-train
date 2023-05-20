from app import db, User

#user_list = []
#for i in range(60):
#    user_list.append(User(f"temp_user{i}@test.com", f"Temp User{i}", "111", "0"))
    
user1 = User(email="test_user1@test.com", username="Test User1", password="123", administrator="0")
#db.session.add_all(user_list)
db.session.add(user1)
db.session.commit()