from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
#тестирую тут функции
mod_pwd = str(gph('123'))
checkpwd = cph(mod_pwd, '123')
print(mod_pwd, checkpwd)