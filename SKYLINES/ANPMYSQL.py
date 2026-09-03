#这是一个自定义的MySQL数据库操作类，主要用于SkylineMods爬虫数据的存储。
#以下将会对SQL内容进行配置
import pymysql
import os
import json

# ---------- 定位项目根目录（因为ANPMYSQL.py在SKYLINES/子文件夹下） ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 向上两级到项目根目录
CONFIG_FILE = os.path.join(BASE_DIR, 'db_config.json')

def load_db_config():
    """从项目根目录加载 db_config.json 配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('mysql', {})
        except:
            pass
    return {}  # 文件不存在或损坏返回空字典

class ANPmysql:
    # 初始化：优先使用传入参数，其次读取配置文件，最后使用兜底默认值
    def __init__(self, host=None, user=None, password=None, database=None, charset='utf8mb4', port=3306):
        config = load_db_config()
        
        self.host = host if host is not None else config.get('host', '127.0.0.1')
        self.user = user if user is not None else config.get('user', 'root')
        self.password = password if password is not None else config.get('password', '')
        self.database = database if database is not None else config.get('database', 'cslmods')
        self.charset = charset if charset is not None else config.get('charset', 'utf8mb4')
        self.port = port
        self.connection = None
        self.cursor = None
        
        # 如果配置文件不存在，给出友好提示
        if not config:
            print("⚠️ 未检测到 db_config.json，使用默认配置（127.0.0.1/root/空密码/cslmods）。")
            print("📝 如需自定义，请先运行项目根目录下的 export_data.py 生成配置文件。")

    # 连接
    def connect(self):
        try:
            if self.connection and self.connection.open:
                self.connection.close()
            self.connection = pymysql.connect(
                host=self.host, user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()
            print(f"✅ 数据库连接成功 (数据库: {self.database})")
            return True
        except pymysql.Error as e:
            print(f"❌ 数据库连接失败: {e}")
            print(f"   当前配置: host={self.host}, user={self.user}, database={self.database}")
            if not self.password:
                print("   ⚠️ 密码为空，请确认是否正确。")
            self.connection = None
            self.cursor = None
            return False

    # ---------- 以下方法保持不变（create_table, insert, delete, update, information, close） ----------
    def create_table(self):
        try:
            drop_table_sql = """DROP TABLE IF EXISTS CITYSKYLINESMODS;"""
            self.cursor.execute(drop_table_sql)
            self.connection.commit()
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS CITYSKYLINESMODS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `modname` VARCHAR(500) NOT NULL,
                `modlink` VARCHAR(500) NOT NULL,
                `modimg` VARCHAR(500),
                `modattr` VARCHAR(500),
                `publishdate` VARCHAR(500),
                `upgradedate` VARCHAR(500),
                `downloadurl` VARCHAR(500),
                `filesize` VARCHAR(500),
                `steamlink` VARCHAR(500)
            );
            """
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            return True
        except pymysql.Error as e:
            print(f"❌ 创建表失败: {e}")
            return False

    def insert(self, table, data):
        try:
            col = ','.join([f'`{key}`' for key in data.keys()])
            place = ','.join(['%s'] * len(data))
            sql = f"INSERT INTO {table} ({col}) VALUES({place})"
            affected_rows = self.cursor.execute(sql, tuple(data.values()))
            self.connection.commit()
            return affected_rows
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"❌ 插入失败: {e}")
            return 0

    def delete(self, table, condition, params):
        try:
            sql = f"DELETE FROM {table} WHERE {condition}"
            affected_rows = self.cursor.execute(sql, params)
            self.connection.commit()
            return affected_rows
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"❌ 删除失败:{e}")
            return 0

    def update(self, table, new, where, params):
        try:
            sql = f"UPDATE {table} SET {new} WHERE {where}"
            affected_rows = self.cursor.execute(sql, params)
            self.connection.commit()
            return affected_rows
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"❌ 更新失败:{e}")
            return 0

    def information(self, table, condition=None, params=None):
        try:
            sql = f"SELECT * FROM {table}"
            if condition:
                sql += f" WHERE {condition}"
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print(f"❌ 查询失败:{e}")
            return []

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔒 数据库连接已关闭")