from fastapi import FastAPI, Request
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from app.bot import bot, dp
from app.config import WEBHOOK_URL
import asyncio

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}