import json
import os
from datetime import UTC, datetime
from typing import Any

import boto3
import pandas as pd

try:
    from src.fetch_data import fetch_resources_by_year
    from src.process_data import process_data
except ImportError:  # pragma: no cover - only hit inside the Lambda container
    from fetch_data import fetch_resources_by_year  # type: ignore[no-redef]
    from process_data import process_data  # type: ignore[no-redef]

s3_client = boto3.client("s3")


def save_data(
    df: pd.DataFrame, bucket_name: str | None, year: int, prefix: str = "bndes-data"
) -> str:
    local_output_dir = os.environ.get("LOCAL_OUTPUT_DIR")

    date_str = datetime.now(UTC).strftime("%Y/%m/%d")
    filename = f"balanco_patrimonial_{year}_consolidado.parquet"
    key = f"{prefix}/{date_str}/{filename}"

    if local_output_dir:
        full_path = os.path.join(local_output_dir, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        df.to_parquet(full_path, index=False, compression="snappy")
        print(f"Saved: {full_path}")
        return full_path

    if not bucket_name:
        raise ValueError("bucket_name is required when LOCAL_OUTPUT_DIR is not set")

    try:
        parquet_buffer = df.to_parquet(index=False, compression="snappy")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=parquet_buffer,
            ContentType="application/octet-stream",
        )
        print(f"Saved to S3: s3://{bucket_name}/{key}")
        return key
    except Exception as e:
        print(f"Error saving to S3: {e}")
        raise


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    local_output_dir = os.environ.get("LOCAL_OUTPUT_DIR")

    if not bucket_name and not local_output_dir:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": "Neither S3_BUCKET_NAME nor LOCAL_OUTPUT_DIR environment variables are set"
                }
            ),
        }

    year = event.get("year")
    if not year and "body" in event:
        try:
            body = json.loads(event["body"])
            year = body.get("year")
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

    if not year:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing required parameter: 'year'"}),
        }

    all_dfs = []

    try:
        print(f"Starting processing for year: {year}")

        for name, df in fetch_resources_by_year(year):
            if not df.empty:
                df = process_data(df)
                all_dfs.append(df)

        if not all_dfs:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"No data found for year {year}"}),
            }

        print(f"Consolidating {len(all_dfs)} files...")
        final_df = pd.concat(all_dfs, ignore_index=True)

        location = save_data(final_df, bucket_name, year)

        storage_type = "Local Filesystem" if local_output_dir else "S3"

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": f"Consolidated data for {year} saved to {storage_type}",
                    "records_processed": len(final_df),
                    "location": location,
                    "source_files_count": len(all_dfs),
                },
                ensure_ascii=False,
            ),
        }
    except Exception as e:
        print(f"Critical error in lambda_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Critical error: {e}"}),
        }
