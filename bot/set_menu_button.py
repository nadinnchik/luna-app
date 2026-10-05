#!/usr/bin/env python3
"""
Sets the Telegram WebApp Menu Button for @Luna_Astrologer_Bot
Points directly to https://nadinnchik.github.io/luna-app/
"""

import os
import sys
import json
import socket
import urllib.request
import urllib.error

# Force IPv4 to prevent IPv6 hangs on macOS
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_v4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_v4

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7968512345:AAExampleTokenPlaceholderForLocalDev")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nadinnchik.github.io/luna-app/")


def set_menu_button(bot_token: str, webapp_url: str):
    url = f"https://api.telegram.org/bot{bot_token}/setChatMenuButton"
    payload = {
        "menu_button": {
            "type": "web_app",
            "text": "🌙 Открыть LUNA",
            "web_app": {
                "url": webapp_url
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                print("✅ Telegram Menu Button successfully configured!")
                print(f"🔗 Target WebApp URL: {webapp_url}")
            else:
                print(f"⚠️ Telegram API response: {data}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]
    
    if "Placeholder" in BOT_TOKEN:
        print("ℹ️ Provide your bot token via environment variable or argument:")
        print("   python3 set_menu_button.py <YOUR_BOT_TOKEN>")
        sys.exit(1)
        
    set_menu_button(BOT_TOKEN, WEBAPP_URL)
