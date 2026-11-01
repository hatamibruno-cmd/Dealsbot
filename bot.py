import os
import re
import html
import time
import feedparser
import requests

# Récupération des secrets GitHub
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

# Flux RSS des sites de deals internationaux
FEEDS = [
    {"url": "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&rss=1", "site": "Slickdeals 🇺🇸", "lang": "US"},
    {"url": "https://www.dealabs.com/rss/hot", "site": "Dealabs 🇫🇷", "lang": "FR"}
]

def strip_html(text):
    """Nettoie les balises HTML pour éviter que Telegram ne rejette le message"""
    if not text:
        return ""
    # Supprime les balises HTML
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Décode les entités HTML (comme &amp; ou &#39;)
    return html.unescape(text).strip()

def fetch_real_deals():
    real_deals = []
    
    for feed_info in FEEDS:
        try:
            print(f"Lecture du flux : {feed_info['site']}...")
            feed = feedparser.parse(feed_info["url"])
            
            for entry in feed.entries:
                title = strip_html(entry.get('title', 'Offre spéciale'))
                link = entry.get('link', '')
                summary = strip_html(entry.get('summary', entry.get('description', '')))
                
                if not link:
                    continue
                
                # Création du titre bilingue
                if feed_info["lang"] == "US":
                    title_fr = f"🔥 Deal US : {title}"
                    title_en = title
                else:
                    title_fr = title
                    title_en = f"🔥 Deal FR : {title}"
                
                # Raccourcir la description si elle est trop longue
                short_summary = summary[:200] + "..." if len(summary) > 200 else summary
                
                real_deals.append({
                    "site": feed_info["site"],
                    "title_fr": title_fr,
                    "title_en": title_en,
                    "summary": short_summary,
                    "link": link
                })
        except Exception as e:
            print(f"Erreur avec {feed_info['site']} : {e}")

    # Déduplication par lien (pour éviter d'envoyer 2 fois la même offre)
    seen_links = set()
    unique_deals = []
    for deal in real_deals:
        if deal["link"] not in seen_links:
            seen_links.add(deal["link"])
            unique_deals.append(deal)

    # On garde uniquement les 8 premières offres
    return unique_deals[:8]

def send_to_telegram(deals):
    if not deals:
        print("Aucun deal trouvé pour le moment.")
        return

    print(f"--- Envoi de {len(deals)} offres réelles ---")
    
    for index, deal in enumerate(deals, 1):
        message = (
            f"🛒 <b>{deal['site']}</b> ({index}/{len(deals)})\n\n"
            f"🇫🇷 <b>{deal['title_fr']}</b>\n"
            f"🇬🇧 <i>{deal['title_en']}</i>\n\n"
            f"📝 {deal['summary']}\n\n"
            f"👉 <a href='{deal['link']}'>Voir l'offre / See deal</a>"
        )

        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
        )

        if response.status_code == 200:
            print(f"✅ Envoyé : {deal['title_fr'][:40]}...")
        else:
            print(f"❌ Erreur Telegram : {response.text}")

        # Pause de 2 secondes OBLIGATOIRE pour éviter le bannissement par Telegram
        time.sleep(2)

if __name__ == "__main__":
    print("Démarrage du bot...")
    live_deals = fetch_real_deals()
    send_to_telegram(live_deals)
    print("Fin du processus.")
