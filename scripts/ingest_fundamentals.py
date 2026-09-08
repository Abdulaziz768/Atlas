from atlas.storage.s3 import S3Storage
from atlas.storage.paths import S3PathBuilder
from atlas.pipelines.fundamentals import FundamentalsPipeline
from atlas.transformation.fundamentals import FundamentalsTransformer
from atlas.quality.fundamentals import FundamentalsQualityChecker
from atlas.quality.processor import QualityProcessor


BUCKET_NAME = "atlas-raw-data-6304"


def main():
    storage = S3Storage(BUCKET_NAME)
    paths = S3PathBuilder()

    pipeline = FundamentalsPipeline(
        transformer=FundamentalsTransformer(
            as_of_date=paths.processing_date
        ),
        quality_processor=QualityProcessor(
            FundamentalsQualityChecker()
        ),
        storage=storage,
        paths=paths,
    )

    raw_key = paths.company_raw("AAPL")

    pipeline.process_from_s3(raw_key)

    print("AAPL fundamentals processing completed successfully")


if __name__ == "__main__":
    main()