"""AWS S3 client utilities"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import structlog

logger = structlog.get_logger()

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
) if settings.AWS_ACCESS_KEY_ID else None


def upload_file(file_content: bytes, s3_key: str, content_type: str = None) -> bool:
    """Upload file to S3"""
    if not s3_client:
        logger.warning("S3 client not configured")
        return False
    
    try:
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            **extra_args
        )
        return True
    except ClientError as e:
        logger.error("S3 upload error", error=str(e))
        return False


def delete_file(s3_key: str) -> bool:
    """Delete file from S3"""
    if not s3_client:
        return False
    
    try:
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        return True
    except ClientError as e:
        logger.error("S3 delete error", error=str(e))
        return False


def generate_presigned_url(s3_key: str, expiration: int = None) -> str:
    """Generate presigned URL for file access"""
    if not s3_client:
        return ""
    
    expiration = expiration or settings.S3_PRESIGNED_URL_EXPIRATION
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error("S3 presigned URL error", error=str(e))
        return ""
