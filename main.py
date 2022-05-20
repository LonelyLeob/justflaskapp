from flask import Flask, make_response, render_template as rt, request, url_for as uf, g, flash, abort, redirect
import sqlite3 as sql
import os
from dbase import FDB
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from userlogin import UserLogin as UL
from forms import *

#get wsgi-app from Flask class and setup tokens
app = Flask(__name__)
a = app.config.from_object('tokens')

#get login-manager for set user-session
logmng = LoginManager(app=app)
logmng.login_view = 'auth_user'
logmng.login_message = 'Для доступа необходимо авторизоваться:)'
logmng.login_message_category = 'success'

#message about user login
@logmng.user_loader
def load_user(user_id):
    print(f'Юзер {user_id} загружен')
    return UL().fromDB(user_id, accdb)

#DB path
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flrun.db')))


def conndb():
    '''Try DB connection'''
    conn = sql.connect(app.config['DATABASE'])
    conn.row_factory = sql.Row
    return conn

def createdb():
    '''Create db function'''
    db = conndb()
    with app.open_resource('sq_db_cr.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Check for connection in appcontext'''
    if not hasattr(g, 'link_db'):
        g.link_db = conndb()
    return g.link_db

@app.before_request
def conn_before():
    '''Set DB connection before every requests'''
    global accdb
    db = get_db()
    accdb = FDB(db)


@app.route('/works')
def index():
    '''Main page with works'''
    src = accdb.getWorks()
    return rt('index.html', lst = src)


@app.route('/add_work', methods=['POST', 'GET'])
def add_work():
    """Add one of works"""

    #extra-data
    title = 'Добавить работу'

    if request.method == 'POST':
        file = request.files['file']
        img = file.read()
        res = accdb.addWorks(request.form['title'], request.form['desc'], img)
        if not res:
            flash('Ошибка добавления твоей работы', category='error')
        else: flash('Работа успешно добавлена, проверяй:)', category='success')
    
    return rt('add_work.html', title=title)


@app.route('/works/<int:id_work>')
def show_work(id_work):
    """Show detail design work"""

    #extra-data
    title = f'Работа № {id_work}'
    
    name, desc, photo = accdb.getWork(id_work)

    if name == None:
        abort(404)

    return rt('show_work.html', title=title, name=name, desc=desc)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    """Registration user"""

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
    """Autenthicated user"""

    #extra-data
    title = 'Вход'

    form = LoginForm()
    if form.validate_on_submit():
        user = accdb.getUserByName(form.uname.data)
        if user and cph(user['pwd'], form.pwd.data):
            userlogin = UL().create(user)
            r = form.remember.data
            login_user(userlogin, remember=r)
            return redirect(uf('index'))
        flash('К сожалению, войти не удалось:(')
    return rt('auth.html', title=title, form=form)

@app.route('/profile')
@login_required
def profile():
    """User profile with info"""
    #extra-data
    title = 'Профиль'

    return rt('profile.html', title=title)

@app.route('/userpic')
@login_required
def userpic():
    """Default userpic if userpic None"""
    img = current_user.getPhoto(app)
    if not img: return None

    h = make_response(img)
    h.headers['Content-type'] = 'image/png'
    return h


@app.route('/upload', methods=['GET','POST'])
@login_required
def upload_pic():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = accdb.updateUserPic(img, current_user.get_id())
                if not res:
                    flash('Ошибка добавления аватара', category='error')
                    return redirect(uf('profile'))
                flash('Аватар успешно обновлен', category='success')
            except FileNotFoundError as e:
                flash(f'Ошибка чтения файла: {e}', category='error')
        else: flash('Ошибка добавления аватара', category='error')
    return redirect(uf('profile'))

@app.route('/logout')
@login_required
def logout():
    """Logout from profile"""
    logout_user()
    flash('Вы успешно вышли из профиля', category='success')
    return redirect(uf('auth_user'))


@app.teardown_appcontext
def set_close_db(error):
    '''Set close DB connection when appcontext g teardown'''
    if hasattr (g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run()