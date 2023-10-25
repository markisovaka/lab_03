import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import io
matplotlib.use('agg')

#функция вывода диаграммы доходов
def visual_incomes(update, context, user_id):

    #подключение к базе данных
    db = sqlite3.connect('finances.db', check_same_thread=False)
    cursor = db.cursor()

    #т.к. user_id сейчас не закреплен, выводим лист tipe_id(каждый tipe_id встречается один раз), где делаем проверку на user_id)
    cursor.execute("SELECT type_id FROM 'incomes' WHERE user_id =?", (user_id,))
    types = cursor.fetchall()
    types = [i[0] for i in types]
    types = list(set(types))

    #создаем массив названий по type_id
    exp_labels = []
    for elem1 in types:
        cursor.execute("SELECT name FROM 'income_types' WHERE id = ?", (elem1,))
        result = cursor.fetchone()
        exp_labels.append(result[0])
        if len(exp_labels) == 0:
            return "У вас нет доходов"

    # создаем массив значений по type_id
    exp_values = []
    for elem2 in types:
        cursor.execute("SELECT SUM(amount) FROM 'incomes' WHERE type_id = ?", (elem2,))
        result = cursor.fetchone()
        exp_values.append(result[0])

    #визуальная составляющая matplotlip и создание pie chart
    plt.style.use('ggplot')
    plt.title('Диаграмма доходов')
    plt.pie(x=exp_values, labels=exp_labels, autopct='%.2f%%', shadow=True, startangle=90)
    plt.axis("equal")
    plt.legend(loc='upper left')
    circle = plt.Circle(xy=(0, 0), radius=.75, facecolor='white')
    plt.gca().add_artist(circle)

    # Сохранение картинки в буффер
    db.commit()
    db.close()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Отправка картинки пользователю
    context.bot.send_photo(chat_id=user_id, photo=buf)
    plt.close()
    return 0

#функция вывода диаграммы расходов
def visual_expenses(update, context, user_id):
    # подключение к базе данных
    db = sqlite3.connect('finances.db', check_same_thread=False)
    cursor = db.cursor()

    # т.к. user_id сейчас не закреплен, выводим лист tipe_id(каждый tipe_id встречается один раз), где делаем проверку на user_id)
    cursor.execute("SELECT type_id FROM 'expenses' WHERE user_id =?", (user_id,))
    types = cursor.fetchall()
    types = [i[0] for i in types]
    types = list(set(types))

    # создаем массив названий по type_id
    exp_labels = []
    for elem1 in types:
        cursor.execute("SELECT name FROM 'expense_types' WHERE id = ?", (elem1,))
        result = cursor.fetchone()
        exp_labels.append(result[0])
        if len(exp_labels) == 0:
            return "У вас нет расходов"

    # создаем массив значений по type_id
    exp_values = []
    for elem2 in types:
        cursor.execute("SELECT SUM(amount) FROM 'expenses' WHERE type_id = ?", (elem2,))
        result = cursor.fetchone()
        exp_values.append(result[0])

    # визуальная составляющая matplotlip и создание pie chart
    plt.style.use('ggplot')
    plt.title('Диаграмма расходов')
    plt.pie(x=exp_values, labels=exp_labels, autopct='%.2f%%', shadow=True, startangle=90)
    plt.axis("equal")
    plt.legend(loc='upper left')
    circle = plt.Circle(xy=(0, 0), radius=.75, facecolor='white')
    plt.gca().add_artist(circle)

    # Сохранение картинки в буффер
    db.commit()
    db.close()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Отправка картинки пользователю
    context.bot.send_photo(chat_id=user_id, photo=buf)
    plt.close()
    return 0
