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
    return {"message": "API is Live using IDM-VTON Model"}

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

        # التغيير هنا: استخدام موديل IDM-VTON المستقر
        client = Client("yisol/IDM-VTON")
        
        result = client.predict(
            dict={"background": handle_file(person_path), "layers": [], "composite": None}, # صورة الشخص
            garm_img=handle_file(garment_path), # صورة اللبس
            garment_des="fashion item",         # وصف بسيط
            is_checked=True,                    # الموافقة
            is_checked_det=True,                # الموافقة على التفاصيل
            denoise_steps=30,                   # جودة الصورة
            seed=42,                            # Seed ثابت للنتيجة
            api_name="/predict"                 # اسم الـ API المستقر
        )

        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        # الموديل ده بيرجع قائمة، النتيجة هي أول عنصر
        final_image_url = result[0] if isinstance(result, list) else result

        return {"status": "success", "result": final_image_url}

    except Exception as e:
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        return {"status": "error", "message": str(e)}