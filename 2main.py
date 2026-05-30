import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

API_KEYS = [
os.getenv("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"),
os.getenv("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")
]

MODEL = "openai/gpt-4o-mini"

chat_history = []

def ask_ai(message):
messages = [
{
"role": "system",
"content": "You are Jarvis, a helpful AI assistant. Answer clearly and naturally."
}
]

messages.extend(chat_history)

messages.append({
    "role": "user",
    "content": message
})

for api_key in API_KEYS:
    if not api_key:
        continue

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages
            },
            timeout=30
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]

            chat_history.append({
                "role": "user",
                "content": message
            })

            chat_history.append({
                "role": "assistant",
                "content": reply
            })

            if len(chat_history) > 20:
                del chat_history[:2]

            return reply

    except Exception:
        pass

return "All API keys failed."

@app.get("/", response_class=HTMLResponse)
def home():
return """

<!DOCTYPE html><html>
<head>
<title>Jarvis AI</title><style>
body{
background:#1e1e1e;
color:white;
font-family:Arial,sans-serif;
max-width:900px;
margin:auto;
padding:20px;
}

#chat{
height:500px;
overflow-y:auto;
background:#252525;
padding:10px;
border-radius:10px;
margin-bottom:15px;
}

.user{
background:#0b57d0;
padding:10px;
border-radius:10px;
margin:10px;
text-align:right;
}

.ai{
background:#333;
padding:10px;
border-radius:10px;
margin:10px;
}

input{
width:75%;
padding:12px;
background:#333;
color:white;
border:none;
border-radius:8px;
}

button{
padding:12px;
border:none;
border-radius:8px;
cursor:pointer;
}
</style></head><body><h1>Jarvis AI</h1><div id="chat"></div><input id="msg" placeholder="Type a message...">
<button onclick="send()">Send</button><script>
async function send(){

let msg=document.getElementById("msg").value;

if(!msg) return;

document.getElementById("chat").innerHTML +=
'<div class="user">'+msg+'</div>';

document.getElementById("msg").value='';

let response = await fetch(
'/chat?msg=' + encodeURIComponent(msg)
);

let data = await response.json();

document.getElementById("chat").innerHTML +=
'<div class="ai">'+data.reply+'</div>';

document.getElementById("chat").scrollTop =
document.getElementById("chat").scrollHeight;
}

document.getElementById("msg").addEventListener(
"keypress",
function(event){
if(event.key==="Enter"){
send();
}
});
</script></body>
</html>
"""@app.get("/chat")
def chat(msg: str):
return {"reply": ask_ai(msg)}