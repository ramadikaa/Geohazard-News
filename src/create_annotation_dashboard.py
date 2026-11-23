import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_DEFAULT = ROOT / "data" / "interim" / "annotation" / "annotation_sample.csv"
OUTPUT_DEFAULT = ROOT / "data" / "interim" / "annotation" / "annotation_review.html"

HAZARDS = [
    ("gunungapi", "Gunung api"),
    ("gempabumi", "Gempa bumi"),
    ("tsunami", "Tsunami"),
    ("tanah_longsor", "Tanah longsor"),
    ("likuefaksi", "Likuefaksi"),
    ("abrasi_pantai", "Abrasi pantai"),
    ("penurunan_tanah", "Penurunan tanah"),
    ("semburan_gas_lumpur", "Semburan gas/lumpur"),
]


def truthy(value):
    return str(value).strip().lower() in {"true", "1", "yes", "ya"}


def string_value(row, column):
    value = row.get(column, "")
    return "" if pd.isna(value) else str(value)


def prepare_records(frame):
    records = []
    for _, row in frame.iterrows():
        hazard_labels = [
            label for column, label in HAZARDS if truthy(row.get(column, ""))
        ]
        records.append({
            "article_id": string_value(row, "article_id"),
            "title": string_value(row, "title"),
            "publish_date": string_value(row, "publish_date"),
            "source": string_value(row, "source"),
            "primary_query": string_value(row, "primary_query"),
            "split": string_value(row, "split"),
            "dual_annotation": truthy(row.get("dual_annotation", "")),
            "relevance": string_value(row, "relevance"),
            "context": string_value(row, "context"),
            "hazards": hazard_labels,
            "ambiguous": truthy(row.get("ambiguous", "")),
            "annotator_1": string_value(row, "annotator_1"),
            "annotator_2": string_value(row, "annotator_2"),
            "adjudicated_label": string_value(row, "adjudicated_label"),
            "notes": string_value(row, "notes"),
            "link": string_value(row, "link"),
            "content": string_value(row, "content_clean"),
        })
    return records


def build_html(records):
    payload = json.dumps(records, ensure_ascii=False)
    payload = (
        payload.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )

    return r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Geohazard-News | Pemeriksa Anotasi</title>
<style>
:root {
  color-scheme: light;
  --ink: #172b3a;
  --muted: #587080;
  --line: #d7e1e8;
  --paper: #f3f7fa;
  --card: #fff;
  --blue: #136b8a;
  --green: #237b57;
  --amber: #a4610a;
  --red: #ad3d44;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 15px/1.5 "Segoe UI", Arial, sans-serif; }
header { padding: 28px clamp(18px, 4vw, 52px) 20px; background: #12394b; color: white; }
header h1 { margin: 0 0 5px; font-size: clamp(24px, 3vw, 34px); }
header p { margin: 0; color: #d2e6ef; }
main { max-width: 1500px; margin: auto; padding: 20px clamp(14px, 3vw, 40px) 48px; }
.notice { margin: 0 0 18px; padding: 13px 16px; border-left: 4px solid #d18a1c; border-radius: 6px; background: #fff7e8; color: #62400e; }
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 12px; margin: 16px 0; }
.metric, .panel { background: var(--card); border: 1px solid var(--line); border-radius: 10px; box-shadow: 0 2px 6px #17394a0a; }
.metric { padding: 15px 17px; }
.metric strong { display: block; font-size: 25px; line-height: 1.2; color: var(--blue); }
.metric span { color: var(--muted); font-size: 13px; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 14px; margin: 16px 0; }
.panel { padding: 16px; }
.panel h2 { margin: 0 0 12px; font-size: 17px; }
.bar-row { display: grid; grid-template-columns: minmax(100px, 145px) 1fr 38px; gap: 9px; align-items: center; margin: 8px 0; font-size: 13px; }
.bar-track { height: 12px; overflow: hidden; background: #e8eff3; border-radius: 8px; }
.bar { height: 100%; background: #2986a4; border-radius: inherit; }
.bar.actual_event { background: #29956a; }
.bar.non_event { background: #d29129; }
.bar.irrelevant { background: #c85c62; }
.bar.context { background: #4a79a4; }
.bar.hazard { background: #7780b3; }
.bar-row b { text-align: right; font-variant-numeric: tabular-nums; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; align-items: end; }
label { display: block; color: var(--muted); font-size: 12px; font-weight: 600; }
input, select, button { width: 100%; min-height: 40px; margin-top: 4px; padding: 8px 10px; border: 1px solid #bdcdd7; border-radius: 6px; background: white; color: var(--ink); font: inherit; }
button { cursor: pointer; border-color: var(--blue); background: var(--blue); color: white; font-weight: 650; }
button:hover { background: #0b5874; }
.results { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin: 16px 0 9px; color: var(--muted); }
.table-wrap { overflow: auto; border: 1px solid var(--line); border-radius: 9px; background: white; }
table { width: 100%; border-collapse: collapse; min-width: 960px; }
th, td { padding: 11px 12px; border-bottom: 1px solid #e6edf1; text-align: left; vertical-align: top; }
th { position: sticky; top: 0; z-index: 1; background: #eaf1f5; color: #385566; font-size: 12px; letter-spacing: .03em; text-transform: uppercase; }
tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #f7fafb; }
.title { min-width: 290px; font-weight: 650; }
.small { color: var(--muted); font-size: 12px; }
.badge, .tag { display: inline-block; margin: 2px 3px 2px 0; padding: 3px 8px; border-radius: 99px; background: #e8eff3; color: #355468; font-size: 12px; white-space: nowrap; }
.badge.actual_event { background: #e1f4e9; color: #1d6947; }
.badge.non_event { background: #fff0d6; color: #80500c; }
.badge.irrelevant { background: #fde7e8; color: #96363c; }
.badge.ambiguous { background: #ffefce; color: #87530c; }
.tag { background: #edf0fb; color: #4a5488; }
details { min-width: 230px; }
summary { color: var(--blue); cursor: pointer; font-size: 13px; font-weight: 600; }
.article-content { max-height: 350px; overflow: auto; margin: 8px 0; padding: 10px; border-radius: 5px; background: #f4f7f9; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 13px; }
.notes { max-width: 270px; color: #6b4c23; font-size: 12px; }
.empty { padding: 28px; text-align: center; color: var(--muted); }
@media (max-width: 650px) {
  .results { align-items: flex-start; flex-direction: column; }
  .bar-row { grid-template-columns: 100px 1fr 32px; }
}
</style>
</head>
<body>
<header>
  <h1>Pemeriksa Anotasi Geohazard-News</h1>
  <p>Ringkasan distribusi dan pemeriksaan artikel satu per satu dari annotation_sample.csv</p>
</header>
<main>
  <div class="notice"><strong>Catatan validitas:</strong> Label ini adalah draft AI, bukan anotasi manusia independen. Kolom anotator 1 dan 2 tidak menghasilkan Cohen’s Kappa yang valid. Baris test juga sudah diberi label, sehingga bukan test set untouched.</div>
  <section class="metrics" id="metrics"></section>
  <section class="charts">
    <div class="panel"><h2>Relevansi</h2><div id="relevance-chart"></div></div>
    <div class="panel"><h2>Konteks pemberitaan</h2><div id="context-chart"></div></div>
    <div class="panel"><h2>Jenis bencana (multi-label)</h2><div id="hazard-chart"></div></div>
  </section>
  <section class="panel">
    <h2>Filter dan pencarian</h2>
    <div class="filters">
      <label>Cari judul, isi, sumber, ID<input id="search" type="search" placeholder="Ketik kata kunci..."></label>
      <label>Relevansi<select id="relevance-filter"><option value="">Semua</option></select></label>
      <label>Konteks<select id="context-filter"><option value="">Semua</option></select></label>
      <label>Jenis bencana<select id="hazard-filter"><option value="">Semua</option></select></label>
      <label>Kueri utama<select id="query-filter"><option value="">Semua</option></select></label>
      <label>Sumber<select id="source-filter"><option value="">Semua</option></select></label>
      <label>Pemisahan data<select id="split-filter"><option value="">Semua</option></select></label>
      <label>Perlu ditinjau<select id="review-filter"><option value="">Semua</option><option value="ambiguous">Ambigu</option><option value="unadjudicated">Belum adjudikasi</option><option value="dual">Dual annotation</option></select></label>
      <button id="download">Unduh hasil filter (.csv)</button>
    </div>
  </section>
  <div class="results"><strong id="result-count"></strong><span>Gunakan “Baca isi” untuk membandingkan label dengan isi artikel.</span></div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Artikel</th><th>Label</th><th>Konteks</th><th>Jenis bencana</th><th>Review</th><th>Isi dan catatan</th></tr></thead>
      <tbody id="article-rows"></tbody>
    </table>
    <div class="empty" id="empty" hidden>Tidak ada artikel yang cocok dengan filter.</div>
  </div>
</main>
<script>
const articles = __DATA__;
const hazardNames = ["Gunung api","Gempa bumi","Tsunami","Tanah longsor","Likuefaksi","Abrasi pantai","Penurunan tanah","Semburan gas/lumpur"];
const relevanceNames = ["actual_event","non_event","irrelevant"];
const contextNames = ["new_event","update","impact_report","aid_response","expert_analysis"];
const byId = id => document.getElementById(id);
const uniqueValues = key => [...new Set(articles.map(a => a[key]).filter(Boolean))].sort((a,b) => a.localeCompare(b,"id"));
function optionList(id, values) {
  const select = byId(id);
  values.forEach(value => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}
function setText(node, value) { node.textContent = value || "—"; }
function addMetric(label, value) {
  const card = document.createElement("div"); card.className = "metric";
  const number = document.createElement("strong"); number.textContent = value;
  const caption = document.createElement("span"); caption.textContent = label;
  card.append(number, caption); byId("metrics").appendChild(card);
}
function renderBars(targetId, rows, cssClass) {
  const root = byId(targetId);
  const max = Math.max(1, ...rows.map(row => row.count));
  rows.forEach(row => {
    const line = document.createElement("div"); line.className = "bar-row";
    const name = document.createElement("span"); name.textContent = row.name;
    const track = document.createElement("div"); track.className = "bar-track";
    const bar = document.createElement("div"); bar.className = "bar " + cssClass;
    bar.style.width = (row.count / max * 100) + "%";
    const count = document.createElement("b"); count.textContent = row.count;
    track.appendChild(bar); line.append(name, track, count); root.appendChild(line);
  });
}
function renderSummary() {
  const actual = articles.filter(a => a.relevance === "actual_event").length;
  const notRelevant = articles.filter(a => a.relevance === "non_event" || a.relevance === "irrelevant").length;
  const multi = articles.filter(a => a.hazards.length > 1).length;
  const ambiguous = articles.filter(a => a.ambiguous).length;
  const dual = articles.filter(a => a.dual_annotation).length;
  const test = articles.filter(a => a.split === "test").length;
  addMetric("Total artikel", articles.length);
  addMetric("Kejadian aktual", actual);
  addMetric("Non-event + tidak relevan", notRelevant);
  addMetric("Multi-label", multi);
  addMetric("Ambigu", ambiguous);
  addMetric("Dual annotation", dual);
  addMetric("Baris test (sudah berlabel)", test);
  renderBars("relevance-chart", relevanceNames.map(name => ({
    name, count: articles.filter(a => a.relevance === name).length
  })), "relevance");
  renderBars("context-chart", contextNames.map(name => ({
    name, count: articles.filter(a => a.context === name).length
  })), "context");
  renderBars("hazard-chart", hazardNames.map(name => ({
    name, count: articles.filter(a => a.hazards.includes(name)).length
  })), "hazard");
}
function matches(article) {
  const query = byId("search").value.trim().toLocaleLowerCase("id");
  const relevance = byId("relevance-filter").value;
  const context = byId("context-filter").value;
  const hazard = byId("hazard-filter").value;
  const primaryQuery = byId("query-filter").value;
  const source = byId("source-filter").value;
  const split = byId("split-filter").value;
  const review = byId("review-filter").value;
  const searchable = [article.article_id,article.title,article.content,article.source,article.primary_query,article.notes].join(" ").toLocaleLowerCase("id");
  if (query && !searchable.includes(query)) return false;
  if (relevance && article.relevance !== relevance) return false;
  if (context && article.context !== context) return false;
  if (hazard && !article.hazards.includes(hazard)) return false;
  if (primaryQuery && article.primary_query !== primaryQuery) return false;
  if (source && article.source !== source) return false;
  if (split && article.split !== split) return false;
  if (review === "ambiguous" && !article.ambiguous) return false;
  if (review === "unadjudicated" && article.adjudicated_label) return false;
  if (review === "dual" && !article.dual_annotation) return false;
  return true;
}
function cell(className) { const td = document.createElement("td"); if (className) td.className = className; return td; }
function badge(text, kind) { const node = document.createElement("span"); node.className = "badge " + (kind || ""); node.textContent = text; return node; }
function renderArticles() {
  const list = articles.filter(matches);
  const body = byId("article-rows"); body.replaceChildren();
  byId("result-count").textContent = list.length + " dari " + articles.length + " artikel";
  byId("empty").hidden = list.length !== 0;
  list.forEach(article => {
    const tr = document.createElement("tr");
    const articleCell = cell("title");
    const title = document.createElement("div"); title.textContent = article.title || "(tanpa judul)";
    const meta = document.createElement("div"); meta.className = "small";
    meta.textContent = [article.article_id, article.source, article.publish_date, article.primary_query, article.split].filter(Boolean).join(" · ");
    articleCell.append(title, meta);
    if (article.link) {
      const link = document.createElement("a"); link.href = article.link; link.target = "_blank"; link.rel = "noopener noreferrer";
      link.textContent = "Buka sumber"; link.className = "small"; articleCell.appendChild(link);
    }

    const relevanceCell = cell(); relevanceCell.appendChild(badge(article.relevance, article.relevance));
    const contextCell = cell(); contextCell.appendChild(badge(article.context));
    const hazardCell = cell();
    if (article.hazards.length) article.hazards.forEach(name => {
      const tag = document.createElement("span"); tag.className = "tag"; tag.textContent = name; hazardCell.appendChild(tag);
    });
    else hazardCell.textContent = "—";

    const reviewCell = cell();
    reviewCell.appendChild(badge(article.split, ""));
    if (article.ambiguous) reviewCell.appendChild(badge("ambigu", "ambiguous"));
    if (article.dual_annotation) reviewCell.appendChild(badge("dual", ""));
    const adjudication = document.createElement("div"); adjudication.className = "small";
    adjudication.textContent = "Adjudikasi: " + (article.adjudicated_label || "kosong");
    reviewCell.appendChild(adjudication);

    const detailCell = cell();
    const details = document.createElement("details");
    const summary = document.createElement("summary"); summary.textContent = "Baca isi artikel";
    const content = document.createElement("div"); content.className = "article-content"; content.textContent = article.content || "(isi kosong)";
    details.append(summary, content); detailCell.appendChild(details);
    if (article.notes) { const note = document.createElement("div"); note.className = "notes"; note.textContent = article.notes; detailCell.appendChild(note); }
    const annotators = document.createElement("div"); annotators.className = "small";
    annotators.textContent = [article.annotator_1, article.annotator_2].filter(Boolean).join(" / ");
    if (annotators.textContent) detailCell.appendChild(annotators);

    tr.append(articleCell, relevanceCell, contextCell, hazardCell, reviewCell, detailCell);
    body.appendChild(tr);
  });
}
function csvEscape(value) { return '"' + String(value ?? "").replaceAll('"','""') + '"'; }
function downloadFiltered() {
  const rows = articles.filter(matches);
  const columns = ["article_id","title","publish_date","source","primary_query","split","relevance","context","hazards","ambiguous","dual_annotation","adjudicated_label","notes","link"];
  const lines = [columns.join(",")];
  rows.forEach(article => lines.push(columns.map(column => csvEscape(column === "hazards" ? article.hazards.join("; ") : article[column])).join(",")));
  const blob = new Blob(["\ufeff" + lines.join("\r\n")], {type:"text/csv;charset=utf-8"});
  const anchor = document.createElement("a"); anchor.href = URL.createObjectURL(blob);
  anchor.download = "annotation_filtered.csv"; anchor.click(); URL.revokeObjectURL(anchor.href);
}
optionList("relevance-filter", uniqueValues("relevance"));
optionList("context-filter", uniqueValues("context"));
optionList("query-filter", uniqueValues("primary_query"));
optionList("source-filter", uniqueValues("source"));
optionList("split-filter", uniqueValues("split"));
optionList("hazard-filter", hazardNames);
["search","relevance-filter","context-filter","hazard-filter","query-filter","source-filter","split-filter","review-filter"].forEach(id => {
  byId(id).addEventListener("input", renderArticles);
  byId(id).addEventListener("change", renderArticles);
});
byId("download").addEventListener("click", downloadFiltered);
renderSummary(); renderArticles();
</script>
</body>
</html>""".replace("__DATA__", payload)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a standalone interactive annotation review dashboard."
    )
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    required = {
        "article_id", "title", "source", "relevance", "context",
        "split", "content_clean",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    records = prepare_records(frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(records), encoding="utf-8")
    print(f"Generated dashboard for {len(records)} articles: {args.output}")


if __name__ == "__main__":
    main()
