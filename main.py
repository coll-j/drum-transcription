from fastapi import FastAPI, File, UploadFile, Request, Response
from fastapi.responses import HTMLResponse
from utils.predict import do_transcription
import sys
import os
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/predict")
async def predict_audio(request: Request, audio_file: UploadFile = File(...)):
    try:
        suffix = Path(audio_file.filename).suffix
        name = os.path.splitext(audio_file.filename)[0]
        
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(audio_file.file, tmp)
            tmp_path = Path(tmp.name)
            HH, SD, KD, bpm = do_transcription(tmp_path)
            result = {
                "HH": HH,
                "SD": SD,
                "KD": KD
            }

        return templates.TemplateResponse("result.html", 
        {
        "request": request, 
        "bpm": bpm, 
        "song_title": name, 
        "result": result,
        "tmp_path": audio_file.filename
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        respond = {
            "msg": str(e),
            "file": fname,
            "line": exc_tb.tb_lineno
        }

    return {"message": respond}