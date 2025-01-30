from aiogram import types, F
from aiogram.filters.command import Command
from database import get_quiz_state, update_quiz_state, get_leaderboard
from quiz_data import quiz_data
from keyboards import generate_options_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def register_handlers(dp):
    @dp.callback_query(F.data.startswith("right_answer_"))
    async def right_answer(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        button_text = callback.data.split('_')[2]  # Получаем текст кнопки из callback.data
        await callback.bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        await callback.message.answer(f"Ваш ответ: {button_text}, Правильно!")
        current_question_index, correct_answers = await get_quiz_state(user_id)
        current_question_index += 1
        correct_answers += 1

        await update_quiz_state(user_id, current_question_index, correct_answers)

        if current_question_index < len(quiz_data):
            await get_question(callback.message, user_id)
        else:
            await callback.message.answer("Это был последний вопрос. Квиз завершен!")
            await show_leaderboard(callback.message)

    @dp.callback_query(F.data.startswith("wrong_answer_"))
    async def wrong_answer(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        current_question_index, correct_answers = await get_quiz_state(user_id)
        correct_option = quiz_data[current_question_index]['options'][quiz_data[current_question_index]['correct_option']]
        button_text = callback.data.split('_')[2]  # Получаем текст кнопки из callback.data
        await callback.bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        await callback.message.answer(f"Ваш ответ: {button_text}, Неправильно! Правильный ответ: {correct_option}")
        current_question_index += 1
        await update_quiz_state(user_id, current_question_index, correct_answers)

        if current_question_index < len(quiz_data):
            await get_question(callback.message, user_id)
        else:
             await callback.message.answer("Это был последний вопрос. Квиз завершен!")
             await show_leaderboard(callback.message)

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Начать игру"))
        await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

    async def get_question(message, user_id):
        current_question_index, _ = await get_quiz_state(user_id)
        correct_index = quiz_data[current_question_index]['correct_option']
        opts = quiz_data[current_question_index]['options']
        kb = generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

    async def new_quiz(message):
        user_id = message.from_user.id
        # Исправленный вызов
        await update_quiz_state(user_id, 0, 0)
        await get_question(message, user_id)

    @dp.message(F.text == "Начать игру")
    @dp.message(Command("quiz"))
    async def cmd_quiz(message: types.Message):
        await message.answer(f"Давайте начнем квиз!")
        await new_quiz(message)

    @dp.message(Command("leaderboard"))
    async def cmd_leaderboard(message: types.Message):
        await show_leaderboard(message)

    async def show_leaderboard(message: types.Message):
        leaderboard = await get_leaderboard()
        if leaderboard:
            text = "Таблица лидеров:\n"
            for index, (user_id, correct_answers) in enumerate(leaderboard):
                 text += f"{index + 1}. User: {user_id}, Правильных ответов: {correct_answers}\n"
            await message.answer(text)
        else:
            await message.answer("Пока нет результатов в таблице лидеров.")