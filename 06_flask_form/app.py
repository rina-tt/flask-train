from flask import Flask, render_template, url_for, redirect, session, flash, request, abort
from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,Email,EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

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
login_manager = LoginManager()
login_manager.init_app(app) 
# ログインが必要なページを開こうとすると表示されるview関数
login_manager.login_view = 'login'

def localize_callback(*args, **kwargs):
    return 'このページにアクセスするには、ログインが必要です。'
login_manager.localize_callback = localize_callback

# 外部キー制約を有効にする
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 現在のログインユーザーの情報を保持し、必要な時に参照できる
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Userモデルの定義
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    post = db.relationship('BlogPost', backref='author', lazy='dynamic')
    
    def __init__(self, email, username, password, administrator):
        self.email = email
        self.username = username
        self.password = password
        self.administrator = administrator
        
    def __repr__(self):
        return f"UserName: {self.username}"
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # 管理者かどうかを判断
    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            0
    
    
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

# ログインフォーム用クラス
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='正しいメールアドレスを入力してください。')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('ログイン')

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

# 権限がないページへのリクエスト
@app.errorhandler(403)
def error_403(error):
    return render_template('error_pages/403.html'), 403

# 存在しないページへのリクエスト
@app.errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html'), 404

# ユーザー登録用view関数
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # 該当ユーザーが存在する場合
        if user is not None:
            # パスワードが一致
            if user.check_password(form.password.data):
                # ログイン状態として扱われるようになる
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('user_maintenance')
                return redirect(next)
            # パスワードが一致しない
            else:
                flash('パスワードが一致しません')
        # 存在しない場合
        else:
            flash('入力されたユーザーは存在しません')
            
    return render_template('login.html',form=form)

# ログアウト用view関数
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 登録用view関数
@app.route('/register', methods=['GET','POST'])
@login_required
def register():
    form = RegistrationForm()
    if not current_user.is_administrator():
        abort(403)
    
    # フォームの内容に問題がされたらTrue
    if form.validate_on_submit():
        # session['email'] = form.email.data
        # session['username'] = form.username.data
        # session['password'] = form.password.data
        user = User(email=form.email.data, username=form.username.data, password=form.password.data, administrator="0")
        db.session.add(user)
        db.session.commit()
        flash('ユーザーが登録されました')
        return redirect(url_for('user_maintenance'))
    
    # フォームに入力がされていないとき
    return render_template('register.html',form=form)

# ユーザー管理 view関数
@app.route('/user_maintenance')
@login_required
def user_maintenance():
    page = request.args.get('page', 1, type=int) # 1=最初のページ
    users = User.query.order_by(User.id).paginate(page=page, per_page=10) #user id の昇順で取得
    return render_template('user_maintenance.html', users=users)

# ユーザー更新 view関数
@app.route('/<int:user_id>/account', methods=['GET', 'POST'])
@login_required
def account(user_id):
    user = User.query.get_or_404(user_id) #見つからない場合404エラー
    
    # 自分のアカウント出ない　かつ　管理者ではない
    if user.id != current_user.id and not current_user.is_administrator():
        abort(403)
        
    form = UpdateUserForm(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data 
        db.session.commit()
        flash('ユーザーアカウントが更新されました')
        return redirect(url_for('user_maintenance'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    
    return render_template('account.html',form=form)

@app.route('/<int:user_id>/delete', methods=['GET','POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_administrator():
        abort(403)
    #
    if user.is_administrator():
        flash('管理者は削除できません')
        return redirect(url_for('account', user_id = user_id))
    db.session.delete(user)
    db.session.commit()
    flash('ユーザーアカウントが削除されました')
    return redirect(url_for('user_maintenance'))
    

if __name__ == '__main__':
    app.run(debug=True)
    
