import pandas as pd


def 정제(df):
    결과 = df.copy()

    # 점수가 비어 있는 행을 삭제한다.
    결과 = 결과[결과["점수"].notna()].copy()
    print("점수 결측 행 삭제 후:", len(결과))

    # 반과 과목 값의 앞뒤 공백을 제거한다.
    결과["반"] = 결과["반"].str.strip()
    결과["과목"] = 결과["과목"].str.strip()
    print("공백 제거 후:", len(결과))

    # 모든 열의 값이 같은 중복 행을 삭제한다. (뒤의 행을 지운다)
    결과 = 결과.drop_duplicates().copy()
    print("중복 행 삭제 후:", len(결과))

    # 점수가 0 이상 100 이하인 행만 남긴다.
    결과 = 결과[결과["점수"].between(0, 100)].copy()
    print("점수 범위 확인 후:", len(결과))

    return 결과


def 반별평균(df):
    # 반으로 묶어 점수 평균을 구하고, 소수 둘째 자리까지 반올림한다.
    return df.groupby("반")["점수"].mean().round(2)


if __name__ == "__main__":
    df = pd.read_csv("scores_2026.csv", encoding="utf-8", dtype={"학번": str})
    print("원본:", df.shape)

    정제된_df = 정제(df)

    반별_통계 = 정제된_df.groupby("반")["점수"].agg(
        개수="count", 중앙값="median", 최댓값="max"
    )
    반별_통계["평균"] = 반별평균(정제된_df)
    반별_통계 = 반별_통계[["개수", "평균", "중앙값", "최댓값"]].round(2)
    print("반별 점수 통계:")
    print(반별_통계)

    과목_반별_평균 = 정제된_df.groupby(["과목", "반"])["점수"].mean()
    print("과목·반별 점수 평균:")
    print(과목_반별_평균)

    수학_df = 정제된_df[정제된_df["과목"] == "수학"]
    print("수학 행 수:", len(수학_df))
    print(수학_df.head())
    print(sorted(정제된_df["반"].unique()))
    print(sorted(정제된_df["과목"].unique()))

    print("\n")
    # ② 합계 일치 — 묶어도 총합은 변하지 않아야 한다
    print(정제된_df.groupby("반")["점수"].sum().sum(), 정제된_df["점수"].sum())
    print(정제된_df.groupby("반")["점수"].count().sum(), len(정제된_df))

    # ④ 스팟 체크 — 1반 수학을 직접 확인
    print(정제된_df[(정제된_df["반"] == "1반") & (정제된_df["과목"] == "수학")]["점수"])
