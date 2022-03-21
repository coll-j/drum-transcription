from fastapi import FastAPI, File, UploadFile
from utils.predict import test_librosa

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bye World"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        sig, fs = test_librosa(file.file)
        print("sig: ", sig)
    except Exception as e:
        return {"message": str(e)}
    return {"message": "success"}