import os
import requests
import json

ERP_URL = os.getenv("ERP_URL")
ERP_SITE = os.getenv("ERP_SITE")
ERP_API_KEY = os.getenv("ERP_API_KEY")
ERP_API_SECRET = os.getenv("ERP_API_SECRET")

HEADERS = {
    "Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}",
    "Host": ERP_SITE,
}

def upload_file_to_erpnext(
    file_path: str,
    filename: str,
    is_private: int = 1,
    doctype: str | None = None,
    docname: str | None = None,
):
    """
    Upload file to ERPNext using multipart/form-data
    """

    data = {
        "is_private": str(is_private),
    }

    if doctype and docname:
        data["doctype"] = doctype
        data["docname"] = docname

    with open(file_path, "rb") as f:
        files = {
            "file": (filename, f),
        }

        response = requests.post(
            f"{ERP_URL}/api/method/upload_file",
            headers=HEADERS,
            data=data,
            files=files,
        )

    response.raise_for_status()
    return response.json()["message"]


def create_invoice_ocr_record(
    file_url: str,
    ocr_raw: str,
    ocr_json: dict | None = None,
):
    payload = {
        "doctype": "Invoice OCR Record",
        "invoice_file": file_url,
        "ocr_raw": ocr_raw,
        "status": "Extracted",
        "source": "Streamlit OCR",
    }

    if ocr_json:
        payload["ocr_json"] = json.dumps(ocr_json, indent=2)

    response = requests.post(
        f"{ERP_URL}/api/resource/Invoice OCR Record",
        headers=HEADERS,
        json=payload,
    )

    response.raise_for_status()
    return response.json()["data"]

