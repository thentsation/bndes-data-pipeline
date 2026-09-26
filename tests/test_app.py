import json
from unittest.mock import patch

import pandas as pd
import pytest

# 1. Mock boto3 BEFORE importing app to prevent real client creation
with patch("boto3.client") as mock_boto:
    from src.app import lambda_handler, save_data


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("LOCAL_OUTPUT_DIR", "/tmp")


@patch("src.app.fetch_resources_by_year")
@patch("src.app.process_data")
def test_lambda_handler_success(mock_process, mock_fetch, mock_env_vars):
    """Test successful execution of lambda handler."""

    # Mock s3_client usage inside handler.
    # Note: Since we mocked boto3.client at import, src.app.s3_client is already a mock.
    # We don't need to patch 'src.app.s3_client' again, but we can access it via the module if needed
    # or just trust the logic flow. Here we focus on the return value.

    # Mock data fetch
    mock_df = pd.DataFrame({"col": [1, 2]})
    mock_fetch.return_value = [("Resource 2023", mock_df)]

    # Mock process
    mock_process.return_value = mock_df

    # Event with year
    event = {"year": 2023}

    # We also need to patch save_data inside app because it uses s3_client
    # Or we can let it run since s3_client is mocked.
    # Let's mock s3_client.put_object to ensure no errors.

    # Access the mocked s3_client instance
    from src.app import s3_client

    s3_client.put_object.return_value = {}

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "Consolidated data for 2023 saved" in body["message"]
    assert body["records_processed"] == 2


@patch("src.app.fetch_resources_by_year")
def test_lambda_handler_no_data(mock_fetch, mock_env_vars):
    mock_fetch.return_value = []
    event = {"year": 2023}
    response = lambda_handler(event, None)
    assert response["statusCode"] == 404


def test_lambda_handler_missing_year(mock_env_vars):
    event = {}
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400


def test_lambda_handler_year_from_body(monkeypatch, mock_env_vars):
    with patch("src.app.fetch_resources_by_year", return_value=[]):
        response = lambda_handler({"body": json.dumps({"year": 2023})}, None)
    assert response["statusCode"] == 404


def test_lambda_handler_malformed_body_falls_through_to_missing_year(mock_env_vars):
    response = lambda_handler({"body": "not-json"}, None)
    assert response["statusCode"] == 400


def test_lambda_handler_missing_storage_config(monkeypatch):
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
    monkeypatch.delenv("LOCAL_OUTPUT_DIR", raising=False)
    response = lambda_handler({"year": 2023}, None)
    assert response["statusCode"] == 500


@patch("src.app.fetch_resources_by_year")
def test_lambda_handler_critical_error_is_caught(mock_fetch, mock_env_vars):
    mock_fetch.side_effect = RuntimeError("boom")
    response = lambda_handler({"year": 2023}, None)
    assert response["statusCode"] == 500
    assert "boom" in response["body"]


def test_save_data_writes_to_local_filesystem(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCAL_OUTPUT_DIR", str(tmp_path))
    df = pd.DataFrame({"col": [1, 2]})

    path = save_data(df, bucket_name=None, year=2023)

    assert path.startswith(str(tmp_path))
    assert path.endswith(".parquet")


def test_save_data_uploads_to_s3(monkeypatch):
    monkeypatch.delenv("LOCAL_OUTPUT_DIR", raising=False)
    df = pd.DataFrame({"col": [1, 2]})

    from src.app import s3_client

    s3_client.put_object.return_value = {}
    key = save_data(df, bucket_name="test-bucket", year=2023)

    assert key.startswith("bndes-data/")
    s3_client.put_object.assert_called_once()


def test_save_data_reraises_s3_errors(monkeypatch):
    monkeypatch.delenv("LOCAL_OUTPUT_DIR", raising=False)
    df = pd.DataFrame({"col": [1, 2]})

    from src.app import s3_client

    s3_client.put_object.side_effect = RuntimeError("s3 down")

    with pytest.raises(RuntimeError, match="s3 down"):
        save_data(df, bucket_name="test-bucket", year=2023)


def test_save_data_without_bucket_or_local_dir_raises(monkeypatch):
    monkeypatch.delenv("LOCAL_OUTPUT_DIR", raising=False)
    df = pd.DataFrame({"col": [1, 2]})

    with pytest.raises(ValueError, match="bucket_name is required"):
        save_data(df, bucket_name=None, year=2023)
