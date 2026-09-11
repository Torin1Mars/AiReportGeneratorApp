

class ChatGptRequestModule:
    def __init__(self, validApiKey:str, modelName: str):
        super().__init__()

        self.currentApiKey = validApiKey
        self.currentModelName = modelName


    def run_preparation_query(self, initialPrompt:str, rawUserFeaReports:list[str],
                              rawAdditionalDocuments:list[str], allowingRequestTime:int):
        #TODO later
        pass


    def run_generating_report_query(self,initialPrompt:str, template:str,
                                    processedUserData:list[str], allowingRequestTime:int):
        #TODO later
        pass
