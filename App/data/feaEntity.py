from dataclasses import dataclass


@dataclass
class ReportSceneInstance:
    sceneTitle:str
    imagePath:str

@dataclass
class FeaReportInstance:
    reportTitle:str
    reportDate:str
    simulationSettings:str
    pythicsConditions:str
    monitorsData:str
    sceneInstances:list[ReportSceneInstance]
