"""
Koopilot AI Service Layer — Gemini Edition
──────────────────────────────────────────
Mimari: Rule-Based Tool Router + Gemini Response Writer

Akış:
  1. Kullanıcı mesajı gelir
  2. Kural tabanlı router → mesajda stok/ürün keyword'ü var mı?
  3. Varsa → check_stock tool çağrılır → DB'den gerçek veri çekilir
  4. Gemini, veriyi + mesajı alarak doğal dil yanıtı üretir
  5. Yanıt + kullanılan araçlar frontend'e döner

SDK: google-genai (yeni nesil, google.generativeai deprecated)
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from services.tools import execute_tool

load_dotenv()

# ── Gemini Client ────────────────────────────────────────────────────────────

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "Sen Koopilot adlı bir kooperatif operasyon asistanısın. "
    "Görevin kooperatif çalışanlarına stok bilgisi ve operasyonel "
    "sorularında yardımcı olmak.\n"
    "Kuralların:\n"
    "- Her zaman Türkçe yanıt ver\n"
    "- Kısa ve net cevaplar ver\n"
    "- Samimi ve profesyonel bir dil kullan\n"
    "- Sana verilen stok verisini doğrudan kullan, asla uydurma\n"
)


# ── Rule-Based Tool Router ───────────────────────────────────────────────────

# Stok sorgusu tetikleyen anahtar kelimeler
STOCK_KEYWORDS = [
    "stok", "var mı", "varmı", "var mi", "kaç", "kac",
    "mevcut", "miktar", "adet", "kaldı", "kaldi",
    "tükendi", "tukendi", "bitti", "depoda",
]

# Veritabanındaki bilinen ürünler (genişletilebilir)
KNOWN_PRODUCTS = [
    "domates", "biber", "patates", "soğan", "sogan", "salatalık", "salatalik",
]


def detect_stock_query(message: str):
    """
    Mesajda stok sorgusu varsa hedef ürün adını döndürür.
      None         → stok sorusu yok
      "__unknown__"→ stok sorusu var, ürün tanımlanamadı
      str          → tespit edilen ürün adı
    """
    msg_lower = message.lower()

    has_stock_kw = any(kw in msg_lower for kw in STOCK_KEYWORDS)
    if not has_stock_kw:
        return None

    for product in KNOWN_PRODUCTS:
        if product in msg_lower:
            return product

    return "__unknown__"


# ── Agent Entry Point ────────────────────────────────────────────────────────

def get_ai_response(user_message: str) -> dict:
    """
    Kullanıcı mesajını işler; rule-based routing + Gemini yanıtı döndürür.

    Returns:
        dict: {
            "response": str,
            "tools_used": list[str]
        }
    """
    tools_used = []
    tool_context = ""

    # ── Tool Routing ─────────────────────────────────────────────────────────
    detected = detect_stock_query(user_message)

    if detected == "__unknown__":
        tool_context = (
            "\n[Sistem Notu]: Kullanıcı stok sorgusu yapıyor ancak "
            "hangi ürünü sorduğu anlaşılamadı. "
            "Kullanıcıdan ürün adını açıkça belirtmesini iste.\n"
        )
    elif detected is not None:
        stock_result = execute_tool("check_stock", {"product_name": detected})
        tools_used.append("check_stock")
        tool_context = f"\n[Stok Verisi]: {stock_result}\n"

    # ── Gemini Prompt ─────────────────────────────────────────────────────────
    if tool_context:
        prompt = (
            f"{SYSTEM_PROMPT}"
            f"{tool_context}\n"
            f"Kullanıcı sorusu: {user_message}\n\n"
            "Yukarıdaki veriyi kullanarak kısa ve net bir Türkçe yanıt ver."
        )
    else:
        prompt = f"{SYSTEM_PROMPT}\nKullanıcı sorusu: {user_message}"

    # ── Gemini API Çağrısı ────────────────────────────────────────────────────
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=512,
            ),
        )
        return {
            "response": response.text,
            "tools_used": tools_used,
        }
    except Exception as e:
        print(f"Gemini API hatasi: {e}")
        return {
            "response": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
            "tools_used": tools_used,
        }
