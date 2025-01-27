import websocket

def on_message(ws, message):
    print("Message received:", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connected to server")
    ws.send("Hello, server!")

ws = websocket.WebSocketApp(
    "ws://192.168.29.126:8000",  # Replace with your WebSocket server's address
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.on_open = on_open
ws.run_forever()