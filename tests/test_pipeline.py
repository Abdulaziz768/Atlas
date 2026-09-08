from unittest.mock import Mock

from atlas.pipelines.company import CompanyPipeline
from atlas.quality.company import CompanyQualityChecker
from atlas.quality.processor import QualityProcessor
from atlas.storage.paths import S3PathBuilder
from atlas.transformation.company import CompanyTransformer

def create_company_data():
    return {
    "Symbol": "AAPL",
    "Name": "Apple Inc.",
    "Exchange": "NASDAQ",
    "Sector": "TECHNOLOGY",
    "Industry": "CONSUMER ELECTRONICS",
    "Currency": "USD",
    }

def create_pipeline(service, storage):
    return CompanyPipeline(
    service=service,
    transformer=CompanyTransformer(),
    quality_processor=QualityProcessor(
    CompanyQualityChecker()
    ),
    storage=storage,
    paths=S3PathBuilder(),
    )

def test_company_pipeline_ingests_and_processes_valid_company():
    service = Mock()
    service.get_company_data.return_value = create_company_data()

    storage = Mock()
    storage.read_json.return_value = create_company_data()

    pipeline = create_pipeline(service, storage)

    result = pipeline.ingest("AAPL")

    assert result.ticker == "AAPL"
    assert result.name == "Apple Inc."
    assert result.exchange == "NASDAQ"
    assert result.currency == "USD"
    assert result.sector == "TECHNOLOGY"
    assert result.industry == "CONSUMER ELECTRONICS"

    service.get_company_data.assert_called_once_with("AAPL")

    storage.upload_json.assert_any_call(
        data=create_company_data(),
        key=pipeline.paths.company_raw("AAPL"),
    )

def test_company_pipeline_quarantines_invalid_company():
    service = Mock()

    invalid_data = create_company_data()
    invalid_data["Name"] = ""

    service.get_company_data.return_value = invalid_data

    storage = Mock()
    storage.read_json.return_value = invalid_data

    pipeline = create_pipeline(service, storage)

    result = pipeline.ingest("AAPL")

    assert result is None

    storage.upload_json.assert_any_call(
        data=invalid_data,
        key=pipeline.paths.company_raw("AAPL"),
    )

    storage.upload_json.assert_any_call(
        data={
            "ticker": "AAPL",
            "errors": ["company name is missing"],
            "record": {
                "ticker": "AAPL",
                "name": "",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "TECHNOLOGY",
                "industry": "CONSUMER ELECTRONICS",
            },
        },
        key=pipeline.paths.company_quarantine("AAPL"),
    )

def test_company_pipeline_processes_existing_s3_data():
    storage = Mock()

    raw_data = create_company_data()
    storage.read_json.return_value = raw_data

    pipeline = create_pipeline(
        service=Mock(),
        storage=storage,
    )

    raw_key = pipeline.paths.company_raw("AAPL")

    result = pipeline.process_from_s3(raw_key)

    assert result.ticker == "AAPL"
    assert result.name == "Apple Inc."

    storage.read_json.assert_called_once_with(raw_key)

    storage.upload_json.assert_called_once_with(
        data={
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "sector": "TECHNOLOGY",
            "industry": "CONSUMER ELECTRONICS",
        },
        key=pipeline.paths.company_processed("AAPL"),
    )

def test_company_pipeline_quarantines_invalid_existing_s3_data():
    storage = Mock()

    raw_data = create_company_data()
    raw_data["Name"] = ""

    storage.read_json.return_value = raw_data

    pipeline = create_pipeline(
        service=Mock(),
        storage=storage,
    )

    raw_key = pipeline.paths.company_raw("AAPL")

    result = pipeline.process_from_s3(raw_key)

    assert result is None

    storage.read_json.assert_called_once_with(raw_key)

    storage.upload_json.assert_called_once_with(
        data={
            "ticker": "AAPL",
            "errors": ["company name is missing"],
            "record": {
                "ticker": "AAPL",
                "name": "",
                "exchange": "NASDAQ",
                "currency": "USD",
                "sector": "TECHNOLOGY",
                "industry": "CONSUMER ELECTRONICS",
            },
        },
        key=pipeline.paths.company_quarantine("AAPL"),
    )