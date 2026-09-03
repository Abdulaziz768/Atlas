import json
import boto3

class S3Storage:
    """Handle storage operations in amazon s3"""

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = boto3.client("s3")

    def upload_json(self, data: dict, key: str) -> None:
        """Upload a JSON object to s3"""
        self.client.put_object(
            Bucket = self.bucket_name,
            Key = key,
            Body = json.dumps(data, indent=2),
            ContentType = "application/json",
        )