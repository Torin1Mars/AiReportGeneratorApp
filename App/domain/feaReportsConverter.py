from bs4 import BeautifulSoup
from pydantic_core.core_schema import none_schema
from App.data.feaEntity import FeaReportInstance

class FeaReportsConverter:

    def readFeaReports(self, filesPaths:list[str]) ->list[str]:

        for path in filesPaths:
            file = open(path)
            soup = BeautifulSoup(file, "lxml")

            # TODO Continue working about report file persing
            '''
            for card in soup.select("div.job-card"):
            title_el = card.select_one("h2.title a")
            company_el = card.select_one(".company")
            salary_el = card.select_one("span.salary")'''

        '''
        class FeaReportInstance:
        reportTitle:str
        reportDate:str
        simulationSettings:str
        pythicsConditions:str
        monitorsData:str
        sceneInstances:list[ReportSceneInstance]'''

        return list["Ok"]
