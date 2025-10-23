import asyncio
import websockets
from datetime import datetime
import random
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8080))

clients = {}

async def broadcast(message, sender_websocket=None):
    disconnected_clients = []
    for ws in clients:
        if ws != sender_websocket:
            try:
                await ws.send(message)
            except:
                disconnected_clients.append(ws)
    for ws in disconnected_clients:
        if ws in clients:
            del clients[ws]

async def handle_client(websocket):
    name = "Anonymous"
    try:
        await websocket.send("Enter your name: ")
        name = (await websocket.recv()).strip()
        
        clients[websocket] = name
        join_message = f"{datetime.now().strftime('%H:%M')} {name} has joined the chat."
        print(f"Client {name} joined. Total: {len(clients)}")
        await broadcast(join_message, websocket)
        
        async for message in websocket:
            message = message.strip()
            if not message:
                continue
            if message.lower() == "exit()":
                break
                
            full_message = f"{datetime.now().strftime('%H:%M')} {name}: {message}"
            print(f"{datetime.now().strftime('%H:%M')} {name}: {message}")
            await broadcast(full_message, websocket)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if websocket in clients:
            name = clients[websocket]
            leave_message = f"{datetime.now().strftime('%H:%M')} {name} has left the chat."
            await broadcast(leave_message, websocket)
            del clients[websocket]

async def main():
    print(f"🚀 Starting server on {HOST}:{PORT}")
    async with websockets.serve(handle_client, HOST, PORT):
        print("✅ WebSocket server is running!")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
