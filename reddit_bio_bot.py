
import os
import json
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

# === API KEYS FROM ENV ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === CONFIG ===
TAG_CHARS = ['\U000E0308', '\U000E0309', '\U000E030A', '\U000E030B', '\U000E030C', '\U000E030D', '\U000E030E', '\U000E030F']
CTA_OPTIONS = ["TG", "Tele", "Telegram", "Tgram", "Tgm", "telgrm", "tgrm"]
HANDLE_FILE = "handles.json"

client = OpenAI(api_key=OPENAI_API_KEY)

def obfuscate(text, num_tags=1):
    result = ''
    for char in text:
        shuffled = ''.join(random.sample(TAG_CHARS, num_tags))
        result += char + shuffled
    return result

def get_telegram_handle(model_name):
    if not os.path.exists(HANDLE_FILE):
        return None
    with open(HANDLE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(model_name.strip().lower())

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /generate <ModelName> <City>")
        return

    model = context.args[0]
    city = " ".join(context.args[1:])
    handle = get_telegram_handle(model)

    if not handle:
        await update.message.reply_text(f"❌ No Telegram handle found for model: {model}")
        return

    cta = random.choice(CTA_OPTIONS)
    obfuscated_handle = obfuscate(handle)

    prompt = (
        f"You are an AI that writes long-form Tinder bios designed to drive traffic to the middle of the profile, "
        f"where the Telegram prompt is placed.\n\n"
        f"The model you’re writing for is: {model}, a flirtatious and friendly girl from {city}.\n"
        f"Your goal is to generate a bio that:\n"
        f"- Sounds like a real girl texting her thoughts\n"
        f"- Is between 425–475 characters\n"
        f"- Uses lowercase and emotional hooks\n"
        f"- Guides the reader toward the Telegram handle\n"
        f"- Ends with something like: {cta};{obfuscated_handle}\n\n"
        f"Important: Do not mention OnlyFans. Write casually with human imperfections.\n\n"
        f"Now write the bio:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=300
        )
        bio = response.choices[0].message.content.strip()
        await update.message.reply_text(bio)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating bio: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("generate", generate))
    print("✅ Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
