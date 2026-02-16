import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient("trading_session", api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    chat = await event.get_chat()
    print("\n--- NEW MESSAGE ---")
    print("TITLE:", getattr(chat, "title", None))
    print("USERNAME:", getattr(chat, "username", None))
    print("CHAT_ID:", getattr(chat, "id", None))
    print("TEXT:", event.text)

async def main():
    print("Listening... send any message in your VIP group/channel now.")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())