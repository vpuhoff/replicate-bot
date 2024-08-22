import os
from random import randint
import replicate
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO

# Замените на свой токен Telegram бота
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправь мне текст, и я сгенерирую изображение на его основе.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    
    # Отправляем сообщение о начале генерации
    await update.message.reply_text('Генерирую изображение, пожалуйста, подождите...')
    
    # Настройка параметров для Replicate API
    input_data = {
        "prompt": text,
        "seed": randint(0, 99999999),  # Можно сделать случайным или настраиваемым
        "steps": 50,
        "guidance": 3,
        "interval": 2,
        "aspect_ratio": "1:1",  # Можно сделать настраиваемым
        "safety_tolerance": 2
    }
    
    try:
        #test = replicate.models.get("black-forest-labs/flux-pro")
        # Запуск модели Replicate
        output = replicate.run(
            #"black-forest-labs/FLUX.1-schnell",
            "black-forest-labs/flux-pro:caf8d6bf110808c53bb90767ea81e1bbd0f0690ba37a4a24b27b17e2f9a5c011",
            # stability-ai/stable-diffusion-3
            # "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input=input_data 
        )
        print(output)
        
        # Получение URL изображения из вывода
        image_url = output  # Предполагаем, что первый элемент вывода - это URL изображения
        
        # Асинхронная загрузка изображения
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    # Отправка изображения пользователю
                    await update.message.reply_photo(photo=BytesIO(image_data))
                else:
                    await update.message.reply_text(f'Ошибка при загрузке изображения: HTTP статус {response.status}')
    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка при генерации или загрузке изображения: {str(e)}')

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()