from typing import Any

from App.domain.feaReportsConverter import FeaReportsConverter
from App.domain.wordDocumentsConverter import WordDocConverter





class InputFilesLoader:
    def __init__(self):
        self.wordDocConverter = WordDocConverter()
        self.feaReportsConverter = FeaReportsConverter()

    def loadInputFiles (self, template_filesPaths:list[list[str]],
                        reports_filesPaths:list[list[str]],
                        explanation_filesPaths:list[list[str]]):

        if template_filesPaths:
            try:
                #convertedTemplate = self._unpackTemplateDocs(template_filesPaths)
                pass

            except Exception as e:
                print("Couldn't load template doc")
                print(e)

        if reports_filesPaths:
            try:
                self._unpackReportsDocs(reports_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)

        if explanation_filesPaths:
            try:
                self._unpackExplanationDocs(explanation_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)


    def _unpackTemplateDocs(self, filesPaths:list[list[str]])->dict[str, Any]:
        path = filesPaths[0]
        return  self.wordDocConverter.docx_to_json(path)


    def _unpackReportsDocs(self, filesPaths):
        self.feaReportsConverter.readFeaReports(filesPaths)



    def _unpackExplanationDocs(self, filesPaths):
        pass

