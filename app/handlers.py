from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
import re

from app.scorer import score_candidate
from app.link_validator import validate_link
from app.sheets import append_row
from app.config import ADMIN_IDS
from app.bot import bot

router = Router()

# =========================
# FSM States
# =========================

class Screening(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    link = State()


QUESTIONS = [
    "1️⃣ Расскажите о проекте с AI: цель, ваша роль, результат.",
    "2️⃣ Опишите конкретный prompt или LLM pipeline, который вы использовали.",
    "3️⃣ Какие метрики использовали для оценки качества?",
    "4️⃣ Как решали trade-off между качеством, latency и cost?",
    "5️⃣ Пример ошибки модели и как вы её исправили.",
    "6️⃣ Пришлите ссылку на проект / демо / GitHub."
]


# =========================
# START
# =========================

@router.message(F.text == "/start")
async def start_screening(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "👋 Привет! Это AI-first HR-скрининг.\n"
        "Я задам 6 вопросов.\n"
        "Отвечайте развернуто.\n\n"
        "Поехали.\n\n"
        + QUESTIONS[0]
    )

    await state.set_state(Screening.q1)


# =========================
# QUESTION HANDLERS
# =========================

async def handle_answer(message: Message, state: FSMContext, next_state, question_text):

    text = message.text.strip()

    if len(text) < 10:
        await message.answer("Пожалуйста, дайте более развернутый ответ (минимум 10 символов).")
        return

    current_state = await state.get_state()
    await state.update_data(**{current_state.split(":")[1]: text})

    if next_state:
        await message.answer(question_text)
        await state.set_state(next_state)
    else:
        await finish_screening(message, state)


@router.message(Screening.q1)
async def q1_handler(message: Message, state: FSMContext):
    await handle_answer(message, state, Screening.q2, QUESTIONS[1])


@router.message(Screening.q2)
async def q2_handler(message: Message, state: FSMContext):
    await handle_answer(message, state, Screening.q3, QUESTIONS[2])


@router.message(Screening.q3)
async def q3_handler(message: Message, state: FSMContext):
    await handle_answer(message, state, Screening.q4, QUESTIONS[3])


@router.message(Screening.q4)
async def q4_handler(message: Message, state: FSMContext):
    await handle_answer(message, state, Screening.q5, QUESTIONS[4])


@router.message(Screening.q5)
async def q5_handler(message: Message, state: FSMContext):
    await message.answer(QUESTIONS[5])
    await state.set_state(Screening.link)


# =========================
# LINK HANDLER
# =========================

@router.message(Screening.link)
async def link_handler(message: Message, state: FSMContext):

    link = message.text.strip()

    if not re.match(r"https?://", link):
        await message.answer("Похоже, это не ссылка. Пришлите корректный URL.")
        return

    await message.answer("🔎 Проверяю ссылку...")

    validation = validate_link(link)

    if not validation.get("valid"):
        await message.answer(
            f"⚠️ Ссылка выглядит подозрительно:\n{validation.get('reason')}\n"
            "Если это реальный проект — отправьте другую ссылку."
        )
        return

    await state.update_data(link=link)
    await finish_screening(message, state)


# =========================
# FINISH FLOW
# =========================

async def finish_screening(message: Message, state: FSMContext):

    data = await state.get_data()

    user = message.from_user

    payload = {
        "full_name": user.full_name,
        "username": user.username,
        "answers": data
    }

    await message.answer("🧠 Анализирую ответы...")

    scoring = score_candidate(payload)

    avg = scoring["avg"]
    hot = scoring["hot"]

    # Save to Google Sheets
    row = [
        datetime.utcnow().isoformat(),
        user.id,
        user.username,
        user.full_name,
        data.get("q1"),
        data.get("q2"),
        data.get("q3"),
        data.get("q4"),
        data.get("q5"),
        data.get("link"),
        scoring["scores"]["AI_engineering"],
        scoring["explanations"]["AI_engineering"],
        scoring["scores"]["Product_impact"],
        scoring["explanations"]["Product_impact"],
        scoring["scores"]["Prompting_evaluation"],
        scoring["explanations"]["Prompting_evaluation"],
        avg,
        str(hot)
    ]

    append_row(row)

    # Notify admins if HOT
    if hot:
        text = (
            f"🔥 HOT CANDIDATE\n\n"
            f"{user.full_name}\n"
            f"@{user.username}\n"
            f"Avg: {avg}\n"
            f"{data.get('link')}"
        )

        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, text)

    await message.answer(
        f"✅ Скрининг завершён!\n\n"
        f"Ваш средний балл: {avg}\n"
        "Если вы подходите — мы свяжемся с вами."
    )

    await state.clear()


@router.message(F.text == "/admin_stats")
async def admin_stats(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    rows = get_all_rows()
    total = len(rows)

    if total == 0:
        await message.answer("Нет данных")
        return

    avg_score = sum(r["avg_score"] for r in rows) / total
    hot = sum(1 for r in rows if r["hot_candidate"] == "TRUE")

    await message.answer(
        f"Всего кандидатов: {total}\n"
        f"Средний балл: {round(avg_score,2)}\n"
        f"Hot: {hot}"
    )


@router.message(F.text == "/top3")
async def top3(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    rows = get_all_rows()

    sorted_rows = sorted(rows, key=lambda x: float(x["avg_score"]), reverse=True)[:3]

    text = "🏆 Топ-3 кандидата:\n\n"

    for r in sorted_rows:
        text += (
            f"{r['full_name']} — {r['avg_score']}\n"
            f"{r['link']}\n\n"
        )

    await message.answer(text)