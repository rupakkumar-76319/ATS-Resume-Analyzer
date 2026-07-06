from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import os
import pypdf
import docx2txt
import io
import httpx
import json

load_dotenv()

app= FastAPI()

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("Gemini API Key is not set in the .env file..")

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extracts text from PDF, DOCX, or TXT Files."""
    file_extension= filename.split(".")[-1].lower()
    text=""

    try: 
        if file_extension=="pdf":
            
            pdf_file= io.BytesIO(file_bytes)
            reader=pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                page_text=page.extract_text()
                if page_text:
                    text+=page_text +"\n"
        elif file_extension in ["docx", "doc"]:
            # Wrap bytes in a file-like stream for docx2txt
            docx_file= io.BytesIO(file_bytes)
            text= docx2txt.process(docx_file)
        elif file_extension == "txt":
            text=file_bytes.decode("utf-8")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: .{file_extension}. Please upload PDF, DOCX, or TXT."
            )

        if not text.strip():
            raise HTTPException(status_code=400, detail="The uploaded file seems to be empty or unreadable.")
        return text.strip()

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/resume_Analyzer")
async def analyze_resume(
    job_description: str = Form(...),
    file: UploadFile= File(...)
):
    file_bytes= await file.read()

    resume_text= extract_text(file_bytes, file.filename)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    response_schema= {
        "type": "OBJECT",
        "properties":{
            "match_score": {"type":"INTEGER"},
            "matched_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
            "missing_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
            "strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
            "actionable_feedback": {"type": "ARRAY", "items": {"type": "STRING"}}
        },
        "required":["match_score", "matched_keywords", "missing_keywords", "strengths", "actionable_feedback"]
    }
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"You are an expert ATS (Applicant Tracking System) and senior technical recruiter.\n"
                    f"Analyze the following resume text against the provided job description.\n\n"
                    f"Job Description:\n{job_description}\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
            "temperature": 0.2
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            
            result_json = response.json()
            generated_text = result_json['candidates'][0]['content']['parts'][0]['text']
            
            analysis_data = json.loads(generated_text)
            return analysis_data
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Gemini API Error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")