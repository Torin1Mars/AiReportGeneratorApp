import json
from pathlib import Path
from typing import Any

from App.domain.TemplateLoader import TemplateLoader
from App.domain.feaReportsConverter import FeaReportsConverter

class InputFilesLoader:
    def __init__(self):
        self.convertedTemplate:object
        self.convertedReports:object

        self.feaReportsConverter = FeaReportsConverter()
        self.templateLoader = TemplateLoader()


    def loadInputFiles (self, template_filePath:str,
                        reports_filesPaths:list[list[str]],
                        explanation_filesPaths:list[list[str]]):

        if template_filePath:
            try:

                #TODO its need to set up propper template file loader
                template = self.templateLoader.unpackTemplateFile(template_filePath)
                print(template)

            except Exception as e:
                print("Couldn't load template doc")
                print(e)

        '''if reports_filesPaths:
            try:
                self._unpackReportsDocs(reports_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)'''

        if explanation_filesPaths:
            try:
                self.convertedReports = self._unpackExplanationDocs(explanation_filesPaths)
            except Exception as e:
                print("Couldn't load report docs")
                print(e)


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
