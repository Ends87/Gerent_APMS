from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return 'Bem-vindo à aplicação web do seu bot!'


@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)