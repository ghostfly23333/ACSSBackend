from analyzer import users
from classes.UserInfo import UserInfo
from .__init__ import container


def register(username, password):
    if username in users:
        return False

    new_user = UserInfo(username, password, 0)
    users[username] = new_user
    container.add_user(username)
    return True


def login(username, password, auth):
    if username in users:
        if users[username].id == username and users[username].password == password and users[username].auth == auth:
            # print("登录成功！")
            return True

    # print("用户名或密码错误。")
    return False
