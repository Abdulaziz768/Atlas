from atlas.storage.s3 import S3Storage

def test_upload_json():
    storage = S3Storage("atlas-raw-data-6304")

    data = {
        "ticker" : "AAPL",
        "source" : "test",
        "message" : "Atlas s3 test",
    }

    storage.upload_json(
        data=data,
        key="raw/test/AAPL.json"
    )