from tkinter import messagebox

from App.AiModule.chatGptRequestModule import ChatGptRequestModule
from App.SupportingData.initalSettings import CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME


class MainWindowLogic:

    def __init__(self):
        self.templateFiles = None
        self.reportsFiles = None
        self.explanationDocumentsPaths = None

        self.requestAiModule = ChatGptRequestModule(CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME)


    def set_new_inputs (self, templateFiles:list[str] = None, reportsFiles:list[str] = None, explanationDocumentsPaths:list[str]= None ):

        #TODO Need to set up proper behaviour here :
        self.templateFiles = templateFiles
        self.reportsFiles = reportsFiles
        self.explanationDocumentsPaths = explanationDocumentsPaths

    def runPreperationStage(self, allowingDelay:int):

        print(self.templateFiles)
        print(self.reportsFiles)

        #Short input validation
        if self.templateFiles is not None and self.reportsFiles is not None:
            print("Here")
            self._runPreparation("", ["",""], ["",""], allowingDelay)
        else:
            print("No here")
            self._showInformationMsg("No input data found!")


    def runGenerateStage(self, allowingDelay:int):
        #Short input validation
        pass

    def _runPreparation(self, basicPrompt:str, rawFeaReports:list[str], documents:list[str], allowingTime:int):
        self.requestAiModule.run_preparation_query(basicPrompt, rawFeaReports, documents, allowingTime)


    def _runGeneration(self, basicPrompt:str, templateFile:str, preparedData:str, allowingTime:int):
        self.requestAiModule.run_generating_report_query(basicPrompt, templateFile, preparedData, allowingTime)

    def _showInformationMsg(self, msgText:str):
        messagebox.showwarning("Input Error!", msgText)
