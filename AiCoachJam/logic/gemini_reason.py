import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_reason(program, personality_profile):
    prompt = (
        f"Bir öğrenci RIASEC kişilik tipine göre '{personality_profile}' baskın özelliklerine sahip. "
        f"Bu kişiliğe sahip birine '{program}' bölümünü neden önerirsin? "
        f"Kısa ama ikna edici bir açıklama yap."
    )

    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")

    response = model.generate_content(prompt)
    return response.text.strip()
