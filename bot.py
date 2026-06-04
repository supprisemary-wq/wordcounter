import os
import re
from collections import Counter
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Retrieve token from Render Environment
TOKEN = os.getenv("TOKEN", "YOUR_WORDCOUNTER_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a friendly welcome message on /start."""
    welcome_text = (
        "📊 **Welcome to the Text Analytics Bot!**\n\n"
        "Send me any text article, ad copy, or paragraph, and I will instantly analyze:\n"
        "🔹 Word & Character counts\n"
        "🔹 Sentences & Paragraphs\n"
        "🔹 Estimated Reading Time\n"
        "🔹 Top Keyword Density\n\n"
        "Ready when you are! Just paste your text below."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

def analyze_text(text: str) -> str:
    """Perform text analysis and return a formatted markdown string."""
    # Basic Counts
    char_count_with_spaces = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    
    # Extract words using regex
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    # Count Sentences (split by ., !, ?)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    if word_count > 0 and sentence_count == 0:
        sentence_count = 1  # Fallback for single line without punctuation
        
    # Count Paragraphs (split by double newlines or clean line breaks)
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Calculate Reading Time (Average reading speed: 200 words per minute)
    # Reading time in minutes = words / 200. Convert to seconds if under a minute.
    reading_time_minutes = word_count / 200
    if reading_time_minutes < 1:
        seconds = round(reading_time_minutes * 60)
        reading_time_str = f"{seconds} seconds"
    else:
        reading_time_str = f"{round(reading_time_minutes, 1)} minutes"
        
    # Calculate Keyword Density (Ignore common short stop-words under 3 letters)
    filtered_words = [w for w in words if len(w) > 3]
    word_counts = Counter(filtered_words)
    top_keywords = word_counts.most_common(5)
    
    density_str = ""
    if top_keywords and word_count > 0:
        for word, count in top_keywords:
            percentage = (count / word_count) * 100
            density_str += f"   • *{word}*: {count} times ({percentage:.1f}%)\n"
    else:
        density_str = "   • _Not enough text to analyze keywords._\n"

    # Format the final report response
    report = (
        "📈 **TEXT ANALYSIS REPORT**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **Words:** {word_count}\n"
        f"🔤 **Characters (with spaces):** {char_count_with_spaces}\n"
        f"🧱 **Characters (no spaces):** {char_count_no_spaces}\n"
        f"🎯 **Sentences:** {sentence_count}\n"
        f"📂 **Paragraphs:** {paragraph_count}\n"
        f"⏱️ **Est. Reading Time:** {reading_time_str}\n\n"
        f"🔑 **Top Keyword Density:**\n{density_str}"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    return report

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the user's incoming text message."""
    user_text = update.message.text
    
    # Send a quick processing notice for clean UX
    status_message = await update.message.reply_text("📊 Analyzing text statistics... please wait.")
    
    # Generate statistics report
    analysis_report = analyze_text(user_text)
    
    # Edit the placeholder message with the final numbers
    await status_message.edit_text(analysis_report, parse_mode="Markdown")

def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run polling
    print("✅ Word Counter Bot is successfully running...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
