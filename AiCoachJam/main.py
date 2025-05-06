from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from logic.programs import PROGRAMS_BY_SCORE_AND_TYPE
from logic.gemini_reason import get_reason

app = FastAPI()

# HTML + CSS dosyaları için tanımlar
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 🔵 HTML rotaları
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/puan", response_class=HTMLResponse)
def puan_page(request: Request):
    return templates.TemplateResponse("puan.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/sonuc", response_class=HTMLResponse)
def sonuc_page(request: Request):
    return templates.TemplateResponse("sonuc.html", {"request": request})


# 🔵 API model ve öneri mantığı (öncekiler)
class RIASECInput(BaseModel):
    scores: List[int]

class YKSInput(BaseModel):
    say: float
    ea: float
    soz: float

class CombinedInput(BaseModel):
    riasec: RIASECInput
    yks: YKSInput

def calculate_profile(scores):
    return {
        "R": sum(scores[0:5]),
        "I": sum(scores[5:10]),
        "A": sum(scores[10:15]),
        "S": sum(scores[15:20]),
        "E": sum(scores[20:25]),
        "C": sum(scores[25:30])
    }

def get_best_score_type(yks):
    return max(yks, key=yks.get)

@app.post("/recommend")
def recommend(data: CombinedInput):
    profile = calculate_profile(data.riasec.scores)
    dominant = sorted(profile, key=profile.get, reverse=True)[:2]
    best_score_type = get_best_score_type({
        "SAY": data.yks.say,
        "EA": data.yks.ea,
        "SOZ": data.yks.soz,
        "DIL": 0
    })

    matched_programs = []
    score_data = PROGRAMS_BY_SCORE_AND_TYPE.get(best_score_type, {})

    for dtype in dominant:
        for program in score_data.get(dtype, []):
            matched_programs.append({
                "program": program,
                "reason": get_reason(program, "/".join(dominant))
            })

    return {
        "profile": profile,
        "dominant": dominant,
        "dominant_labels": map_riasec_labels(dominant),
        "score_type": best_score_type,
        "recommendations": matched_programs
    }


RIASEC_LABELS = {
    "R": "Gerçekçi",
    "I": "Araştırmacı",
    "A": "Sanatsal",
    "S": "Sosyal",
    "E": "Girişimci",
    "C": "Geleneksel"
}

def map_riasec_labels(codes):
    return [RIASEC_LABELS.get(code, code) for code in codes]
