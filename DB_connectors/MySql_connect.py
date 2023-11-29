from datetime import date
from .config import host, user, password, port
import pymysql


class Database:
    def __init__(self, db_name):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            port=port,
            password=password,
            database=db_name,
        )
        self.connection.autocommit(True)

    def cbdt(self):
        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS users
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        telegram_id BIGINT UNIQUE NOT NULL ,
                        full_name TEXT,
                        username TEXT,
                        pay_end TEXT
                        );"""
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS admins
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(512) UNIQUE NOT NULL
                    );
                    """
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """    CREATE TABLE IF NOT EXISTS users_bots
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    api_id BIGINT UNIQUE,
                    api_hash TEXT,
                    phone TEXT,
                    system_role TEXT,
                    dialogs_counts INT DEFAULT 0,
                    is_active BOOL DEFAULT FALSE,
                    month_dialog_count INT DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    );
                    """

            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS analytics
                    (id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT ,
                    phone TEXT UNIQUE,
                    sheets_table_name TEXT UNIQUE,
                    dialog_count BIGINT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                    );
                    """
            cursor.execute(create)
            self.connection.commit()

    def create_analytics(self, user_id, phone, table_name):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT IGNORE INTO analytics (user_id, phone, sheets_table_name) VALUES( (SELECT id FROM users WHERE telegram_id=%s), %s, %s )''', (user_id, phone, table_name))
            self.connection.commit()
            self.connection.close()

    def update_table(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''ALTER TABLE users_bots MODIFY phone TEXT UNIQUE''')
            self.connection.commit()
            self.connection.close()

    def get_analytic_sheet_name(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT * FROM analytics where phone=%s  ''', (phone))
            data = cursor.fetchone()
            self.connection.commit()
            self.connection.close()
        if not data:
            return False

        return data[3]

    def get_analytic_sheet_exist(self, name, user_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT * FROM analytics where sheets_table_name= %s and user_id != %s ''', (name, user_id))
            data = cursor.fetchone()
            self.connection.commit()
            self.connection.close()
        if not data:
            return False

        return True

    def create_user(self, telegram_id, full_name: str, username: str, pay_end):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT IGNORE INTO users (telegram_id, full_name, username, pay_end) VALUES(%s, %s, %s, %s)', (telegram_id, full_name, username, pay_end))
            self.connection.commit()
            self.connection.close()

    def pay(self, username: str, end_date):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET pay_end=%s WHERE username=%s', (end_date, username))
            self.connection.commit()
            self.connection.close()

    def is_pay(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''SELECT pay_end FROM users WHERE telegram_id=(%s)''', (telegram_id,))
            pay_end = cursor.fetchone()[0]
            """По хорошему
            переписать на проверку на
            типах данных DATETIME"""
            self.connection.close()
        return str(pay_end) >= str(date.today())

    def add_admin(self, username):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''INSERT IGNORE INTO admins(username) VALUES (%s)''', (username,))
            self.connection.commit()
            self.connection.close()

    def is_admin(self, username):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT username FROM admins")
            res = cursor.fetchall()
            self.connection.close()
        return username in [i[0]for i in res]

    def create_client(self, telegram_id, api_id, api_hash, phone_number):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO users_bots(api_id, api_hash, phone,user_id) VALUES(%s,%s,%s, (SELECT id FROM users WHERE telegram_id=%s)) ",
                           (api_id, api_hash, phone_number, telegram_id))
            res = cursor.fetchall()
        self.connection.close()
        return res in [i[0]for i in res]

    def all_user_bots(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT phone FROM users_bots WHERE user_id=(SELECT id FROM users WHERE telegram_id=%s)", (telegram_id,))
            res = cursor.fetchall()
        self.connection.close()
        return [i[0]for i in res]

    def update_description(self, phone, system_role_description):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE users_bots SET system_role=%s WHERE phone=%s ",
                           (system_role_description, phone))
        self.connection.close()

    def get_data_for_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users_bots WHERE phone=%s ", (phone))
            res = cursor.fetchall()
        self.connection.close()
        return res[0]

    def start_new_dialog_counter_update(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE users_bots SET dialogs_counts=dialogs_counts+1 WHERE phone=%s ",
                           (phone))
        self.connection.close()

    def get_dialog_counter(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT dialogs_counts FROM users_bots WHERE phone=%s ", (phone))
            res = cursor.fetchall()
        self.connection.close()
        return res[0]

    def is_active(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT is_active FROM users_bots WHERE phone=%s", (phone))
            res = cursor.fetchone()[0]
            self.connection.close()
        return res

    def set_bot_ative(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE users_bots SET is_active=1 WHERE phone=%s ",
                           (phone))
        self.connection.close()

    def all_active_bots(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users_bots WHERE is_active=1")
            res = cursor.fetchall()
            self.connection.close()
        # return [i[0]for i in res]
        return res

    def activate_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users_bots SET is_active=1 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()

    def deactivate_client(self, phone):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users_bots SET is_active=0 WHERE phone=%s", (phone))
            res = cursor.fetchall()
            self.connection.close()


if __name__ == "__main__":
    a = Database("swm")
    a.cbdt()
    a.update_table()
