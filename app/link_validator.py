from openai import OpenAI
import json
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def validate_link(link: str):

    prompt = f"""
    Это ссылка кандидата: {link}
    Это реальная ссылка на проект/демо/репозиторий?
    Верни JSON: {{"valid": true/false, "reason": "text"}}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return json.loads(resp.choices[0].message.content)