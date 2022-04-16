from fastapi import FastAPI, File, UploadFile, Request
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
async def predict_audio(upload_file: UploadFile = File(...)):
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
            HH, SD, KD = do_transcription(tmp_path)
            respond = {
                "HH": HH,
                "SD": SD,
                "KD": KD
            }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        respond = {
            "msg": str(e),
            "file": fname,
            "line": exc_tb.tb_lineno
        }

    return {"message": respond}