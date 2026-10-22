from __future__ import annotations

import gzip

from app.infrastructure.dataset.csv_loader import DatasetLoader

CSV_CONTENT = "code,product_name,brands\n1001,Sugar Cookies,BrandA\n1002,Salt Chips,BrandB\n1003,Rice Cakes,BrandC\n"


def _write_csv(tmp_path, content: str = CSV_CONTENT):
    p = tmp_path / "sample.csv"
    p.write_text(content)
    return p


class TestDatasetLoader:
    def test_exists_false_for_missing_file(self, tmp_path) -> None:
        loader = DatasetLoader(tmp_path / "missing.csv")
        assert loader.exists() is False

    def test_stream_rows_missing_file_raises(self, tmp_path) -> None:
        loader = DatasetLoader(tmp_path / "missing.csv")
        try:
            list(loader.stream_rows())
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_stream_rows_yields_dicts(self, tmp_path) -> None:
        loader = DatasetLoader(_write_csv(tmp_path))
        rows = list(loader.stream_rows())
        assert len(rows) == 3
        assert rows[0]["product_name"] == "Sugar Cookies"

    def test_stream_batches_respects_batch_size(self, tmp_path) -> None:
        loader = DatasetLoader(_write_csv(tmp_path))
        batches = list(loader.stream_batches(batch_size=2))
        assert len(batches) == 2
        assert len(batches[0]) == 2
        assert len(batches[1]) == 1

    def test_skip_rows_for_resume(self, tmp_path) -> None:
        loader = DatasetLoader(_write_csv(tmp_path))
        rows = list(loader.stream_rows(skip_rows=1))
        assert len(rows) == 2
        assert rows[0]["product_name"] == "Salt Chips"

    def test_count_rows(self, tmp_path) -> None:
        loader = DatasetLoader(_write_csv(tmp_path))
        assert loader.count_rows() == 3

    def test_count_rows_missing_file_returns_zero(self, tmp_path) -> None:
        loader = DatasetLoader(tmp_path / "missing.csv")
        assert loader.count_rows() == 0

    def test_stream_rows_reads_gzip_and_detects_tab_delimiter(self, tmp_path) -> None:
        path = tmp_path / "openfoodfacts.csv.gz"
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            fh.write("code\tproduct_name\n1001\tSugar Cookies\n")

        rows = list(DatasetLoader(path).stream_rows())
        assert rows == [{"code": "1001", "product_name": "Sugar Cookies"}]
