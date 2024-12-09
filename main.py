import os  # Модуль для работы с файловой системой (поиск и чтение файлов)
import telebot  # Библиотека для взаимодействия с Telegram API
from telebot import types  # Модуль для создания кнопок и меню в Telegram

# Папка, где хранятся тексты произведений
TEXTS_FOLDER = "texts"

# Папка, где хранятся изображения произведений и портрет писателя
IMAGES_FOLDER = "images"

# Инициализация Telegram-бота с вашим API-токеном
bot = telebot.TeleBot("7553764929:AAHWsWeQ8H_EQ-bzYqLnKh5vQeXEAW5ex8Q")

# Функция для создания главного меню
def get_main_menu():
    # Создаем объект разметки для кнопок
    markup = types.ReplyKeyboardMarkup()
    # Добавляем кнопки для меню
    btn1 = types.KeyboardButton("Поиск произведения по названию")
    btn2 = types.KeyboardButton("Поиск произведения по отрывку или слову")
    btn3 = types.KeyboardButton("О чат-боте")
    # Располагаем кнопки в две строки
    markup.row(btn1, btn2)
    markup.row(btn3)
    return markup

# Хэндлер для команд "/start", "/run", "/activate"
@bot.message_handler(commands=["start", "run", "activate"])
def send_welcome(message):
    # Приветственное сообщение с главным меню
    bot.send_message(
        message.chat.id,
        "<b>Добро пожаловать!</b>👋🏼\n"
        "Этот бот помогает находить произведения Ф.М. Достоевского📖\n"
        "Выберите действие:",
        parse_mode="html",  # Указываем форматирование HTML для текста
        reply_markup=get_main_menu()  # Прикрепляем кнопки
    )

# Хэндлер для обработки выбора в главном меню
@bot.message_handler(func=lambda message: message.text in ["О чат-боте", "Поиск произведения по названию", "Поиск произведения по отрывку или слову"])
def handle_main_menu(message):
    if message.text == "О чат-боте":
        # Сообщение с информацией о боте и возвращение главного меню
        bot.send_message(
            message.chat.id,
            "Этот бот разработан студентом ТПУ группы 8И42 <u>Резнов И.В</u> для поиска информации о произведениях Ф.М. Достоевского.\n"
            "Выберите действие:",
            parse_mode="html",
            reply_markup=get_main_menu()
        )
    elif message.text == "Поиск произведения по названию":
        # Запрашиваем у пользователя название произведения
        bot.send_message(message.chat.id, "Введите название произведения:")
        # Передаем управление функции поиска по названию
        bot.register_next_step_handler(message, search_by_name)
    elif message.text == "Поиск произведения по отрывку или слову":
        # Запрашиваем у пользователя фрагмент текста
        bot.send_message(message.chat.id, "Введите отрывок или слово из произведения для поиска:")
        # Передаем управление функции поиска по фрагменту
        bot.register_next_step_handler(message, search_by_fragment)

# Функция для поиска произведения по названию
def search_by_name(message):
    title = message.text  # Получаем введенное пользователем название
    text_path = os.path.join(TEXTS_FOLDER, f"{title}.txt")  # Путь к файлу текста
    image_path = os.path.join(IMAGES_FOLDER, f"{title}.jpg")  # Путь к изображению произведения
    default_image_path = os.path.join(IMAGES_FOLDER, "portrait.jpg")  # Путь к портрету писателя

    # Проверяем, существует ли файл текста
    if os.path.exists(text_path):
        try:
            # Открываем файл с текстом в кодировке UTF-8
            with open(text_path, "r", encoding="utf-8") as file:
                path_text = file.read().split("\n")[:4]  # Читаем первые 4 строки текста
                fragment = "Отрывок из произведения:\n\n" + '\n'.join(path_text)
        except UnicodeDecodeError:
            # Если UTF-8 вызывает ошибку, пробуем открыть файл в кодировке Windows-1251
            with open(text_path, "r", encoding="windows-1251", errors="ignore") as file:
                path_text = file.read().split("\n")[:4]  # Читаем первые 4 строки текста
                fragment = "Отрывок из произведения:\n\n" + '\n'.join(path_text)

        # Проверяем наличие изображения произведения
        if os.path.exists(image_path):
            # Если изображение есть, отправляем его с текстом
            with open(image_path, "rb") as img:
                bot.send_photo(message.chat.id, img, caption=fragment)
        else:
            # Если изображения произведения нет, отправляем портрет писателя
            with open(default_image_path, "rb") as img:
                bot.send_photo(message.chat.id, img, caption=fragment)

        # После отправки результата возвращаем пользователя в главное меню
        bot.send_message(
            message.chat.id,
            "Выберите следующее действие:",
            reply_markup=get_main_menu()
        )
    else:
        # Если файл текста не найден, уведомляем пользователя
        bot.send_message(
            message.chat.id,
            "Произведение не найдено🤔\n"
            "Попробуйте другое название.",
            reply_markup=get_main_menu()
        )


# Функция для поиска произведений по отрывку или слову
def search_by_fragment(message):
    fragment = message.text.lower()  # Получаем текст от пользователя и приводим его к нижнему регистру
    results = []  # Список для хранения названий произведений, где найден фрагмент

    # Проходим по всем файлам в папке с текстами
    for filename in os.listdir(TEXTS_FOLDER):
        if filename.endswith(".txt"):  # Проверяем, что файл имеет формат .txt
            file_path = os.path.join(TEXTS_FOLDER, filename)
            try:
                # Открываем файл с текстом в кодировке UTF-8
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read().lower()  # Читаем и приводим текст к нижнему регистру
            except UnicodeDecodeError:
                # Если UTF-8 вызывает ошибку, пробуем открыть файл в кодировке Windows-1251
                with open(file_path, "r", encoding="windows-1251", errors="ignore") as file:
                    content = file.read().lower()

            # Проверяем, содержится ли фрагмент в тексте
            if fragment in content:
                # Если фрагмент найден, добавляем название произведения (без расширения .txt) в список результатов
                results.append(filename.replace(".txt", ""))

    # Если есть совпадения
    if results:
        bot.send_message(
            message.chat.id,
            f"Фрагмент найден в произведении(-ях): {', '.join(results)}",
            reply_markup=get_main_menu()
        )
    else:
        # Если совпадений нет, сообщаем об этом
        bot.send_message(
            message.chat.id,
            "Фрагмент не найден. Попробуйте другой текст.",
            reply_markup=get_main_menu()
        )


# Запуск бота для бесконечного ожидания сообщений
bot.infinity_polling()