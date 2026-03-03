from flask import Flask, render_template_string, request, jsonify
import socket
import threading
import json

app = Flask(__name__)

# --- Professional Milky UI with Glassmorphism & SVG ---
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bit Chat - Guest</title>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            --glass-bg: rgba(255, 255, 255, 0.65);
            --glass-border: rgba(255, 255, 255, 0.6);
            --accent: #ec4899;
            --text-main: #1f2937;
            --text-muted: #6b7280;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-image: var(--bg-gradient); height: 100vh; display: flex; justify-content: center; align-items: center; color: var(--text-main); }
        
        .chat-container {
            width: 100%; max-width: 420px; height: 80vh; 
            background: var(--glass-bg);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 24px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            display: flex; flex-direction: column; overflow: hidden;
        }

        /* Header */
        .chat-header {
            padding: 20px; display: flex; align-items: center; 
            border-bottom: 1px solid rgba(255,255,255,0.5);
            background: rgba(255,255,255,0.4);
        }
        .logo { width: 45px; height: 45px; margin-right: 15px; }
        .user-info h2 { font-size: 18px; font-weight: 700; color: var(--text-main); }
        .status { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; transition: background 0.3s; }
        .status-dot.active { background: #10b981; box-shadow: 0 0 8px #10b981; }

        /* Chat Box */
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }

        /* Messages */
        .message-row { display: flex; flex-direction: column; max-width: 80%; }
        .message-row.sent { align-self: flex-end; align-items: flex-end; }
        .message-row.received { align-self: flex-start; align-items: flex-start; }

        .bubble {
            padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.5;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            backdrop-filter: blur(4px);
        }
        .message-row.sent .bubble { background: rgba(236, 72, 153, 0.2); color: #9d174d; border: 1px solid rgba(236, 72, 153, 0.3); }
        .message-row.received .bubble { background: rgba(255, 255, 255, 0.8); color: var(--text-main); border: 1px solid rgba(255,255,255,0.8); }
        
        .timestamp { font-size: 9px; color: var(--text-muted); margin-top: 5px; text-align: right; }

        /* Image & File Styling */
        .bubble img { max-width: 100%; max-height: 180px; border-radius: 10px; margin-bottom: 5px; }
        .file-bubble { display: flex; align-items: center; gap: 12px; text-decoration: none; color: inherit; }
        .file-icon { width: 40px; height: 40px; background: rgba(255,255,255,0.6); border-radius: 10px; display: flex; align-items: center; justify-content: center; }
        .file-info { flex: 1; }
        .file-name { font-weight: 600; font-size: 13px; }
        .file-size { font-size: 10px; color: var(--text-muted); }

        /* Input Area */
        .input-area {
            padding: 15px 20px; background: rgba(255,255,255,0.4); 
            border-top: 1px solid rgba(255,255,255,0.5);
            display: flex; align-items: center; gap: 10px;
        }
        .icon-btn {
            background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.8);
            width: 40px; height: 40px; border-radius: 12px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; color: var(--text-muted); transition: all 0.2s;
        }
        .icon-btn:hover { background: white; color: var(--accent); transform: translateY(-1px); }
        
        .message-input {
            flex: 1; padding: 12px 18px; border-radius: 16px; border: none;
            background: white; outline: none; font-size: 14px; color: var(--text-main);
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }
        .send-btn {
            width: 42px; height: 42px; border-radius: 14px; border: none;
            background: var(--accent); color: white; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3); transition: transform 0.1s;
        }
        .send-btn:active { transform: scale(0.95); }
        
        .system-msg { align-self: center; font-size: 11px; color: var(--text-muted); background: rgba(0,0,0,0.05); padding: 5px 12px; border-radius: 10px; margin: 10px 0; }
        
        #file-input, #image-input { display: none; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <!-- SVG Logo: Modern Chat Icon -->
        <svg class="logo" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" fill="#ec4899" fill-opacity="0.2" stroke="#ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="8" cy="11" r="1" fill="#ec4899"/>
            <circle cx="12" cy="11" r="1" fill="#ec4899"/>
            <circle cx="16" cy="11" r="1" fill="#ec4899"/>
        </svg>
        <div class="user-info">
            <h2>Guest</h2>
            <div class="status">
                <span class="status-dot" id="status-dot"></span>
                <span id="status-text">Offline</span>
            </div>
        </div>
    </div>

    <div class="chat-box" id="chat-box"></div>

    <div class="input-area">
        <button class="icon-btn" onclick="document.getElementById('image-input').click()">🖼️</button>
        <button class="icon-btn" onclick="document.getElementById('file-input').click()">📎</button>
        <input type="file" id="image-input" accept="image/*" onchange="handleFileSelect(this, 'image')">
        <input type="file" id="file-input" onchange="handleFileSelect(this, 'file')">
        <input type="text" id="msg-input" class="message-input" placeholder="Type a message..." disabled>
        <button class="send-btn" id="send-btn" onclick="sendMessage()" disabled>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const msgInput = document.getElementById('msg-input');
    const sendBtn = document.getElementById('send-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    let connected = false;

    function formatBytes(bytes, decimals = 2) {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
    }

    function setConnected(isConnected) {
        connected = isConnected;
        msgInput.disabled = !isConnected;
        sendBtn.disabled = !isConnected;
        if (isConnected) {
            statusDot.classList.add('active');
            statusText.innerText = "Online";
            chatBox.innerHTML = ''; // Clear old status
        } else {
            statusDot.classList.remove('active');
            statusText.innerText = "Offline";
        }
    }

    function addMessage(data) {
        if (data.type !== 'system') {
            const sysMsgs = document.querySelectorAll('.system-msg');
            sysMsgs.forEach(el => el.remove());
        }

        const row = document.createElement('div');
        row.className = `message-row ${data.type}`; 
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        let bubbleContent = '';

        if (data.type === 'system') {
            row.className = 'system-msg';
            row.innerText = data.text;
            chatBox.appendChild(row);
            chatBox.scrollTop = chatBox.scrollHeight;
            return;
        }

        if (data.fileType === 'image') {
            bubbleContent = `<img src="data:image/jpeg;base64,${data.fileData}" onclick="window.open(this.src)"><span class="timestamp">${time}</span>`;
        } else if (data.fileType === 'file') {
            const dlLink = `data:application/octet-stream;base64,${data.fileData}`;
            bubbleContent = `<a href="${dlLink}" download="${data.fileName}" class="file-bubble">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">${data.fileName}</div>
                    <div class="file-size">${formatBytes(data.fileSize)}</div>
                </div>
            </a><span class="timestamp">${time}</span>`;
        } else {
            bubbleContent = `${data.text} <span class="timestamp">${time}</span>`;
        }

        row.innerHTML = `<div class="bubble">${bubbleContent}</div>`;
        chatBox.appendChild(row);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Initial Status Check
    fetch('/get_status').then(r => r.json()).then(data => {
        if(data.connected) setConnected(true);
        else addMessage({type: 'system', text: 'Connecting to Host...'});
    });

    // Polling
    setInterval(() => {
        fetch('/get_status').then(r => r.json()).then(data => {
            if(data.connected && !connected) setConnected(true);
        });
        
        if(!connected) return;
        fetch('/get_messages').then(r => r.json()).then(data => {
            if(data.messages) {
                data.messages.forEach(msg => {
                    msg.type = 'received'; 
                    addMessage(msg);
                });
            }
        });
    }, 1000);

    function sendMessage() {
        const text = msgInput.value;
        if(!text) return;
        fetch('/send_message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: 'text', text: text})
        }).then(r => r.json()).then(res => {
            if(res.status === 'success') {
                addMessage({type: 'sent', text: text});
                msgInput.value = '';
            }
        });
    }

    function handleFileSelect(input, fileType) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64 = e.target.result.split(',')[1];
                const payload = { fileType: fileType, fileName: file.name, fileSize: file.size, fileData: base64 };
                fetch('/send_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                }).then(r => r.json()).then(res => {
                    if(res.status === 'success') addMessage({type: 'sent', ...payload});
                });
            };
            reader.readAsDataURL(file);
        }
        input.value = '';
    }

    msgInput.addEventListener("keypress", function(event) { if (event.key === "Enter") sendMessage(); });
</script>
</body>
</html>
"""

# --- Python Backend ---
state = {'sock': None, 'connected': False, 'messages': []}

def listen():
    while True:
        try:
            data = state['sock'].recv(10485760)
            if not data: break
            state['messages'].append(data.decode('utf-8'))
        except: break
    state['connected'] = False

def run_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 12345))
        state['sock'] = s
        state['connected'] = True
        threading.Thread(target=listen, daemon=True).start()
        print("[GUEST] Connected.")
    except Exception as e:
        print(f"[GUEST] Connection failed: {e}")

@app.route('/')
def index():
    if not state['connected']:
        threading.Thread(target=run_client, daemon=True).start()
    return render_template_string(HTML)

@app.route('/get_status')
def get_status():
    return jsonify({'connected': state['connected']})

@app.route('/get_messages')
def get_messages():
    out = []
    for m in state['messages']:
        try: out.append(json.loads(m))
        except: pass
    state['messages'] = []
    return jsonify({'messages': out})

@app.route('/send_message', methods=['POST'])
def send_message():
    if not state['connected']: return jsonify({'status': 'error'})
    try:
        data = request.json
        state['sock'].send(json.dumps(data).encode('utf-8'))
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    print("[GUEST] Running on http://127.0.0.1:5001")
    app.run(port=5001, debug=False)