import json
import boto3
import io
import csv

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

    def read_json(self, key: str) -> dict:
        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=key,
        )

        content = response['Body'].read().decode("utf-8")

        return json.loads(content)

    def upload_csv(self, data: list[dict], key: str) -> None:
        """Upload csv records to s3"""

        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=data[0].keys(),
        )

        writer.writeheader()
        writer.writerows(data)

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=output.getvalue(),
            ContentType="text/csv",
        )

    def read_csv(self, key: str) -> list[dict]:
        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=key
        )

        content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))

        return list(reader)
