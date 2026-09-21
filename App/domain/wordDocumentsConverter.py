from __future__ import annotations

from typing import Any, Iterator, Optional, Union

from docx import Document
from docx.document import Document as _Document
from docx.oxml.ns import qn
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.text.run import Run

_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
_EMU_PER_PT = 12700


class WordDocConverter:

    def _pt(self, length) -> Optional[float]:
        """python-docx Length -> points (rounded), or None."""
        return None if length is None else round(length.pt, 2)


    def _style_chain(self, style):
        """Yield a style and all of its base styles."""
        while style is not None:
            yield style
            style = style.base_style

    def _from_styles(self, styles, getter):
        """First non-None value of getter(style) along the style chain."""
        for st in styles:
            val = getter(st)
            if val is not None:
                return val
        return None


    def _underline(self, value) -> Optional[bool]:
        if value is None or isinstance(value, bool):
            return value
        return getattr(value, "name", str(value)).upper() != "NONE"


    # --------------------------------------------------------------------------- #
    # runs
    # --------------------------------------------------------------------------- #
    def _run_format(self, run: Run, par_styles: list) -> dict:
        """Effective run formatting (direct -> character style -> paragraph style)."""
        styles = []
        if run._r.rPr is not None and run._r.rPr.rStyle is not None:
            styles += list(self._style_chain(run.style))
        styles += par_styles

        def resolve(attr):
            val = getattr(run.font, attr)
            if val is None:
                val = self._from_styles(styles, lambda s: getattr(s.font, attr))
            return val

        fmt = {
            "bold": resolve("bold"),
            "italic": resolve("italic"),
            "underline": self._underline(resolve("underline")),
            "strike": resolve("strike"),
            "superscript": run.font.superscript,
            "subscript": run.font.subscript,
            "font": resolve("name"),
            "size": self._pt(resolve("size")),
            "color": None,
            "highlight": run.font.highlight_color.name if run.font.highlight_color else None,
        }
        try:
            if run.font.color is not None and run.font.color.rgb is not None:
                fmt["color"] = str(run.font.color.rgb)
        except Exception:  # theme colours etc.
            pass
        # keep the JSON compact: drop empty / false values
        return {k: v for k, v in fmt.items() if v not in (None, False)}


    def _paragraph_runs(self, par: Paragraph, par_styles: list) -> list:
        """
        Runs in document order. Includes runs inside <w:ins> (tracked insertions)
        and <w:hyperlink>; text inside <w:del> is ignored automatically.
        """
        out: list[dict] = []
        r_elems = par._p.xpath("./w:r | ./w:ins/w:r | ./w:hyperlink/w:r | ./w:hyperlink/w:ins/w:r")

        for r in r_elems:
            run = Run(r, par)
            fmt = self._run_format(run, par_styles)

            # hyperlink target (if the run sits inside a hyperlink)
            parent = r.getparent()
            if parent.tag == qn("w:ins"):
                parent = parent.getparent()
            if parent.tag == qn("w:hyperlink"):
                rid = parent.get(qn("r:id"))
                if rid and rid in par.part.rels:
                    fmt["link"] = par.part.rels[rid].target_ref

            text = run.text
            if text:
                out.append({"text": text, **fmt})

            for br in r.xpath("./w:br[@w:type='page']"):
                out.append({"page_break": True})

            for ext in r.xpath(".//wp:extent"):  # inline / floating pictures (no binary data)
                out.append({
                    "image": True,
                    "width": round(int(ext.get("cx", 0)) / _EMU_PER_PT, 2),
                    "height": round(int(ext.get("cy", 0)) / _EMU_PER_PT, 2),
                })

        # merge neighbouring text runs that have identical formatting
        merged: list[dict] = []
        for item in out:
            if (
                    merged
                    and "text" in item
                    and "text" in merged[-1]
                    and {k: v for k, v in item.items() if k != "text"}
                    == {k: v for k, v in merged[-1].items() if k != "text"}
            ):
                merged[-1]["text"] += item["text"]
            else:
                merged.append(item)
        return merged


    # --------------------------------------------------------------------------- #
    # paragraphs
    # --------------------------------------------------------------------------- #
    def _list_info(self, doc: _Document, par: Paragraph, par_styles: list) -> Optional[dict]:
        """Return {'level', 'ordered'} if the paragraph is a list item."""
        numPr = par._p.pPr.numPr if par._p.pPr is not None else None
        if numPr is None:
            for st in par_styles:
                ppr = st.element.pPr
                if ppr is not None and ppr.numPr is not None:
                    numPr = ppr.numPr
                    break
        if numPr is None or numPr.numId is None or numPr.numId.val == 0:
            return None

        level = numPr.ilvl.val if numPr.ilvl is not None else 0
        ordered = None
        try:
            numbering = doc.part.numbering_part.element
            abs_id = numbering.xpath(
                f"w:num[@w:numId='{numPr.numId.val}']/w:abstractNumId/@w:val"
            )[0]
            fmt = numbering.xpath(
                f"w:abstractNum[@w:abstractNumId='{abs_id}']/w:lvl[@w:ilvl='{level}']/w:numFmt/@w:val"
            )
            if fmt:
                ordered = fmt[0] != "bullet"
        except Exception:
            pass
        return {"level": level, "ordered": ordered}


    def _paragraph(self, doc: _Document, par: Paragraph) -> dict:
        par_styles = list(self._style_chain(par.style))
        pf = par.paragraph_format

        def resolve(attr):
            val = getattr(pf, attr)
            if val is None:
                val = self._from_styles(par_styles, lambda s: getattr(s.paragraph_format, attr))
            return val

        align = resolve("alignment")
        spacing = resolve("line_spacing")
        if spacing is not None and not isinstance(spacing, float):  # exact / at-least in points
            rule = resolve("line_spacing_rule")
            spacing = {"pt": self._pt(spacing), "rule": rule.name.lower() if rule is not None else None}

        style_name = par.style.name if par.style is not None else None
        heading = None
        if style_name and style_name.lower().startswith("heading "):
            tail = style_name.split(" ", 1)[1]
            heading = int(tail) if tail.isdigit() else None
        elif style_name == "Title":
            heading = 0

        data = {
            "type": "paragraph",
            "style": style_name,
            "heading_level": heading,
            "alignment": align.name.lower() if align is not None else None,
            "indent_left": self._pt(resolve("left_indent")),
            "indent_right": self._pt(resolve("right_indent")),
            "indent_first_line": self._pt(resolve("first_line_indent")),
            "space_before": self._pt(resolve("space_before")),
            "space_after": self._pt(resolve("space_after")),
            "line_spacing": spacing,
            "page_break_before": resolve("page_break_before") or None,
            "list": self._list_info(doc, par, par_styles),
            "runs": self._paragraph_runs(par, par_styles),
        }
        return {k: v for k, v in data.items() if v is not None}


    # --------------------------------------------------------------------------- #
    # tables / body traversal
    # --------------------------------------------------------------------------- #
    def _iter_blocks(self, doc: _Document, parent_elm, parent) -> Iterator[Union[Paragraph, Table]]:
        """Paragraphs and tables in real document order (looks inside content controls)."""
        for child in parent_elm.iterchildren():
            if child.tag == qn("w:p"):
                yield Paragraph(child, parent)
            elif child.tag == qn("w:tbl"):
                yield Table(child, parent)
            elif child.tag == qn("w:sdt"):
                content = child.find(qn("w:sdtContent"))
                if content is not None:
                    yield from self._iter_blocks(doc, content, parent)


    def _blocks(self, doc: _Document, parent_elm, parent) -> list:
        out = []
        for block in self._iter_blocks(doc, parent_elm, parent):
            out.append(self._table(doc, block) if isinstance(block, Table) else self._paragraph(doc, block))
        return out


    def _table(self, doc: _Document, table: Table) -> dict:
        rows = []
        for tr in table._tbl.tr_lst:
            cells = []
            for tc in tr.tc_lst:  # real cells only (python-docx repeats merged ones)
                cell = _Cell(tc, table)
                item = {"content": self._blocks(doc, tc, cell)}
                if tc.grid_span and tc.grid_span > 1:
                    item["colspan"] = tc.grid_span
                if tc.vMerge:
                    item["vmerge"] = tc.vMerge  # 'restart' or 'continue'
                cells.append(item)
            rows.append({"cells": cells})
        return {
            "type": "table",
            "style": table.style.name if table.style is not None else None,
            "rows": rows,
        }


    # --------------------------------------------------------------------------- #
    # page setup
    # --------------------------------------------------------------------------- #
    def _sections(self, doc: _Document) -> list:
        result = []
        for s in doc.sections:
            item = {
                "page_width": self._pt(s.page_width),
                "page_height": self._pt(s.page_height),
                "orientation": s.orientation.name.lower() if s.orientation is not None else "portrait",
                "margin_top": self._pt(s.top_margin),
                "margin_bottom": self._pt(s.bottom_margin),
                "margin_left": self._pt(s.left_margin),
                "margin_right": self._pt(s.right_margin),
            }
            for name, part in (("header", s.header), ("footer", s.footer)):
                if not part.is_linked_to_previous:
                    text = "\n".join(p.text for p in part.paragraphs).strip()
                    if text:
                        item[name] = text
            result.append(item)
        return result


    # --------------------------------------------------------------------------- #
    # public API
    # --------------------------------------------------------------------------- #
    def docx_to_json(self, file_path: str) -> dict[str, Any]:
        """
        Open a .docx file and return its content as a JSON-serializable dict:

            {
              "sections": [ {page size, orientation, margins (pt), header, footer}, ... ],
              "content":  [ paragraph | table, ... ]      # document order
            }

        All measurements are in points. No document metadata (author, dates,
        revision number, last modified by, ...) is included.

        Use json.dumps(result, ensure_ascii=False) if you need a string.
        """
        doc = Document(file_path)

        #TODO need to fix section converting :
        return {
            "sections": self._sections(doc),
            #"content": self._blocks(doc, doc.element.body, doc),
        }
