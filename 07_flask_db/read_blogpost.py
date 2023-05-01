from app import db, User, BlogPost

all_posts = BlogPost.query.all()
print(all_posts)