import io
import json

from atlas.storage.s3 import S3Storage


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


def create_storage():
    client = FakeS3Client()
    storage = S3Storage("atlas-bucket")
    storage.client = client
    return storage, client


def test_upload_csv():
    storage, client = create_storage()

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

    key = "raw/stock_price/2026-09-05/AAPL.csv"

    storage.upload_csv(data=data, key=key)

    uploaded = client.objects[key]

    assert uploaded["ContentType"] == "text/csv"
    assert uploaded["Body"] == (
        "ticker,date,open,close\r\n"
        "AAPL,2026-09-05,240.50,243.10\r\n"
        "AAPL,2026-09-04,239.10,240.20\r\n"
    )


def test_read_csv():
    storage, client = create_storage()

    key = "raw/stock_price/AAPL.csv"

    client.objects[key] = {
        "Body": (
            "ticker,date,open,close\r\n"
            "AAPL,2026-09-05,240.50,243.10\r\n"
            "AAPL,2026-09-04,239.10,240.20\r\n"
        ),
        "ContentType": "text/csv",
    }

    records = storage.read_csv(key)

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
    storage, client = create_storage()

    data = {
        "ticker": "AAPL",
        "source": "test",
        "message": "Atlas s3 test",
    }

    key = "raw/test/AAPL.json"

    storage.upload_json(data=data, key=key)

    uploaded = client.objects[key]

    assert uploaded["ContentType"] == "application/json"
    assert json.loads(uploaded["Body"]) == data


def test_read_json():
    storage, client = create_storage()

    data = {
        "ticker": "AAPL",
        "source": "test",
        "message": "Atlas s3 test",
    }

    key = "raw/test/AAPL.json"

    client.objects[key] = {
        "Body": json.dumps(data),
        "ContentType": "application/json",
    }

    result = storage.read_json(key)

    assert result == data