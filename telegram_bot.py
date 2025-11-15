from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from data_manager import DataManager
data = DataManager.load_data()

import requests
from datetime import datetime

now = datetime.now()
BOT_TOKEN = "8484007800:AAG7Ue5fD_S0xJJVBndif-gPKQ-_gTNXrvg"

spreadsheetId = "1LBF5RNskIjOPsos-nUjh4-smF54Au25GwWGcXIJRMtI"

endpoint_sheet = f"/v4/spreadsheets/{spreadsheetId}/values/Лист1"
url_sheet = "https://sheets.googleapis.com"
API_key = "AIzaSyA4pouqwMbU7WT_w0YVjoLN8XmoJeNmI8U"
paramkey = "?key="+API_key


def check_time_intervals(data_array):
    """Проверяет пересечение текущего времени с интервалами в данных"""

    now = datetime.now()
    current_date = now.strftime("%d.%m.%Y")
    current_time = now.strftime("%H:%M")

    headers = data_array["values"][0]
    rows = data_array["values"][1:]

    # Находим индексы колонок
    date_col = headers.index("Дата")
    start_col = headers.index("Начало")
    end_col = headers.index("Конец")
    module_col = headers.index("Модуль") if "Модуль" in headers else -1

    active_events = []

    for i, row in enumerate(rows):
        if len(row) > date_col and row[date_col] == current_date:
            start_time = row[start_col] if start_col < len(row) else ""
            end_time = row[end_col] if end_col < len(row) else ""
            project = row[module_col] if module_col < len(row) and module_col != -1 else "Не указан"

            if start_time and end_time:
                # Простое сравнение строк (работает для формата HH:MM)
                if start_time <= current_time <= end_time:
                    active_events.append({
                        'row': i + 2,
                        'start': start_time,
                        'end': end_time,
                        'project': project
                    })

    return active_events, current_date, current_time, project
def find_demo():

    response = requests.get(url = url_sheet+endpoint_sheet+paramkey)

    if response.status_code == 200:
        data = response.json()
        DataManager.update_data(data)

        active_events, current_date, current_time, project = check_time_intervals(data)

        print(f"Проверка на {project} {current_date} {current_time}:")
        if active_events:
            print("🚨 Обнаружены активные события!")
            for event in active_events:
                return (f" 🚨 Обнаружены активные события!  \nСобытие {event['project']}: {event['start']} - {event['end']}")
        else:
            return ("✅ Активных событий не обнаружено")

# Клавиатура с кнопками
def main_keyboard():
    keyboard = [
        [KeyboardButton("📊 Информация"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("🆘 Помощь"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_keyboard()

    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Информация":
        result = find_demo()
        await update.message.reply_text(result)
    elif text == "⚙️ Настройки":
        await update.message.reply_text("Раздел настроек.")
    elif text == "🆘 Помощь":
        await update.message.reply_text("Чем могу помочь?")
    elif text == "📞 Контакты":
        await update.message.reply_text("Контакты: example@email.com")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Доступные команды:
/start - начать работу
/help - показать справку
/echo - эхо-сообщение

    """
    await update.message.reply_text(help_text)

# Команда /echo
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"Вы сказали: {text}")
    else:
        await update.message.reply_text("Напишите текст после команды /echo")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = f"Вы написали: {text}"
    await update.message.reply_text(response)

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

    application.add_error_handler(error_handler)

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()