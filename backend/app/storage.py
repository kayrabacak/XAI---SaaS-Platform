import boto3
import os
from botocore.exceptions import NoCredentialsError

# MinIO Bağlantı Ayarları
MINIO_URL = os.environ.get("MINIO_URL", "http://minio:9000")
ACCESS_KEY = os.environ.get("MINIO_ROOT_USER", "minioadmin")
SECRET_KEY = os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET_NAME = "xai-models"

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=MINIO_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

def init_bucket():
    """Bucket yoksa oluşturur"""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' oluşturuldu.")

def upload_file(file_obj, object_name):
    """Dosyayı MinIO'ya yükler"""
    s3 = get_s3_client()
    try:
        # Dosya imlecini başa al
        file_obj.seek(0)
        s3.upload_fileobj(file_obj, BUCKET_NAME, object_name)
        return f"{BUCKET_NAME}/{object_name}"
    except Exception as e:
        print(f"Yükleme Hatası: {e}")
        return None


def download_file(object_name, local_path):
    """MinIO'dan dosyayı yerele indirir"""
    s3 = get_s3_client()
    try:
        # Klasör yoksa oluştur
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(BUCKET_NAME, object_name, local_path)
        return True
    except Exception as e:
        print(f"İndirme Hatası: {e}")
        return False
