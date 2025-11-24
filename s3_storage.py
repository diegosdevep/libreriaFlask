import boto3
from botocore.exceptions import ClientError
from config import Config
from datetime import datetime
from werkzeug.utils import secure_filename
import os

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_S3_REGION
    )


def subir_a_s3(archivo, user_id):
    if not archivo or not archivo.filename:
        return None
    
    s3_client = get_s3_client()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(archivo.filename)
    nombre_base, extension = os.path.splitext(filename)
    key = f"manuscritos/{user_id}_{timestamp}_{nombre_base}{extension}"
    
    try:
        s3_client.upload_fileobj(
            archivo,
            Config.AWS_S3_BUCKET,
            key,
            ExtraArgs={
                'ContentType': archivo.content_type,
                'ServerSideEncryption': 'AES256'
            }
        )
        
        url = f"https://{Config.AWS_S3_BUCKET}.s3.{Config.AWS_S3_REGION}.amazonaws.com/{key}"
        return url
        
    except ClientError as e:
        raise ValueError("Error al subir el archivo a S3")


def eliminar_de_s3(url):
    if not url or not url.startswith('https://'):
        return False
    
    try:
        parts = url.split('.amazonaws.com/')
        if len(parts) != 2:
            return False
        
        key = parts[1]
        
        s3_client = get_s3_client()
        s3_client.delete_object(
            Bucket=Config.AWS_S3_BUCKET,
            Key=key
        )
        
        return True
        
    except ClientError:
        return False


def generar_url_descarga(url, expiracion=3600):
    if not url or not url.startswith('https://'):
        return url
    
    try:
        parts = url.split('.amazonaws.com/')
        if len(parts) != 2:
            return url
        
        key = parts[1]
        
        s3_client = get_s3_client()
        url_firmada = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': Config.AWS_S3_BUCKET,
                'Key': key
            },
            ExpiresIn=expiracion
        )
        
        return url_firmada
        
    except ClientError:
        return url