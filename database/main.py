import sqlite3


conn = sqlite3.connect('database/database.db',
                       check_same_thread=False)
cursor = conn.cursor()


def save_userdata(username, password) -> None:
    userdata = [username, password]
    cursor.execute("INSERT INTO Userdata VALUES(?,?)", userdata)
    conn.commit()


def get_userdata(username) -> None:
    cursor.execute('SELECT password FROM Userdata WHERE username=?',[username])
    password = cursor.fetchone()
    if password is None:
        return password[0]
    else:
        return None


def save_message(message) -> None:
    data = [message["username"],
            message["text"],
            message["timestamp"]]
    cursor.execute("INSERT INTO messages VALUES(?,?,?)", data)
    conn.commit()


def get_messages() -> list:
    messages = []
    for data in cursor.execute('SELECT * FROM messages'):
        messages.append({
                    "mode": "message",
                    "username": data[0],
                    "text": data[1],
                    "timestamp": data[2]
                        })
    return messages
