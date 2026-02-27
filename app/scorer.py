from openai import OpenAI
import json
from app.config import OPENAI_API_KEY, HOT_THRESHOLD

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты — HR ассессор AI-first разработчиков.
Верни строго JSON:
{
 "scores": {"AI_engineering": int, "Product_impact": int, "Prompting_evaluation": int},
 "explanations": {"AI_engineering": "text", "Product_impact": "text", "Prompting_evaluation": "text"},
 "avg": float
}
"""

def score_candidate(data: dict):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":json.dumps(data, ensure_ascii=False)}
        ],
        temperature=0
    )

    parsed = json.loads(response.choices[0].message.content)

    hot = parsed["avg"] >= HOT_THRESHOLD and any(
        v >= 9 for v in parsed["scores"].values()
    )

    parsed["hot"] = hot
    return parsed