import sys, requests, time
import openpyxl
import time


class HTTP:
    server = None
    token = None

    @classmethod
    def get_token(cls, username, password):
        data = {'username': username, 'password': password}
        url = "/api/v1/authentication/auth/"
        res = requests.post(cls.server + url, data)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            token = res_data.get('token')
            cls.token = token
        else:
            print("获取 token 错误, 请检查输入项是否正确")
            sys.exit()

    @classmethod
    def get(cls, url, params=None, **kwargs):
        url = cls.server + url
        headers = {
            'Authorization': "Bearer {}".format(cls.token)
        }
        kwargs['headers'] = headers
        res = requests.get(url, params, **kwargs)
        return res

    @classmethod
    def post(cls, url, data=None, json=None, **kwargs):
        url = cls.server + url
        headers = {
            'Authorization': "Bearer {}".format(cls.token)
        }
        kwargs['headers'] = headers
        res = requests.post(url, data, json, **kwargs)
        return res


class User(object):

    def __init__(self):
        self.id = None
        self.name = user_name
        self.username = user_username
        self.email = user_email
        self.password = user_password

    def exist(self):
        url = '/api/v1/users/users/'
        params = {'username': self.username}
        res = HTTP.get(url, params=params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
        else:
            self.create()

    def create(self):
        print("创建用户 {}".format(self.username))
        url = '/api/v1/users/users/'
        data = {
            'name': self.name,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'is_active': True
        }
        res = HTTP.post(url, json=data)
        self.id = res.json().get('id')

    def perform(self):
        self.exist()


class Node(object):

    def __init__(self):
        self.id = None
        self.name = asset_node_name

    def exist(self):
        url = '/api/v1/assets/nodes/'
        params = {'value': self.name}
        res = HTTP.get(url, params=params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
        else:
            self.create()

    def create(self):
        print("创建资产节点 {}".format(self.name))
        url = '/api/v1/assets/nodes/'
        data = {
            'value': self.name
        }
        res = HTTP.post(url, json=data)
        self.id = res.json().get('id')

    def perform(self):
        self.exist()


class AdminUser(object):

    def __init__(self):
        self.id = None
        self.name = assets_admin_name
        self.username = assets_admin_username
        self.password = assets_admin_password

    def exist(self):
        url = '/api/v1/assets/admin-user/'
        params = {'username': self.name}
        res = HTTP.get(url, params=params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
        else:
            self.create()

    def create(self):
        print("创建管理用户 {}".format(self.name))
        url = '/api/v1/assets/admin-users/'
        data = {
            'name': self.name,
            'username': self.username,
            'password': self.password
        }
        res = HTTP.post(url, json=data)
        self.id = res.json().get('id')

    def perform(self):
        self.exist()


class Asset(object):

    def __init__(self):
        self.id = None
        self.name = asset_name
        self.ip = asset_ip
        self.platform = asset_platform
        self.protocols = asset_protocols
        self.admin_user = AdminUser()
        self.node = Node()

    def exist(self):
        url = '/api/v1/assets/assets/'
        params = {
            'hostname': self.name
        }
        res = HTTP.get(url, params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
        else:
            self.create()

    def create(self):
        print("创建资产 {}".format(self.ip))
        self.admin_user.perform()
        self.node.perform()
        url = '/api/v1/assets/assets/'
        data = {
            'hostname': self.name,
            'ip': self.ip,
            'platform': self.platform,
            'protocols': self.protocols,
            'admin_user': self.admin_user.id,
            'nodes': [self.node.id],
            'is_active': True
        }
        res = HTTP.post(url, json=data)
        self.id = res.json().get('id')

    def perform(self):
        self.exist()


class SystemUser(object):

    def __init__(self):
        self.id = None
        self.name = assets_system_name
        self.username = assets_system_username

    def exist(self):
        url = '/api/v1/assets/system-users/'
        params = {'name': self.name}
        res = HTTP.get(url, params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
        else:
            self.create()

    def create(self):
        print("创建系统用户 {}".format(self.name))
        url = '/api/v1/assets/system-users/'
        data = {
            'name': self.name,
            'username': self.username,
            'login_mode': 'auto',
            'protocol': 'ssh',
            'auto_push': True,
            'sudo': 'All',
            'shell': '/bin/bash',
            'auto_generate_key': True,
            'is_active': True
        }
        res = HTTP.post(url, json=data)
        self.id = res.json().get('id')

    def perform(self):
        self.exist()


class AssetPermission(object):

    def __init__(self):
        self.name = perm_name
        self.user = User()
        self.asset = Asset()
        self.system_user = SystemUser()

    def create(self):
        print("创建资产授权名称 {}".format(self.name))
        url = '/api/v1/perms/asset-permissions/'
        data = {
            'name': self.name,
            'users': [self.user.id],
            'assets': [self.asset.id],
            'system_users': [self.system_user.id],
            'actions': ['all'],
            'is_active': True,
            'date_start': perm_date_start,
            'date_expired': perm_date_expired
        }
        res = HTTP.post(url, json=data)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            print("创建资产授权规则成功: ", res_data)
        else:
            print("创建授权规则失败: ", res_data)

    def perform(self):
        self.user.perform()
        self.asset.perform()
        self.system_user.perform()
        self.create()


class APICreateAssetPermission(object):

    def __init__(self):
        self.jms_url = jms_url
        self.username = jms_username
        self.password = jms_password
        self.token = None
        self.server = None

    def init_http(self):
        HTTP.server = self.jms_url
        HTTP.get_token(self.username, self.password)

    def perform(self):
        self.init_http()
        self.perm = AssetPermission()
        self.perm.perform()


def main(user_name1, user_username1, user_password1, asset_ip1, asset_node_name1, assets_system_name1, asset_name1):
    global jms_url
    global jms_username
    global jms_password
    global asset_node_name
    global asset_name
    global asset_ip
    global asset_platform
    global asset_protocols
    global assets_admin_name
    global assets_admin_username
    global assets_admin_password
    global assets_system_name
    global assets_system_username
    global user_name
    global user_username
    global user_email
    global user_password
    global perm_name
    global perm_date_start
    global perm_date_expired
    # =====================================

    # jumpserver url 地址
    jms_url = 'http://172.31.0.251:17254'

    # 管理员账户
    jms_username = 'ming'
    jms_password = 'Ming@123'
    #######################################################

    # 资产节点
    asset_node_name = asset_node_name1

    # 资产信息
    asset_name = asset_name1
    asset_ip = asset_ip1
    asset_platform = 'Linux'
    asset_protocols = ['ssh/22', 'vnc/6901']  #

    # 资产管理用户    ------------- 固定
    assets_admin_name = 'root'
    assets_admin_username = 'root'
    assets_admin_password = ''

    # 资产系统用户    ------------ 固定
    assets_system_name = assets_system_name1
    assets_system_username = ''

    # 用户用户名     
    user_name = user_name1  # 姓名
    user_username = user_username1  # 登录名
    user_email = user_username + '@bjwb.com'  # 邮箱
    user_password = user_password1  # 用户密码

    # 资产授权
    perm_name = f'{user_name}+{asset_name}+{assets_system_name}-'  # 用户名+资产名
    perm_date_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    perm_date_expired = '2121-06-01 14:25:47 +0800'

    api = APICreateAssetPermission()
    api.perform()


if __name__ == '__main__':
    # filename=r"C:\vmctl\test.xlsx"

    # book = openpyxl.load_workbook(filename)
    # sheet = book.active

    filename = r"C:\vmctl\test.csv"
    with open(filename, encoding='utf8') as f:
        rows = f.readlines()
    for row0 in rows:
        row = row0.split(',')
        if 'user_name' in row[0]:
            continue

        # 用户用户名     
        user_name = row[0].strip()  # 姓名
        user_username = row[1].strip()  # 登录名
        user_password = row[2].strip()  # 用户密码
        asset_ip = row[3].strip()  # 资产IP
        asset_node_name = row[8].strip()  # 资产节点
        assets_system_name = row[9].strip()  # 资产系统用户
        asset_name = row[10].strip()  # 资产信息

        main(user_name, user_username, user_password, asset_ip, asset_node_name, assets_system_name, asset_name)
