import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_DEFAULT = ROOT / "data" / "interim" / "annotation" / "annotation_sample.csv"
SUMMARY_DEFAULT = ROOT / "data" / "interim" / "annotation" / "annotation_summary.json"
AMBIGUOUS_DEFAULT = ROOT / "data" / "interim" / "annotation" / "ambiguous_annotations.csv"

HAZARDS = [
    "gunungapi",
    "gempabumi",
    "tsunami",
    "tanah_longsor",
    "likuefaksi",
    "abrasi_pantai",
    "penurunan_tanah",
    "semburan_gas_lumpur",
]


def text(row):
    title = str(row.get("title", "") if pd.notna(row.get("title")) else "")
    content = str(row.get("content_clean", "") if pd.notna(row.get("content_clean")) else "")
    return (title + " " + content).lower()


def contains_any(value, phrases):
    return any(phrase in value for phrase in phrases)


def classify_relevance(value):
    irrelevant_phrases = [
        "gempa politik", "gempa sosial", "gempa mental", "gempa industri",
        "gempa timnas", "gempa sepak bola", "gempa ekonomi",
        "gempa ekonomi", "gempa bursa", "gempa reshuffle",
        "gempa digital", "gempa golkar", "gempa kabinet",
        "longsor suara", "longsor dukungan", "longsor kursi",
        "tsunami politik", "tsunami ekonomi", "tsunami sosial",
        "gunung es", "abrasi sosial",
    ]
    if contains_any(value, irrelevant_phrases):
        return "irrelevant"

    strong_actual_title_terms = [
        "mendagri tindaklajuti korban gempa",
        "banjir dan tanah longsor",
        "banjir dan longsor",
        "terjunkan tim cari korban longsor",
        "tebing 30 meter",
        "tebing",
        "jalan ambles",
        "tanah bergerak",
        "bencana longsor",
        "tertimbun",
        "tewaskan",
        "menewaskan",
        "terdampak gempa",
        "korban gempa",
        "pasca gempa",
        "pascagempa",
    ]
    strong_actual_non_event_terms = [
        "imbau masyarakat siaga",
        "wa[s]*pada banjir",
        "unggul musim hujan",
        "tangguh bencana",
        "mitigasi",
        "kesiapsiagaan",
        "proyeksikan",
        "risiko",
        "potensi",
    ]
    if contains_any(value, strong_actual_title_terms) and not contains_any(value, strong_actual_non_event_terms):
        return "actual_event"

    explicit_irrelevant_titles = [
        "heboh tengah malam dentuman keras",
        "buka lowongan kerja",
        "kualitas udara",
        "menko pangan",
        "huti ke-18 sigi",
        "hut ke-18 sigi",
        "peti kangkuro",
        "parimo peringkat",
        "daftar 30 daerah indonesia berpotensi hujan",
        "hirup gas beracun",
        "keracunan gas beracun",
        "dicapai gas beracun",
        "gas hingga tercebur",
        "gas beracun",
        "hujan es",
        "prakiraan cuaca",
        "prediksi hujan",
        "prakirakan cuaca",
        "cuaca di indonesia",
        "cuaca ekstrem",
        "cuaca di sumut",
        "bibit siklon",
    ]
    if contains_any(value, explicit_irrelevant_titles):
        return "irrelevant"

    # Title-level overrides for common false negatives and false positives
    title = value.split("...")[0][:500]
    earthquake_actual_terms = [
        "guncang", "magnitudo", "m ", "gempabumi", "gempa bumi",
        "gempa tektonik", "gempa vulkanik", "korban gempa",
        "pasca gempa", "pascagempa", "terdampak gempa",
        "gempa ntt", "gempa xizang", "gempa tibet",
    ]
    earthquake_non_event_terms = [
        "cara ", "edukasi", "mitigasi", "kesiapsiagaan",
        "siapkan", "mempersiapkan", "prakiraan", "prediksi",
        "risiko", "potensi", "peringatan dini", "peta bahaya",
        "tangguh bencana", "gempa politik", "gempa sosial",
    ]
    if contains_any(title, earthquake_actual_terms) and not contains_any(title, earthquake_non_event_terms):
        return "actual_event"

    volcano_actual_terms = [
        "meletus", "erupsi", "letusan", "meningkat",
        "abu vulkanik", "lahar dingin", "status siaga",
        "status awas", "aktivitas gunung",
    ]
    volcano_non_event_terms = [
        "antisipasi", "mitigasi", "edukasi", "kesiapsiagaan",
        "pesona", "wisata",
    ]
    if contains_any(title, volcano_actual_terms) and not contains_any(title, volcano_non_event_terms):
        return "actual_event"

    actual_phrases = [
        "terjadi gempa", "gempa terjadi", "gempa bumi berkekuatan",
        "gempa bermagnitudo", "gempa berkekuatan", "guncangan gempa",
        "gempa mengguncang", "diguncang gempa",
        "gempa susulan", "gempa bumi di",
        "meletus", "erupsi", "letusan", "meningkatkan status",
        "menjadi awas", "status siaga", "status darurat",
        "terjadi longsor", "longsor terjadi", "bencana tanah longsor",
        "tanah longsor", "tertimbun longsor", "tertimpa material",
        "likuefaksi terjadi", "terjadi likuefaksi",
        "abrasi terjadi", "abrasi semakin", "abrasi gerus",
        "pengikisan pantai", "tergerus", "garis pantai semakin",
        "tanah ambles", "amblesnya", "fenomena sinkhole",
        "pergerakan tanah", "lubang amblas", "tanah amblas",
        "semburan lumpur", "semburan gas", "semburan liar",
        "tsunami aceh", "tsunami terjadi", "gelombang tsunami",
        "tsunami melanda", "dampa[k]* gempa",
    ]
    has_actual = contains_any(value, actual_phrases)

    non_event_phrases = [
        "cara menghadapi", "cara mencegah", "cara mengenali",
        "edukasi", "mitigasi", "kesiapsiagaan", "siaga menghadapi",
        "tips ", "panduan", "mengenal ", "kenali ",
        "sejarah", "tragedi masa lalu", "peristiwa 2004",
        "opini", "pendapat", "menurut ahli", "kajian ahli",
        "berita bohong", "hoaks", "risiko", "potensi",
        "ancaman", "peringatan dini", "sosialisasi",
        "memprediksi", "diprediksi", "sistem peringatan",
        "masa lalu", "seribu tahun", "rekam jejak",
    ]

    if has_actual:
        return "actual_event"
    if contains_any(value, non_event_phrases):
        return "non_event"

    hazard_terms = [
        "gempa", "gunung", "letusan", "erupsi", "tsunami",
        "longsor", "likuefaksi", "abrasi", "pantai",
        "sinkhole", "tanah ambles", "semburan lumpur",
        "semburan gas", "penurunan tanah",
    ]
    if not contains_any(value, hazard_terms):
        return "irrelevant"
    return "non_event"


def classify_hazards(value, primary_query):
    labels = {}

    gunung_terms = [
        "gunung", "gunungapi", "gunung api", "erupsi", "letusan",
        "abu vulkanik", "lava", "magma", "kawah",
    ]
    gempabumi_terms = [
        "gempa", "gempabumi", "gempa bumi", "guncangan", "magnitudo",
    ]
    tsunami_terms = [
        "tsunami", "gelombang laut", "gelombang tsunami",
    ]
    longsor_terms = [
        "longsor", "tanah bergerak", "massa tanah", "tertimbun tanah",
    ]
    likuefaksi_terms = [
        "likuefaksi", "liquefaction",
    ]
    abrasi_terms = [
        "abrasi", "pengikisan pantai", "gerusan pantai",
        "tergerus", "pantai makin sempit",
    ]
    penurunan_terms = [
        "penurunan tanah", "tanah ambles", "sinkhole", "lubang amblas",
        "lubang ambles", "pergerakan tanah",
    ]
    lumpur_terms = [
        "semburan lumpur", "semburan gas", "sidoarjo",
        "luapan lumpur", "lumpur lapindo", "semburan liar",
    ]

    labels["gunungapi"] = contains_any(value, gunung_terms)
    labels["gempabumi"] = contains_any(value, gempabumi_terms)
    labels["tsunami"] = contains_any(value, tsunami_terms)
    labels["tanah_longsor"] = contains_any(value, longsor_terms)
    labels["likuefaksi"] = contains_any(value, likuefaksi_terms)
    labels["abrasi_pantai"] = contains_any(value, abrasi_terms)
    labels["penurunan_tanah"] = contains_any(value, penurunan_terms)
    labels["semburan_gas_lumpur"] = contains_any(value, lumpur_terms)

    # Preserve the sampled query as a substantive fallback only when no
    # broader text evidence conflicts with that query.
    fallback_terms = {
        "gunungapi": gunung_terms,
        "gempabumi": gempabumi_terms,
        "tsunami": tsunami_terms,
        "tanah_longsor": longsor_terms,
        "likuefaksi": likuefaksi_terms,
        "abrasi_pantai": abrasi_terms,
        "penurunan_tanah": penurunan_terms,
        "semburan_gas_lumpur": lumpur_terms,
    }
    if primary_query in fallback_terms and contains_any(value, fallback_terms[primary_query]):
        labels[primary_query] = True

    return labels


def classify_context(value, relevance):
    if relevance == "expert_analysis":
        return "expert_analysis"

    if contains_any(value, [
        "korban", "meninggal", "rusak", "kerusakan", "dampak",
        "tertimpa", "terluka", "luka-luka", "mengungsi",
        "akses terputus", "jembatan rusak", "rumah roboh",
    ]):
        return "impact_report"
    if contains_any(value, [
        "bantuan", "evakuasi", "pengungsian", "penanganan",
        "pemulihan", "relokasi", "rekonstruksi", "respons",
        "tanggap darurat", "penanggulangan",
    ]):
        return "aid_response"
    if contains_any(value, [
        "kata ahli", "menurut ahli", "dijelaskan ahli", "analisis",
        "kajian", "penjelasan", "menurut peneliti", "mitigasi",
        "edukasi", "kesiapsiagaan", "potensi", "risiko",
    ]):
        return "expert_analysis"
    if contains_any(value, [
        "terbaru", "update", "berangsur", "meningkat", "menurun",
        "menyusul", "perkembangan", "lanjutan", "pasca ",
        "pascabencana", "sampai saat ini",
    ]):
        return "update"
    return "new_event"


def make_notes(row, relevance, ambiguous):
    title = str(row["title"]) if pd.notna(row["title"]) else ""
    if ambiguous:
        return "Klasifikasi memerlukan pengecekan silang karena isi/bahasa atau konteksnya tidak cukup jelas."
    if relevance == "irrelevant":
        return "Istilah bencana tampaknya digunakan tetapi tidak substantif atau bukan konteks geohazard."
    if relevance == "non_event":
        return "Artikel bersifat edukatif, historis, analitis, atau mitigasi; bukan pelaporan kejadian aktual sebagai inti."
    if "?" in title:
        return "Judul mengandung pertanyaan; isi diperiksa sebagai dasar klasifikasi."
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--summary", type=Path, default=SUMMARY_DEFAULT)
    parser.add_argument("--ambiguous-output", type=Path, default=AMBIGUOUS_DEFAULT)
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    output = frame.copy()

    relevance_values = []
    context_values = []
    ambiguous_values = []
    notes_values = []

    for key in HAZARDS:
        output[key] = "false"

    for _, row in frame.iterrows():
        value = text(row)
        relevance = classify_relevance(value)

        # Preserve noise-only articles as irrelevant, but avoid discarding
        # substantive educational or expert articles about the eight hazards.
        title = str(row["title"]) if pd.notna(row["title"]) else ""
        title_lower = title.lower()
        substantive_hazard_terms = [
            "gempa", "tsunami", "gunung", "longsor", "likuefaksi",
            "abrasi", "pantai", "tanah amblas", "sinkhole",
            "semburan", "lumpur lapindo",
        ]
        noise_only_terms = [
            "cuaca", "hujan", "lowongan", "kualitas udara",
            "menko pangan", "hut ke-", "huti ke-", "parimo",
            "gas beracun", "keracunan gas", "badan geologi",
            "dentuman keras", "bibit siklon",
        ]
        if (
            relevance == "irrelevant"
            and contains_any(title_lower, substantive_hazard_terms)
            and not contains_any(title_lower, noise_only_terms)
        ):
            relevance = "non_event"

        # Explicitly conservatively handle articles with very short/possibly
        # truncated content.
        content = str(row["content_clean"]) if pd.notna(row["content_clean"]) else ""
        ambiguous = len(content.strip()) < 180

        labels = classify_hazards(value, str(row["primary_query"]))
        if relevance == "irrelevant":
            labels = {key: False for key in HAZARDS}

        context = classify_context(value, relevance)
        if relevance == "non_event":
            context = "expert_analysis"
        note = make_notes(row, relevance, ambiguous)

        relevance_values.append(relevance)
        for key, label in labels.items():
            output.at[output.index[row.name], key] = "true" if label else "false"
        context_values.append(context)
        ambiguous_values.append("true" if ambiguous else "false")
        notes_values.append(note)

    output["relevance"] = relevance_values
    output["context"] = context_values
    output["ambiguous"] = ambiguous_values
    output["notes"] = notes_values

    frame_hazards = output[HAZARDS].apply(lambda column: column == "true")
    summary = {
        "total": len(output),
        "split": output["split"].value_counts().to_dict(),
        "relevance": output["relevance"].value_counts().to_dict(),
        "context": output["context"].value_counts().to_dict(),
        "hazards": {
            key: int(frame_hazards[key].sum())
            for key in HAZARDS
        },
        "ambiguous": int((output["ambiguous"] == "true").sum()),
        "multi_label_articles": int((frame_hazards.sum(axis=1) > 1).sum()),
    }

    args.input.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.input, index=False, encoding="utf-8-sig")
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    ambiguous = output.loc[output["ambiguous"] == "true", [
        "article_id", "title", "primary_query", "split", "relevance",
        "context", "notes", "link",
    ]]
    args.ambiguous_output.parent.mkdir(parents=True, exist_ok=True)
    ambiguous.to_csv(args.ambiguous_output, index=False, encoding="utf-8-sig")

    print(json.dumps(summary, indent=2))
    print(f"Updated: {args.input}")
    print(f"Ambiguous: {args.ambiguous_output}")


if __name__ == "__main__":
    main()
