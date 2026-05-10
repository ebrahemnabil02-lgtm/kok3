from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import os
import shutil
import uuid

app = FastAPI()

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Kolors Virtual Try-On API is Live!"}

@app.post("/tryon")
async def try_on(person: UploadFile = File(...), garment: UploadFile = File(...)):
    # إنشاء أسماء فريدة للملفات
    session_id = str(uuid.uuid4())
    person_path = f"person_{session_id}.jpg"
    garment_path = f"garment_{session_id}.jpg"

    try:
        # حفظ الصور المرفوعة مؤقتاً
        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)
        with open(garment_path, "wb") as f:
            shutil.copyfileobj(garment.file, f)

        # الاتصال بموديل Kolors
        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        
        # التعديل الحاسم: إرسال القيم بالترتيب (Positional Arguments)
        # الترتيب: صورة الشخص، صورة اللبس، الـ Seed، الموافقة على الشروط
        result = client.predict(
            handle_file(person_path), 
            handle_file(garment_path),
            0,     # seed
            True,  # is_checked
            fn_index=0
        )

        # تنظيف الملفات المؤقتة
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        return {"status": "success", "result": result}

    except Exception as e:
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        return {"status": "error", "message": str(e)}