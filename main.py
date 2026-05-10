from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import os
import shutil
import uuid

app = FastAPI()

# إعدادات CORS للسماح بالاتصال من المتصفح أو الموبايل
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
    # إنشاء أسماء فريدة للملفات لتجنب التداخل بين المستخدمين
    session_id = str(uuid.uuid4())
    person_path = f"person_{session_id}.jpg"
    garment_path = f"garment_{session_id}.jpg"

    try:
        # حفظ الصور المرفوعة مؤقتاً على السيرفر
        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)
        with open(garment_path, "wb") as f:
            shutil.copyfileobj(garment.file, f)

        # الاتصال بموديل Kolors على Hugging Face
        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        
        # التعديل النهائي: إرسال صورتين فقط كما يتطلب الموديل حالياً
        result = client.predict(
            handle_file(person_path),   # صورة الشخص
            handle_file(garment_path),  # صورة الملابس
            fn_index=0
        )

        # حذف الملفات المؤقتة بعد انتهاء العملية لتوفير مساحة السيرفر
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        return {"status": "success", "result": result}

    except Exception as e:
        # التأكد من حذف الملفات حتى في حالة حدوث خطأ
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        return {"status": "error", "message": str(e)}