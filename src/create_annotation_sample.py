import argparse

import json
from math import floor
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_DEFAULT = ROOT / "data" / "processed" / "articles_indonesia.csv"
OUTPUT_DEFAULT = ROOT / "data" / "interim" / "annotation"

QUERY_NAMES = [
    "gunungapi",
    "gempabumi",
    "tsunami",
    "tanah_longsor",
    "likuefaksi",
    "abrasi_pantai",
    "penurunan_tanah",
    "semburan_gas_lumpur",
]


def parse_queries(value):
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def first_query(value):
    queries = parse_queries(value)
    return queries[0] if queries else "unknown"


def largest_remainder_allocate(group_sizes, total):
    group_sizes = {key: int(size) for key, size in group_sizes.items()}
    available = sum(group_sizes.values())
    if available == 0:
        return {}

    allocations = {key: 0 for key in group_sizes}
    remaining = total - sum(allocations.values())
    if remaining <= 0:
        return allocations

    proportion = {
        key: remaining * size / available
        for key, size in group_sizes.items()
    }
    for key in group_sizes:
        allocation = floor(proportion[key])
        allocations[key] += allocation
        proportion[key] -= allocation

    remaining = total - sum(allocations.values())
    for key in sorted(proportion, key=proportion.get, reverse=True)[:remaining]:
        allocations[key] += 1
    return allocations


def stratified_sample(frame, count, key_columns, random_seed):
    frame = frame.copy()
    frame["_stratum"] = frame[key_columns].fillna("unknown").astype(str).agg("|".join, axis=1)
    stratum_sizes = frame["_stratum"].value_counts().to_dict()
    allocations = largest_remainder_allocate(stratum_sizes, count)

    parts = []
    for stratum, requested in allocations.items():
        candidates = frame.loc[frame["_stratum"] == stratum]
        take = min(requested, len(candidates))
        if take:
            parts.append(candidates.sample(n=take, random_state=random_seed))

    result = pd.concat(parts).drop(columns="_stratum").drop_duplicates("article_id")
    if len(result) < count:
        selected_ids = set(result["article_id"])
        remainder = frame.loc[~frame["article_id"].isin(selected_ids)]
        result = pd.concat([
            result,
            remainder.sample(n=count - len(result), random_state=random_seed),
        ])
    return result.sample(frac=1, random_state=random_seed).reset_index(drop=True)


def make_output_columns(frame):
    result = frame.rename(columns={"hazard_type": "hazard_type_scraper"})
    result["query_groups"] = result["query_group"].fillna("[]")
    result["primary_query"] = result["query_group"].map(first_query)
    result["relevance"] = ""
    for hazard in QUERY_NAMES:
        result[hazard] = ""
    result["context"] = ""
    result["ambiguous"] = ""
    result["annotator_1"] = ""
    result["annotator_2"] = ""
    result["adjudicated_label"] = ""
    result["notes"] = ""

    columns = [
        "article_id", "title", "publish_date", "source", "primary_query",
        "hazard_type_scraper", "query_groups", "link", "split",
        "dual_annotation", "relevance",
        "gunungapi", "gempabumi", "tsunami", "tanah_longsor",
        "likuefaksi", "abrasi_pantai", "penurunan_tanah",
        "semburan_gas_lumpur", "context", "ambiguous",
        "annotator_1", "annotator_2", "adjudicated_label", "notes",
        "content_clean",
    ]
    return result[columns]


def main():
    parser = argparse.ArgumentParser(
        description="Buat sampel anotasi berstrata dan test set yang terkunci."
    )
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--sample-size", type=int, default=400)
    parser.add_argument("--test-size", type=int, default=80)
    parser.add_argument("--dual-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261120)
    parser.add_argument(
        "--include-duplicates",
        action="store_true",
        help="Jangan kecualikan artikel yang terhubung sebagai exact/near duplicate.",
    )
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    if "article_id" not in frame or "link" not in frame:
        raise ValueError("Input harus memiliki kolom article_id dan link.")
    frame = frame.drop_duplicates("article_id").copy()

    if not args.include_duplicates and "duplicate_of" in frame:
        frame = frame.loc[frame["duplicate_of"].isna()].copy()

    if len(frame) < args.sample_size:
        raise ValueError(
            f"Hanya tersedia {len(frame)} artikel unik setelah filtering; "
            f"sampel diminta {args.sample_size}."
        )

    frame["primary_query"] = frame["query_group"].map(first_query)

    test = stratified_sample(
        frame,
        args.test_size,
        ["primary_query", "source"],
        args.seed,
    )
    test_ids = set(test["article_id"])
    training_pool = frame.loc[~frame["article_id"].isin(test_ids)].copy()

    remaining_needed = args.sample_size - args.test_size
    training = stratified_sample(
        training_pool,
        remaining_needed,
        ["primary_query", "source"],
        args.seed + 1,
    )
    training_ids = set(training["article_id"])

    test["split"] = "test"
    training["split"] = "train"

    dual = stratified_sample(
        training,
        min(args.dual_size, len(training)),
        ["primary_query", "source"],
        args.seed + 2,
    )
    dual_ids = set(dual["article_id"])

    selected = pd.concat([test, training], ignore_index=True)
    selected["dual_annotation"] = selected["article_id"].isin(dual_ids)

    output = make_output_columns(selected)
    test_output = output.loc[output["split"] == "test"].copy()
    annotation_output = output.copy()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    annotation_output.to_csv(
        args.output_dir / "annotation_sample.csv",
        index=False,
        encoding="utf-8-sig",
    )
    test_output.to_csv(
        args.output_dir / "test_set.csv",
        index=False,
        encoding="utf-8-sig",
    )
    dual_output = annotation_output.loc[
        annotation_output["dual_annotation"] == True
    ].copy()
    dual_output.to_csv(
        args.output_dir / "dual_annotation.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary = {
        "input_rows": len(frame),
        "sample_size": len(annotation_output),
        "test_size": len(test_output),
        "train_size": len(annotation_output.loc[annotation_output["split"] == "train"]),
        "dual_size": len(dual_output),
        "seed": args.seed,
        "duplicates_excluded": not args.include_duplicates,
    }
    (args.output_dir / "sampling_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print(f"Output: {args.output_dir}")


if __name__ == "__main__":
    main()
