import json
import base64
import requests
from pathlib import Path

API = "https://discord.com/api/v10"

PATHS_TO_TRY = [
    Path.cwd() / "database" / "emojis.json",
    Path(__file__).resolve().parents[2] / "database" / "emojis.json",
]

ALL_EMOJIS = []

for path in PATHS_TO_TRY:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            ALL_EMOJIS = json.load(f)
        break

EMOJI_IDS_PATH = Path("database/emojis_ids.json")
EMOJI_IDS_PATH.parent.mkdir(exist_ok=True)

def headers(token):
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

def fetch_emojis(app_id, token):
    r = requests.get(
        f"{API}/applications/{app_id}/emojis",
        headers=headers(token)
    )
    return r.json().get("items", [])

def download_image(url):
    r = requests.get(url)
    mime = r.headers.get("Content-Type", "image/png")
    b64 = base64.b64encode(r.content).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def save_emoji_id(name, emoji_id, animated):
    data = {}
    if EMOJI_IDS_PATH.exists():
        data = json.load(open(EMOJI_IDS_PATH))

    data[name] = {
        "id": emoji_id,
        "animated": animated,
        "full": f"<{'a' if animated else ''}:{name}:{emoji_id}>"
    }

    json.dump(data, open(EMOJI_IDS_PATH, "w"), indent=2)

def clear_emoji_ids():
    json.dump({}, open(EMOJI_IDS_PATH, "w"), indent=2)

def create_emoji(app_id, token, name, image_url):
    image = download_image(image_url)

    r = requests.post(
        f"{API}/applications/{app_id}/emojis",
        headers=headers(token),
        json={"name": name, "image": image}
    )

    if r.status_code == 201:
        data = r.json()
        save_emoji_id(name, data["id"], data["animated"])

def delete_emoji(app_id, token, emoji_id):
    requests.delete(
        f"{API}/applications/{app_id}/emojis/{emoji_id}",
        headers=headers(token)
    )

def emojis_different(existing, new):
    return {e["name"] for e in existing} != {e["name"] for e in new}

def upload_emojis(bot):
    token = bot.http.token
    app_id = bot.application_id

    try:
        existing = fetch_emojis(app_id, token)
    except:
        return None

    replace = emojis_different(existing, ALL_EMOJIS)

    if replace:
        clear_emoji_ids()
        for e in existing:
            delete_emoji(app_id, token, e["id"])

    success = 0
    failed = 0

    for emoji in ALL_EMOJIS:
        if not replace and any(e["name"] == emoji["name"] for e in existing):
            continue
        
        try:
            create_emoji(app_id, token, emoji["name"], emoji["image"])
            success += 1
        except:
            failed += 1

    return {
        "total": len(ALL_EMOJIS),
        "success": success,
        "failed": failed,
        "finalCount": success
    }