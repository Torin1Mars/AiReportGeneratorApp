import ast

##################Settings constants for project#############################
class SettingsManager :

    def __init__(self, appPath):
        #This parameter dynamically changing depends on the current file location
        self.current_App_folder = appPath
        self.report_name_template =  "Report_${time}_${lang}.html"

        self.TARGET_FOLDER = appPath

        #Default Parameters
        self.MAIN_WINDOW_HEIGHT:int = 800
        self.MAIN_WINDOW_WIDTH:int = 1000

        self.SETTINGS_WINDOW_HEIGHT:int = 500
        self.SETTINGS_WINDOW_WIDTH:int = 400

        self.REPORT_LANGUAGES_VARIANTS:list[str] = []

        #Ai setups
        self.GPT_MODEL_NAME:str = "gpt-5.4-mini"
        self.GPT_KEY:str = ""

        self.PREPARATION_TIME_LIMIT:int = 60  #In seconds
        self.GPT_REPORT_GENERATION_TIME:int = 90  #In seconds

        self.GPT_PROMPT_SYSTEM_INITIAL:str = "Input data format = json format data. Respond format: html report document according to initial structure."
        self.GPT_PROMPT_SYSTEM_RESPOND_LANGUAGE:str = ""
        self.GPT_PROMPT_SYSTEM_RESPOND_STYLE:str = ""
        self.GPT_PROMPT_SYSTEM_ROLE_EXPLANATION:str = ("You are experienced design engineer who is working on railway company you are working on projects for metro and trams."
                                                      "Your goal is to write structured simulation report based on user input data with accordance to user document structure." )

        self.AppSettingsContainer = {
            "MAIN_WINDOW_HEIGHT": self.MAIN_WINDOW_HEIGHT,
            "MAIN_WINDOW_WIDTH": self.MAIN_WINDOW_WIDTH,

            "SETTINGS_WINDOW_HEIGHT": self.SETTINGS_WINDOW_HEIGHT,
            "SETTINGS_WINDOW_WIDTH": self.SETTINGS_WINDOW_WIDTH,

            "REPORT_LANGUAGES_VARIANTS": self.REPORT_LANGUAGES_VARIANTS,

            "GPT_MODEL_NAME": self.GPT_MODEL_NAME,
            "GPT_KEY": self.GPT_KEY,

            "PREPARATION_TIME_LIMIT": self.PREPARATION_TIME_LIMIT,
            "GPT_REPORT_GENERATION_TIME": self.GPT_REPORT_GENERATION_TIME,

            "GPT_PROMPT_SYSTEM_INITIAL": self.GPT_PROMPT_SYSTEM_INITIAL,
            "GPT_PROMPT_SYSTEM_RESPOND_LANGUAGE": self.GPT_PROMPT_SYSTEM_RESPOND_LANGUAGE,
            "GPT_PROMPT_SYSTEM_RESPOND_STYLE": self.GPT_PROMPT_SYSTEM_RESPOND_STYLE,
            "GPT_PROMPT_SYSTEM_ROLE_EXPLANATION": self.GPT_PROMPT_SYSTEM_ROLE_EXPLANATION,

            "TARGET_FOLDER" : self.TARGET_FOLDER
        }

        self._load_local_config("SETTINGS.txt")

    def _load_local_config(self, configFileName:str)->None:
        #Config file should be in same directory as app
        currentLocalSettings:str

        filePath = str(self.TARGET_FOLDER) + "\\" + configFileName

        with open(filePath, "r", encoding="utf-8") as settings:
            settingsLines = [
                line.rstrip("\n")
                for line in settings
                    if line.strip() and not line.lstrip().startswith(("#", "'"))
            ]

            for instance in settingsLines:
                parameter, value = instance.split("=", 1)

                parameter = parameter.strip()
                value = value.strip()

                if hasattr(self, parameter):
                    old_value = getattr(self, parameter)

                    #Type setting
                    if isinstance(old_value, int):
                        value = int(value)
                    elif isinstance(old_value, float):
                        value = float(value)
                    elif isinstance(old_value, list):
                        value = ast.literal_eval(value)
                    else:
                        value = str(value)

                    setattr(self, parameter, value)
