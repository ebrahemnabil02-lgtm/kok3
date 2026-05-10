from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client, handle_file
import os
import shutil
import uuid

app = FastAPI()

# إعدادات CORS للسماح بالوصول من أي مكان (مهم جداً للـ Frontend)
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
    # إنشاء أسماء فريدة للملفات باستخدام UUID لتجنب التداخل
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
        
        # التعديل الأكيد: استخدام fn_index=0 بدلاً من api_name
        # هذا يتخطى مشكلة تغير أسماء الوظائف في الموديل
        result = client.predict(
            person_img=handle_file(person_path),
            garment_img=handle_file(garment_path),
            seed=0,
            is_checked=True,
            fn_index=0
        )

        # حذف الملفات المؤقتة بعد المعالجة لتوفير مساحة السيرفر
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)

        # إرجاع النتيجة (غالباً ما تكون رابط الصورة النهائية)
        return {"status": "success", "result": result}

    except Exception as e:
        # تنظيف الملفات في حالة حدوث خطأ أيضاً
        if os.path.exists(person_path): os.remove(person_path)
        if os.path.exists(garment_path): os.remove(garment_path)
        
        print(f"Detailed Error: {str(e)}") # ستظهر في Railway Logs
        return {"status": "error", "message": str(e)}

# تأكد من أن ملف requirements.txt يحتوي على:
# fastapi
# uvicorn
# gradio_client
# python-multipart