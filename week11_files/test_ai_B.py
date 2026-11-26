import csv
import math
from pathlib import Path

import pytest


def load_scores(path):
    """CSV 파일의 이름과 점수를 읽어 dict로 반환한다."""
    csv_path = Path(path)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV에 헤더가 없습니다")

        fieldnames = [name.strip() for name in reader.fieldnames]
        if "name" not in fieldnames or "score" not in fieldnames:
            raise ValueError("CSV 헤더에는 name과 score가 필요합니다")

        name_index = fieldnames.index("name")
        score_index = fieldnames.index("score")
        original_names = reader.fieldnames

        scores = {}
        for line_number, row in enumerate(reader, start=2):
            name = (row.get(original_names[name_index]) or "").strip()
            raw_score = (row.get(original_names[score_index]) or "").strip()

            if not name:
                raise ValueError(f"{line_number}번 줄의 이름이 비어 있습니다")
            if not raw_score:
                raise ValueError(f"{line_number}번 줄의 점수가 비어 있습니다")

            try:
                score = float(raw_score)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{line_number}번 줄의 점수가 숫자가 아닙니다") from exc

            if not math.isfinite(score) or not 0 <= score <= 100:
                raise ValueError(f"{line_number}번 줄의 점수는 0~100 범위여야 합니다")
            if name in scores:
                raise ValueError(f"중복된 이름입니다: {name}")

            scores[name] = score

        return scores


def test_load_scores_normal(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text("name,score\nAlice,87\nBob,64.5\n", encoding="utf-8")

    assert load_scores(csv_file) == {"Alice": 87.0, "Bob": 64.5}


def test_load_scores_boundary_zero_and_hundred(tmp_path):
    csv_file = tmp_path / "boundaries.csv"
    csv_file.write_text("name,score\nZero,0\nFull,100\n", encoding="utf-8")

    assert load_scores(csv_file) == {"Zero": 0.0, "Full": 100.0}


@pytest.mark.parametrize("bad_score", ["-1", "101", "abc", "NaN", "inf"])
def test_load_scores_invalid_score(tmp_path, bad_score):
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(f"name,score\nAlice,{bad_score}\n", encoding="utf-8")

    if bad_score in ("-1", "101"):
        with pytest.raises(ValueError, match="0~100"):
            load_scores(csv_file)
    elif bad_score in ("NaN", "inf"):
        with pytest.raises(ValueError, match="0~100"):
            load_scores(csv_file)
    else:
        with pytest.raises(ValueError, match="숫자가 아닙니다"):
            load_scores(csv_file)


@pytest.mark.parametrize("csv_text, message", [
    ("name,score\n,50\n", "이름이 비어"),
    ("name,score\nAlice,\n", "점수가 비어"),
])
def test_load_scores_missing_required_value(tmp_path, csv_text, message):
    csv_file = tmp_path / "missing.csv"
    csv_file.write_text(csv_text, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_scores(csv_file)


def test_load_scores_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_scores(tmp_path / "not-found.csv")


def test_load_scores_missing_headers(tmp_path):
    csv_file = tmp_path / "bad-header.csv"
    csv_file.write_text("student,points\nAlice,80\n", encoding="utf-8")

    with pytest.raises(ValueError, match="name과 score"):
        load_scores(csv_file)


def test_load_scores_duplicate_name(tmp_path):
    csv_file = tmp_path / "duplicate.csv"
    csv_file.write_text("name,score\nAlice,80\nAlice,90\n", encoding="utf-8")

    with pytest.raises(ValueError, match="중복된 이름"):
        load_scores(csv_file)
