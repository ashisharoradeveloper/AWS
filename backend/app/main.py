import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.csv_analysis import CsvAnalysisError, analyze_csv

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = FastAPI(title="AWS File Processing Lab API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The CSV file must be 5 MB or smaller.")

    try:
        result = analyze_csv(content)
        result["filename"] = file.filename
        return result
    except CsvAnalysisError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
