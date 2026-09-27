from openai import OpenAI

#from App.AiModule.inputFilesLoader import InputFilesLoader


class ChatGptRequestModule:
    def __init__(self, validApiKey:str, modelName: str):
        super().__init__()

        #Ai client
        self.currentApiKey = validApiKey
        self.currentModelName = modelName

        self.aiClient = OpenAI(api_key = validApiKey)

    def run_preparation_query(self, convertedInputData:object, allowingTime:int)->None:
        respond = self._sendAiRequest(convertedInputData)
        print(respond)

    def run_generating_report_query(self,initialPrompt:str, template:str,
                                    processedUserData:str, allowingRequestTime:int):
        #TODO later
        pass

    def _sendAiRequest(self, userSerializebleData:object)->str:
        try:
            print("Request has sent")
            # Send the question to the ChatCompletions endpoint
            response = self.aiClient.chat.completions.create(
                model = self.currentModelName,
                messages=[
                    {"role": "user", "content": userSerializebleData}
                ]
            )

            # TODO need to extract Ai Answer from here
            return response.choices[0].message.content

        except Exception as e:
            print(e)
