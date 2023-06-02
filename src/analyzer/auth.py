from src.analyzer import users
from src.classes.UserInfo import UserInfo


def register(username, password):
    if username in users:
        # print("用户名已存在，请选择其他用户名。")
        return False

    new_user = UserInfo(username, password, 0)
    users[username] = new_user
    # print("注册成功！")
    return True


def login(username, password, auth):
    if username in users:
        if users[username].id == username and users[username].password == password and users[username].auth == auth:
            # print("登录成功！")
            return True

    # print("用户名或密码错误。")
    return False
