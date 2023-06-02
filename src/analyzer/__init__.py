from classes.UserInfo import UserInfo
users_info = {
        "user1": "password1",
        "user2": "password2",
        "user3": "password3"
}
users = {}
# 使用userinfo字典来初始化User类的实例
for user_id, password in users_info.items():
    user = UserInfo(user_id, password,0)
    users[user_id] = user
    #users.append(user)
# initialize root
users["root"] = UserInfo("root", "123456",1)