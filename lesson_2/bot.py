from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import FSInputFile, Message
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from datetime import datetime
from aiogram.enums.dice_emoji import DiceEmoji
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config
from aiogram import F
from aiogram import html

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()


# Если не указать фильтр F.text,
# то хэндлер сработает даже на картинку с подписью /test

@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    await message.answer(
        "Hello, <b>world</b>!",
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        "Hello, *world*\!",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await message.answer("Сообщение с <u>HTML-разметкой</u>")
    await message.answer(
        "Сообщение без <s>какой-либо разметки</s>",
        parse_mode=None
    )


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())


# @dp.message(F.text)
# async def echo_with_time(message: Message):
#     # Получаем текущее время в часовом поясе ПК
#     time_now = datetime.now().strftime('%H:%M')
#     # Создаём подчёркнутый текст
#     added_text = html.underline(f"Создано в {time_now}")
#     # Отправляем новое сообщение с добавленным текстом
#     await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")


@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )


@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []

    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим"
    # открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти
    # после проведения каких-либо манипуляций, например, редактированием через Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Изображение из буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере"
    )
    file_ids.append(result.photo[-1].file_id)

    # Отправка файла по ссылке
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Изображение по ссылке"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"./tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # для Windows пути надо подправить
        destination=f"./tmp/{message.sticker.file_id}.webp"
    )


@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(
        caption="Общая подпись для будущего альбома"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg"),
        caption="Подпись к конкретному медиа",

    )
    # Если мы сразу знаем тип, то вместо общего add
    # можно сразу вызывать add_<тип>
    album_builder.add_photo(
        # Для ссылок или file_id достаточно сразу указать значение
        media="https://picsum.photos/seed/groosha/400/300"
    )
    # album_builder.add_photo(
    #     media="<ваш file_id>"
    # )
    await message.answer_media_group(
        # Не забудьте вызвать build()
        media=album_builder.build()
    )


@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
