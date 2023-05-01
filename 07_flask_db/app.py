import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

# 今のファイルが格納されたディレクトリのパスを取得
basedir = os.path.abspath(os.path.dirname(__file__))
# OSに依存しない
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

# 外部キー制約を有効にする
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    post = db.relationship('BlogPost', backref='author', lazy='dynamic')
    
    def __init__(self, email, username, password_hash, administrator):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.administrator = administrator
        
    def __repr__(self):
        return f"UserName: {self.username}"
    
class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 外部キー
    date = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Tokyo')))
    title = db.Column(db.String(140))
    text = db.Column(db.Text)
    summary = db.Column(db.String(140))
    featured_image = db.Column(db.String(140))
    
    def __init__(self, title, text, featured_image, user_id, summary):
        self.title = title
        self.text = text
        self.featured_image = featured_image
        self.user_id = user_id
        self.summary = summary
        
    def __repr__(self):
        return f"PostId: {self.id}, Title: {self.title}, Author: {self.author} \n"


if __name__ == '__main__':
    app.run(debug=True)