# Gemini_Image_Analysis


# Step-1: Start ERP server
The docker file pwd.yml is for erp. 
-> docker compose -p pwd -f pwd.yml

# Step-2: Run OCR docker 
-> docker compose up -d --build

# Step-3: Open streamlit app and attach the invoice (sample invoice in sample_img folder). 

# Step-4: open the erpnext server (for me: http://localhost:8080/app/invoice-ocr-record/qh2dcksga6) for this i needed to create a doctype that will have invoice_id and json. 