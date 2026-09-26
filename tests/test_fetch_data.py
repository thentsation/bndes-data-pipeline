from unittest.mock import MagicMock, patch

from src.fetch_data import fetch_resources_by_year

# Mock data for package_show
MOCK_PACKAGE_SHOW = {
    "result": {
        "resources": [
            {
                "id": "res-1",
                "name": "Balanço 2023",
                "datastore_active": True,
                "url": "http://example.com/2023.csv",
                "format": "CSV",
            },
            {
                "id": "res-2",
                "name": "Balanço 2020",  # Wrong year
                "datastore_active": True,
                "url": "http://example.com/2020.csv",
                "format": "CSV",
            },
            {
                "id": "res-3",
                "name": "Balanço 2023 (PDF)",  # Not datastore active check logic
                "datastore_active": False,
                "url": "http://example.com/2023.pdf",
                "format": "PDF",
            },
        ]
    }
}

# Mock data for datastore_search
MOCK_DATASTORE_SEARCH = {
    "result": {"records": [{"id": 1, "col": "val1"}, {"id": 2, "col": "val2"}]}
}


@patch("src.fetch_data.requests.get")
def test_fetch_resources_by_year_success(mock_get):
    """Test fetching resources for a specific year successfully."""

    # Configure mock side effects for sequential calls
    # 1. package_show
    # 2. datastore_search (for the matching resource)
    mock_response_pkg = MagicMock()
    mock_response_pkg.json.return_value = MOCK_PACKAGE_SHOW
    mock_response_pkg.raise_for_status.return_value = None

    mock_response_ds = MagicMock()
    mock_response_ds.json.return_value = MOCK_DATASTORE_SEARCH
    mock_response_ds.raise_for_status.return_value = None

    # O mock vai retornar o pacote primeiro, depois o datastore
    mock_get.side_effect = [mock_response_pkg, mock_response_ds]

    # Run function
    generator = fetch_resources_by_year(2023)
    results = list(generator)

    # Assertions
    assert len(results) == 1
    name, df = results[0]

    assert name == "Balanço 2023"
    assert len(df) == 2
    assert "source_resource_name" in df.columns
    assert df.iloc[0]["col"] == "val1"


@patch("src.fetch_data.requests.get")
def test_fetch_resources_no_match(mock_get):
    """Test fetching when no resources match the year."""

    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_PACKAGE_SHOW
    mock_get.return_value = mock_response

    # Search for year that doesn't exist in mock
    generator = fetch_resources_by_year(2099)
    results = list(generator)

    assert len(results) == 0


@patch("src.fetch_data.requests.get")
def test_fetch_resources_matching_resource_with_no_records(mock_get):
    """Covers the branch where a matching resource's datastore has no records."""

    mock_response_pkg = MagicMock()
    mock_response_pkg.json.return_value = MOCK_PACKAGE_SHOW
    mock_response_pkg.raise_for_status.return_value = None

    mock_response_ds = MagicMock()
    mock_response_ds.json.return_value = {"result": {"records": []}}
    mock_response_ds.raise_for_status.return_value = None

    mock_get.side_effect = [mock_response_pkg, mock_response_ds]

    results = list(fetch_resources_by_year(2023))

    assert results == []
