# FastAPI PDF Extraction API

FastAPI app with a PDF upload endpoint that extracts text and tables using `pdfplumber` and returns structured JSON.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

## Endpoint

`POST /extract`

- Form field: `file` (PDF file)
- Response:
  - `file_name`
  - `page_count`
  - `pages[]`
    - `page_number`
    - `text`
    - `tables` (list of extracted tables, each table is rows/cells)
