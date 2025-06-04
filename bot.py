import telebot
from telebot import types
from config import BOT_TOKEN
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# ========== НАСТОЯЩИЙ БОТ ==========
bot = telebot.TeleBot(BOT_TOKEN)

# Вопросы и варианты ответов
questions = [
    {"text": "Какой цвет тебе нравится?", "options": ["Красный", "Синий", "Зелёный"]},
    {"text": "Любимое время года?", "options": ["Весна", "Лето", "Осень", "Зима"]},
    {"text": "Предпочитаешь кофе или чай?", "options": ["Кофе", "Чай"]}
]

# Состояния пользователей
user_data = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"answers": [], "current": 0}
    ask_question(chat_id, 0)

def ask_question(chat_id, index):
    if index >= len(questions):
        show_results(chat_id)
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for option in questions[index]["options"]:
        markup.add(option)

    bot.send_message(chat_id, questions[index]["text"], reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, handle_answer, index=index)

def handle_answer(message, index):
    chat_id = message.chat.id
    answer = message.text
    user_data[chat_id]["answers"].append(answer)
    ask_question(chat_id, index + 1)

def show_results(chat_id):
    answers = user_data[chat_id]["answers"]
    result_text = "Вы выбрали:\n"
    for i, ans in enumerate(answers):
        result_text += f"{i+1}. {questions[i]['text']} → {ans}\n"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Пройти снова"))
    bot.send_message(chat_id, result_text, reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, restart_poll)

def restart_poll(message):
    if message.text == "Пройти снова":
        start(message)
    else:
        bot.send_message(message.chat.id, "Напишите что угодно, чтобы начать.")


# ========== МИНИМАЛЬНЫЙ HTTP-СЕРВЕР (для Timeweb) ==========
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running.")

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleServer)
    httpd.serve_forever()

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    # Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Запускаем бота
    print("Бот запущен...")
    bot.polling(none_stop=True)