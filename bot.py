import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHANNEL_ID"]

message = (
    "🔥 **Écouteurs Bluetooth XYZ**\n\n"
    "💰 ~~89,99€~~ → **53,99€**\n"
    "📉 -40%\n"
    "⚡ Stock limité\n\n"
    "👉 [Voir le deal](https://ton-lien-affilie.com)"
)

requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
)
print("Deal publié !")
