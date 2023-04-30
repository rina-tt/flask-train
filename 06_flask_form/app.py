from flask import Flask, render_template, url_for, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,Email,EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

class RegistrationForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='正しいメールアドレスを入力してください')]) #必須入力、eメール
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo('pass_confirm',message='パスワードが一致していません')]) # 他人から見えないように隠してくれる
    pass_confirm = PasswordField('パスワード(確認)', validators=[DataRequired()])
    submit = SubmitField('登録')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()   
    
    # フォームの内容に問題がされたらTrue
    if form.validate_on_submit():
        session['email'] = form.email.data
        session['username'] = form.username.data
        session['password'] = form.password.data
        flash('ユーザーが登録されました')
        return redirect(url_for('user_maintenance'))
    
    # フォームに入力がされていないとき
    return render_template('register.html',form=form)

@app.route('/user_maintenance')
def user_maintenance():
    return render_template('user_maintenance.html')
    

#@app.errorhandler(404)
#def error_404(error):
#    return render_template('error_pages/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
    
