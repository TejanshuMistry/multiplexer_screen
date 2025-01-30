import asyncio
import websockets
import json

connected_clients = set()

async def handle_client(websocket):
    print(f"New connection from {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message} from {websocket.remote_address}")
            # Echo the message back to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(str(message))
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected.")
    finally:
        connected_clients.remove(websocket)

async def main():
    print("WebSocket server is running on ws://localhost:8765")
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())