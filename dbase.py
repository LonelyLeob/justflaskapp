import sqlite3


class FDB:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    
    def getWorks(self):
        try:
            self.__cur.execute(''' SELECT id, title, desc FROM works ''')
            res = self.__cur.fetchall()
            return res
        except:
            print('Ошибка чтения в БД')
        return []

    def getWork(self, id):
        self.__cur.execute(f'SELECT title, desc FROM works where id = {id}')
        res = self.__cur.fetchone()
        if res:
            return res
        elif not res:
            return None

    def addWorks(self, title, desc):
        try:
            self.__cur.execute(f"INSERT into works (title, desc) VALUES ('{title}', '{desc}')")
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print('Ошибка:' + str(e))
            return False


    def getUser(self, us_id):
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
        try:
            self.__cur.execute(f'INSERT INTO users ("uname", "email", "pwd", "photo") VALUES (?, ?, ?, NULL)', (uname, email, hpwd))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f'Ошибка: {e}')