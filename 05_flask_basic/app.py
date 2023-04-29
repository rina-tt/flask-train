from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return '<h1>Hello Test!</h1>'

@app.route('/user/<int:user_id>')
def user(user_id):
    return '<h1>Hello User {0}</h1>'.format(user_id)

if __name__ == '__main__':
    app.run(debug=True)
    
