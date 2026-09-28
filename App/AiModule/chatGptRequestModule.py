import os
import webbrowser
import openai

from openai import OpenAI
from openai.types.chat import ChatCompletion

from App.SupportingData.initalSettings import GPT_REPORT_GENERATION_TIME, GPT_PROMPT_SYSTEM_INITIAL, \
    GPT_PROMPT_SYSTEM_ROLE_EXPLANATION, TEMP_TARGET_FOLDER

class ChatGptRequestModule:
    def __init__(self, validApiKey:str, modelName: str, ):
        super().__init__()

        #Ai client
        self.currentApiKey = validApiKey
        self.currentModelName = modelName

        self.aiClient = OpenAI(api_key = validApiKey)

    def run_generating_report_query(self,userData:object, user_prompt:str, reportLanguage:str, reportStyle:str)->None:
        try:
            ok = userData
            respond = self._sendAiRequest(userData, user_prompt, reportLanguage,reportStyle)

            #Succes response
            self._processAiRespond(respond)

        except openai.APIConnectionError as e:
            print(f"Network error: {e}")

        except openai.RateLimitError as e:
            print(f"Tokens limit (429): {e}")

        except openai.APIStatusError as e:
            print(f"API respond error ({e.status_code}): {e.response.text}")

        except Exception as e:
            # Other
            print(f"Error: {e}")

    def _sendAiRequest(self, userSerializebleData:object, aditionalPrompt:str, reportLanguage:str, reportStyle:str )->ChatCompletion:
        try:
            print("Request has been sent")

            # Send the question to the ChatCompletions endpoint
            response:ChatCompletion = self.aiClient.chat.completions.create(
                model = self.currentModelName,
                messages=[
                    {"role": "system", "content": GPT_PROMPT_SYSTEM_INITIAL},
                    {"role": "system", "content": reportStyle},
                    {"role": "system", "content": reportLanguage},

                    {"role": "user", "content": userSerializebleData},

                    {"role": "assistant", "content": GPT_PROMPT_SYSTEM_ROLE_EXPLANATION},

                    {"role": "user", "content": aditionalPrompt}
                ])
            return response

        except Exception as e:
            print(e)

    def _processAiRespond(self, respond:ChatCompletion)->None:
        data = respond.choices[0].message.content

        targetFolder = TEMP_TARGET_FOLDER
        fileName = f"Report_.html"

        fullPath = os.path.join(targetFolder,  fileName)

        with open(fullPath, "w", encoding="utf-8") as f:
            f.write(data)

            webbrowser.open(f"file:///{fullPath}")
