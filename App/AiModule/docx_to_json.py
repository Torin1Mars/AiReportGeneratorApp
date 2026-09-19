"""
docx_to_json.py — convert .docx documents into JSON-serializable structures.

    docx_to_plain_json(path)      -> list[str]
        Raw text only. One list item ("row") per paragraph, no formatting.

    docx_to_formatted_json(path)  -> dict
        Paragraphs, runs and tables together with their formatting
        (styles, alignment, lists, bold/italic/underline, font, size, color,
        hyperlinks, indents, spacing, table structure ...).

Both functions optionally write the result to a JSON file (UTF-8, so Cyrillic
and other non-ASCII text stays readable).

Usage (from inside another function):

    from docx_to_json import docx_to_plain_json, docx_to_formatted_json

    def process(path):
        rows = docx_to_plain_json(path)                 # list[str]
        data = docx_to_formatted_json(path, "out.json")  # dict (also saved)
        ...

Requires: python-docx >= 1.0   ->   pip install python-docx
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Union

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table, _Cell
from docx.text.hyperlink import Hyperlink
from docx.text.paragraph import Paragraph

PathLike = Union[str, Path]


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _iter_blocks(parent) -> Iterator[Union[Paragraph, Table]]:
    """Yield paragraphs and tables of a Document or table cell in real document order."""
    parent_elm = parent._tc if isinstance(parent, _Cell) else parent.element.body
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _row_cells(table: Table, row) -> list[_Cell]:
    """Real <w:tc> cells of a row (merged cells are NOT repeated, unlike row.cells)."""
    return [_Cell(tc, table) for tc in row._tr.tc_lst]


def _dump(data: Any, json_path: PathLike) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- #
# 1) Plain text: one row per paragraph, formatting ignored
# --------------------------------------------------------------------------- #
def docx_to_plain_json(
    docx_path: PathLike,
    json_path: Optional[PathLike] = None,
    *,
    skip_empty: bool = True,
    include_tables: bool = True,
) -> list[str]:
    """
    Return the document's raw text as a list of strings — every paragraph
    becomes a new row. Formatting is ignored.

    skip_empty      : drop paragraphs that are empty / whitespace-only.
    include_tables  : also read text inside tables (each cell paragraph is a row,
                      in document order). Set False to ignore tables.
    json_path       : if given, the list is also saved there as JSON.
    """
    doc = Document(str(docx_path))
    rows: list[str] = []

    def walk(parent) -> None:
        for block in _iter_blocks(parent):
            if isinstance(block, Paragraph):
                text = block.text
                if skip_empty and not text.strip():
                    continue
                rows.append(text)
            elif include_tables:
                for row in block.rows:
                    for cell in _row_cells(block, row):
                        walk(cell)

    walk(doc)

    if json_path:
        _dump(rows, json_path)
    return rows


# --------------------------------------------------------------------------- #
# 2) Formatting-aware conversion
# --------------------------------------------------------------------------- #
def _style_chain(style) -> Iterator[Any]:
    """The style itself, then the style it is based on, and so on."""
    while style is not None:
        yield style
        style = style.base_style


class _FormattedConverter:
    def __init__(self, doc, *, merge_runs: bool, include_tables: bool, skip_empty: bool):
        self.doc = doc
        self.merge_runs = merge_runs
        self.include_tables = include_tables
        self.skip_empty = skip_empty
        self.defaults = self._read_doc_defaults()
        self._num_cache: dict[tuple[int, int], Optional[str]] = {}

    # ---- document-wide defaults (used as the last fallback) -------------- #
    def _read_doc_defaults(self) -> dict:
        out: dict = {}
        rpr = self.doc.styles.element.xpath("w:docDefaults/w:rPrDefault/w:rPr")
        if rpr:
            rfonts = rpr[0].find(qn("w:rFonts"))
            if rfonts is not None and rfonts.get(qn("w:ascii")):
                out["font"] = rfonts.get(qn("w:ascii"))
            sz = rpr[0].find(qn("w:sz"))
            if sz is not None:
                out["size_pt"] = int(sz.get(qn("w:val"))) / 2
        return out

    # ---- property resolution: direct formatting -> styles ---------------- #
    @staticmethod
    def _resolve_run(run, paragraph, getter: Callable[[Any], Any]):
        value = getter(run.font)
        if value is not None:
            return value
        for style in (run.style, paragraph.style):
            for st in _style_chain(style):
                value = getter(st.font)
                if value is not None:
                    return value
        return None

    @staticmethod
    def _resolve_para(paragraph, getter: Callable[[Any], Any]):
        value = getter(paragraph.paragraph_format)
        if value is not None:
            return value
        for st in _style_chain(paragraph.style):
            value = getter(st.paragraph_format)
            if value is not None:
                return value
        return None

    # ---- runs ------------------------------------------------------------ #
    @staticmethod
    def _color(font) -> Optional[str]:
        color = font.color
        if color is None or color.type is None:
            return None
        if color.rgb is not None:
            return str(color.rgb)
        if color.theme_color is not None:
            return f"theme:{color.theme_color.name.lower()}"
        return None

    def _run_format(self, run, paragraph) -> dict:
        res = lambda getter: self._resolve_run(run, paragraph, getter)  # noqa: E731
        fmt: dict[str, Any] = {}

        for key in ("bold", "italic", "strike", "all_caps", "small_caps", "superscript", "subscript"):
            if res(lambda f, k=key: getattr(f, k)):
                fmt[key] = True

        underline = res(lambda f: f.underline)
        if underline not in (None, False) and getattr(underline, "name", "") != "NONE":
            fmt["underline"] = True if underline is True else underline.name.lower()

        name = res(lambda f: f.name) or self.defaults.get("font")
        if name:
            fmt["font"] = name

        size = res(lambda f: f.size)
        if size is not None:
            fmt["size_pt"] = round(size.pt, 1)
        elif "size_pt" in self.defaults:
            fmt["size_pt"] = self.defaults["size_pt"]

        color = res(self._color)
        if color:
            fmt["color"] = color

        highlight = res(lambda f: f.highlight_color)
        if highlight is not None:
            fmt["highlight"] = highlight.name.lower()

        return fmt

    def _run(self, run, paragraph, hyperlink: Optional[str]) -> dict:
        out: dict[str, Any] = {"text": run.text}
        fmt = self._run_format(run, paragraph)
        if fmt:
            out["format"] = fmt
        if hyperlink:
            out["hyperlink"] = hyperlink
        if run._r.xpath(".//w:drawing") or run._r.xpath(".//w:pict"):
            out["has_image"] = True
        return out

    def _runs(self, paragraph: Paragraph) -> list[dict]:
        items: list[dict] = []
        for item in paragraph.iter_inner_content():  # yields Run and Hyperlink in order
            if isinstance(item, Hyperlink):
                url = item.url or None
                items.extend(self._run(r, paragraph, url) for r in item.runs)
            else:
                items.append(self._run(item, paragraph, None))

        items = [r for r in items if r["text"] or r.get("has_image")]
        if not self.merge_runs:
            return items

        # Word splits text into many runs; glue neighbours with identical formatting.
        merged: list[dict] = []
        for run in items:
            prev = merged[-1] if merged else None
            if (
                prev
                and not run.get("has_image")
                and not prev.get("has_image")
                and run.get("format") == prev.get("format")
                and run.get("hyperlink") == prev.get("hyperlink")
            ):
                prev["text"] += run["text"]
            else:
                merged.append(run)
        return merged

    # ---- lists ------------------------------------------------------------ #
    @staticmethod
    def _find_numpr(paragraph: Paragraph):
        pPr = paragraph._p.pPr
        if pPr is not None and pPr.numPr is not None:
            return pPr.numPr
        for st in _style_chain(paragraph.style):  # e.g. "List Bullet" carries numbering
            st_ppr = st.element.pPr
            if st_ppr is not None and st_ppr.numPr is not None:
                return st_ppr.numPr
        return None

    def _num_format(self, num_id: int, ilvl: int) -> Optional[str]:
        key = (num_id, ilvl)
        if key not in self._num_cache:
            fmt = None
            try:
                numbering = self.doc.part.numbering_part.element
                abstract = numbering.xpath(f'w:num[@w:numId="{num_id}"]/w:abstractNumId/@w:val')
                if abstract:
                    found = numbering.xpath(
                        f'w:abstractNum[@w:abstractNumId="{abstract[0]}"]'
                        f'/w:lvl[@w:ilvl="{ilvl}"]/w:numFmt/@w:val'
                    )
                    fmt = found[0] if found else None
            except Exception:
                pass
            self._num_cache[key] = fmt
        return self._num_cache[key]

    def _list_info(self, paragraph: Paragraph) -> Optional[dict]:
        numpr = self._find_numpr(paragraph)
        if numpr is None or numpr.numId is None or not numpr.numId.val:
            return None
        num_id = int(numpr.numId.val)
        ilvl = int(numpr.ilvl.val) if numpr.ilvl is not None else 0
        return {"level": ilvl, "format": self._num_format(num_id, ilvl), "num_id": num_id}

    # ---- paragraphs -------------------------------------------------------- #
    @staticmethod
    def _heading_level(style) -> Optional[int]:
        for st in _style_chain(style):
            m = re.fullmatch(r"Heading (\d)", st.name or "")
            if m:
                return int(m.group(1))
        return None

    def _layout(self, paragraph: Paragraph) -> dict:
        out: dict[str, Any] = {}
        for key in ("left_indent", "right_indent", "first_line_indent", "space_before", "space_after"):
            value = self._resolve_para(paragraph, lambda pf, k=key: getattr(pf, k))
            if value is not None:
                out[key + "_pt"] = round(value.pt, 1)
        spacing = self._resolve_para(paragraph, lambda pf: pf.line_spacing)
        if spacing is not None:
            if hasattr(spacing, "pt"):
                out["line_spacing_pt"] = round(spacing.pt, 1)
            else:
                out["line_spacing_multiple"] = round(float(spacing), 2)
        return out

    def _paragraph(self, paragraph: Paragraph) -> dict:
        style = paragraph.style
        out: dict[str, Any] = {"type": "paragraph", "style": style.name if style else None}

        level = self._heading_level(style)
        if level is not None:
            out["heading_level"] = level

        align = self._resolve_para(paragraph, lambda pf: pf.alignment)
        if align is not None:
            out["alignment"] = align.name.lower()

        lst = self._list_info(paragraph)
        if lst:
            out["list"] = lst

        layout = self._layout(paragraph)
        if layout:
            out["layout"] = layout

        out["text"] = paragraph.text
        out["runs"] = self._runs(paragraph)
        return out

    # ---- tables / blocks ---------------------------------------------------- #
    def _table(self, table: Table) -> dict:
        rows = []
        for row in table.rows:
            cells = []
            for cell in _row_cells(table, row):
                tc = cell._tc
                entry: dict[str, Any] = {"blocks": self._blocks(cell)}
                if tc.grid_span > 1:
                    entry["colspan"] = tc.grid_span
                if tc.vMerge:
                    entry["vmerge"] = tc.vMerge  # "restart" = first cell, "continue" = merged into above
                cells.append(entry)
            rows.append(cells)

        out: dict[str, Any] = {"type": "table", "rows": rows}
        if table.style is not None:
            out["style"] = table.style.name
        return out

    def _blocks(self, parent) -> list[dict]:
        blocks: list[dict] = []
        for block in _iter_blocks(parent):
            if isinstance(block, Paragraph):
                if self.skip_empty and not block.text.strip() and not block._p.xpath(".//w:drawing"):
                    continue
                blocks.append(self._paragraph(block))
            elif self.include_tables:
                blocks.append(self._table(block))
        return blocks


def docx_to_formatted_json(
    docx_path: PathLike,
    json_path: Optional[PathLike] = None,
    *,
    merge_runs: bool = True,
    include_tables: bool = True,
    skip_empty: bool = False,
) -> dict:
    """
    Convert a .docx into a JSON-serializable dict that keeps the formatting:

        {
          "source": "file.docx",
          "blocks": [
            {"type": "paragraph", "style": "Heading 1", "heading_level": 1,
             "alignment": "center", "list": {...}, "layout": {...},
             "text": "full paragraph text",
             "runs": [{"text": "...", "format": {"bold": true, "size_pt": 12, ...},
                       "hyperlink": "https://..."}]},
            {"type": "table", "style": "...", "rows": [[{"blocks": [...], "colspan": 2}, ...]]}
          ]
        }

    Run "format" only lists properties that are actually in effect. Values set
    directly on the text as well as values inherited from character/paragraph
    styles (e.g. bold coming from "Heading 1") are resolved.

    merge_runs      : merge neighbouring runs that have identical formatting.
    include_tables  : convert tables (nested blocks per cell). False skips them.
    skip_empty      : drop empty paragraphs (default keeps them to preserve layout).
    json_path       : if given, the result is also saved there as JSON.
    """
    doc = Document(str(docx_path))
    converter = _FormattedConverter(
        doc, merge_runs=merge_runs, include_tables=include_tables, skip_empty=skip_empty
    )
    result = {"source": Path(docx_path).name, "blocks": converter._blocks(doc)}

    if json_path:
        _dump(result, json_path)
    return result
