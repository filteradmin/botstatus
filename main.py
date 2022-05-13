import os
import pytz
import asyncio
import logging
import subprocess
from time import sleep
from dotenv import load_dotenv
from datetime import datetime as dt
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors.rpcerrorlist import MessageNotModifiedError, FloodWaitError

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)

if os.path.exists("config.env"):
    os.remove("config.env")
subprocess.run(["wget", "-q", "-O", "config.env", os.environ["CONFIG"]])


async def S1BOTS():
  def getConfig(name: str):
      return os.environ[name]
  try:
      load_dotenv("config.env")
      bots = getConfig("BOTS").split()
      user_bot = TelegramClient(
            StringSession(getConfig("SESSION")),
            int(getConfig("APP_ID")),
            getConfig("API_HASH")
        )
  except Exception as e:
      print(f"[ERROR] {str(e)}")
  print("[INFO] Starting client...")
  async with user_bot:
    try:
        await user_bot.edit_message(
            int(getConfig("CHANNEL_ID")),
            int(getConfig("MESSAGE_ID")),
            "**Our Bot's 🤖 Status 📈 :**\n\n`Performing a periodic check...`",
        )
    except MessageNotModifiedError:
        pass
    c = 0
    edit_text = "**Our Bot's 🤖 Status 📈 :**\n(Updating Every 30 Minutes)\n\n"
    print("[INFO] Starting to check uptime...")
    for bot in bots:
        try:
            print(f"[INFO] checking @{bot}")
            snt = await user_bot.send_message(bot, "/start")
            await asyncio.sleep(10)
            history = await user_bot(
                    GetHistoryRequest(
                        peer=bot,
                        offset_id=0,
                        offset_date=None,
                        add_offset=0,
                        limit=1,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )
            msg = history.messages[0].id
            if snt.id == msg:
                print(f"[WARNING] @{bot} is down.")
                edit_text += f"🤖 **@{bot}** → ❌\n"
            elif snt.id + 1 == msg:
                edit_text += f"🤖 **@{bot}** → ✅\n"
            c += 1
            await user_bot.send_read_acknowledge(bot)
        except MessageNotModifiedError:
            pass
        except FloodWaitError as f:
            print(f"[WARNING] Floodwait, sleeping for {f.seconds}...")
            sleep(f.seconds + 10)

    tz = pytz.timezone("Asia/Dhaka")
    edit_text += f"\n**Last Checked ⏳ On** :"
    print(f"[INFO] Checks since last restart - {c}")
    edit_text += f"\n`{dt.now(tz).strftime('%d %B %Y')} - {dt.now(tz).strftime('%H:%M:%S')} [BST]`"
    await user_bot.edit_message(int(getConfig("CHANNEL_ID")), int(getConfig("MESSAGE_ID")), edit_text)
    os.system(f"kill -9 {os.getpid()} && python3 main.py")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(S1BOTS())
