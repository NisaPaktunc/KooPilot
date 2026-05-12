"""
Koopilot AI Service — Gemini Function Calling Edition
───────────────────────────────────────────────────────
Mimari: Gerçek Gemini Function Calling (ReAct döngüsü)

Eski (kural tabanlı):  if "domates" in message → check_stock()
Yeni (agent):          Gemini hangi tool'u çağıracağına kendi karar verir

Akış:
  1. Kullanıcı mesajı + konuşma geçmişi Gemini'ye gönderilir
  2. Gemini bir tool çağırmak istiyorsa function_call bloğu döner
  3. Backend tool'u çalıştırır, sonucu Gemini'ye geri verir
  4. Gemini yeterli bilgiye sahip olana kadar döngü devam eder
  5. Son doğal dil yanıtı kullanıcıya döner
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from services.tools import execute_tool, TOOL_DEFINITIONS

load_dotenv()

# ── Gemini Client ──────────────────────────────────────────────────────────────

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """Sen Koopilot'sun — küçük işletmeler ve kooperatifler için 
yapay zeka destekli operasyon asistanı.

GÖREVLER:
- Müşterilerin sipariş, kargo ve ürün sorularını yanıtla
- Stok durumlarını kontrol et, kritik durumlarda yöneticiyi bilgilendir
- Yöneticilere günlük özet ve operasyonel bilgi sun
- Proaktif ol: sorun fark edersen söyle

KURALLAR:
- Her zaman önce ilgili tool'u çağır, bilgiyi gerçek veriden al, asla uydurma
- Birden fazla bilgi gerekiyorsa birden fazla tool çağır
- Stok kritikse MUTLAKA send_manager_notification tool'unu da çağır
- Kargo gecikmesi varsa hem müşteriyi bilgilendir hem yöneticiye gönder
- Türkçe konuş, samimi ama profesyonel ol
- Kısa ve net cümleler kur, emoji kullan ama abartma

YANIT STILI:
- Somut bilgi ver: tarih, saat, miktar, sipariş numarası
- Belirsizlik varsa sormaktan çekinme
- Müşteriyi asla boş bırakma
"""


# ── Ana Agent Fonksiyonu ───────────────────────────────────────────────────────

def get_ai_response(user_message: str, conversation_history: list = None) -> dict:
    """
    Gerçek Gemini function calling ile ReAct döngüsü.

    Args:
        user_message: Kullanıcının son mesajı
        conversation_history: Önceki mesajlar listesi (Gemini formatında)

    Returns:
        {
            "response": str,           — kullanıcıya gösterilecek yanıt
            "tools_used": list[str],   — çağrılan tool adları (UI badge için)
            "tool_details": list[dict] — tool input/output detayları
        }
    """
    if conversation_history is None:
        conversation_history = []

    tools_used    = []
    tool_details  = []

    # Gemini tools nesnesi
    gemini_tools = [
        types.Tool(function_declarations=[
            types.FunctionDeclaration(**t) for t in TOOL_DEFINITIONS
        ])
    ]

    # Mevcut konuşma + yeni mesaj
    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=gemini_tools,
        temperature=0.3,
        max_output_tokens=1024,
    )

    # ── ReAct Döngüsü ──────────────────────────────────────────────────────────
    max_iterations = 5  # sonsuz döngü koruması
    iteration = 0

    def _has_function_call(part):
        """Güvenli function_call kontrolü — attribute eksikliğine karşı koruma."""
        try:
            return bool(part.function_call and part.function_call.name)
        except Exception:
            return False

    while iteration < max_iterations:
        iteration += 1

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        parts      = candidate.content.parts

        # parts None olabilir — güvenli kontrol
        if parts is None:
            break

        # Tool call var mı kontrol et
        function_calls = [p for p in parts if _has_function_call(p)]

        if not function_calls:
            # Tool call yok — son yanıt hazır
            break

        # Tool çağrılarını işle
        function_response_parts = []

        for part in function_calls:
            fc        = part.function_call
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}

            # Tool'u çalıştır
            result = execute_tool(tool_name, tool_args)

            tools_used.append(tool_name)
            tool_details.append({
                "tool":   tool_name,
                "input":  tool_args,
                "output": result
            })

            function_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=tool_name,
                        response={"result": result}
                    )
                )
            )

        # Gemini'nin tool call'ını ve sonuçları history'ye ekle
        contents.append(types.Content(role="model",  parts=parts))
        contents.append(types.Content(role="user",   parts=function_response_parts))

    # Son yanıtı çıkar
    final_text = ""
    last_candidate = response.candidates[0] if response.candidates else None
    
    if last_candidate and last_candidate.content and last_candidate.content.parts:
        for part in last_candidate.content.parts:
            if hasattr(part, "text") and part.text:
                final_text += part.text

    if not final_text:
        final_text = "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."

    return {
        "response":     final_text,
        "tools_used":   list(dict.fromkeys(tools_used)),  # tekrar eden tool'ları temizle
        "tool_details": tool_details,
    }
