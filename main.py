import io
from typing import Any

import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile


app = FastAPI(title="FastAPI PDF Extraction API")


def normalize_table(table: list[list[Any]] | None) -> list[list[str]]:
    if not table:
        return []
    normalized: list[list[str]] = []
    for row in table:
        normalized.append(
            ["" if cell is None else str(cell).strip() for cell in row]
        )
    return normalized


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pdf-extraction-api"}


@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or ""
    is_pdf_name = filename.lower().endswith(".pdf")
    is_pdf_type = (file.content_type or "").lower() == "application/pdf"
    if not is_pdf_name and not is_pdf_type:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages: list[dict[str, Any]] = []
            for index, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                extracted_tables = page.extract_tables() or []
                tables = [normalize_table(table) for table in extracted_tables]
                pages.append(
                    {
                        "page_number": index,
                        "text": page_text.strip(),
                        "tables": tables,
                    }
                )
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse PDF: {exc}"
        ) from exc

    return {
        "file_name": filename,
        "page_count": len(pages),
        "pages": pages,
    }
