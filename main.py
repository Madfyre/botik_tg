import itertools

import telebot
from telebot import types
import pymysql

from config import *

bot = telebot.TeleBot(BOT_TOKEN)


connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=3306,
    cursorclass=pymysql.cursors.DictCursor,
)

INSERT_USER_QUERY_ACC_ID = """
                    INSERT INTO users(account_id)
                    VALUES (%s)
                    """
INSERT_USER_QUERY_USERNAME = """
                    UPDATE users
                    SET username = %s
                    """
INSERT_USER_QUERY_FIRST_NAME = """
                    UPDATE users
                    SET first_name = %s
                    """
INSERT_USER_QUERY_LAST_NAME = """
                    UPDATE users
                    SET last_name = %s
                    """
INSERT_USER_QUERY_AGE = """
                    UPDATE users
                    SET age = %s
                    """
INSERT_USER_QUERY_SEX = """
                    UPDATE users
                    SET sex = %s
                    """
INSERT_USER_QUERY_ANKETA = """
                    UPDATE users
                    SET anketa = %s
                    """
INSERT_USER_SEEK_FOR = """
                    UPDATE users
                    SET seek_for = %s
                    """
INSERT_QUESTIONS = """
                    INSERT INTO questions(question)
                    VALUES (%s);
                    """
VERIFY_USER_QUERY = """
                    UPDATE users
                    SET verified = %s
                    """
SELECT_USER_DATA_QUERY = """
                    SELECT account_id
                    FROM users
                    """
SELECT_PEOPLE = """
                    SELECT first_name, last_name, age, sex
                    FROM users
                    """
SELECT_ANSWERS = """
                    SELECT first_name, last_name, age, sex
                    FROM user_question
                    """
ADMIN_CHOICE = (
    "Чтобы добавить вопрос, напиши /add\n"
    "Чтобы вывести все вопросы, напиши /read\n"
    "Чтобы удалить вопрос, напиши /delete\n"
    "Чтобы начать рассылку вопросов /start_mailing\n"
    "Чтобы выйти из режима админа нажми /exit\n"
)

DELETE_QUESTIONS = """
    UPDATE questions
    SET visability = 0
    WHERE id = %s;
    """



@bot.message_handler(commands=["start"])
def start(message):
    account_id = message.from_user.id
    account_username = message.from_user.username
    with connection.cursor() as cursor:
        try:
            cursor.execute(INSERT_USER_QUERY_ACC_ID, (account_id,))
            connection.commit()
        except pymysql.err.IntegrityError:
            pass

        try:
            cursor.execute(
                INSERT_USER_QUERY_USERNAME + " WHERE account_id = %s;",
                (account_username, account_id),
            )
            connection.commit()
        except:
            connection.rollback()
    a = types.ReplyKeyboardRemove()
    bot.send_message(account_id, "Привет! Введи свое имя", reply_markup=a)
    bot.register_next_step_handler(message, first_name)


def first_name(message):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                INSERT_USER_QUERY_FIRST_NAME + " WHERE account_id = %s;",
                (message.text, message.from_user.id),
            )
            connection.commit()
        except:
            connection.rollback()
    bot.send_message(message.from_user.id, "Какая у тебя фамилия?")
    bot.register_next_step_handler(message, get_last_name)


def get_last_name(message):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                INSERT_USER_QUERY_LAST_NAME + " WHERE account_id = %s;",
                (message.text, message.from_user.id),
            )
            connection.commit()
        except:
            connection.rollback()
    bot.send_message(message.from_user.id, "Сколько тебе лет?")
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    if not message.text.isnumeric():
        bot.send_message(message.from_user.id, "Цифрами, пожалуйста")
        bot.register_next_step_handler(message, get_age)
        return
    if int(message.text) > 120 or int(message.text) < 18:
        bot.send_message(message.from_user.id, "🤨")
        bot.send_message(message.from_user.id, "Допустимый возраст от 18 до 120\nВведи возраст еще раз, пожалуйста")
        bot.register_next_step_handler(message, get_age)
        return
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                INSERT_USER_QUERY_AGE + " WHERE account_id = %s;",
                (int(message.text), message.from_user.id),
            )
            connection.commit()
        except:
            connection.rollback()

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="Мужской", callback_data="Male")
    item2 = types.InlineKeyboardButton(text="Женский", callback_data="Female")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, "Какой у тебя пол?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in {"Male", "Female"})
def callback_worker(call):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                INSERT_USER_QUERY_SEX + " WHERE account_id = %s;",
                (call.data, call.from_user.id),
            )
            connection.commit()
        except:
            connection.rollback()
    # message = bot.send_message(call.from_user.id, "Хорошо, запомнил! :)")
    '''
    with connection.cursor() as cursor:
        cursor.execute(
            SELECT_USER_DATA_QUERY + " WHERE account_id = %s;",
            (call.from_user.id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                call.from_user.id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        sex = "Парень" if row["sex"] == "Male" else "Девушка"
        if 5 <= int(str(row["age"])[-2:]) <= 20:
            age_word = "лет"
        elif 2 <= int(str(row["age"])[-1]) <= 4:
            age_word = "года"
        elif int(str(row["age"])[-1]) == 0:
            age_word = "лет"
        else:
            age_word = "год"
        message = bot.send_message(
            call.from_user.id,
            "Тебя зовут {} {}\nТебе {} {}\nТы {}".format(
                row["first_name"], row["last_name"], row["age"], age_word, sex
            ),
        )
    '''
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None
        )
    except telebot.apihelper.ApiTelegramException:
        pass

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="Парня", callback_data="Boy")
    item2 = types.InlineKeyboardButton(text="Девушку", callback_data="Girl")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(call.message.chat.id, "Кого ты ищешь?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in {"Boy", "Girl"})
def callback_seek_for(call):
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None
        )
    except telebot.apihelper.ApiTelegramException:
        pass
    if call.data == "Boy":
        seeking_for = "парня"
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    INSERT_USER_SEEK_FOR + " WHERE account_id = %s;",
                    ('boy', call.from_user.id),
                )
                connection.commit()
            except:
                connection.rollback()
    elif call.data == "Girl":
        seeking_for = "девушку"
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    INSERT_USER_SEEK_FOR + " WHERE account_id = %s;",
                    ('girl', call.from_user.id),
                )
                connection.commit()
            except:
                connection.rollback()

    with connection.cursor() as cursor:
        cursor.execute(
            SELECT_USER_DATA_QUERY + " WHERE account_id = %s;",
            (call.from_user.id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                call.from_user.id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        sex = "парень" if row["sex"] == "Male" else "девушка"
        if 5 <= int(str(row["age"])[-2:]) <= 20:
            age_word = "лет"
        elif 2 <= int(str(row["age"])[-1]) <= 4:
            age_word = "года"
        elif int(str(row["age"])[-1]) == 0:
            age_word = "лет"
        else:
            age_word = "год"
        message = bot.send_message(
            call.from_user.id,
            "Тебя зовут {} {}\nТебе {} {}\nТы {}\nТы ищешь {}".format(
                row["first_name"], row["last_name"], row["age"], age_word, sex, seeking_for
            ),
        )

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="Да", callback_data="Yes")
    item2 = types.InlineKeyboardButton(text="Нет", callback_data="No")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, "Все верно?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in {"Yes", "No"})
def verify(call):
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None
        )
    except telebot.apihelper.ApiTelegramException:
        pass
    if call.data == "Yes":
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    VERIFY_USER_QUERY + " WHERE account_id = %s;",
                    (1, call.from_user.id),
                )
                bot.send_message(call.from_user.id, "Теперь жди 14 февраля и мы тебе подберем идеальную пару/друга")
                connection.commit()
            except:
                connection.rollback()
    if call.data == "No":
        message = bot.send_message(call.from_user.id, "Тогда придется ввести данные повторно")
        bot.register_next_step_handler(message, first_name)
        bot.send_message(call.from_user.id, "Введи свое имя")

'''
def verify(message):
    if message.text.lower().strip() == "да":
        bot.send_message(message.from_user.id, "Хорошо, скоро тут будут вопросы")
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    VERIFY_USER_QUERY + " WHERE account_id = %s;",
                    (1, message.from_user.id),
                )
                connection.commit()
            except:
                connection.rollback()
    elif message.text.lower().strip() == "нет":
        bot.send_message(message.from_user.id, "Тогда придется ввести данные повторно")
        return start(message)
    else:
        bot.send_message(message.from_user.id, "Да/Нет")
        bot.register_next_step_handler(message, verify)
'''

@bot.message_handler(commands=["admin"])
def admin(message):
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT first_name, admin_rights FROM users WHERE account_id = %s;",
            (message.from_user.id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                message.from_user.id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        if not row["admin_rights"]:
            bot.send_message(
                message.from_user.id,
                "Извини, у тебя недостаточно прав для этой команды",
            )
            return
    bot.send_message(
        message.from_user.id,
        f"Добро пожаловать, {row['first_name']}\nРад тебя видеть :)",
    )
    bot.send_message(
        message.from_user.id,
        ADMIN_CHOICE,
    )
    bot.register_next_step_handler(message, admin_choice)


def admin_choice(message):
    if message.text == "/add":
        bot.send_message(message.from_user.id, "Хорошо, введи новый вопрос для анкеты")
        bot.register_next_step_handler(message, add_question)
    elif message.text == "/read":
        read_questions(message)
    elif message.text == "/delete":
        bot.send_message(message.from_user.id, "Хорошо, введи номер вопроса, который хочешь удалить \n"
                                               "Если хочешь отменить удаление, напиши /cancel")
        bot.register_next_step_handler(message, delete_question)
    elif message.text == "/start_mailing":
        bot.send_message(message.from_user.id, "Точно начать рассылку?\n/Yes\n/No")
        bot.register_next_step_handler(message, start_mailing_attention)
    elif message.text == "/fuck":
        bot.send_message(message.from_user.id, "Точно начать сношения?\n/Yes\n/No")
        bot.register_next_step_handler(message, start_fuck_attention)
    elif message.text == "/exit":
        bot.send_message(message.from_user.id, "Выхожу из админки")


def read_questions(message):
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM questions WHERE visability = 1 ORDER BY id ASC;")
        questions = cursor.fetchall()

    for question in questions:
        id_of_question = question["id"]
        text = f"{id_of_question}) " + question["question"] + "\n" + "\n".join(question["possible_answers"].split(";"))
        bot.send_message(
            message.from_user.id,
            text,
        )
    bot.send_message(
        message.from_user.id,
        ADMIN_CHOICE,
    )
    bot.register_next_step_handler(message, admin_choice)

def delete_question(message):
    if message.text == "/cancel":
        bot.send_message(
            message.from_user.id,
            ADMIN_CHOICE,
        )
        bot.register_next_step_handler(message, admin_choice)
        return
    if not message.text.isnumeric():
        bot.send_message(message.from_user.id, "Цифрами, пожалуйста")
        bot.register_next_step_handler(message, delete_question)
        return
    with connection.cursor() as cursor:
        cursor.execute(
            DELETE_QUESTIONS,
            (int(message.text),),
        )
        connection.commit()
        #connection.rollback()
    bot.send_message(
        message.from_user.id,
        "Удален номер " + message.text + '!',
    )
    bot.send_message(
        message.from_user.id,
        ADMIN_CHOICE,
    )
    bot.register_next_step_handler(message, admin_choice)


def add_question(message):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                INSERT_QUESTIONS,
                (message.text,),
            )
            connection.commit()
        except:
            connection.rollback()
        cursor.execute(
            "SELECT id FROM questions ORDER BY id DESC LIMIT 1;",
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                message.from_user.id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
    id_ = row["id"]
    bot.send_message(message.from_user.id, f"Вопрос добавлен. id = {id_}")
    bot.send_message(
        message.from_user.id,
        "Теперь чтобы добавить варианты ответа напиши так:\n<id Вопроса>\n<Варианты ответов каждый с новой строки>",
    )
    bot.register_next_step_handler(message, add_question_answers)


def add_question_answers(message):
    id_, *answers = message.text.split("\n")
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "UPDATE questions SET possible_answers = %s WHERE id = %s",
                (";".join(answers), id_),
            )
            connection.commit()
        except:
            connection.rollback()
    bot.send_message(message.from_user.id, "Вопрос добавлен!")
    bot.send_message(
        message.from_user.id,
        ADMIN_CHOICE,
    )
    bot.register_next_step_handler(message, admin_choice)


def start_mailing_attention(message):
    if message.text == "/Yes":
        bot.send_message(message.from_user.id, "Начинаю рассылку...")
        start_mailing()
    elif message.text == "/No":
        bot.send_message(message.from_user.id, "Отмена")
        bot.send_message(
            message.from_user.id,
            ADMIN_CHOICE,
        )
        bot.register_next_step_handler(message, admin_choice)


def start_mailing():
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE admin_rights = 0 AND verified = 1;")
        users = cursor.fetchall()
        cursor.execute("SELECT * FROM questions WHERE visability = 1 AND possible_answers != '' ORDER BY id ASC;")
        questions = cursor.fetchall()
        questions_map = {q["id"]: q for q in questions}
        for user in users:
            cursor.execute(
                "SELECT question_id FROM user_question WHERE user_id = %s AND answer != '' ORDER BY question_id DESC LIMIT 1",
                (user["id"],),
            )
            last_question_id = cursor.fetchall()
            if not last_question_id:
                last_question_id = min(questions_map.keys())
            else:
                try:
                    last_question_id = next(filter(lambda x: x > last_question_id[0]["question_id"], questions_map.keys()))
                except StopIteration:
                    continue
            markup = types.InlineKeyboardMarkup()
            try:
                items = [
                    types.InlineKeyboardButton(
                        text=answer, callback_data=f"{last_question_id}%{i}"
                    )
                    for i, answer in enumerate(
                        questions_map[last_question_id]["possible_answers"].split(";")
                    )
                ]
            except IndexError:
                continue
            [markup.add(item) for item in items]
            bot.send_message(
                user["account_id"],
                questions_map[last_question_id]["question"],
                reply_markup=markup,
            )
            try:
                cursor.execute(
                    "INSERT INTO user_question (user_id, question_id) VALUES (%s, %s);",
                    (user["id"], last_question_id),
                )
                connection.commit()
            except:
                connection.rollback()


@bot.callback_query_handler(func=lambda call: "%" in call.data)
def callback_worker(call):
    question_id, answer_index = map(int, call.data.split("%"))
    account_id = call.from_user.id
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT possible_answers FROM questions WHERE id = %s",
            (question_id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                account_id,
                "Извини что-то пошло не так, попробуй немного позднее :B",
            )
            return
        try:
            possible_answers = row["possible_answers"].split(";")
        except KeyError:
            bot.send_message(
                account_id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        try:
            cursor.execute(
                "UPDATE user_question "
                "JOIN users ON user_question.user_id = users.id "
                "JOIN questions ON user_question.question_id = questions.id "
                "SET user_question.answer = %s "
                "WHERE questions.id = %s AND users.account_id = %s",
                (possible_answers[answer_index], question_id, account_id),
            )
            connection.commit()
        except:
            connection.rollback()
            bot.send_message(
                account_id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=None,
            )
        except telebot.apihelper.ApiTelegramException:
            pass
        bot.send_message(call.from_user.id, "Ответ записан :)")
        cursor.execute(
            "SELECT id FROM questions WHERE id > %s AND visability = 1 ORDER BY id LIMIT 1",
            (question_id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            next_question(account_id, -1)
            return
        next_question(account_id, int(row["id"]))


def next_question(account_id, next_question_id):
    connection.begin()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT question, possible_answers FROM questions WHERE id = %s",
            (next_question_id,),
        )
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                account_id,
                "На этом всё :)\nУже 14 февраля мы подберем тебе человека для знакомства)",
            )
            return
        question = row["question"]
        possible_answers = row["possible_answers"].split(";")
        cursor.execute("SELECT id FROM users WHERE account_id = %s", (account_id,))
        rows = cursor.fetchall()
        try:
            row = next(iter(rows))
        except StopIteration:
            bot.send_message(
                account_id,
                "Извини что-то пошло не так, попробуй немного позднее :(",
            )
            return
        user_id = row["id"]
        markup = types.InlineKeyboardMarkup()
        items = [
            types.InlineKeyboardButton(
                text=answer, callback_data=f"{next_question_id}%{i}"
            )
            for i, answer in enumerate(possible_answers)
        ]
        [markup.add(item) for item in items]
        bot.send_message(
            account_id, "Следующий вопрос:\n" + question, reply_markup=markup
        )
        try:
            cursor.execute(
                "INSERT INTO user_question (user_id, question_id) VALUES (%s, %s);",
                (user_id, next_question_id),
            )
            connection.commit()
        except:
            connection.rollback()



'''
def start_fuck_attention(message):
    if message.text == "/Yes":
        bot.send_message(message.from_user.id, "Начинаю сношения...")
        start_fuck()
    elif message.text == "/No":
        bot.send_message(message.from_user.id, "Отмена")
        bot.send_message(
            message.from_user.id,
            ADMIN_CHOICE,
        )
        bot.register_next_step_handler(message, admin_choice)

def start_fuck():
    people = SELECT_PEOPLE
    people_preferences =
    itertools.combinations(people)
    combinations('ABCD', 2)
'''

bot.polling(none_stop=True, interval=1, timeout=600)
