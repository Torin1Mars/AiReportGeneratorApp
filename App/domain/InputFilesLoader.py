import json
from pathlib import Path

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
                        explanation_filesPaths:list[list[str]])->object:

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
                self.convertedAdditionalDocs = self._unpackExplanationDocs(explanation_filesPaths)
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

    def _unpackExplanationDocs(self, filesPaths:list[str])->object:
        readedReports = {}

        try:
            for path in filesPaths:
                number = 1

                with open(path, "r", encoding="utf-8") as file:
                    raw_file_data = file.read()
                    file_name = Path(path).stem

                    if raw_file_data:
                        data = {
                            "filename": file_name,
                            "content": raw_file_data
                        }

                        readedReports[file_name] = raw_file_data
                        number +=1

        except Exception as e:
            print(e)

        jsonOutput = json.dumps(readedReports, indent=4,ensure_ascii=False)

        return jsonOutput
