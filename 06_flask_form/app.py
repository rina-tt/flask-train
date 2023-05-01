from flask import Flask, render_template, url_for, redirect, session, flash, request
from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,Email,EqualTo

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

# 秘密鍵の設定
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

# Userモデルの定義
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
    
# BlogPostモデルの定義
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

# ユーザー登録フォーム用クラス
class RegistrationForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='正しいメールアドレスを入力してください。')]) #必須入力、eメール
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo('pass_confirm',message='パスワードが一致していません。')]) # 他人から見えないように隠してくれる
    pass_confirm = PasswordField('パスワード(確認)', validators=[DataRequired()])
    submit = SubmitField('登録')
    
    # 既にユーザー名が存在するか確認
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('入力されたユーザー名は既に使われています。')
    # メールアドレスが存在するか確認
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスは既に使われています。')

# ユーザー情報更新フォーム用クラス
class UpdateUserForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='正しいメールアドレスを入力してください。')])
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[EqualTo('pass_confirm',message='パスワードが一致していません。')])
    pass_confirm = PasswordField('パスワード(確認)')
    submit = SubmitField('更新')
    
    def __init__(self, user_id, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.id = user_id
    
    # 他にユーザーが存在するか確認
    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError('入力されたユーザー名は既に使われています。')
        
    # 他にメールアドレスが存在するか確認
    def validate_email(self, field):
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスは既に使われています。')



# 登録用view関数
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()   
    
    # フォームの内容に問題がされたらTrue
    if form.validate_on_submit():
        # session['email'] = form.email.data
        # session['username'] = form.username.data
        # session['password'] = form.password.data
        user = User(email=form.email.data, username=form.username.data, password_hash=form.password.data, administrator="0")
        db.session.add(user)
        db.session.commit()
        flash('ユーザーが登録されました')
        return redirect(url_for('user_maintenance'))
    
    # フォームに入力がされていないとき
    return render_template('register.html',form=form)

# ユーザー管理 view関数
@app.route('/user_maintenance')
def user_maintenance():
    page = request.args.get('page', 1, type=int) # 1=最初のページ
    users = User.query.order_by(User.id).paginate(page=page, per_page=10) #user id の昇順で取得
    return render_template('user_maintenance.html', users=users)

# ユーザー更新 view関数
@app.route('/<int:user_id>/account', methods=['GET', 'POST'])
def account(user_id):
    user = User.query.get_or_404(user_id) #見つからない場合404エラー
    form = UpdateUserForm(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password_hash = form.password.data 
        db.session.commit()
        flash('ユーザーアカウントが更新されました')
        return redirect(url_for('user_maintenance'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    
    return render_template('account.html',form=form)

@app.route('/<int:user_id>/delete', methods=['GET','POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('ユーザーアカウントが削除されました')
    return redirect(url_for('user_maintenance'))
    
#@app.errorhandler(404)
#def error_404(error):
#    return render_template('error_pages/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
    
