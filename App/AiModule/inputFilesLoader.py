import json
import sys
from typing import Any

from App.AiModule.wordDocumentsConverter import WordDocConverter


class InputFilesLoader:

    def __init__(self):
        self.wordDocConverter = WordDocConverter()

    def loadInputFiles (self, template_filesPaths:list[list[str]],
                        reports_filesPaths:list[list[str]],
                        explanation_filesPaths:list[list[str]]):

        if template_filesPaths:
            try:
                convertedTemplate = self._unpackTemplateDocs(template_filesPaths)

            except Exception as e:
                print("Couldn't load template doc")
                print(e)

        if reports_filesPaths:
            try:
                self._unpackReportsDocs(template_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)

        if explanation_filesPaths:
            try:
                self._unpackExplanationDocs(template_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)


    def _unpackTemplateDocs(self, template_filesPaths:list[list[str]])->dict[str, Any]:
        path = template_filesPaths[0]
        return  self.wordDocConverter.docx_to_json(path)


    def _unpackReportsDocs(self, template_filesPaths):
        pass


    def _unpackExplanationDocs(self, template_filesPaths):
        pass

