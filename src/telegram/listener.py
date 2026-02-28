import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from datetime import datetime, timedelta

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient("trading_session", api_id, api_hash)
TARGET_CHATS = [2343296096]
trade_state = {
    "active_trades": {},
    "pending_orders": {},
    "allocated_margin_today": 0,
    "last_reset": datetime.utcnow()
}

MAX_DAILY_MARGIN = 15
MARGIN_PER_TRADE = 1

@client.on(events.NewMessage(chats=TARGET_CHATS))
async def handler(event):
    chat = await event.get_chat()
    print("\n--- NEW MESSAGE ---")
    print("TITLE:", getattr(chat, "title", None))
    print("USERNAME:", getattr(chat, "username", None))
    print("CHAT_ID:", getattr(chat, "id", None))
    print("TEXT:", event.text)

    parsed = parse_group1_signal(event.text)

    if not parsed:
        return

    symbol = parsed["symbol"]

    # Reset daily allocation if 24h passed
    if datetime.utcnow() - trade_state["last_reset"] > timedelta(hours=24):
        trade_state["allocated_margin_today"] = 0
        trade_state["last_reset"] = datetime.utcnow()

    # Check if symbol already active
    if symbol in trade_state["active_trades"]:
        print(f"❌ Trade already active for {symbol}")
        return

    # Check daily margin cap
    if trade_state["allocated_margin_today"] + MARGIN_PER_TRADE > MAX_DAILY_MARGIN:
        print("❌ Daily margin cap reached.")
        return

    print("\n✅ VALID SIGNAL DETECTED")
    print(parsed)

    simulate_trade_execution(parsed)
def parse_group1_signal(text):
    if "Entry price" not in text or "Targets(USDT)" not in text:
        return None  # Not a valid signal

    lines = text.splitlines()

    direction = None
    symbol = None
    leverage = None
    entry_price = None
    targets = []

    for line in lines:
        line = line.strip()

        # Direction
        if "Short" in line:
            direction = "SHORT"
        elif "Long" in line:
            direction = "LONG"

        # Symbol
        if line.startswith("Name:"):
            symbol = line.replace("Name:", "").strip()

        # Leverage
        if "Margin mode:" in line:
            if "(" in line and "X" in line:
                leverage = line.split("(")[-1].replace(")", "").replace("X", "").strip()

        # Entry
        if line.replace(".", "", 1).isdigit():
            if entry_price is None:
                entry_price = float(line)

        # Targets
        if ")" in line and any(char.isdigit() for char in line):
            try:
                price_part = line.split(")")[-1].strip()
                if price_part.lower() != "🔝 unlimited":
                    targets.append(float(price_part))
            except:
                pass

    # Limit to first 4 targets
    targets = targets[:4]

    if direction and symbol and entry_price and targets:
        return {
            "direction": direction,
            "symbol": symbol,
            "entry_price": entry_price,
            "leverage": leverage,
            "targets": targets
        }

    return None

def simulate_trade_execution(parsed):
    symbol = parsed["symbol"]
    direction = parsed["direction"]
    entry_price = parsed["entry_price"]
    targets = parsed["targets"]

    leverage = 10
    margin = MARGIN_PER_TRADE

    if direction == "LONG":
        stop_loss = round(entry_price * 0.96, 6)
    else:
        stop_loss = round(entry_price * 1.04, 6)

    print("\nSIMULATED TRADE EXECUTION")
    print(f"Symbol: {symbol}")
    print(f"Direction: {direction}")
    print(f"Entry: {entry_price}")
    print(f"Leverage: {leverage}x")
    print(f"Margin: {margin} USDT")
    print(f"Stop Loss: {stop_loss}")
    print(f"Take Profits: {targets[:4]}")

    trade_state["allocated_margin_today"] += margin

    trade_state["pending_orders"][symbol] = {
        "direction": direction,
        "entry": entry_price,
        "stop_loss": stop_loss,
        "targets": targets[:4],
        "margin": margin
    }
    
    print(f"\nAllocated Today: {trade_state['allocated_margin_today']} / {MAX_DAILY_MARGIN} USDT")
async def main():
    print("Listening... send any message in your VIP group/channel now.")
    phone = os.getenv("PHONE")
    await client.start(phone=phone)
    await client.run_until_disconnected()
if __name__ == "__main__":
    asyncio.run(main())