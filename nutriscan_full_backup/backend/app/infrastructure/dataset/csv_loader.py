from __future__ import annotations

import csv
import gzip
from collections.abc import Iterator
from pathlib import Path
from typing import TextIO


class DatasetLoader:
    """
    Streams rows from a CSV file without loading the whole file into memory.
    Reusable across any dataset (Open Food Facts, USDA, or future sources) -
    doesn't assume a particular schema, just yields dict rows and batches.
    Safe to instantiate even if the file doesn't exist yet; existence is
    only checked when iteration actually starts.
    """

    def __init__(self, file_path: str | Path, encoding: str = "utf-8", delimiter: str | None = None) -> None:
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.delimiter = delimiter

    def exists(self) -> bool:
        return self.file_path.is_file()

    def _open_text(self) -> TextIO:
        """Open plain CSV and gzip-compressed CSV exports without extracting them."""
        if self.file_path.suffix.lower() == ".gz":
            return gzip.open(self.file_path, "rt", encoding=self.encoding, newline="")
        return self.file_path.open("r", encoding=self.encoding, newline="")

    def _dialect(self, fh: TextIO) -> csv.Dialect:
        if self.delimiter:
            return csv.excel_tab if self.delimiter == "\t" else csv.excel
        sample = fh.read(8192)
        fh.seek(0)
        try:
            return csv.Sniffer().sniff(sample, delimiters=",\t")
        except csv.Error:
            return csv.excel_tab if "\t" in sample else csv.excel

    def stream_rows(self, skip_rows: int = 0) -> Iterator[dict[str, str]]:
        if not self.exists():
            raise FileNotFoundError(f"Dataset file not found: {self.file_path}")

        with self._open_text() as fh:
            reader = csv.DictReader(fh, dialect=self._dialect(fh))
            for i, row in enumerate(reader):
                if i < skip_rows:
                    continue
                yield row

    def stream_batches(self, batch_size: int = 500, skip_rows: int = 0) -> Iterator[list[dict[str, str]]]:
        batch: list[dict[str, str]] = []
        for row in self.stream_rows(skip_rows=skip_rows):
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def count_rows(self) -> int:
        """Full pass just to count - O(n) but still streaming, no full-file buffering."""
        if not self.exists():
            return 0
        with self._open_text() as fh:
            reader = csv.reader(fh, dialect=self._dialect(fh))
            next(reader, None)  # header
            return sum(1 for _ in reader)
