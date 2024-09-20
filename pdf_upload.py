import boto3
import os
from io import BytesIO
import uuid  # Import UUID library to generate unique IDs

def initialize_aws_services():
    """Initialize and return AWS DynamoDB and S3 clients."""
    s3 = boto3.client('s3')
    return s3

def upload_pdf_to_s3(s3, bucket_name, file_name, file_path):
    """Upload a PDF to an S3 bucket into a specified folder."""
    folder_path = f"techcombank_pdfs/{file_name}"
    try:
        with open(file_path, 'rb') as pdf_data:
            s3.upload_fileobj(
                pdf_data,
                bucket_name,
                folder_path,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'ACL': 'public-read'
                }
            )
        print(f"Uploaded {file_name} to S3 bucket {bucket_name} in folder techcombank_pdfs")
    except boto3.exceptions.S3UploadFailedError as e:
        print(f"Failed to upload {file_name} to S3: {e}")

def process_pdfs(s3, bucket_name, pdf_folder):
    """Process PDFs from the local folder and upload them to S3."""
    for file_name in os.listdir(pdf_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, file_name)
            upload_pdf_to_s3(s3, bucket_name, file_name, file_path)

def main():
    """Main function to orchestrate the AWS operations."""
    s3 = initialize_aws_services()

    # S3 PDF uploading
    bucket_name = 'aws-cloud-computing'  # Replace with your actual S3 bucket name
    pdf_folder = 'techcombank_pdf_file'  # Local folder where your PDFs are stored
    process_pdfs(s3, bucket_name, pdf_folder)

if __name__ == "__main__":
    main()
