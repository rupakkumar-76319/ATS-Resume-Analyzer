# AI-Powered ATS Resume Analyzer

An industry-grade, asynchronous FastAPI backend service that simulates enterprise-level Applicant Tracking Systems (ATS). Using Google's Gemini 2.5 Flash model with strict structural schema parsing, this application processes resumes in multiple formats (PDF, DOCX, TXT) and matches them against job descriptions to provide automated, data-driven analysis.

---

## 1. Project Purpose

The AI-Powered ATS Resume Analyzer is designed to automatically parse, evaluate, and score job applications against a target Job Description (JD). It provides hiring managers, recruitment pipelines, and applicants with data-driven insights, keyword identification, and actionable feedback to determine role compatibility without manual screening overhead.

---

## 2. Architecture Rationale (Why This Tech Stack?)

The choice of this specific technical ecosystem is guided by performance, safety, and modern production standards:

* **FastAPI over Flask/Django:** FastAPI leverages Python's modern `asyncio` runtime natively. This enables the server to handle highly concurrent requests without blocking operations while awaiting slow network I/O operations (such as multi-page file reads or external API handshakes). Furthermore, it handles data serialization automatically and renders instant interactive documentation interfaces at `/docs`.
* **Gemini 2.5 Flash with Strict Response Schemas:** Instead of relying on standard LLM interactions that output unstructured text payloads (which are difficult for software systems to parse reliably), our code configures a programmatic `responseSchema`. This binds the generative model to output structural JSON objects matching our system types, mitigating text anomalies and data conversion errors.
* **In-Memory Streaming Buffers (`io.BytesIO`):** Rather than saving uploaded resume documents directly onto disk storage—which presents server cleanup requirements and introduces disk latency—the application handles documents directly within volatile memory buffers, speeding up processing cycles and keeping file system states clean.
* **HTTPX over Requests:** Because FastAPI is asynchronous, using the traditional `requests` library would block the entire server thread during the 20-30 seconds it takes to process the AI payload. `httpx.AsyncClient` allows the system to pause the individual request execution path while waiting for the Gemini API, letting the server handle thousands of other incoming traffic connections simultaneously.

---

## 3. Value Proposition for Students & Job Seekers

Corporate hiring pathways rely closely on automated Applicant Tracking Systems to screen out up to 75% of incoming applications before human review. This platform flips the advantage back to students and job seekers by:

1.  **Removing the System Guesswork:** By providing transparency into how resume parsers evaluate professional documentation, candidates can correct missing parameters ahead of submissions.
2.  **Highlighting Critical Skill Gaps:** The system automatically flags relevant industry terms, missing technical concepts, and keyword variations that human eyes might miss but ATS algorithms prioritize.
3.  **Actionable Strategy Delivery:** Rather than providing generalized advice, the platform generates tailored tactical steps to optimize resume impact for specific roles.

---

## 4. Comprehensive Codebase Blueprint (`main.py` Breakdown)

Here is a breakdown of how the logic operates behind the scenes across every major module:

### 4.1. Module Initializations & Security Shield
```python
load_dotenv()
app = FastAPI()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("Gemini API Key is not set in the .env file..")
```

What it does: Imports structural ecosystem dependencies and initializes the core application object. load_dotenv() acts as a security gateway, looking inside system files for your private token configurations. If GEMINI_API_KEY is missing, the code immediately throws a RuntimeError to block broken execution processes.

### 4.2. Multi-Format Text Extraction Pipeline
```Python
def extract_text(file_bytes: bytes, filename: str) -> str:
    file_extension = filename.split(".")[-1].lower()
    text = ""
```
# Routing Logic for PDF, DOCX, and TXT extensions

What it does: Receives raw document bytes and determines their file format.
PDF: Loads the binary stream through pypdf.PdfReader without writing to disk, reading layout vectors page by page.
DOCX/DOC: Utilizes docx2txt to scan open XML word formats.
TXT: Decodes bytes to standard utf-8 text strings.
Validation: If the resulting text block is blank, it throws a 400 Bad Request exception to let the user know the file could not be parsed.

### 4.3. Core Analytical Endpoint (POST /resume_Analyzer)
```Python
@app.post("/resume_Analyzer")
async def analyze_resume(job_description: str = Form(...), file: UploadFile = File(...)):
```
What it does: Serves as the main gateway for data processing. It accepts multi-part form input: a string for the job description and an uploaded document payload.
The Schema Contract: It passes a structural JSON dictionary model down to the AI model:
match_score: An exact rating out of 100.
matched_keywords/missing_keywords: Comprehensive technical string arrays.
strengths/actionable_feedback: Written professional guidance insights.

### 4.4. Asynchronous Network Commits
```Python
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=payload, timeout=30.0)
```
What it does: Opens a non-blocking asynchronous HTTP network tunnel, firing the serialized data payload over to Google's remote endpoints. The application stays responsive to other users while waiting for the AI calculation to finish. Once received, it parses the payload via json.loads and returns clean JSON structured text directly to the user interface.

### 4.5. End-to-End Workflow Execution Pipeline
The flowchart below traces data movement as it flows through the system:

[Candidate Interface] 
       │ 
       ▼ (1. Submits Text Job Description + Binary Resume File via Form)
[FastAPI Router Enters] 
       │ 
       ▼ (2. Passes raw bytes into specialized in-memory extraction tools)
[File Parsing Layer] ──(Validates text string outputs)──> [Error Checks Fail? Drop with 400]
       │
       ▼ (3. Bundles extracted text with Strict JSON Output Specifications)
[API Payload Builder] 
       │ 
       ▼ (4. Triggers Non-Blocking Asynchronous Network Request via HTTPX)
[Google Gemini Engine] 
       │ 
       ▼ (5. Evaluates alignment match and sends back strict schema data)
[FastAPI Output Matrix] ──(Transforms data arrays)──> [Final Clean JSON User Payload]
### 4.6. Local Operations & Quickstart Manual
Follow these quick setup steps to get your service running on your machine:

1. Workspace Verification
Ensure your project files match this exact structural pattern within your working folder:

Plaintext
my-resume-analyzer/
├── main.py
├── requirements.txt
├── Dockerfile
└── .env
2. Configure Environment Parameters
Create a file named exactly .env inside the root workspace folder and add your private API key:

### Code snippet
GEMINI_API_KEY=**********************************************
3. Spin Up Application Directly
Install the required application dependencies and start your local server using Uvicorn:

### Bash
``` Python
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000/docs in your browser. Expand the green POST option block, click "Try it out", upload your test resume file, paste an open job description, and click Execute to view your structured analysis report instantly!

***