import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Инициализация базы данных
db = sqlite3.connect('finances.db', check_same_thread=False)
cursor = db.cursor()
def goal(update, context):
    print("goal")
    # добавляем кнопки для работы с целями
    keyboard = [[InlineKeyboardButton("Добавить цель", callback_data='add_goal')],
                [InlineKeyboardButton("Посмотреть цели", callback_data='view_goals')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # выводим кнопки
    update.message.reply_text('Выберите, что вы хотите сделать:', reply_markup=reply_markup)
    return ConversationHandler.END


def goal_action_button(update, context):
    print("goal_button")
    query = update.callback_query
    # Получение значения поля "data" из callback
    action = query.data
    # Получение идентификатора чата пользователя из callback
    user_id = update.callback_query.message.chat.id
    if action == 'add_goal':
        keyboard = [[InlineKeyboardButton("Расходы", callback_data='goal_expense')],
                    [InlineKeyboardButton("Доходы", callback_data='goal_income')]]
        reply_markup = InlineKeyboardMarkup(keyboard)  # Создание разметки клавиатуры с кнопками
        query.message.reply_text('К чему вы хотите привязать цель:', reply_markup=reply_markup)
    elif action == 'view_goals':
            query.message.reply_text("тут что-то будет")
    return ConversationHandler.END


# обработчик кнопки
def goal_type_button(update, context):
    print("goal_type_button")
    # получаем id пользователя
    user_id = update.callback_query.message.chat.id
    query = update.callback_query
    goal_type = query.data
    # сохраняем тип цели в словаре user_data
    context.user_data['goal_type'] = goal_type.split("goal_", maxsplit=1)[1]
    # если тип цели - расход
    if context.user_data['goal_type'] == 'expense':
        cursor.execute("SELECT name FROM expense_types WHERE user_id=?", (user_id,))
        types_names = cursor.fetchall()
        # если у пользователя нет типов расходов
        if len(types_names) == 0:
            update.message.reply_text('У вас пока нет типов расходов. Добавьте тип с помощью команды /add_type.')
            return ConversationHandler.END
    # если тип цели - доход
    elif context.user_data['goal_type'] == 'income':
        cursor.execute("SELECT name FROM income_types WHERE user_id=?", (user_id,))
        types_names = cursor.fetchall()
        # если у пользователя нет типов доходов
        if len(types_names) == 0:
            update.message.reply_text('У вас пока нет типов доходов. Добавьте тип с помощью команды /add_type.')
            return ConversationHandler.END
    # создание кнопки
    keyboard = [[InlineKeyboardButton(types_name[0], callback_data=("goal_name:" + types_name[0]))] for
                types_name in types_names]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('К чему вы хотите привязать цель:', reply_markup=reply_markup)
    return ConversationHandler.END


def goal_name_button(update, context):
    print("goal_name_button")
    query = update.callback_query
    # Получить тип цели из данных о нажатии кнопки
    goal_type = query.data
    context.user_data['goal_name'] = goal_type.split("goal_name:", maxsplit=1)[1]
    # Получить имя цели из типа цели и сохранить в словаре user_data
    query.message.reply_text('Введите сумму цели:')
    return "goal_amount"


def goal_amount(update, context):
    print("goal_amount")
    amount = update.message.text  # Записываем введенный текст в переменную amount
    if not amount.isdigit():  # Проверяем, является ли введенный текст числом
        update.message.reply_text("Сумма должна быть целым неотрицательным числом\nПопробуйте еще раз")
        return "goal_amount"
    amount = int(amount)
    # Сохраняем введенную сумму в словаре user_data
    context.user_data['goal_amount'] = amount
    update.message.reply_text('Введите дедлайн достижения цели в формате ГГГГ-MM-ДД:')

    return "goal_date"


# Функция для обработки команды /start
def start(update, context):
    print("start")
    user_id = update.message.from_user.id

    # Проверяем, есть ли пользователь в бд
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        # Если пользователя нет в бд, добавляем его
        cursor.execute("INSERT INTO users VALUES (?)", (user_id,))
        db.commit()
        update.message.reply_text("Добро пожаловать в трекер бюджета!")
    else:
        update.message.reply_text("Вы уже зарегистрированы в трекере бюджета")


# Функция команды /add_type
def add_type(update, context):
    print("add_type")
    # Создаем клавиатуру с кнопками "Расходы" и "Доходы"
    keyboard = [[InlineKeyboardButton("Расходы", callback_data='expense')],
                [InlineKeyboardButton("Доходы", callback_data='income')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Выводим сообщение и клавиатуру
    update.message.reply_text('Выберите куда добавить тип:', reply_markup=reply_markup)


# Функция кнопки выбора типа
def type_button(update, context):
    print("type_button")
    query = update.callback_query

    # Получаем выбранный тип из данных кнопки
    type_name = query.data

    # Запрашиваем у пользователя название типа
    if type_name == 'expense':
        query.message.reply_text('Введите название типа расходов:')
    elif type_name == 'income':
        query.message.reply_text('Введите название типа доходов:')

    # Сохраняем данные о выбранном типе в контексте
    context.user_data['type_name'] = type_name
    return "type"


# Функция сообщения с названием типа
def save_type(update, context):
    print("save_type")
    user_id = update.message.from_user.id
    type_name = context.user_data['type_name']
    name = update.message.text

    # Проверяем, есть ли уже у пользователя такой тип
    if type_name == 'expense':
        cursor.execute("SELECT * FROM expense_types WHERE user_id=? AND name=?", (user_id, name))
    elif type_name == 'income':
        cursor.execute("SELECT * FROM income_types WHERE user_id=? AND name=?", (user_id, name))

    type_info = cursor.fetchone()

    if type_info is None:
        # Если типа нет, добавляем его в бд
        if type_name == 'expense':
            cursor.execute("INSERT INTO expense_types (user_id, name) VALUES (?, ?)", (user_id, name))
        elif type_name == 'income':
            cursor.execute("INSERT INTO income_types (user_id, name) VALUES (?, ?)", (user_id, name))

        db.commit()
        update.message.reply_text(f'Тип "{name}" сохранен!')
    else:
        update.message.reply_text(f'Тип "{name}" уже существует')

    # Удаляем выбранный тип из контекста
    del context.user_data['type_name']
    return ConversationHandler.END


# Функция команды /add_expense
def add_expense(update, context):
    print("add_expense")
    user_id = update.message.from_user.id

    # Получаем список типов расходов пользователя
    cursor.execute("SELECT * FROM expense_types WHERE user_id=?", (user_id,))
    expense_types = cursor.fetchall()
    # Говорим пользователю добавить тип, если их нет
    if len(expense_types) == 0:
        update.message.reply_text('У вас пока нет типов расходов. Добавьте тип с помощью команды /add_type.')
        return

    # Создаем клавиатуру типов расходов
    keyboard = [[InlineKeyboardButton(expense_type[2], callback_data=("EXPENSE:" + str(expense_type[0])))] for
                expense_type in expense_types]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выберите тип расходов:', reply_markup=reply_markup)
    return "expense_button"


# Функция кнопки выбора типа расходов
def expense_button(update, context):
    print("expense_button")
    query = update.callback_query
    # Получаем выбранный тип расходов из данных кнопки
    type_id = int(query.data.split("EXPENSE:", maxsplit=1)[1])
    # Сохраняем выбранный тип расходов в контексте
    context.user_data['type_id'] = type_id

    # Запрашиваем у пользователя сумму расходов
    query.message.reply_text(f'Введите сумму расходов:')
    return "expense"


# Функция сообщения с суммой расходов
def save_expense(update, context):
    print("save_expense")
    comment = ""
    user_id = update.message.chat.id
    type_id = context.user_data["type_id"]
    # Получаем размер расходов и комментарий
    if " " in update.message.text:
        amount, comment = update.message.text.split(maxsplit=1)
    else:
        amount = update.message.text
    amount = int(amount)

    # Добавляем расходы в бд
    cursor.execute(
        "INSERT INTO expenses (user_id, type_id, amount, comment, timestamp) VALUES (?, ?, ?, ?, datetime('now'))",
        (user_id, type_id, amount, comment))
    db.commit()

    update.message.reply_text('Расходы сохранены!')

    # Удаляем данные о выбранном типе расходов из контекста
    del context.user_data['type_id']
    return ConversationHandler.END


# Функция команды /add_income
def add_income(update, context):
    print("add_income")
    user_id = update.message.from_user.id

    # Получаем список типов доходов пользователя
    cursor.execute("SELECT * FROM income_types WHERE user_id=?", (user_id,))
    income_types = cursor.fetchall()

    # Говорим пользователю добавить тип, если их нет
    if len(income_types) == 0:
        update.message.reply_text('У вас пока нет типов доходов. Добавьте тип с помощью команды /add_type.')
        return

    # Создаем клавиатуру типов доходов
    keyboard = [[InlineKeyboardButton(income_type[2], callback_data=("INCOME:" + str(income_type[0])))] for income_type
                in income_types]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выберите тип доходов:', reply_markup=reply_markup)
    return "income_button"


# Функция сообщения с суммой доходов
def save_income(update, context):
    print("save_income")
    comment = ""
    user_id = update.message.chat.id
    type_id = context.user_data["type_id"]
    # Получаем размер расходов и комментарий
    if " " in update.message.text:
        amount, comment = update.message.text.split(maxsplit=1)
    else:
        amount = update.message.text
    amount = int(amount)

    # Добавляем расходы в бд
    cursor.execute(
        "INSERT INTO incomes (user_id, type_id, amount, comment, timestamp) VALUES (?, ?, ?, ?, datetime('now'))",
        (user_id, type_id, amount, comment))
    db.commit()

    update.message.reply_text('Доходы сохранены!')

    # Удаляем данные о выбранном типе доходов из контекста
    del context.user_data['type_id']

    return ConversationHandler.END


# Функция кнопки выбора типа доходов
def income_button(update, context):
    print("income_button")
    query = update.callback_query
    user_id = query.from_user.id

    # Получаем выбранный тип доходов из данных кнопки
    type_id = int(query.data.split("INCOME:", maxsplit=1)[1])

    # Сохраняем выбранный тип доходов в контексте
    context.user_data['type_id'] = type_id

    # Запрашиваем у пользователя сумму доходов
    query.message.reply_text('Введите сумму доходов:')
    return "income"


# Функция обработки неизвестных команд
def unknown_command(update, context):
    update.message.reply_text("Извините, я не понимаю эту команду.")


# Функция обработки ошибок
def error(update, context):
    print(f"Update {update} caused error {context.error}")


# Создание объекта Updater и передача токена бота
updater = Updater('5953145226:AAECAh2UaB5kCEfFM6YvsZ1zpBEYJTft83E', use_context=True)

# Получение диспетчера для регистрации обработчиков
dispatcher = updater.dispatcher

dispatcher.add_handler(CallbackQueryHandler(check_button, pattern='^(expense_list|income_list)$'))

# Регистрация обработчиков команд
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('add_type', add_type))
dispatcher.add_handler(CommandHandler('add_expense', add_expense))
dispatcher.add_handler(CommandHandler('add_income', add_income))
dispatcher.add_handler(CommandHandler('goal', goal))

# Регистрация обработчика неизвестных команд
dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

dispatcher.add_handler(CallbackQueryHandler(goal_action_button, pattern='^(add_goal|view_goals)$'))
dispatcher.add_handler(CallbackQueryHandler(goal_type_button, pattern='^goal_(expense|income)$'))
dispatcher.add_handler(CallbackQueryHandler(history_type_button, pattern='^(expense_history|income_history)$'))

# Регистрация обработчика ошибок
dispatcher.add_error_handler(error)
# MessageHandler(Filters.text & ~Filters.command, save_expense)
# регистрация обработчика сценариев
handlers_list = [CallbackQueryHandler(expense_button, pattern='^EXPENSE:\d+$'),
                 CallbackQueryHandler(type_button, pattern='^(expense|income)$'),
                 CallbackQueryHandler(income_button, pattern='^INCOME:\d+$'),
                 CallbackQueryHandler(goal_name_button, pattern='^goal_name:')]
handler_conv = ConversationHandler(
    entry_points=handlers_list,
    states={
        "expense": [MessageHandler(Filters.text & ~Filters.command, save_expense)] + handlers_list,
        "type": [MessageHandler(Filters.text & ~Filters.command, save_type)] + handlers_list,
        "income": [MessageHandler(Filters.text & ~Filters.command, save_income)] + handlers_list,
        "goal_amount": [MessageHandler(Filters.text & ~Filters.command, goal_amount)] + handlers_list,
        "goal_date": [MessageHandler(Filters.text & ~Filters.command, goal_date)] + handlers_list,

    },

    fallbacks=[]
)

dispatcher.add_handler(handler_conv)

# Запуск бота
updater.start_polling()
updater.idle()

# Закрытие базы данных
db.close()
 
