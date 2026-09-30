import os
import webbrowser
from datetime import datetime
from string import Template

import openai

from openai import OpenAI
from openai.types.chat import ChatCompletion
from App.supportingData.settingsManager import SettingsManager

class ChatGptRequestModule:
    def __init__(self, validApiKey:str, modelName: str, settings:SettingsManager):
        super().__init__()

        self.appSettings = settings

        #Ai client
        self.currentApiKey = validApiKey
        self.currentModelName = modelName

        self.aiClient = OpenAI(api_key = validApiKey)

    def run_generating_report_query(self, userData:object, user_prompt:str, reportLanguage:str, reportStyle:str)->None:
        try:
            print("Query have been sent!")
            respond = self._sendAiRequest(userData, user_prompt, reportLanguage,reportStyle)

            #Succes response
            self._processAiRespond(respond, reportLanguage)

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
            # Send the question to the ChatCompletions endpoint
            response:ChatCompletion = self.aiClient.chat.completions.create(
                model = self.currentModelName,
                messages=[
                    {"role": "system", "content": self.appSettings.GPT_PROMPT_SYSTEM_INITIAL},
                    {"role": "system", "content": reportStyle},
                    {"role": "system", "content": "Output report file language: " + reportLanguage},

                    {"role": "user", "content": userSerializebleData},

                    {"role": "assistant", "content": self.appSettings.GPT_PROMPT_SYSTEM_ROLE_EXPLANATION},

                    {"role": "user", "content": aditionalPrompt}
                ])
            return response

        except Exception as e:
            print(e)

    def _processAiRespond(self, respond:ChatCompletion, outputReportLanguage)->None:
        now = datetime.now()
        date_string = now.strftime("%d-%m-%Y_%H-%M")

        report_name_tmpl = Template(self.appSettings.report_name_template)
        current_report_name = report_name_tmpl.substitute(time= date_string, lang = outputReportLanguage)

        data = respond.choices[0].message.content

        targetFolder = self.appSettings.TARGET_FOLDER
        fileName = current_report_name

        fullPath = os.path.join(targetFolder,  fileName)

        with open(fullPath, "w", encoding="utf-8") as f:
            f.write(data)

            webbrowser.open(f"file:///{fullPath}")
