var ws = new WebSocket("ws://localhost:8000/ws");
var viewtext = ""
ws.onmessage = function(event) {
    var message = JSON.parse(event.data)
    var datemessages = new Date(message["timestamp"]*1000)
    var dt = datemessages.getHours()+":"+datemessages.getMinutes()+":"+datemessages.getSeconds()
    viewtext = viewtext + "["+dt+" "+message["username"]+"]\n";
    viewtext = viewtext + message["text"]+"\n\n"
    document.getElementById("view").innerHTML=viewtext

};
function send_message() {
    var user={
        "username": document.getElementById('username').value,
        "text":document.getElementById('input').value
    }
    ws.send(JSON.stringify(user))
    document.getElementById('input').value=""
};