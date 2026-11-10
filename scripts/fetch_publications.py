#!/usr/bin/env python3
"""Fetch my publication list and write _data/publications_auto.json.

Sources
  1. OpenAlex (primary): every work linked to the PI's ORCID iD.
  2. PubMed (cross-check): PMIDs matching PUBMED_QUERY that OpenAlex missed.

Manual additions and hidden entries live in _data/publications.yml (edited
through the CMS) and are merged at build time by Jekyll
(_includes/publication-list.html), so this script never touches them.

Also writes _data/peer_reviews_auto.json from ORCID's public peer-review
records; manual peer-review entries live in _data/peer_reviews.yml.

Adapted from github.com/johannesnicolaus/luscombelab_website.

Standard library only. Run from the repository root:
    python3 scripts/fetch_publications.py
Environment (optional):
    OPENALEX_API_KEY  OpenAlex API key, if you have one
    OPENALEX_MAILTO   contact e-mail for OpenAlex's "polite pool"
    NCBI_API_KEY      NCBI key (raises PubMed rate limit)
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# --- configuration -----------------------------------------------------------
ORCID = "0000-0002-2452-8702"          # Johannes Nicolaus Wibisana
PUBMED_QUERY = "Wibisana JN[Author]"
OUTPUT = Path(__file__).resolve().parent.parent / "_data" / "publications_auto.json"

KEEP_TYPES = {"article", "review", "preprint", "book-chapter", "book", "conference-paper", "letter"}
# DOI prefixes of data/repository hosts whose records are not papers.
REPOSITORY_DOI_PREFIXES = ("10.5281/", "10.6084/", "10.17605/", "10.5061/")
PARATEXT_TITLE = re.compile(
    r"^(author correction|publisher correction|correction|erratum|corrigendum|retraction|"
    r"reply to|response to|decision letter|author response|peer review)",
    re.I,
)
PREPRINT_VENUES = re.compile(r"biorxiv|medrxiv|arxiv|research square|preprints\.org|ssrn", re.I)
# Institutional/aggregator copies of papers published elsewhere.
REPOSITORY_VENUES = re.compile(
    r"discovery|repository|eprints|europe pmc|pubmed central|research portal|research explorer|"
    r"\bhal\b|zenodo|figshare|archive|depositonce|edoc|\bpure\b", re.I)
SURNAME_PARTICLES = {"van", "von", "de", "del", "der", "den", "da", "di", "dos", "das", "la", "le", "du", "ten", "ter"}

UA = "jnicolaus-website-publication-sync (+https://github.com/johannesnicolaus/johannesnicolaus.github.io)"


# --- helpers -----------------------------------------------------------------
def get(url: str, params: dict | None = None, accept: str = "application/json", retries: int = 4) -> bytes:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if attempt == retries - 1 or code in (400, 401, 403, 404):
                if isinstance(e, urllib.error.HTTPError):
                    body = e.read()[:500].decode("utf-8", "replace")
                    raise RuntimeError(f"HTTP {code} from {url.split('?')[0]}: {body}") from e
                raise
            time.sleep(2 ** attempt * 2)
    raise RuntimeError("unreachable")


def norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi or None


def norm_title(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", html.unescape(t or "")).lower()
    return re.sub(r"[^a-z0-9]+", "", t)


ALLOWED_TAGS = re.compile(r"</?(i|em|sub|sup|b|strong)>", re.I)


def clean_title(t: str) -> str:
    """Keep simple inline markup (italics for species names, sub/sup); drop everything else."""
    t = html.unescape(t or "").strip()
    keep = {}

    def stash(m):
        key = f"\x00{len(keep)}\x00"
        keep[key] = m.group(0).lower().replace("<em>", "<i>").replace("</em>", "</i>") \
            .replace("<strong>", "<b>").replace("</strong>", "</b>")
        return key

    t = ALLOWED_TAGS.sub(stash, t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.escape(t, quote=False)
    for k, v in keep.items():
        t = t.replace(k, v)
    t = re.sub(r"\s+", " ", t).strip()
    return t.rstrip(".")


def short_name(full: str) -> str:
    """'Nicholas M. Luscombe' -> 'NM Luscombe'; 'Maria Sara Del Rio-Pisula' -> 'MS Del Rio-Pisula'."""
    full = re.sub(r"\s+", " ", (full or "").replace(".", ". ")).strip()
    if not full:
        return ""
    if "," in full:  # "Luscombe, Nicholas M."
        last, _, first = full.partition(",")
        tokens = first.split() + last.split()
    else:
        tokens = full.split()
    if len(tokens) == 1:
        return tokens[0]
    # surname = last token plus any lowercase-able particles before it
    i = len(tokens) - 1
    while i > 1 and tokens[i - 1].lower().rstrip(".") in SURNAME_PARTICLES:
        i -= 1
    given, surname = tokens[:i], " ".join(tokens[i:])
    initials = ""
    for g in given:
        g = g.strip(".")
        if not g:
            continue
        if g.isupper() and len(g) <= 3:  # already initials, e.g. "NM"
            initials += g
        else:
            initials += "-".join(p[0].upper() for p in g.split("-") if p)
    return f"{initials} {surname}".strip()


def clean_venue(v: str | None) -> str:
    if not v:
        return ""
    v = re.sub(r"\s*\((cold spring harbor laboratory|elsevier bv|springer nature)\)\s*$", "", v, flags=re.I)
    return v.strip()


# --- OpenAlex ----------------------------------------------------------------
def fetch_openalex() -> list[dict]:
    params = {
        "filter": f"author.orcid:https://orcid.org/{ORCID}",
        "per-page": "200",
        "page": "1",  # basic paging works without a key (cursor paging needs one); fine for <10k works
        "select": "id,doi,title,display_name,publication_year,publication_date,type,ids,"
                  "primary_location,best_oa_location,authorships,biblio,is_paratext,is_retracted",
    }
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    if os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = os.environ["OPENALEX_MAILTO"]
    works = []
    while True:
        d = json.loads(get("https://api.openalex.org/works", params))
        works.extend(d["results"])
        if not d["results"] or len(works) >= d["meta"]["count"]:
            break
        params["page"] = str(int(params["page"]) + 1)
    return works


def from_openalex(w: dict) -> dict:
    src = ((w.get("primary_location") or {}).get("source") or {})
    venue = clean_venue(src.get("display_name"))
    pmid = (w.get("ids") or {}).get("pmid")
    pmid = pmid.rstrip("/").rsplit("/", 1)[-1] if pmid else None
    b = w.get("biblio") or {}
    oa = w.get("best_oa_location") or {}
    typ = w.get("type") or "article"
    doi = norm_doi(w.get("doi"))
    if PREPRINT_VENUES.search(venue):
        typ = "preprint"
    elif typ == "preprint" and venue and not REPOSITORY_VENUES.search(venue):
        typ = "article"  # e.g. Genome Research "advance online" papers share the 10.1101 prefix
    return {
        "doi": doi,
        "pmid": pmid,
        "openalex": w["id"].rsplit("/", 1)[-1],
        "title": clean_title(w.get("title") or w.get("display_name") or ""),
        "authors": [short_name((a.get("author") or {}).get("display_name") or a.get("raw_author_name") or "")
                    for a in w.get("authorships") or []],
        "venue": venue,
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "volume": b.get("volume"),
        "issue": b.get("issue"),
        "pages": "-".join(x for x in (b.get("first_page"), b.get("last_page")) if x) or None,
        "type": typ,
        "oa_url": oa.get("pdf_url") or oa.get("landing_page_url"),
        "_src_type": w.get("type"),
        "_paratext": w.get("is_paratext"),
    }


def keep(rec: dict, reasons: dict) -> bool:
    def drop(why):
        reasons[why] = reasons.get(why, 0) + 1
        return False
    if rec["_src_type"] not in KEEP_TYPES:
        return drop(f"type:{rec['_src_type']}")
    if rec["_paratext"]:
        return drop("paratext")
    if PARATEXT_TITLE.search(re.sub(r"<[^>]+>", "", rec["title"])):
        return drop("correction/review-report title")
    if rec["doi"] and rec["doi"].startswith(REPOSITORY_DOI_PREFIXES):
        return drop("repository DOI (figshare/zenodo/...)")
    if not rec["title"] or not rec["year"]:
        return drop("missing title/year")
    return True


# --- PubMed ------------------------------------------------------------------
def ncbi_params(p: dict) -> dict:
    p = {**p, "tool": "luscombelab-website"}
    if os.environ.get("NCBI_API_KEY"):
        p["api_key"] = os.environ["NCBI_API_KEY"]
    return p


def pubmed_search() -> list[str]:
    d = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                       ncbi_params({"db": "pubmed", "term": PUBMED_QUERY, "retmax": "1000", "retmode": "json"})))
    return d["esearchresult"]["idlist"]


def pubmed_fetch(pmids: list[str]) -> list[dict]:
    out = []
    for i in range(0, len(pmids), 150):
        time.sleep(0.4)
        xml = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                  ncbi_params({"db": "pubmed", "id": ",".join(pmids[i:i + 150]), "retmode": "xml"}),
                  accept="application/xml")
        root = ET.fromstring(xml)
        for art in root.findall("PubmedArticle"):
            out.append(from_pubmed(art))
    return out


def _text(el) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def from_pubmed(art) -> dict:
    mc = art.find("MedlineCitation")
    a = mc.find("Article")
    title_el = a.find("ArticleTitle")
    # keep <i>/<sub>/<sup> from PubMed XML
    raw = ET.tostring(title_el, encoding="unicode", method="xml") if title_el is not None else ""
    raw = re.sub(r"^<ArticleTitle[^>]*>|</ArticleTitle>$", "", raw)
    authors = []
    for au in a.findall("AuthorList/Author"):
        if au.find("CollectiveName") is not None:
            authors.append(_text(au.find("CollectiveName")))
        else:
            authors.append(f"{_text(au.find('Initials'))} {_text(au.find('LastName'))}".strip())
    year = _text(a.find("Journal/JournalIssue/PubDate/Year")) or \
        _text(a.find("Journal/JournalIssue/PubDate/MedlineDate"))[:4] or \
        _text(art.find("PubmedData/History/PubMedPubDate[@PubStatus='pubmed']/Year"))
    doi = None
    for aid in art.findall("PubmedData/ArticleIdList/ArticleId"):
        if aid.get("IdType") == "doi":
            doi = norm_doi(aid.text)
    pub_types = {_text(p).lower() for p in a.findall("PublicationTypeList/PublicationType")}
    typ = "review" if "review" in pub_types else "preprint" if "preprint" in pub_types else "article"
    paratext = bool(pub_types & {"published erratum", "retraction of publication", "comment"}) and "journal article" not in pub_types
    return {
        "doi": doi,
        "pmid": _text(mc.find("PMID")),
        "openalex": None,
        "title": clean_title(raw),
        "authors": authors,
        "venue": _text(a.find("Journal/ISOAbbreviation")) or _text(a.find("Journal/Title")),
        "year": int(year) if year[:4].isdigit() else None,
        "date": None,
        "volume": _text(a.find("Journal/JournalIssue/Volume")) or None,
        "issue": _text(a.find("Journal/JournalIssue/Issue")) or None,
        "pages": _text(a.find("Pagination/MedlinePgn")) or None,
        "type": typ,
        "oa_url": None,
        "_src_type": typ,
        "_paratext": paratext,
    }


# --- merge -------------------------------------------------------------------
def rank(rec: dict) -> tuple:
    """Higher is better when choosing between duplicate versions of the same paper."""
    venue = rec["venue"] or ""
    return (
        rec["type"] != "preprint",
        bool(venue) and not REPOSITORY_VENUES.search(venue) and not PREPRINT_VENUES.search(venue),
        bool(rec["doi"]),
        bool(rec["pmid"]),
        -(rec["year"] or 9999),  # earliest record of the final version
    )


def _tokens(title: str) -> set[str]:
    t = re.sub(r"<[^>]+>", "", html.unescape(title)).lower()
    return set(re.findall(r"[a-z0-9]+", t))


def _first_author(rec: dict) -> str:
    return (rec["authors"][0].split()[-1].lower() if rec["authors"] else "")


def is_weak(rec: dict) -> bool:
    """Preprints and repository copies are candidates to fold into a published version."""
    return rec["type"] == "preprint" or not rec["doi"] or bool(REPOSITORY_VENUES.search(rec["venue"] or ""))


def fuzzy_fold(records: list[dict], threshold: float = 0.8) -> tuple[list[dict], list[str]]:
    """Fold a weak record into a stronger one when first authors match and >=80% of the
    shorter title's words appear in the other title. Catches preprints renamed on
    publication and repository copies such as "Title (vol 12, pg R101, 2011)"."""
    strong = [r for r in records if not is_weak(r)]
    out, log = [], []
    for r in records:
        if not is_weak(r):
            out.append(r)
            continue
        tr, fa = _tokens(r["title"]), _first_author(r)
        match = None
        for s in strong:
            if s is r or _first_author(s) != fa or (s["year"] or 0) < (r["year"] or 0) - 1:
                continue
            ts = _tokens(s["title"])
            shorter = min(len(tr), len(ts))
            if shorter >= 5 and len(tr & ts) / shorter >= threshold:
                match = s
                break
        if match is None:
            out.append(r)
        else:
            merge_pair(match, r)
            log.append(f"  folded {r['year']} {r['type']} {r.get('doi') or r.get('venue')} -> {match.get('doi')}")
    return out, log


def merge_pair(best: dict, other: dict) -> dict:
    for k in ("doi", "pmid", "openalex", "oa_url", "volume", "issue", "pages", "date"):
        if not best.get(k) and other.get(k) and not (k == "doi" and other["type"] == "preprint"):
            best[k] = other[k]
    if other["type"] == "preprint" and best["type"] != "preprint" and other.get("doi"):
        best.setdefault("preprint_doi", other["doi"])
    return best


def dedupe(records: list[dict]) -> tuple[list[dict], int]:
    by_key: dict[str, dict] = {}
    alias: dict[str, str] = {}
    merged = 0
    for r in records:
        keys = [k for k in (f"doi:{r['doi']}" if r["doi"] else None,
                            f"pmid:{r['pmid']}" if r["pmid"] else None,
                            f"t:{norm_title(r['title'])}") if k]
        hit = next((alias[k] for k in keys if k in alias), None)
        if hit is None:
            canon = keys[0]
            by_key[canon] = r
        else:
            merged += 1
            cur = by_key[hit]
            a, b = (r, cur) if rank(r) > rank(cur) else (cur, r)
            by_key[hit] = merge_pair(a, b)
            canon = hit
        for k in keys:
            alias.setdefault(k, canon)
        for k in ("doi", "pmid"):
            v = by_key[canon].get(k)
            if v:
                alias.setdefault(f"{k}:{v}", canon)
    return list(by_key.values()), merged


def finalize(r: dict) -> dict:
    r = {k: v for k, v in r.items() if not k.startswith("_")}
    r["id"] = f"doi:{r['doi']}" if r["doi"] else f"pmid:{r['pmid']}" if r["pmid"] else f"openalex:{r['openalex']}"
    return {k: r[k] for k in sorted(r) if r[k] not in (None, "", [])}


PEER_REVIEW_OUTPUT = OUTPUT.parent / "peer_reviews_auto.json"


def journal_name(group_id: str, fallback: str | None) -> str | None:
    """Turn an ORCID review-group-id such as 'issn:2041-1723' into a journal title.

    ORCID's own group-id lookup needs an authenticated client, so resolve ISSNs
    through OpenAlex instead and fall back to the convening organisation name.
    """
    if group_id and group_id.lower().startswith("issn:"):
        issn = group_id.split(":", 1)[1].strip()
        try:
            params = {"select": "display_name"}
            if os.environ.get("OPENALEX_API_KEY"):
                params["api_key"] = os.environ["OPENALEX_API_KEY"]
            src = json.loads(get(f"https://api.openalex.org/sources/issn:{issn}", params))
            if src.get("display_name"):
                return src["display_name"]
        except Exception as e:  # unresolved ISSN: use the fallback below
            print(f"  could not resolve {group_id}: {e}", file=sys.stderr)
    return fallback


def fetch_peer_reviews() -> None:
    """Write ORCID's public peer-review records as [{journal, year, source}]."""
    data = json.loads(get(f"https://pub.orcid.org/v3.0/{ORCID}/peer-reviews"))
    out = []
    for group in data.get("group", []):
        for pr_group in group.get("peer-review-group", []):
            for s in pr_group.get("peer-review-summary", []):
                org = (s.get("convening-organization") or {}).get("name")
                journal = journal_name(s.get("review-group-id") or "", org)
                year = (((s.get("completion-date") or {}).get("year")) or {}).get("value")
                if journal:
                    out.append({"journal": journal, "year": int(year) if year else None, "source": "orcid"})
    out.sort(key=lambda r: (-(r["year"] or 0), r["journal"].lower()))
    text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if PEER_REVIEW_OUTPUT.exists() and PEER_REVIEW_OUTPUT.read_text(encoding="utf-8") == text:
        print("Peer reviews: no changes.", file=sys.stderr)
    else:
        PEER_REVIEW_OUTPUT.write_text(text, encoding="utf-8")
        print(f"Peer reviews: wrote {len(out)} record(s) to {PEER_REVIEW_OUTPUT}", file=sys.stderr)


def main() -> int:
    try:  # a peer-review hiccup must never block the publication list
        fetch_peer_reviews()
    except Exception as e:
        print(f"Peer reviews: fetch failed, keeping the existing file: {e}", file=sys.stderr)

    reasons: dict[str, int] = {}
    print("OpenAlex: fetching works for ORCID", ORCID, file=sys.stderr)
    oa_raw = fetch_openalex()
    oa = [r for r in map(from_openalex, oa_raw) if keep(r, reasons)]
    print(f"  {len(oa_raw)} works, {len(oa)} kept; dropped: {reasons}", file=sys.stderr)

    try:
        pmids = pubmed_search()
        known = {r["pmid"] for r in oa if r["pmid"]}
        missing = [p for p in pmids if p not in known]
        print(f"PubMed: {len(pmids)} hits for {PUBMED_QUERY!r}, {len(missing)} not linked in OpenAlex", file=sys.stderr)
        pm_reasons: dict[str, int] = {}
        pm = [r for r in pubmed_fetch(missing) if keep(r, pm_reasons)] if missing else []
    except Exception as e:  # PubMed is a cross-check only; never fail the run on it
        print(f"PubMed cross-check failed, continuing with OpenAlex only: {e}", file=sys.stderr)
        pm = []

    records, merged = dedupe(oa + pm)
    records, folded = fuzzy_fold(records)
    pm_only = [r for r in records if not r.get("openalex")]
    print(f"Merged {merged} exact duplicates and {len(folded)} preprint/repository copies "
          f"-> {len(records)} publications", file=sys.stderr)
    for line in folded:
        print(line, file=sys.stderr)
    if pm_only:
        print(f"{len(pm_only)} added from PubMed only (check these for wrong-author matches):", file=sys.stderr)
        for r in sorted(pm_only, key=lambda r: -(r["year"] or 0)):
            print(f"  {r['year']}  pmid:{r['pmid']}  {re.sub('<[^>]+>', '', r['title'])[:90]}", file=sys.stderr)

    # newest first; title as a stable tie-breaker so reruns produce identical output
    out = sorted((finalize(r) for r in records),
                 key=lambda r: (r.get("year") or 0, r.get("date") or "", r["title"].lower()), reverse=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == text:
        print("No changes.", file=sys.stderr)
    else:
        OUTPUT.write_text(text, encoding="utf-8")
        print(f"Wrote {len(out)} publications to {OUTPUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
