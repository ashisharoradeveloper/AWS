import pytest

from app.csv_analysis import CsvAnalysisError, analyze_csv


def test_analyze_csv_returns_counts_and_numeric_ranges() -> None:
    content = b"name,price\nWidget,10.5\n,\n"

    result = analyze_csv(content)

    assert result["total_records"] == 2
    assert result["column_count"] == 2
    assert result["missing_values"] == 2
    assert result["numeric_columns"] == {"price": {"minimum": 10.5, "maximum": 10.5}}


def test_analyze_csv_rejects_empty_files() -> None:
    with pytest.raises(CsvAnalysisError, match="empty"):
        analyze_csv(b"  \n")


def test_analyze_csv_rejects_malformed_csv() -> None:
    with pytest.raises(CsvAnalysisError, match="malformed"):
        analyze_csv(b"name,price\n\"Widget,10\n")


def test_analyze_csv_rejects_empty_data_sets() -> None:
    with pytest.raises(CsvAnalysisError, match="at least one"):
        analyze_csv(b"name,price\n")
