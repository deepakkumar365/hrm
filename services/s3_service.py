
import boto3
from botocore.exceptions import ClientError
import os
import logging
from flask import current_app

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION')
        )
        self.bucket_name = os.environ.get('AWS_S3_BUCKET_NAME')

    @classmethod
    def get_instance(cls):
        """Helper to get an instance (could be singleton if needed)"""
        return cls()

    def upload_file(self, file_obj, object_name, content_type=None):
        """
        Upload a file to an S3 bucket
        :param file_obj: File-like object to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :param content_type: MIME type of the file
        :return: True if file was uploaded, else False
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            logging.error(f"S3 Upload Error: {e}")
            return False

    def delete_file(self, object_name):
        """
        Delete a file from an S3 bucket
        :param object_name: S3 object name to delete
        :return: True if file was deleted, else False
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True
        except ClientError as e:
            logging.error(f"S3 Delete Error: {e}")
            return False

    def generate_presigned_url(self, object_name, expiration=3600):
        """
        Generate a presigned URL to share an S3 object
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logging.error(f"S3 Presigned URL Error: {e}")
            return None
