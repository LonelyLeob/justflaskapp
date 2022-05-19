from flask import Flask, render_template as rt, request, url_for as uf, g, flash, abort, redirect
import sqlite3 as sql
import os
from dbase import FDB
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
from flask_login import LoginManager, login_user
from userlogin import UserLogin as UL


app = Flask(__name__)
a = app.config.from_object('tokens')
logmng = LoginManager(app=app)

@logmng.user_loader
def load_user(user_id):
    print('Юзер загружен')
    return UL().fromDB(user_id, accdb)


app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flrun.db')))
def conndb():
    '''Установка соединения с БД'''
    conn = sql.connect(app.config['DATABASE'])
    conn.row_factory = sql.Row
    return conn

def createdb():
    '''Создание БД при САМОМ первом запросе'''
    db = conndb()
    with app.open_resource('sq_db_cr.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Проверка соединения в контексте приложения g'''
    if not hasattr(g, 'link_db'):
        g.link_db = conndb()
    return g.link_db

@app.before_request
def conn_before():
    global accdb
    db = get_db()
    accdb = FDB(db)


@app.route('/works')
def index():
    '''Индекс хтмл'''
    src = accdb.getWorks()
    return rt('index.html', lst = src)


@app.route('/add_work', methods=['POST', 'GET'])
def add_work():

    #extra-data
    title = 'Добавить работу'

    if request.method == 'POST':
            res = accdb.addWorks(request.form['title'], request.form['desc'])
            if not res:
                flash('Ошибка добавления твоей работы', category='error')
            else: flash('Работа успешно добавлена, проверяй:)', category='success')
    
    return rt('add_work.html', title=title)


@app.route('/works/<int:id_work>')
def show_work(id_work):

    #extra-data
    title = f'Работа № {id_work}'
    
    name, desc = accdb.getWork(id_work)
    if name == None:
        abort(404)

    return rt('show_work.html', title=title, name=name, desc=desc)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    
    #extra-data
    title = 'Регистрация'

    if request.method == 'POST':
        if request.form['pwd'] == request.form['pwd-again']:
            mod_pwd = str(gph(request.form['pwd']))
            src = accdb.addUser(uname=request.form['uname'], email=request.form['email'], hpwd=mod_pwd)
            if not src:
                flash('К сожалению, зарегистрироваться не удалось:(', category='error')
        else: flash('Пароли не совпадают, проверьте правильность', category='error')

    return rt('reg.html', title=title)

@app.route('/auth', methods=['GET', 'POST'])
def auth_user():

    #extra-data
    title = 'Вход'

    if request.method == 'POST':
        user = accdb.getUserByName(request.form['uname'])
        if user and cph(user['pwd'], request.form['pwd']):
            userlogin = UL().create(user)
            login_user(userlogin)
            return redirect(uf('index'))
        flash('К сожалению, войти не удалось:(')
    return rt('auth.html', title=title)


@app.teardown_appcontext
def set_close_db(error):
    '''Закрываем соединение при уничтожении контекста приложения g'''
    if hasattr (g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run()