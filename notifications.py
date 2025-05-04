from fastapi import WebSocket


async def send_notification(client: WebSocket, text: str):
    await client.send_text(text)
