from fastapi import FastAPI, File, UploadFile
from utils.predict import do_transcription
import sys
import os
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bye World"}

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