import csv
import io
import math
from typing import Any


class CsvAnalysisError(ValueError):
    """Raised when an uploaded CSV cannot be analyzed safely."""


def analyze_csv(content: bytes) -> dict[str, Any]:
    if not content.strip():
        raise CsvAnalysisError("The CSV file is empty.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise CsvAnalysisError("The CSV file must use UTF-8 encoding.") from error

    try:
        reader = csv.DictReader(io.StringIO(text), strict=True)
        headers = reader.fieldnames
        if not headers or any(not header.strip() for header in headers):
            raise CsvAnalysisError("The CSV file must include a non-empty header row.")
        if len(set(headers)) != len(headers):
            raise CsvAnalysisError("The CSV file cannot contain duplicate column names.")

        total_records = 0
        missing_values = 0
        numeric_values: dict[str, list[float]] = {header: [] for header in headers}
        non_numeric_values: dict[str, bool] = {header: False for header in headers}

        for row in reader:
            if None in row:
                raise CsvAnalysisError("A row contains more values than the header.")
            total_records += 1
            for header in headers:
                value = (row.get(header) or "").strip()
                if not value:
                    missing_values += 1
                    continue
                try:
                    number = float(value)
                except ValueError:
                    non_numeric_values[header] = True
                else:
                    if math.isfinite(number):
                        numeric_values[header].append(number)
                    else:
                        non_numeric_values[header] = True
    except csv.Error as error:
        raise CsvAnalysisError("The CSV file contains malformed quoting or delimiters.") from error

    if total_records == 0:
        raise CsvAnalysisError("The CSV file must contain at least one data row.")

    numeric_columns = {
        header: {
            "minimum": min(values),
            "maximum": max(values),
        }
        for header, values in numeric_values.items()
        if values and not non_numeric_values[header]
    }

    return {
        "filename": "uploaded.csv",
        "total_records": total_records,
        "column_count": len(headers),
        "columns": headers,
        "missing_values": missing_values,
        "numeric_columns": numeric_columns,
    }
