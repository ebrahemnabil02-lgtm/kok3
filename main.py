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
    return {"message": "API is checking model structure..."}

@app.post("/tryon")
async def try_on(person: UploadFile = File(...), garment: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    person_path = f"person_{session_id}.jpg"
    garment_path = f"garment_{session_id}.jpg"

    try:
        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)
        with open(garment_path, "wb") as f:
            shutil.copyfileobj(garment.file, f)

        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        
        # التعديل الجديد: استخدام api_name="/tryon" 
        # ده بيخلي جرايدو يبعت البيانات للمكان الصح بالأسامي الصح تلقائياً
        result = client.predict(
            person_img=handle_file(person_path),
            garment_img=handle_file(garment_path),
            seed=0,
            is_checked=True,
            api_name="/tryon"
        )

        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        return {"status": "success", "result": result}

    except Exception as e:
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        return {"status": "error", "message": str(e)}