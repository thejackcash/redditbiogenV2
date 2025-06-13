import os
import random
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load model-to-handle mapping
with open("telegram.json", "r") as f:
    model_handles = json.load(f)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

CTA_OPTIONS = [
    "tele 👉", "tg:", "telegram:", "teleme:", "telegrm:", "tele.", "teleg:", "tele📥:"
]

def obfuscate(handle):
    return ''.join(random.choice((c.upper(), c.lower())) for c in handle)

async def generate_bio(model: str, city: str) -> str:
    handle = model_handles.get(model.lower())
    if not handle:
        return "❌ Model not found in telegram.json."

    cta = random.choice(CTA_OPTIONS)
    obfuscated_handle = obfuscate(handle)

    prompt = (
        f"You are an AI that writes long-form Tinder bios designed to drive traffic to the middle of the profile,\n"
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
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error from OpenAI: {str(e)}"

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /generate <model> <city>")
        return

    model = args[0]
    city = ' '.join(args[1:])
    await update.message.reply_text("⏳ Generating...")

    bio = await generate_bio(model, city)
    await update.message.reply_text(bio)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("generate", generate))
    print("✅ Bot is running...")
    app.run_polling()
