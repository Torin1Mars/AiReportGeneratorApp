import json
import sys

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

class InputFilesLoader:

    def loadFiles(self, filesPaths:list[str])->list[list[str]]:

        try :
            convertedFiles = []

            for filePath in filesPaths:
                convertedFiles.append(self.convert_docx_to_json(filePath))
            return convertedFiles

        except Exception as e:
            print(e)


    def convert_docx_to_json(self, file_path)->list[str]:
        # Load a .docx from file_path and return a JSON-serializable
        doc = Document(file_path)

        content = []
        body = doc.element.body
        for child in body.iterchildren():
            if child.tag == qn("w:p"):
                content.append(self._paragraph_to_dict(Paragraph(child, doc)))
            elif child.tag == qn("w:tbl"):
                content.append(self._table_to_dict(Table(child, doc)))
            # sectPr and other structural elements are skipped
        return content

    def _run_to_dict(self, run):
        return {
            "text": run.text,
            "bold": run.bold,
            "italic": run.italic,
            "underline": bool(run.underline) if run.underline is not None else None,
            "font_name": run.font.name,
            "font_size": run.font.size.pt if run.font.size else None,
            "color": str(run.font.color.rgb) if run.font.color and run.font.color.rgb else None,
        }

    def _table_to_dict(self, table):
        rows = []
        for row in table.rows:
            cells = []
        for cell in row.cells:
            # Join all paragraph text within the cell
            cells.append("\n".join(p.text for p in cell.paragraphs))
        rows.append(cells)
        return {
            "type": "table",
            "style": table.style.name if table.style else None,
            "rows": rows,
        }

    def _paragraph_to_dict(self, paragraph):
        return {
            "type": "paragraph",
            "text": paragraph.text,
            "style": paragraph.style.name if paragraph.style else None,
            "alignment": str(paragraph.alignment) if paragraph.alignment is not None else None,
            "runs": [self._run_to_dict(r) for r in paragraph.runs]
        }


"""
Load a .docx file by path and convert its content into a JSON-serializable
structure: paragraphs and tables (in document order).
"""

'''
def _core_properties_to_dict(doc):
    props = doc.core_properties
    return {
        "title": props.title,
        "author": props.author,
        "subject": props.subject,
        "keywords": props.keywords,
        "comments": props.comments,
        "category": props.category,
        "created": props.created.isoformat() if props.created else None,
        "modified": props.modified.isoformat() if props.modified else None,
        "last_modified_by": props.last_modified_by,
        "revision": props.revision,
    }

'''

'''
def main():
    if len(sys.argv) < 2:
        print("Usage: python docx_to_json.py <input.docx> [output.json]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    result = convert_docx_to_json(input_path)
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Wrote JSON to {output_path}")
    else:
        print(output_json)'''
