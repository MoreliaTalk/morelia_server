from time import time
from datetime import datetime

from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket

from fastapi.staticfiles import StaticFiles

from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

import uvicorn

app = FastAPI(debug=True)

# Указываем место хранения шаблонов
templates = Jinja2Templates(directory='templates')

# Указывавем место хранения статичных файлов которые исп. в шаблонах
app.mount('/static', StaticFiles(directory='static'), name='static')


list_userdata = {
                    "Jack": "123"
                }
# Сохраняем список сообщенией,
# TODO: Сохраняем в базу данных
list_message = []
# Сохраняем сессии клиентов
# TODO:   При отключении нужно реализовать их удаление  подумать как их хранить
clients = []


@app.get('/')
async def home_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/status')
async def server_status(request: Request):
    return templates.TemplateResponse('status.html', {
                                            'request': request,
                                            'status': 'Ok',
                                            'time': datetime.now().strftime('%Y-%m-%d: %H:%M:%S'),
                                            'messages': len(list_message),
                                            'users': len(clients)})


# сохраняем сообщение в базу
def save_message(mes):
    list_message.append(mes)


# Отправляем все сообщения чата
async def get_all_messages(newclient):
    for message in list_message:
        await newclient.send_json(message)


# Посылаем сообщение всем клиентам
async def send_message(mes):
    for client in clients:
        await client.send_json(mes)


# TODO: надо релизовать регистрацию
async def reg_user(data):
    if data["username"] in list_userdata:
        if data["password"] == list_userdata[data["username"]]:
            return "true"
        else:
            return "false"
    else:
        list_userdata[data["username"]] = data["password"]
        return "true"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    clients.append(websocket)

    await get_all_messages(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "username": data["username"],
                "text": data["text"],
                "timestamp": time()
            }
            save_message(message)
            print(message)
            await send_message(message)

    except WebSocketDisconnect as e:
        clients.remove(websocket)
        print(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
