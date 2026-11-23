"""D17 report (post hoc): docs/reports/D17_report.md from outputs/D17/ (analysed.json, provenance.json, match.json and
the CSV tables) and outputs/N22/provenance_fetch.json. Usage: python scripts/d17_report.py --plan-commit <commit>
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "outputs/D17"
MAX_M1 = 367_752_438


def fmt_max(v):
    return f"{int(v):,}" if pd.notna(v) and int(v) >= 0 else "-"


def stats_table(df, key, label):
    L = [f"| {label} | records | with an iNaturalist photo id | of which rule E | of which rule X only | largest id | "
         f"above {MAX_M1:,} | records referring to iNaturalist |", "|---|---|---|---|---|---|---|---|"]
    for x in df.itertuples(index=False):
        L.append(f"| {getattr(x, key)} | {x.records:,} | {x.with_id:,} | {x.rule_E:,} | {x.rule_X_only:,} | "
                 f"{fmt_max(x.max_id)} | {x.above_max_M1:,} | {x.refers_inat:,} |")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-commit", required=True)
    a = ap.parse_args()
    fe = json.loads((ROOT / "outputs/N22/provenance_fetch.json").read_text(encoding="utf-8"))
    pr = json.loads((D / "provenance.json").read_text(encoding="utf-8"))
    an = json.loads((D / "analysed.json").read_text(encoding="utf-8"))
    mt = json.loads((D / "match.json").read_text(encoding="utf-8"))
    src = pd.read_csv(D / "provenance_by_source.csv")
    tab = pd.read_csv(D / "matches_by_set_family_stratum.csv")
    tab["stratum"] = tab["stratum"].fillna("none (no stratum in the D4 table)")
    hits = pd.read_csv(D / "matching_photos.csv")
    v = fe["verify"]
    L = ["# D17 - Membership of the analysed photographs in the training data of BioCLIP 2.5 Huge (post hoc)", "",
         f"Decision D17 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit {a.plan_commit}, "
         "before anything was downloaded for it). Scripts: scripts/d17_fetch_provenance.py, scripts/d17_membership.py, "
         "scripts/d17_report.py; outputs in outputs/D17/ (not tracked). No decision rule; the results are described.", "",
         "## Source file", "",
         "dataset/metadata/provenance.parquet of imageomics/TreeOfLife-200M at commit "
         "97e2340877d3a2ccad78078431fa68f404ed4870, downloaded with range requests to outputs/tmp/tol200m_97e2340/ "
         "(git-ignored; kept until this report has been checked).", "",
         "| check | value | result |", "|---|---|---|",
         f"| bytes on disk against the repository listing (10,286,368,327) | {v['bytes']:,} | {'PASS' if v['size_equal'] else 'FAIL'} |",
         f"| SHA-256 of the downloaded file | {v['sha256']} | recorded |",
         f"| SHA-256 against the LFS identifier sent by the server (x-linked-etag) | {v['server_linked_etag']} | "
         f"{'PASS' if v['sha256_equal_etag'] else 'FAIL'} |",
         f"| rows read against the file footer ({pr['rows']:,}) | {pr['rows_read']:,} | "
         f"{'PASS' if pr['control_rows_read_equal_footer'] else 'FAIL'} |", "",
         f"Footer: {pr['rows']:,} rows in {pr['row_groups']} row groups; written by {pr['created_by']}. Columns (name, type): "
         + "; ".join(f"{n} ({t})" for n, t in pr["schema"]) + ".", "",
         "## Reading and parsing rule", "",
         "The file was read row group by row group and, within a row group, column by column (4 row groups in parallel, "
         "each with its own file handle). Columns searched: every string column ("
         + ", ".join(pr["string_columns"]) + "). Values of the columns are not stored or reported; only counts and "
         "photo identifiers.", "",
         "- Rule E, the rule of the earlier gates for source_url: host = lower-case text between the first \"://\" and the "
         "next \"/\", \":\", \"?\" or \"#\"; the host must equal inaturalist-open-data.s3.amazonaws.com; the identifier is "
         "the first match of \"/photos/(digits)/\"; more than 18 digits counts as not matching.",
         "- Rule X, every string column including source_url: the value contains \"inaturalist\" (case-insensitive); the "
         "identifier is the first match, in the lower-cased value, of \"://<host containing inaturalist>[:port]/photos/(digits)\" "
         "(any iNaturalist host; a trailing \"/\" is not required); more than 18 digits counts as not matching.",
         "- A record's iNaturalist photo identifier is that of rule E if there is one, otherwise the first rule-X "
         "identifier over the columns in file order. A record refers to iNaturalist if any string column contains "
         "\"inaturalist\" (case-insensitive).",
         "- Source: the value of data_source (gbif = GBIF, eol = EOL, bioscan = BIOSCAN-5M, fathomnet = FathomNet, any "
         "other value listed as other). Publisher column: "
         + (f"{pr['publisher_column']}." if pr["publisher_column"] else "none in this file, so no per-publisher count is possible from it."), "",
         "## Records per source", ""]
    L += stats_table(src.sort_values("records", ascending=False), "source", "source")
    refcols = [c for c in src.columns if c.startswith("ref_")]
    L += ["", "Records referring to iNaturalist, per source and column:", "",
          "| source | " + " | ".join(c[4:] for c in refcols) + " |", "|---|" + "---|" * len(refcols)]
    for x in src.sort_values("records", ascending=False).itertuples(index=False):
        L.append(f"| {x.source} | " + " | ".join(f"{getattr(x, c):,}" for c in refcols) + " |")
    eol = src[src["source"] == "EOL"]
    if len(eol):
        e = eol.iloc[0]
        L += ["", f"EOL records: {int(e['records']):,}; with any reference to iNaturalist in their columns: "
              f"{int(e['refers_inat']):,}; with an iNaturalist photo identifier: {int(e['with_id']):,}."]
    pubf = D / "provenance_gbif_by_publisher.csv"
    if pubf.exists():
        pub = pd.read_csv(pubf)
        sel = pub[(pub["with_id"] > 0)]
        top = pub.sort_values("records", ascending=False).head(10)
        show = pd.concat([sel, top]).drop_duplicates("pub").sort_values("records", ascending=False)
        L += ["", f"GBIF records per publisher: {len(pub):,} publishers; shown are every publisher with an iNaturalist "
              "photo identifier and the ten largest publishers (full table in outputs/D17/provenance_gbif_by_publisher.csv).", ""]
        L += stats_table(show, "pub", "publisher")
    L += ["", "Whole file: " f"{pr['records_with_id']:,} records with an iNaturalist photo identifier; {pr['distinct_ids']:,} "
          f"distinct identifiers; largest {pr['max_id']:,}; distinct identifiers above {MAX_M1:,}: "
          f"{pr['distinct_ids_above_max_M1']:,}. Comparison with M1 of the earlier gates (revision a8f38b4, "
          f"{pr['M1_distinct']:,} distinct identifiers by rule E): {pr['M1_ids_also_in_new']:,} of them are also "
          f"identifiers of this file; {pr['new_ids_not_in_M1']:,} identifiers of this file are not in M1.", "",
          "## Analysed photographs", "",
          "Every photo identifier (all positions) of every observation of the analysed sets, from photos.csv.gz of the "
          f"snapshot of 2026-10-27 (manifest check: {'PASS' if an['manifest_photos.csv.gz'] else 'FAIL'}; "
          f"{an['snapshot_photo_rows_read']:,} snapshot rows read). Only photo identifiers were read for this check: no "
          "photograph, identification history or model output. Sets: the phase-2 samples (selected rows) of the four "
          "confirmatory sets; the D14 additions (observations whose first photograph is in the D14 photograph manifest, "
          f"found in the D14 raw responses: {an['d14']['D14_observations_found']} of {an['d14']['D14_first_photos_in_manifest']} "
          "first photographs); the D4 sample (all rows); set B of D16 (all sampled rows).", "",
          f"Observations: {mt['analysed_observations']:,} distinct; with photographs in the snapshot: "
          f"{an['observations_with_photos']:,}; without: {an['observations_without_photos']:,}. Stored first photograph found "
          f"among the snapshot photographs of its observation: {an['first_photo_found']:,} of {an['first_photo_checked']:,}. "
          f"Distinct photographs: {mt['analysed_photos']:,}; identifiers from {mt['min_analysed_photo_id']:,} to "
          f"{mt['max_analysed_photo_id']:,}; at or below {MAX_M1:,}: {mt['analysed_photos_at_or_below_max_M1']:,}.", "",
          "## Intersections", "",
          f"Analysed photographs whose identifier is an iNaturalist photo identifier of the provenance file at "
          f"97e2340877d3: {mt['photos_in_new']:,}. Analysed photographs in M1 (revision a8f38b4, available in the inputs): "
          f"{mt['photos_in_M1']:,}.", "",
          "| set | family | stratum | observations | photographs | in the file at 97e2340877d3 | of which first photographs | "
          "observations with a photograph in it | in M1 |", "|---|---|---|---|---|---|---|---|---|"]
    for x in tab.sort_values(["set", "family", "stratum"]).itertuples(index=False):
        L.append(f"| {x.set} | {x.family} | {x.stratum} | {x.observations:,} | {int(x.photos):,} | {int(x.photos_in_new):,} | "
                 f"{int(x.first_photos_in_new):,} | {int(x.observations_with_a_photo_in_new):,} | {int(x.photos_in_M1):,} |")
    L += ["", "## Matching photographs", ""]
    if len(hits):
        L += ["| set | family | stratum | photo id | position | in the file at 97e2340877d3 | in M1 |", "|---|---|---|---|---|---|---|"]
        for x in hits.sort_values(["set", "family", "photo_id"]).itertuples(index=False):
            L.append(f"| {x.set} | {x.family} | {x.stratum} | {int(x.photo_id)} | {int(x.position)} | {x.in_new} | {x.in_M1} |")
        L += ["", "Analysed photographs were found; as fixed in D17, a sensitivity analysis is proposed separately."]
    else:
        L.append("None.")
    L += ["", f"Run time of the provenance pass: {pr['minutes']} minutes; of the snapshot pass: {an['minutes']} minutes.", ""]
    (ROOT / "docs/reports/D17_report.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
