import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

# 今のファイルが格納されたディレクトリのパスを取得
basedir = os.path.abspath(os.path.dirname(__file__))
# OSに依存しない
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    
    def __init__(self, email, username, password_hash, administrator):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.administrator = administrator
        
    def __repr__(self):
        return f"UserName: {self.username}"


if __name__ == '__main__':
    app.run(debug=True)