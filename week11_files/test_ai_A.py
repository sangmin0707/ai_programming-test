import pytest

import test_ai_A


def write_csv(tmp_path, text):
    path = tmp_path / "scores.csv"
    path.write_text(text, encoding="utf-8-sig")
    return path


def test_load_scores_normal(tmp_path):
    path = write_csv(
        tmp_path,
        "name,score\n홍길동,90\nKim,75\n",
    )

    kept, skipped = test_ai_A.load_scores(path)

    assert kept == [("홍길동", 90), ("Kim", 75)]
    assert skipped == []


def test_load_scores_accepts_score_boundaries(tmp_path):
    path = write_csv(tmp_path, "name,score\nmin,0\nmax,100\n")

    kept, skipped = test_ai_A.load_scores(path)

    assert kept == [("min", 0), ("max", 100)]
    assert skipped == []


def test_load_scores_skips_invalid_rows(tmp_path):
    path = write_csv(
        tmp_path,
        "name,score\n"
        "only-one-column\n"
        "too,many,columns\n"
        ",50\n"
        "Alice,\n"
        "Bob,abc\n"
        "Low,-1\n"
        "High,101\n",
    )

    kept, skipped = test_ai_A.load_scores(path)

    assert kept == []
    assert skipped == [
        (2, "only-one-column", "열 개수가 2가 아님"),
        (3, "too,many,columns", "열 개수가 2가 아님"),
        (4, ",50", "이름이 비어 있음"),
        (5, "Alice,", "점수가 비어 있음"),
        (6, "Bob,abc", "점수가 정수가 아님"),
        (7, "Low,-1", "점수가 0~100 밖"),
        (8, "High,101", "점수가 0~100 밖"),
    ]


def test_load_scores_ignores_blank_lines(tmp_path):
    path = write_csv(tmp_path, "name,score\n\nAlice,80\n")

    kept, skipped = test_ai_A.load_scores(path)

    assert kept == [("Alice", 80)]
    assert skipped == []


def test_load_scores_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        test_ai_A.load_scores(tmp_path / "missing.csv")
