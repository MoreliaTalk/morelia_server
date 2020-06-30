import uvicorn
from fastapi import FastAPI, Request, WebSocket
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
from time import time

app = FastAPI()

list_userdata = {
					"Jack":"123"
				}
# Сохраняем список сообщенией,
# TODO: Сохраняем в базу данных
list_message = []
# Сохраняем сессии клиентов
# TODO:   При отключении нужно реализовать их удаление  подумать как их хранить
clients = []


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
		return "newreg"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()

	clients.append(websocket)
	client=websocket
	await get_all_messages(websocket)
	try:
		while True:
			data = await websocket.receive_json()
			if data["mode"] == "message":
				message = {
						"mode": "message",
						"username":data["username"],
						"text":data["text"],
						"timestamp":time()
						}
				save_message(message)
				print(message)
				await send_message(message)
			elif data["mode"] == "reg":
				message = {
						"mode": "reg",
						"status":await reg_user(data)
						}
				await client.send_json(message)

	except WebSocketDisconnect as e:
		clients.remove(websocket)
		print(e)


if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000)
