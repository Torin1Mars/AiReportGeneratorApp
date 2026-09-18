import asyncio
from tkinter import messagebox

from App.AiModule.chatGptRequestModule import ChatGptRequestModule
from App.AiModule.inputFilesLoader import InputFilesLoader
from App.SupportingData.initalSettings import CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME


class MainWindowLogic:

    def __init__(self):
        self.templateFile = None
        self.reportsFiles = None
        self.explanationDocumentsPaths = None

        self.inputFilesLoader = InputFilesLoader()
        self.requestAiModule = ChatGptRequestModule(CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME)

    def set_new_inputs (self, templateFile:list[str] = None, reportsFiles:list[str] = None, explanationDocumentsPaths:list[str]= None ):
        self.templateFile = templateFile
        self.reportsFiles = reportsFiles
        self.explanationDocumentsPaths = explanationDocumentsPaths

    def runPreperationStage(self, allowingDelay:int):

        ###Converting
        #Short input validation
        if len(self.templateFile) != 0 and len(self.reportsFiles) != 0:
            try:
                convertedInputFiles = asyncio.run(asyncio.wait_for(
                    self._convertUserInputFiles(),
                    timeout=allowingDelay))

                self._runPreparation(convertedInputFiles)

            except Exception as e:
                self._showErrornMsg("Couldn't convert input files!")
                print(e)

        else:
            self._showInformationMsg("No input data found!")


    def runGenerateStage(self, allowingDelay:int):
        #Short input validation
        pass

    def _runPreparation(self, convertedInputs:list[list[str]]):
        self.requestAiModule.run_preparation_query(convertedInputs)

    def _runGeneration(self, basicPrompt:str, templateFile:str, preparedData:str, allowingTime:int):
        self.requestAiModule.run_generating_report_query(basicPrompt, templateFile, preparedData, allowingTime)

    async def _convertUserInputFiles (self):
        await self._inputFilesLoading()

    async def _inputFilesLoading(self) -> list[list[str]]:
        convertedData = []

        convertedTemplate = self.inputFilesLoader.loadFiles(self.templateFile)
        convertedFeaReports = self.inputFilesLoader.loadFiles(self.reportsFiles)
        convertedExplanationDocuments = self.inputFilesLoader.loadFiles(self.explanationDocumentsPaths)

        convertedData.append([convertedTemplate, convertedFeaReports, convertedExplanationDocuments])
        return convertedData


    def _showInformationMsg(self, msgText:str):
        messagebox.showwarning("Input Error!", msgText)

    def _showErrornMsg(self, msgText:str):
        messagebox.showerror("Files Error!", msgText)
