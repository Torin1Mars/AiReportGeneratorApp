import json

from bs4 import BeautifulSoup
from pydantic_core.core_schema import none_schema
from App.data.feaEntity import FeaReportInstance

class FeaReportsConverter:

    def readFeaReports(self, filesPaths:list[str]) ->list[str]:

        for path in filesPaths:
            file = open(path)
            soupDoc = BeautifulSoup(file, "lxml")

            reportId = soupDoc.select_one('h2:nth-of-type(3)')
            docAllTables = soupDoc.select('h2:nth-of-type(3) ~ table')


            productMatherialTable = self._convertMatherialTableToJson(docAllTables[1], "Material")
            gasMatherialTable = self._convertMatherialTableToJson(docAllTables[2], "Gas Material")

            fidelityElement = soupDoc.find('h3', string="Fidelity")
            fidelityTable = fidelityElement.find_next('table')
            #TODO continue to work on parser here:
            convertedFidelityTable = self._convertSimpleTableToJson(fidelityTable, "Fidelity table")




            #for card in soup.select("div.job-card"):
            #title_el = card.select_one("h2.title a")


        '''
        class FeaReportInstance:
        reportTitle:str
        reportDate:str
        simulationSettings:str
        pythicsConditions:str
        monitorsData:str
        sceneInstances:list[ReportSceneInstance]'''

        return list["Ok"]

    def _convertSimpleTableToJson(self, htmTable, tableTitle:str) -> object :
        data = []
        data.append({"Table title :", tableTitle})

        rows = htmTable.find_all('tr')
        headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]

        for row in rows[1:]:
            cells = row.find_all('td')
            if not cells:
                continue
            values = [td.get_text(strip=True) for td in cells]
            data.append(dict(zip(headers, values)))

        formatedTable = json.dumps(data, indent=2, ensure_ascii=False)
        return formatedTable

    def _convertMatherialTableToJson(self, htmTable, tableTitle:str) -> object :
        result = {}
        result["Table title"] = tableTitle

        for row in htmTable.select('tr'):
            th = row.find('th')
            td = row.find('td')

            if th and td:
                rowName = th.get_text(strip=True)
                if rowName == "Description":
                    rowData = td.get_text().splitlines()[0]
                    result[rowName] = rowData
                else:
                    key = rowName
                    value = td.get_text(strip=True)
                    result[key] = value

        formatedTable = json.dumps(result, indent=2, ensure_ascii=False)
        return formatedTable
