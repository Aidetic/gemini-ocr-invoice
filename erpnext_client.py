import os
import requests
import json
from pprint import pprint

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


def create_invoice_ocr_record(file_url, invoice_number):
    """
    Pushes OCR data to ERPNext from an external script.
    """
    
    # 1. Prepare the Endpoint URL
    # If using the standard Resource API:
    endpoint = f"{ERP_URL}/api/resource/Invoice OCR Record"
    
    # 3. Prepare Payload
    # ERPNext Resource API expects the data inside a 'data' key or as direct keys
    payload = {
        "invoice_number": invoice_number,
        "file_url": file_url
    }
    
    # 4. Make the POST request
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
        
        # Check for success
        if response.status_code == 200:
            print("Successfully created record!")
            return response.json().get("data")
        else:
            print(f"Failed! Status Code: {response.status_code}")
            print(f"Error Message: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return None


def extract_invoice_number(ocr_entities):
    for entity in ocr_entities:
        if entity.get("entity_type") == "invoice_number":
            table_data = entity.get("table_data", [])
            if table_data and isinstance(table_data, list):
                return table_data[0].get("invoice_number")
    return None