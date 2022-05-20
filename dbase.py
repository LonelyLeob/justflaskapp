import sqlite3

from sqlalchemy import null


class FDB:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    
    def getWorks(self):
        """Search for all works"""
        try:
            self.__cur.execute(''' SELECT id, title, desc FROM works ''')
            res = self.__cur.fetchall()
            return res
        except:
            print('Ошибка чтения в БД')
        return []

    def getWork(self, id):
        """Get detail work by id"""
        self.__cur.execute(f'SELECT title, desc, photo FROM works where id = {id}')
        res = self.__cur.fetchone()
        if res:
            return res
        elif not res:
            return None
    
    
    def getPhotoWork(self, id):
        self.__cur.execute(f'SELECT photo FROM works where id = {id}')
        res = self.__cur.fetchone()
        if res:
            return res


    def addWorks(self, title, desc, photo):
        """Add works like entry in table"""
        if not photo:
            photo = null
        try:
            binary = sqlite3.Binary(photo)
            self.__cur.execute("INSERT into works (title, desc, photo) VALUES (?, ?, ?)", (title, desc, binary))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка:' + str(e))
            return False


    def getUser(self, us_id):
        """Get user entry by id"""
        try:
            self.__cur.execute(f'SELECT * FROM users where id = {us_id} limit 1')
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            
            return res
        except sqlite3.Error as e:
            print (f'Ошибка: {e}')

    def getUserByName(self, uname):
        """Get user by name"""
        try:
            self.__cur.execute(f"SELECT * FROM users where uname LIKE '{uname}' limit 1")
            res = self.__cur.fetchone()
            if not res:
                print('Невозможно получить пользователя по имени')
                return False
            return res
        except sqlite3.Error as e:
            print(f'Ошибка: {e}')


    def addUser(self, uname, email, hpwd):
        """Registration user func for DB"""
        try:
            self.__cur.execute(f'INSERT INTO users ("uname", "email", "pwd", "photo") VALUES (?, ?, ?, NULL)', (uname, email, hpwd))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f'Ошибка: {e}')

    def updateUserPic(self, userpic, user_id):
        """upd UserPicture func"""
        if not userpic:
            return False
        try:
            binary = sqlite3.Binary(userpic)
            self.__cur.execute(f'UPDATE users SET photo = ? WHERE id = ?', (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f'Ошибка добавления аватара в БД: {e}')
            return False
        return True