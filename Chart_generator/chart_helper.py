from Chart_generator.chart_generator import CustomCandlestick, scale_ohlc_data
from Chart_generator.ohlc_sitcom import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def generate_buttons():
    # 1. Define the button structure
    button_list = [
    [
        InlineKeyboardButton("🔗 Website", url="https://degenerative-sitcom.online/"),
        InlineKeyboardButton("🛒 Buy", url="https://raydium.io/swap/?inputMint=sol&outputMint=AK9yVoXKK1Cjww7HDyjYNyW5FujD3FJ2xbjMUStspump")
    ]
    # You can add more rows of buttons here if needed
    # [InlineKeyboardButton("Another Row Button", callback_data="another_action")]
    ]
    # This creates a single row with one button that links to Google.
    # 2. Create the markup object
    reply_markup = InlineKeyboardMarkup(button_list)
    return reply_markup

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /chart command, generates, and sends the chart."""

    CG_KEY = context.bot_data.get("CG_KEY")
    TELEGRAM_BOT_TOKEN = context.bot_data.get("TELEGRAM_BOT_TOKEN")

    chat_id = update.effective_chat.id
    print(chat_id)
    coin_id = 'degenerative-sitcom'
    # await context.bot.send_message(chat_id=chat_id, text="Generating chart... 📊")

    try:
        # 1. GET DATA (Using the imported mock data function)
        original_data = get_ohlc(coin_id,cg_key=CG_KEY)

        volume_mcap_data = get_coin_data(coin_id,cg_key=CG_KEY)

        scale_factor = 1_000_000_000
        scaled_data = scale_ohlc_data(original_data, scale_factor)

        # 2. CREATE AND PLOT CHART using the imported class
        chart = CustomCandlestick(scaled_data, graphic='triangle', width=0.4)
        chart.plot(
            title="",
            xlabel="Time",
            ylabel="Mcap"
        )

        # 3. SAVE CHART TO MEMORY BUFFER
        photo_buffer = chart.get_image_buffer()

        # 4. SEND CHART
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_buffer,
            caption = volume_mcap_data,
            parse_mode = 'HTML',
            reply_markup=generate_buttons()
        )

    except Exception as e:
        print(f"Error generating or sending chart: {e}")

