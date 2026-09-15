from tkinter import *
from tkinter import messagebox

from App.AiRequestModule.chatGptRequestModule import ChatGptRequestModule
from App.SupportingData.initalSettings import CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME


class AppLogicController:
    def __init__(self):
        self.requestModule = ChatGptRequestModule(CHAT_GPT_KEY, CHAT_GPT_MODEL_NAME)

    def runPreperationStage(self, templateFilePath:str, userReportsFiles:list[str], explanationDocs:list[str] ):
       #Short input validation
       self._runPreparation("", ["",""], ["",""],60)

       '''if templateFilePath.strip() or len (userReportsFiles)==0:
           self._runPreparation("", ["",""], ["",""],60)

       else:
           self._showInformationMsg("No input data found!")'''


    def runGenerateStage(self):
        #Short input validation
        pass

    def _runPreparation(self, basicPrompt:str, rawFeaReports:list[str], documents:list[str], allowingTime:int):
        self.requestModule.run_preparation_query(basicPrompt, rawFeaReports, documents, allowingTime)


    def _runGeneration(self, basicPrompt:str, templateFile:str, preparedData:str, allowingTime:int):
        self.requestModule.run_generating_report_query(basicPrompt, templateFile, preparedData, allowingTime)


    def _showInformationMsg(self, msgText:str):
        messagebox.showinfo("Input Error!", msgText)

