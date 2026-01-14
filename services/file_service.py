import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db
from core.models import FileStorage, Tenant
from services.s3_service import S3Service
from flask_login import current_user

class FileService:
    @staticmethod
    def upload_file(file_obj, module, tenant_id, company_id=None, employee_id=None, file_category=None, resize_to=None):
        """
        Uploads a file to S3 and records it in the database.
        Path Structure:
          - Global: tenants/{tenant_id}/global/{category}/{filename}
          - Company: tenants/{tenant_id}/companies/{company_id}/{category}/{filename}
          - Employee: tenants/{tenant_id}/companies/{company_id}/employees/{employee_id}/{category}/{filename}
        
        :param resize_to: Optional tuple (width, height) to resize image before upload.
        """
        try:
            # 1. Prepare Filename
            original_filename = secure_filename(file_obj.filename)
            file_ext = os.path.splitext(original_filename)[1].lower()
            storage_filename = f"{secrets.token_hex(8)}_{original_filename}"
            
            # 1.5 Handle Image Resizing if requested
            if resize_to and file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    from PIL import Image
                    from io import BytesIO
                    
                    # Read image from file_obj
                    img = Image.open(file_obj)
                    
                    # Convert to RGB if necessary (e.g. RGBA to JPEG)
                    if img.mode in ("RGBA", "P"):
                         img = img.convert("RGB")
                    
                    # Resize (thumbnail maintains aspect ratio)
                    img.thumbnail(resize_to, Image.Resampling.LANCZOS)
                    
                    # Save to BytesIO
                    output = BytesIO()
                    # Determine format from extension or default to JPEG
                    save_format = 'JPEG' if file_ext in ['.jpg', '.jpeg'] else 'PNG'
                    if file_ext == '.webp': save_format = 'WEBP'
                    
                    img.save(output, format=save_format, quality=85)
                    output.seek(0)
                    
                    # Replace file_obj with the resized stream
                    file_obj = output
                    # Update content type checks/metadata if needed? 
                    # Usually S3 checks content type passed in arg, so we should update that too if we changed format, but here we keep format roughly same.
                    # But if we want to be safe, we can just treat it as binary stream now.
                except Exception as img_err:
                    # print(f"Warning: Image resizing failed: {img_err}")
                    # Fallback to original file_obj if resize fails
                    file_obj.seek(0)

            # 2. Construct Path
            path_parts = ["tenants", str(tenant_id)]
            
            if employee_id and company_id:
                path_parts.extend(["companies", str(company_id), "employees", str(employee_id)])
                if file_category:
                    path_parts.append(file_category)
            elif company_id:
                path_parts.extend(["companies", str(company_id)])
                if file_category:
                    path_parts.append(file_category)
            else:
                # Global / Tenant Level
                path_parts.append("global")
                if file_category:
                    path_parts.append(file_category)
            
            path_parts.append(storage_filename)
            s3_key = "/".join(path_parts)
            
            # 2. Upload to S3
            s3_service = S3Service()
            # Note: content_type might reference original file object props which is fine for stream wrapped files often
            # If file_obj is BytesIO, it might not have content_type attr.
            content_type = getattr(file_obj, 'content_type', 'application/octet-stream')
            if hasattr(file_obj, 'mimetype'): content_type = file_obj.mimetype # Check for werkzeug FileStorage prop
            
            if not s3_service.upload_file(file_obj, s3_key, content_type=content_type):
                return None
                
            # 3. Create Database Record
            # Calculate size
            file_size = 0
            try:
                file_obj.seek(0, os.SEEK_END)
                file_size = file_obj.tell()
                file_obj.seek(0)
            except:
                pass

            file_record = FileStorage(
                tenant_id=tenant_id,
                module=module,
                original_filename=original_filename,
                storage_filename=storage_filename,
                file_path=s3_key,
                file_size=file_size,
                mime_type=content_type,
                extension=file_ext,
                storage_provider='S3',
                uploaded_by=current_user.id if current_user and current_user.is_authenticated else None
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            return file_record
            
        except Exception as e:
            print(f"Error in FileService.upload_file: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_file_url(file_id):
        """Generates a presigned URL for a file"""
        file_record = FileStorage.query.get(file_id)
        if not file_record:
            return None
            
        s3_service = S3Service()
        return s3_service.generate_presigned_url(file_record.file_path)

    @staticmethod
    def delete_file(file_id):
        """Deletes file from S3 and DB"""
        file_record = FileStorage.query.get(file_id)
        if not file_record:
            return False
            
        try:
            # Delete from S3
            s3_service = S3Service()
            s3_service.delete_file(file_record.file_path)
            
            # Delete from DB
            db.session.delete(file_record)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            db.session.rollback()
            return False
