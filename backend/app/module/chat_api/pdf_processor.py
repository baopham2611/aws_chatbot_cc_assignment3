# ./backend/app/pdf_processor.py
import boto3
import fitz  # PyMuPDF

s3 = boto3.client('s3')

def download_pdf_from_s3(bucket_name, pdf_key):
    """Download a PDF from S3 and return it as bytes."""
    response = s3.get_object(Bucket=bucket_name, Key=pdf_key)
    pdf_data = response['Body'].read()
    return pdf_data

def extract_text_from_pdf(pdf_data):
    """Extract text from a PDF stored as bytes using PyMuPDF."""
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def get_pdf_text_from_s3(bucket_name, pdf_key):
    """Download PDF from S3 and extract its text."""
    pdf_data = download_pdf_from_s3(bucket_name, pdf_key)
    pdf_text = extract_text_from_pdf(pdf_data)
    return pdf_text
