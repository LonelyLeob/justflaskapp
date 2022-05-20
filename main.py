from flask import Flask, make_response, render_template as rt, request, url_for as uf, g, flash, abort, redirect
import sqlite3 as sql
import os
from dbase import FDB
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from userlogin import UserLogin as UL


app = Flask(__name__)
a = app.config.from_object('tokens')

logmng = LoginManager(app=app)
logmng.login_view = 'auth_user'
logmng.login_message = 'Для доступа необходимо авторизоваться:)'
logmng.login_message_category = 'success'

@logmng.user_loader
def load_user(user_id):
    print(f'Юзер {user_id} загружен')
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
            r = True if request.form.get('remain') else False
            login_user(userlogin, remember=r)
            return redirect(uf('index'))
        flash('К сожалению, войти не удалось:(')
    return rt('auth.html', title=title)

@app.route('/profile')
@login_required
def profile():

    #extra-data
    title = 'Профиль'

    return rt('profile.html', title=title)

@app.route('/userpic')
@login_required
def userpic():
    img = current_user.getPhoto(app)
    if not img: return None

    h = make_response(img)
    h.headers['Content-type'] = 'image/png'
    return h


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из профиля', category='success')
    return redirect(uf('auth_user'))

@app.teardown_appcontext
def set_close_db(error):
    '''Закрываем соединение при уничтожении контекста приложения g'''
    if hasattr (g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run()