from olgram.router import dp

from aiogram import types, Bot as AioBot
from olgram.models.models import Bot, User, DefaultAnswer
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from textwrap import dedent
from olgram.utils.mix import edit_or_create, button_text_limit
from olgram.commands import bot_actions

import typing as ty


menu_callback = CallbackData('menu', 'level', 'bot_id', 'operation', 'chat')

empty = "0"


async def send_bots_menu(chat_id: int, user_id: int, call=None):
    """
    Отправить пользователю список ботов
    :return:
    """
    if call:
        await call.answer()

    user = await User.get_or_none(telegram_id=user_id)
    bots = await Bot.filter(owner=user)
    if not bots:
        await AioBot.get_current().send_message(chat_id, dedent("""
        У вас нет добавленных ботов.

        Отправьте команду /addbot, чтобы добавить бот.
        """))
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for bot in bots:
        keyboard.insert(
            types.InlineKeyboardButton(text="@" + bot.name,
                                       callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                       chat=empty))
        )

    text = "Ваши боты"
    if call:
        await edit_or_create(call, text, keyboard)
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard)


async def send_chats_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    chats = await bot.group_chats.all()

    for chat in chats:
        keyboard.insert(
            types.InlineKeyboardButton(text=button_text_limit(chat.name),
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat=chat.id))
        )
    if chats:
        keyboard.insert(
            types.InlineKeyboardButton(text="Личные сообщения",
                                       callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="chat",
                                                                       chat="personal"))
        )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty,
                                                                   chat=empty))
    )

    if not chats:
        text = dedent(f"""
        Этот бот не добавлен в чаты, поэтому все сообщения будут приходить вам в бот.
        Чтобы подключить чат — добавьте бот @{bot.name} в чат, откройте это меню ещё раз и выберите добавленный чат.
        Если ваш бот состоял в групповом чате до того, как его добавили в Olgram - удалите бота из чата и добавьте
        снова.
        """)
    else:
        text = dedent(f"""
        В этом разделе вы можете привязать бота @{bot.name} к чату.
        Выберите чат, куда бот будет пересылать сообщения.
        """)

    await edit_or_create(call, text, keyboard)


async def send_bot_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="Текст",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Чат",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="chat",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Удалить бот",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="delete",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=0, bot_id=empty, operation=empty, chat=empty))
    )

    await edit_or_create(call, dedent(f"""
    Управление ботом @{bot.name}.

    Если у вас возникли вопросы по настройке бота, то посмотрите нашу справку /help или напишите нам
    @civsocit_feedback_bot
    """), reply_markup=keyboard)


async def send_bot_delete_menu(bot: Bot, call: types.CallbackQuery):
    await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="Да, удалить бот",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="delete_yes",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Назад",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    await edit_or_create(call, dedent(f"""
    Вы уверены, что хотите удалить бота @{bot.name}?
    """), reply_markup=keyboard)


async def send_bot_text_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None, chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Завершить редактирование",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Автоответчик",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="next_text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Сбросить текст",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="reset_text",
                                                                   chat=empty))
    )

    text = dedent("""
    Сейчас вы редактируете текст, который отправляется после того, как пользователь отправит вашему боту @{0}
    команду /start

    Текущий текст:
    <pre>
    {1}
    </pre>
    Отправьте сообщение, чтобы изменить текст.
    """)
    text = text.format(bot.name, bot.start_text)
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_second_text_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None,
                                    chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Завершить редактирование",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Предыдущий текст",
                                   callback_data=menu_callback.new(level=2, bot_id=bot.id, operation="text",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Шаблоны ответов...",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id, operation="templates",
                                                                   chat=empty))
    )
    keyboard.insert(
        types.InlineKeyboardButton(text="Сбросить текст",
                                   callback_data=menu_callback.new(level=3, bot_id=bot.id,
                                                                   operation="reset_second_text", chat=empty))
    )

    text = dedent("""
    Сейчас вы редактируете текст автоответчика. Это сообщение отправляется в ответ на все входящие сообщения @{0} \
автоматически. По умолчанию оно отключено.

    Текущий текст:
    <pre>
    {1}
    </pre>
    Отправьте сообщение, чтобы изменить текст.
    """)
    text = text.format(bot.name, bot.second_text if bot.second_text else "(отключено)")
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


async def send_bot_templates_menu(bot: Bot, call: ty.Optional[types.CallbackQuery] = None,
                                    chat_id: ty.Optional[int] = None):
    if call:
        await call.answer()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        types.InlineKeyboardButton(text="<< Завершить редактирование",
                                   callback_data=menu_callback.new(level=1, bot_id=bot.id, operation=empty, chat=empty))
    )

    text = dedent("""
    Сейчас вы редактируете шаблоны ответов для @{0}. Текущие шаблоны:

    <pre>
    {1}
    </pre>
    Отправьте какую-нибудь фразу (например: "Ваш заказ готов, ожидайте!"), чтобы добавить её в шаблон.
    Чтобы удалить шаблон из списка, отправьте его номер в списке (например, 4)
    """)

    templates = await bot.answers
    templates_text = "\n".join(f"{n}. {template.text}" for n, template in enumerate(templates))
    if not templates_text:
        templates_text = "(нет шаблонов)"
    text = text.format(bot.name, templates_text)
    if call:
        await edit_or_create(call, text, keyboard, parse_mode="HTML")
    else:
        await AioBot.get_current().send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")


@dp.message_handler(state="wait_start_text", content_types="text", regexp="^[^/].+")  # Not command
async def start_text_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)
    bot.start_text = message.text
    await bot.save()
    await send_bot_text_menu(bot, chat_id=message.chat.id)


@dp.message_handler(state="wait_second_text", content_types="text", regexp="^[^/].+")  # Not command
async def second_text_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)
    bot.second_text = message.text
    await bot.save()
    await send_bot_second_text_menu(bot, chat_id=message.chat.id)


@dp.message_handler(state="wait_template", content_types="text", regexp="^[^/](.+)?")  # Not command
async def template_received(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:
        bot_id = proxy.get("bot_id")
    bot = await Bot.get_or_none(pk=bot_id)

    if message.text.isdigit():
        # Delete template
        number = int(message.text)
        templates = await bot.answers
        if number < 0 or number >= len(templates):
            await message.answer(f"Неправильное число. Чтобы удалить шаблон, введите число от 0 до {len(templates)}")
            return
        await templates[number].delete()
    else:
        # Add template
        template = DefaultAnswer(text=message.text, bot=bot)
        await template.save()

    await send_bot_templates_menu(bot, chat_id=message.chat.id)


@dp.callback_query_handler(menu_callback.filter(), state="*")
async def callback(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    level = callback_data.get("level")

    if level == "0":
        return await send_bots_menu(call.message.chat.id, call.from_user.id, call)

    bot_id = callback_data.get("bot_id")
    bot = await Bot.get_or_none(id=bot_id)
    if not bot or (await bot.owner).telegram_id != call.from_user.id:
        await call.answer("У вас нет прав на этого бота", show_alert=True)
        return

    if level == "1":
        await state.reset_state()
        return await send_bot_menu(bot, call)

    operation = callback_data.get("operation")
    if level == "2":
        await state.reset_state()
        if operation == "chat":
            return await send_chats_menu(bot, call)
        if operation == "delete":
            return await send_bot_delete_menu(bot, call)
        if operation == "text":
            await state.set_state("wait_start_text")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_text_menu(bot, call)

    if level == "3":
        if operation == "delete_yes":
            return await bot_actions.delete_bot(bot, call)
        if operation == "chat":
            return await bot_actions.select_chat(bot, call, callback_data.get("chat"))
        if operation == "reset_text":
            await bot_actions.reset_bot_text(bot, call)
            return await send_bot_text_menu(bot, call)
        if operation == "next_text":
            await state.set_state("wait_second_text")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_second_text_menu(bot, call)
        if operation == "reset_second_text":
            await bot_actions.reset_bot_second_text(bot, call)
            return await send_bot_second_text_menu(bot, call)
        if operation == "templates":
            await state.set_state("wait_template")
            async with state.proxy() as proxy:
                proxy["bot_id"] = bot.id
            return await send_bot_templates_menu(bot, call)
