import asyncio
from tkinter import messagebox

from App.AiModule.chatGptRequestModule import ChatGptRequestModule
from App.domain.InputFilesLoader import InputFilesLoader
from App.SupportingData.initalSettings import GPT_KEY, GPT_MODEL_NAME, PREPARATION_TIME_LIMIT

class MainWindowLogic:
    def __init__(self):
        self.templateFile = None
        self.reportsFiles = None
        self.explanationDocumentsFiles = None

        self.converted_user_data:object = None

        self.inputFilesLoader = InputFilesLoader()
        self.requestAiModule = ChatGptRequestModule(GPT_KEY, GPT_MODEL_NAME)

    def set_new_inputs (self, templateFile:list[str] = None, reportsFiles:list[str] = None, explanationDocumentsPaths:list[str]= None ):
        self.templateFile = templateFile
        self.reportsFiles = reportsFiles
        self.explanationDocumentsFiles = explanationDocumentsPaths

    def prepareUserInputs(self):
        ###Converting
        ###Short input validation
        if len(self.templateFile) != 0 and len(self.reportsFiles) != 0:
            try:
                asyncio.run(asyncio.wait_for(
                    self._convertUserInputFiles(), timeout = PREPARATION_TIME_LIMIT))

                self._showInformationMsg("Input data has been successfully read!")

            except Exception as e:
                self._showErrornMsg("Couldn't convert input files!")
                print(e)

        else:
            self._showWarningMsg("Input data has not been chosen!")

    def runReportGeneration(self, user_prompt:str, user_report_language:str, user_report_style:str):
        userData = self.converted_user_data

        prompt = user_prompt
        language = user_report_language
        report_style = user_report_style

        self.requestAiModule.run_generating_report_query(userData, prompt, language, report_style)

    async def _convertUserInputFiles (self)->None:
        self.converted_user_data =  await self._inputFilesLoading()

    async def _inputFilesLoading(self) -> object:
        convertedData = self.inputFilesLoader.loadInputFiles(self.templateFile[0], self.reportsFiles, self.explanationDocumentsFiles)
        return convertedData

    #Ui Messages
    def _showInformationMsg(self, msgText:str):
        messagebox.showinfo("Information!", msgText)

    def _showWarningMsg(self, msgText:str):
        messagebox.showwarning("Pay Attention!", msgText)

    def _showErrornMsg(self, msgText:str):
        messagebox.showerror("Pay Attention!", msgText)
