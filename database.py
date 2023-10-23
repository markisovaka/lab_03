import sqlite3
import datetime

# Инициализация базы данных
db = sqlite3.connect('/home/victoria/Testing/finances.db')
cursor = db.cursor()

# Создание таблицы id пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY)''')
# Создание таблицы типов доходов
cursor.execute('''CREATE TABLE IF NOT EXISTS income_types
                  (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  name TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id)
                  )''')
# Создание таблицы типов расходов
cursor.execute('''CREATE TABLE IF NOT EXISTS expense_types
                  (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  name TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id)
                  )''')
# Создание таблицы доходов
cursor.execute('''CREATE TABLE IF NOT EXISTS incomes (
                       id INTEGER PRIMARY KEY,
                       user_id INTEGER,
                       type_id INTEGER,
                       amount INTEGER,
                       comment TEXT,
                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id),
                       FOREIGN KEY (type_id) REFERENCES income_types(id)
                   )''')
# Создание таблицы расходов
cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                       id INTEGER PRIMARY KEY,
                       user_id INTEGER,
                       type_id INTEGER,
                       amount INTEGER,
                       comment TEXT,
                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id),
                       FOREIGN KEY (type_id) REFERENCES expense_types(id)
                   )''')
# Сохранение изменений
db.commit()
cursor.close()
db.close()
