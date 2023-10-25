import sqlite3
from datetime import datetime


# функция, возвращает список целей
def goals_output(user_id):
    db = sqlite3.connect('finances.db', check_same_thread=False)
    cursor = db.cursor()
    # получаем все цели пользователя
    cursor.execute("SELECT *  FROM goals WHERE user_id=?", (user_id,))
    types_names = cursor.fetchall()
    goal_str_list = []
    if len(types_names) == 0:
        return ["У вас нет целей"]
    # перебираем все цели
    for elem in types_names:
        print(elem)
        if elem[3] == "expense":  # если цель связана с расходами
            # получаем id типа, скоторым связана цель
            cursor.execute("SELECT id  FROM expense_types WHERE user_id=? AND name=?", (user_id, elem[1]))
            type_id = cursor.fetchone()[0]
            type_of_ru = "Расходы"
            # получаем актуальные для этой цели суммы
            cursor.execute(
                "SELECT amount  FROM expenses WHERE user_id=? AND type_id=?  AND TIMESTAMP BETWEEN ? AND ?",
                (user_id, type_id, elem[5], elem[2]))
            archive_sum = cursor.fetchall()
            # получаем сумму всех сумм
            archive_sum = sum([i[0] for i in archive_sum])
            if archive_sum <= elem[4]:  # если сумма меньше целевой
                if datetime.now() >= datetime.strptime(elem[2],
                                                       '%Y-%m-%d ' + '%H:%M:%S'):  # если текущая дата больше целевой
                    archivment = f"Ура! Вы потратили {archive_sum} р - это не больше чем {elem[4]} р.\nЦель достигнута"
                else:  # если текущая дата меньше целевой
                    archivment = f"На данный момент вы потратили {archive_sum} р \nВы хотите потратить не больше {elem[4]} р."
            else:  # если сумма больше целевой
                archivment = f"Упс( Вы потратили {archive_sum} р - это больше чем {elem[4]} р.\nЦель провалена"
        else:  # если цель связана с дохходами
            # получаем id типа, скоторым связана цель
            cursor.execute("SELECT id  FROM income_types WHERE user_id=? AND name=?", (user_id, elem[1]))
            type_id = cursor.fetchone()[0]
            type_of_ru = "Доходы"

            # получаем актуальные для этой цели суммы
            cursor.execute(
                "SELECT amount  FROM incomes WHERE user_id=? AND type_id=?  AND TIMESTAMP BETWEEN ? AND ?",
                (user_id, type_id, elem[5], elem[2]))
            archive_sum = cursor.fetchall()

            # получаем сумму всех сумм
            archive_sum = sum([i[0] for i in archive_sum])
            if archive_sum <= elem[4]:  # если сумма меньше целевой
                if datetime.now() >= datetime.strptime(elem[2],
                                                       '%Y-%m-%d ' + '%H:%M:%S'):  # если текущая дата больше целевой
                    archivment = f"Упс( Вы заработали {archive_sum} р - это меньше чем {elem[4]} р.\nЦель провалена"
                else:  # если текущая дата меньше целевой
                    archivment = f"На данный момент вы заработали {archive_sum} р \nВы хотите заработать не меньше {elem[4]} р."
            else:  # если сумма больше целевой
                archivment = f"Ура! Вы заработали {archive_sum} р - это больше чем {elem[4]} р.\nЦель достигнута"
        # форматируем текст сообщения
        goal_str = f"Цель: {type_of_ru} - {elem[1]}\n" \
                   f"Дата начала: {elem[5].split()[0]}\n" \
                   f"Дата окончания: {elem[2].split()[0]}\n" + archivment
        # добавляем в список
        goal_str_list.append(goal_str)
    db.close()

    return goal_str_list


def is_valid_date(input_date):
    print("is_valid_date")
    try:
        # преобразуем строку в объект datetime
        date = datetime.strptime(input_date, '%Y-%m-%d ' + '%H:%M:%S')
        print(date)
        if date > datetime.now():  # дата должна быть больше текущей
            return True
        return False
    except ValueError:
        # если возникла ошибка ValueError, значит, дата введена некорректно
        return False
