from flask_login import UserMixin
from flask import url_for as uf

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self
    
    def create(self, user):
        self.__user = user
        return self
        
    def get_id(self):
        return str(self.__user['id'])
    
    def getName(self):
        return self.__user['uname']

    def getEmail(self):
        return self.__user['email']
    
    def getPhoto(self, app):
        img = None
        if not self.__user['photo']:
            try:
                with app.open_resource(app.root_path + uf('static', filename='photos/default.png'), 'rb') as f:
                    img = f.read()
            except FileNotFoundError as e:
                print(f'Ошибка при нахождении аватара: {e}')
        else: img = self.__user['photo']

        return img