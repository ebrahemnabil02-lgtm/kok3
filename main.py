from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import os
import shutil
import uuid

app = FastAPI()

# إعدادات CORS للسماح بالوصول من أي مكان
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
    # إنشاء أسماء فريدة للملفات باستخدام UUID
    session_id = str(uuid.uuid4())
    person_path = f"person_{session_id}.jpg"
    garment_path = f"garment_{session_id}.jpg"

    try:
        # حفظ الصور المرفوعة مؤقتاً
        with open(person_path, "wb") as f:
            shutil.copyfileobj(person.file, f)
        with open(garment_path, "wb") as f:
            shutil.copyfileobj(garment.file, f)

        # الاتصال بموديل Kolors على Hugging Face
        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        
        # التعديل الشامل: إرسال 5 مدخلات بالترتيب لملء مصفوفة الموديل وتجنب Index Error
        # الترتيب المتوقع: (صورة الشخص، صورة اللبس، ماسك/فارغ، الـ seed، الموافقة)
        result = client.predict(
            handle_file(person_path),   # الخانة 0: صورة الشخص
            handle_file(garment_path),  # الخانة 1: صورة اللبس
            None,                       # الخانة 2: الـ Mask (نرسل None لأنه غير مطلوب هنا)
            0,                          # الخانة 3: الـ Seed
            True,                       # الخانة 4: الموافقة على الشروط is_checked
            fn_index=0
        )

        # حذف الملفات المؤقتة بعد المعالجة
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        # إرجاع النتيجة
        return {"status": "success", "result": result}

    except Exception as e:
        # تنظيف الملفات في حالة حدوث خطأ
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        
        print(f"Error Details: {str(e)}")
        return {"status": "error", "message": str(e)}

# تأكد من تحديث requirements.txt دائماً