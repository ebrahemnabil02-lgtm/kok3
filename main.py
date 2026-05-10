from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import os
import shutil
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Final attempt with positional arguments"}

@app.post("/tryon")
async def try_on(person: UploadFile = File(...), garment: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    person_path = f"p_{session_id}.jpg"
    garment_path = f"g_{session_id}.jpg"

    try:
        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)
        with open(garment_path, "wb") as f:
            shutil.copyfileobj(garment.file, f)

        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        
        # التعديل النهائي والمؤكد بإذن الله:
        # إرسال 4 مدخلات فقط بالترتيب (شخص، لبس، seed، موافقة)
        # وبدون استخدام api_name، فقط fn_index=0
        result = client.predict(
            handle_file(person_path),
            handle_file(garment_path),
            0,
            True,
            fn_index=0
        )

        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        return {"status": "success", "result": result}

    except Exception as e:
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        return {"status": "error", "message": str(e)}