import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from app.core.config import settings
import os
from typing import Optional

class ImageService:
    def __init__(self):
        """Initialize DigitalOcean Spaces client"""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.DIGITAL_OCEAN_SPACES_REGION,
            endpoint_url=settings.DIGITAL_OCEAN_SPACES_ENDPOINT,
            aws_access_key_id=settings.DIGITAL_OCEAN_SPACES_ACCESS_KEY,
            aws_secret_access_key=settings.DIGITAL_OCEAN_SPACES_SECRET_KEY
        )
        self.bucket = settings.DIGITAL_OCEAN_SPACES_BUCKET
        self.cdn_base = settings.IMAGE_CDN_BASE_URL
    
    def upload_image(
        self, 
        file_content: bytes, 
        filename: str,
        content_type: str,
        folder: str = "campusconnect"
    ) -> dict:
        """
        Upload image to DigitalOcean Spaces
        
        Args:
            file_content: The image file bytes
            filename: The filename to save as
            content_type: MIME type (e.g., 'image/jpeg')
            folder: Folder in bucket (default: 'campusconnect')
        
        Returns:
            dict with 'url' and 'key'
        """
        try:
            # Full S3 key (path in bucket)
            s3_key = f"{folder}/{filename}"
            
            # Upload to Spaces
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read',  # Make publicly accessible
                CacheControl='max-age=31536000'  # Cache for 1 year
            )
            
            # Return CDN URL
            cdn_url = f"{self.cdn_base}/{s3_key}"
            
            return {
                "url": cdn_url,
                "key": s3_key,
                "bucket": self.bucket
            }
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    def delete_image(self, s3_key: str) -> bool:
        """
        Delete image from DigitalOcean Spaces
        
        Args:
            s3_key: The full S3 key (e.g., 'campusconnect/institution_1_image.jpg')
        
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image: {str(e)}"
            )
    
    def list_images(self, prefix: str = "campusconnect") -> list:
        """
        List images in a folder
        
        Args:
            prefix: Folder prefix (default: 'campusconnect')
        
        Returns:
            List of image objects with url, key, size, last_modified
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            images = []
            for obj in response['Contents']:
                images.append({
                    "key": obj['Key'],
                    "url": f"{self.cdn_base}/{obj['Key']}",
                    "size_bytes": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
            
            return images
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list images: {str(e)}"
            )

# Singleton instance
image_service = ImageService()
