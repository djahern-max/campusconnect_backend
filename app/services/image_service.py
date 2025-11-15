import boto3
from botocore.client import Config
from fastapi import UploadFile, HTTPException
import os
from pathlib import Path
from app.core.config import settings
import uuid

class ImageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.DIGITAL_OCEAN_SPACES_ENDPOINT,
            aws_access_key_id=settings.DIGITAL_OCEAN_SPACES_ACCESS_KEY,
            aws_secret_access_key=settings.DIGITAL_OCEAN_SPACES_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.DIGITAL_OCEAN_SPACES_REGION
        )
        self.bucket_name = settings.DIGITAL_OCEAN_SPACES_BUCKET
        self.cdn_base_url = settings.IMAGE_CDN_BASE_URL
    
    async def upload_to_spaces(self, file: UploadFile, folder_path: str = "campusconnect"):
        """Upload file to DigitalOcean Spaces"""
        try:
            # Validate file type
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            full_path = f"{folder_path}/{unique_filename}"
            
            # Read file content
            contents = await file.read()
            
            # Upload to Spaces
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_path,
                Body=contents,
                ACL='public-read',
                ContentType=file.content_type
            )
            
            # Generate URLs
            url = f"{settings.DIGITAL_OCEAN_SPACES_ENDPOINT.replace('https://', f'https://{self.bucket_name}.')}/{full_path}"
            cdn_url = f"{self.cdn_base_url}/{full_path}"
            
            return {
                "filename": unique_filename,
                "url": url,
                "cdn_url": cdn_url,
                "path": full_path
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    async def delete_from_spaces(self, file_path: str):
        """Delete file from DigitalOcean Spaces"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
    
    async def list_images(self, folder_path: str = "campusconnect"):
        """List all images in a folder"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder_path
            )
            
            images = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    images.append({
                        "filename": obj['Key'].split('/')[-1],
                        "path": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "url": f"{settings.DIGITAL_OCEAN_SPACES_ENDPOINT.replace('https://', f'https://{self.bucket_name}.')}/{obj['Key']}",
                        "cdn_url": f"{self.cdn_base_url}/{obj['Key']}"
                    })
            
            return images
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

# Singleton instance
image_service = ImageService()
