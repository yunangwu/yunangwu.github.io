#!/usr/bin/env python3
"""Generate _publications/*.md from _bibliography/publications.bib.

Runs automatically before every Jekyll build (see _plugins/bib2pubs.rb), so the
.bib file is the only thing to edit. No third-party dependencies.

Usage: python3 scripts/bib2pubs.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "_bibliography", "publications.bib")
PUB_DIR = os.path.join(ROOT, "_publications")
MARKER = "generated_by: bib2pubs"

# Name to highlight in author lists, read from _config.yml (author.name)
def site_author():
    with open(os.path.join(ROOT, "_config.yml"), encoding="utf-8") as f:
        in_author = False
        for line in f:
            if line.startswith("author:"):
                in_author = True
            elif in_author and re.match(r"\s+name\s*:", line):
                return line.split(":", 1)[1].split("#")[0].strip().strip('"\'')
    return ""

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

ACCENTS = {
    "'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308",
    "~": "\u0303", "=": "\u0304", ".": "\u0307", "c": "\u0327", "v": "\u030c", "u": "\u0306", "H": "\u030b",
}


# ---------------------------------------------------------------- parsing

def parse_bib(text):
    """Return a list of (type, key, fields, raw_entry) tuples."""
    entries = []
    i = 0
    while True:
        m = re.compile(r"@(\w+)\s*\{").search(text, i)
        if not m:
            break
        etype = m.group(1).lower()
        start, j, depth = m.start(), m.end(), 1
        while depth and j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        raw = text[start:j]
        i = j
        if etype in ("comment", "preamble", "string"):
            continue
        body = text[m.end():j - 1]
        key, _, rest = body.partition(",")
        entries.append((etype, key.strip(), parse_fields(rest), raw))
    return entries


def parse_fields(s):
    fields, i = {}, 0
    while i < len(s):
        m = re.compile(r"\s*([\w-]+)\s*=\s*").match(s, i)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        if s[i] == "{":
            depth, j = 1, i + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(s[j], 0)
                j += 1
            value, i = s[i + 1:j - 1], j
        elif s[i] == '"':
            j = s.index('"', i + 1)
            value, i = s[i + 1:j], j + 1
        else:
            j = i
            while j < len(s) and s[j] not in ",\n":
                j += 1
            value, i = s[i:j].strip(), j
        fields[name] = re.sub(r"\s+", " ", value).strip()
        m = re.compile(r"\s*,?").match(s, i)
        i = m.end()
    return fields


def delatex(s):
    s = re.sub(r"\\([`'^\"~=.]|[cvuH](?=[\s{]))\s*\{?\\?([A-Za-z])\}?",
               lambda m: m.group(2) + ACCENTS[m.group(1)], s)
    s = s.replace("--", "\u2013").replace("\\&", "&").replace("~", " ")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    import unicodedata
    return unicodedata.normalize("NFC", s.replace("{", "").replace("}", "")).strip()


def authors(field):
    names = []
    for a in re.split(r"\s+and\s+", field):
        a = delatex(a)
        if "," in a:
            last, first = [p.strip() for p in a.split(",", 1)]
            a = f"{first} {last}"
        names.append(a)
    return names


# ---------------------------------------------------------------- output

def html_escape(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def yaml_str(s):
    return "'" + s.replace("'", "''") + "'"


def category(etype, f):
    if "category" in f:
        return f["category"].strip()
    if etype == "article" and "arxiv" not in f.get("journal", "").lower():
        return "manuscripts"
    if etype in ("inproceedings", "conference", "incollection", "inbook"):
        return "conferences"
    return "preprints"


def venue(f):
    v = f.get("booktitle") or f.get("journal")
    if not v and f.get("eprint"):
        v = f"arXiv preprint arXiv:{f['eprint']}"
    return delatex(v or "")


def paper_url(f):
    if f.get("url"):
        return f["url"]
    if f.get("doi"):
        return "https://doi.org/" + f["doi"]
    if f.get("eprint"):
        return "https://arxiv.org/abs/" + f["eprint"]
    return ""


def render(etype, key, f, me):
    title = delatex(f["title"])
    year = int(f["year"])
    month = f.get("month", "1").strip().lower()[:3]
    month = MONTHS.get(month) or int(re.sub(r"\D", "", month) or 1)
    day = int(f.get("day", 1))
    date = f"{year:04d}-{month:02d}-{day:02d}"
    slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    v = venue(f)

    names = [f"<b>{html_escape(n)}</b>" if n == me else html_escape(n) for n in authors(f["author"])]
    authors_html = ", ".join(names)
    citation = f'{authors_html}. ({year}). &quot;{html_escape(title)}.&quot; <i>{html_escape(v)}</i>.'

    links = []
    url = paper_url(f)
    if f.get("url") or f.get("doi"):
        links.append(("Paper", url))
    if f.get("eprint"):
        links.append(("arXiv", "https://arxiv.org/abs/" + f["eprint"]))
    if f.get("code"):
        links.append(("Code", f["code"]))
    if f.get("slides"):
        links.append(("Slides", f["slides"]))

    fm = [
        "---",
        f"title: {yaml_str(title)}",
        "collection: publications",
        f"category: {category(etype, f)}",
        f"date: {date}",
        f"venue: {yaml_str(v)}",
        f"authors: {yaml_str(authors_html)}",
    ]
    if f.get("abbr"):
        fm.append(f"abbr: {yaml_str(delatex(f['abbr']))}")
    if f.get("note"):
        fm.append(f"note: {yaml_str(delatex(f['note']))}")
    if url:
        fm.append(f"paperurl: {yaml_str(url)}")
    fm.append(f"citation: {yaml_str(citation)}")
    fm.append("links:")
    for name, href in links:
        fm.append(f"  - name: {name}")
        fm.append(f"    url: {yaml_str(href)}")
    fm.append(MARKER)
    fm.append("---")
    return date, slug, "\n".join(fm) + "\n"


def write_if_changed(path, content):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            if fh.read() == content:
                return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return True


def main():
    with open(BIB, encoding="utf-8") as fh:
        entries = parse_bib(fh.read())
    me = site_author()
    os.makedirs(PUB_DIR, exist_ok=True)

    keep_md, changed = set(), 0
    for etype, key, f, raw in entries:
        missing = [k for k in ("title", "author", "year") if k not in f]
        if missing:
            print(f"bib2pubs: skipping {key}: missing {', '.join(missing)}", file=sys.stderr)
            continue
        date, slug, md = render(etype, key, f, me)
        md_name = f"{date}-{slug}.md"
        keep_md.add(md_name)
        changed += write_if_changed(os.path.join(PUB_DIR, md_name), md)

    # Remove files generated earlier for entries that no longer exist (hand-written files are left alone)
    for name in os.listdir(PUB_DIR):
        path = os.path.join(PUB_DIR, name)
        if name not in keep_md and name.endswith(".md"):
            with open(path, encoding="utf-8") as fh:
                if MARKER in fh.read():
                    os.remove(path)
                    changed += 1

    print(f"bib2pubs: {len(keep_md)} publications ({changed} files updated)")


if __name__ == "__main__":
    main()
