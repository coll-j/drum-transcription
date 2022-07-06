from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse
from utils.predict import do_transcription
from sys import exc_info
from os.path import split, splitext
from tempfile import NamedTemporaryFile
from pathlib import Path
from shutil import copyfileobj
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/predict")
async def predict_audio(request: Request, audio_file: UploadFile = File(...), bpm: int = Form(None)):
    try:
        suffix = Path(audio_file.filename).suffix
        name = splitext(audio_file.filename)[0]
        
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            copyfileobj(audio_file.file, tmp)
            tmp_path = Path(tmp.name)
            HH, SD, KD, bpm = do_transcription(tmp_path, bpm=bpm)
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
        exc_type, exc_obj, exc_tb = exc_info()
        fname = split(exc_tb.tb_frame.f_code.co_filename)[1]
        respond = {
            "msg": str(e),
            "file": fname,
            "line": exc_tb.tb_lineno
        }

    return {"message": respond}