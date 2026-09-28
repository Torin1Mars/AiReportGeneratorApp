import json
from pathlib import Path
import docx

from App.domain.TemplateLoader import TemplateLoader
from App.domain.feaReportsConverter import FeaReportsConverter

class InputFilesLoader:
    def __init__(self):
        self.convertedTemplate:object = None
        self.convertedReports:object = None
        self.convertedAdditionalDocs:object = None

        self.feaReportsConverter = FeaReportsConverter()
        self.templateLoader = TemplateLoader()

    def loadInputFiles (self, template_filePath:str,
                        reports_filesPaths:list[list[str]],
                        explanation_filesPaths:list[str])->object:

        if template_filePath:
            try:
                self.convertedTemplate = self.templateLoader.unpackTemplateFile(template_filePath)
            except Exception as e:
                print("Couldn't load template file")
                print(e)

        if reports_filesPaths:
            try:
                self.convertedReports = self._unpackReportsDocs(reports_filesPaths)
            except Exception as e:
                print("Couldn't load reports files")
                print(e)

        if explanation_filesPaths:
            try:
                self.convertedAdditionalDocs = self._unpackAditionalDocs(explanation_filesPaths)
            except Exception as e:
                print("Couldn't load additional files")
                print(e)

        convertedData = {"Report Template":self.convertedTemplate,
                         "Simulation Reports":self.convertedReports,
                         "Additional Documents":self.convertedAdditionalDocs}

        packedData = json.dumps(convertedData, indent=4,ensure_ascii=False)
        return packedData

    def _unpackTemplateDoc(self, filePath:str)->object:
        convertedTemplate = self.templateLoader.unpackTemplateFile(filePath)
        return convertedTemplate

    def _unpackReportsDocs(self, filesPaths)->object:
        convertedReports = self.feaReportsConverter.readFeaReports(filesPaths)
        return convertedReports

    def _unpackAditionalDocs(self, filesPaths:list[str])->object:
        readedDocs = {}

        #Reading docx file as string
        for path in filesPaths:
            try:
                docName:str = Path(path).stem
                doc = docx.Document(path)
                paragraphs_text = [p.text for p in doc.paragraphs]

                data  = "\n".join(paragraphs_text)

                currentDoc :dict = {}
                currentDoc["Document"] = docName
                currentDoc["Document data"] = data

                readedDocs[docName] = currentDoc

            except Exception as e:
                print(f"Reding error: {e}")

        aditionalDocs:dict = {"Additional documents": readedDocs}
        jsonOutput = json.dumps(aditionalDocs, indent=4,ensure_ascii=False)

        return jsonOutput
