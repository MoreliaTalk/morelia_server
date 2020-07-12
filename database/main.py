import sqlite3
conn = sqlite3.connect('database/database.db')
cursor = conn.cursor()
def save_userdata(username,password):
    userdata = [username,password]
    cursor.execute("INSERT INTO Userdata VALUES(?,?)", userdata)
    conn.commit()
def get_userdata(username):
    cursor.execute('SELECT password FROM Userdata WHERE username=?',[username])
    password = cursor.fetchone()
    if password != None:
        return password[0]
    else:
        return None
def save_message(mes):
    mesdata = [mes["username"],mes["text"],mes["timestamp"]]
    cursor.execute("INSERT INTO messages VALUES(?,?,?)", mesdata)
    conn.commit()
def get_messages():
    messages = []
    for data in cursor.execute('SELECT * FROM messages'):
        messages.append({
                        "mode": "message",
                        "username": data[0],
                        "text": data[1],
                        "timestamp": data[2]
                        })
    return messages
    