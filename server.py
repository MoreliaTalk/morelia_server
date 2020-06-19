from flask import Flask
from flask import request
from datetime import datetime
from time import time
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

messages = [
    {
        "username": "Jack",
        "text": "hello",
        "timestamp": time(),
        "time": str(datetime.now().time())[:8]
    },
    {
        "username": "Jack2",
        "text": "helloyyyyy",
        "timestamp": time(),
        "time": str(datetime.now().time())[:8]
    }
        ]

users = {
        "jack": "12345",
        "jack2": "123456"
        }


@app.route("/")
def hello():
    return "Hello,user! " + "<a href=/status>Статус Pocegram</a>"


@app.route("/status")
def status():
    i = 0
    mi = 0
    for user in users:
        i += 1
        for mes in messages:
            mi += 1
    return {
            "status": "true",
            "name": "Pocegram",
            "time": str(datetime.now().time())[:8],
            "current_time_seconds": time(),
            "count_users": i,
            "count_messages": mi
            }


@app.route("/send_message")
def send_message():
    botegtext = ""
    r = request.json
    username = r["username"]
    password = r["password"]
    text = r["text"]
    if username in users:
        if users[username] != password:
            return {"ok": "false"}
    else:
        users[username] = password
    # Поменять имя в сообщении
    if text == "/chname":
        username = "Шашлык недоеденный(" + username + ")"
    messages.append({
                    "username": username,
                    "text": text,
                    "timestamp": time(),
                    "time": str(datetime.now().time())[:8]
                    })
    # Територия Ботов
    if text == "/status":
        for i in status():
            botegtext += i + ": " + str(status()[i]) + "\n"
        messages.append({
                        "username": "БотЪ ЕгорЪ",
                        "text": str(botegtext),
                        "timestamp": time()
                        })
    elif text[:11] == "/copypaster":
        messages.append({
                        "username": "Бот Копи Пастор",
                        "text": text[12:],
                        "timestamp": time()
                        })
    elif text == "/help" or text == "/h":
        messages.append({
                        "username": "БотЪ ЕгорЪ",
                        "text": "/h или /help - вызов этого текста\
                            \n/status - посмотреть статус сервера\
                            \n/copypaster - вызов Пастора Копи\
                            (После команды нужно ввести любой текст иначе \
                                Пастор промолчит)\
                            \n/chname - поменять имя в Этом сообщении\
                            \n/goodbaa - Сюрприз!)))",
                        "timestamp": time()
                        })
    elif text == "/":
        messages.append({
                        "username": "БотЪ ЕгорЪ",
                        "text": "Введи /help для просмотра команд",
                        "timestamp": time()})
    elif text == "/goodbaa":
        messages.append({
                        "username": "БотЪ ЕгорЪ",
                        "text": "Создатель просил передать что скоро выйдет \
                            Pocegram на Windows",
                        "timestamp": time()
                        })
    return {"ok": "true"}


@app.route("/get_messages")
def get_messages():
    after = float(request.args["after"])
    result = []
    for message in messages:
        if message["timestamp"] > after:
            result.append(message)
    return{
        "messages": result
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
