import pymongo
from PyQt5.QtWidgets import QMessageBox


class DatabaseInitializer:
    #初始化数据库
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["zhiwu"]
        self.users_collection = self.db["users"]

        #判断是否用户的集和已创建，没创建就创建

    def create_user(self, username, password):
        # 检查用户是否已存在
        if self.users_collection.find_one({"username": username}):
            print(f"用户 '{username}' 已存在.")
            return False

        # 创建新用户
        user_data = {
            "username": username,
            "password": password
        }
        self.users_collection.insert_one(user_data)
        print(f"用户 '{username}' 创建成功.")
        return True

    def verify_user(self, username, password):
        # 检查用户是否存在并验证密码
        user = self.users_collection.find_one({"username": username, "password": password})
        if user:
            print(f"用户 '{username}' 验证成功.")
            return True
        else:
            print("用户名或密码不正确.")
            return False
    def initialize_user_collection(self, username):
        collection_name = f"{username}"  # 每个用户的集合名称
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name)
            print(f"Collection '{collection_name}' created for user '{username}'.")
        self.current_user_collection = self.db[collection_name]
        return self.current_user_collection


    #将对应的数据存入对应的用户的集合内
    def insert_data(self, batch, name, path, classes, user, time, ispass):
        if self.current_user_collection is not None:
            data = {
                "batch" : batch,
                "name": name,
                "path": path,
                "classes": classes,
                "user": user,
                "time": time,
                "ispass": ispass,
            }


            self.current_user_collection.insert_one(data)
            print("Data inserted successfully.")
        else:
            print("User collection not initialized. Please call 'initialize_user_collection' first.")

    #查找数据
    def find_data(self, query):
        if self.current_user_collection is not None:
            result = self.current_user_collection.find(query)
            return list(result)
        else:
            print("User collection not initialized. Please call 'initialize_user_collection' first.")

    def delete_data(self, query):
        if self.current_user_collection is not None:
            result = self.current_user_collection.delete_one(query)
            print(f"Deleted {result.deleted_count} document.")
        else:
            print("User collection not initialized. Please call 'initialize_user_collection' first.")

    def update_ispassdata(self, batch):
        if self.current_user_collection is not None:
            # 定义查询条件，找出批次值为 batch 的数据
            query = {"batch": batch}
            # 定义更新的值，将 ispass 字段设置为 "pass"
            update_values = {"$set": {"ispass": "pass"}}
            # 使用更新操作更新数据库中的数据
            result = self.current_user_collection.update_many(query, update_values)
            print(f"Updated {result.modified_count} documents where batch is '{batch}'.")

            # 弹出消息框显示更新成功
            msg_box = QMessageBox()
            msg_box.setWindowTitle("更新成功")
            msg_box.setText("数据更新成功。")
            msg_box.exec_()
        else:
            print("User collection not initialized. Please call 'initialize_user_collection' first.")

#示例用法
if __name__ == "__main__":
    #初始化数据库
    #username就是对应的用户名，把参数传给username，调用后面的初始化函数就能实现对某一用户单独创建集合来保存数据
    username = "123456"
    db_initializer = DatabaseInitializer()
    user_collection = db_initializer.initialize_user_collection(username)
    print(f"User '{username}' collection initialized.")

    # #保存数据示例
    # db_initializer.insert_data("example_image3.jpg", "/path/to/example_image3.jpg", "3")

    # 查询数据示例
    query = {}
    results = db_initializer.find_data(query)
    for result in results:
        print(result)


    # 删除数据示例
    # query = {"name": "example_image3.jpg"}  # 按照名称删除数据
    # db_initializer.delete_data(query)

    # # 假设您已经有了要更新的数据和新的字段和值
    # filter_criteria = {}  # 如果不需要特定的筛选条件，可以为空，表示更新所有数据
    # update_values = {
    #     "$set": {
    #         "user": "user_example_user",
    #         "time": "2024-04-02 12:00:00"
    #     }
    # }
    #
    # # 使用更新操作更新数据库中的数据
    # db_initializer.current_user_collection.update_many(filter_criteria, update_values)



    # # 初始化数据库
    # db_initializer = DatabaseInitializer()
    #
    # # 创建用户示例
    # db_initializer.create_user("example_user", "example_password")
    #
    # # 验证用户示例
    # db_initializer.verify_user("example_user", "example_password")