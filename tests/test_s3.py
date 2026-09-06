from atlas.storage.s3 import S3Storage
import json
import io

class FakeS3Client:

    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.objects[Key] = {
            "Body": Body,
            "ContentType": ContentType,
        }

    def get_object(self, Bucket, Key):
        return {
            "Body": io.BytesIO(
                self.objects[Key]["Body"].encode("utf-8")
            )
        }


def test_upload_csv():
    client = FakeS3Client()
    storage = S3Storage("atlas-bucket")
    storage.client = client

    data = [
        {
            "ticker": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "close": "243.10",
        },
        {
            "ticker": "AAPL",
            "date": "2026-09-04",
            "open": "239.10",
            "close": "240.20",
        },
    ]

    storage.upload_csv(
        data=data,
        key="raw/stock_price/2026-09-05/AAPL.csv",
    )

    uploaded = client.objects["raw/stock_price/2026-09-05/AAPL.csv"]

    assert uploaded["ContentType"] == "text/csv"
    assert uploaded["Body"] == (
        "ticker,date,open,close\r\n"
        "AAPL,2026-09-05,240.50,243.10\r\n"
        "AAPL,2026-09-04,239.10,240.20\r\n"
    )


def test_read_csv():
    client = FakeS3Client()
    storage = S3Storage("atlas-bucket")
    storage.client = client

    client.objects["raw/stock_price/AAPL.csv"] = {
        "Body": (
            "ticker,date,open,close\r\n"
            "AAPL,2026-09-05,240.50,243.10\r\n"
            "AAPL,2026-09-04,239.10,240.20\r\n"
        ),
        "ContentType": "text/csv",
    }

    records = storage.read_csv("raw/stock_price/AAPL.csv")

    assert records == [
        {
            "ticker": "AAPL",
            "date": "2026-09-05",
            "open": "240.50",
            "close": "243.10",
        },
        {
            "ticker": "AAPL",
            "date": "2026-09-04",
            "open": "239.10",
            "close": "240.20",
        },
    ]

def test_upload_json():
    client = FakeS3Client()
    storage = S3Storage("atlas-bucket")
    storage.client = client

    data = {
        "ticker": "AAPL",
        "source": "test",
        "message": "Atlas s3 test",
    }

    storage.upload_json(
        data=data,
        key="raw/test/AAPL.json",
    )

    uploaded = client.objects["raw/test/AAPL.json"]

    assert uploaded["ContentType"] == "application/json"
    assert json.loads(uploaded["Body"]) == data
    
def test_read_json():
    client = FakeS3Client()
    storage = S3Storage("atlas-bucket")
    storage.client = client

    data = {
        "ticker": "AAPL",
        "source": "test",
        "message": "Atlas s3 test",
    }

    client.objects["raw/test/AAPL.json"] = {
        "Body": json.dumps(data),
        "ContentType": "application/json",
    }

    result = storage.read_json("raw/test/AAPL.json")

    assert result == data