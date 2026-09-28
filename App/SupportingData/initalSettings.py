##################Settings constants for project#############################

MAIN_WINDOW_HEIGHT:int = 800
MAIN_WINDOW_WIDTH:int = 1000

SETTINGS_WINDOW_HEIGHT:int = 500
SETTINGS_WINDOW_WIDTH:int = 400

FINAL_REPORT_LANGUAGES_VARIANTS = ["English", "Ukrainian", "Polish", "German"]

#Ai setups
GPT_MODEL_NAME = "gpt-5.4-mini"
GPT_KEY = ""

PREPARATION_TIME_LIMIT = 60  #In seconds
GPT_REPORT_GENERATION_TIME = 90  #In seconds

GPT_PROMPT_SYSTEM_INITIAL = "Input data format = json format data. Respond format: html report document according to initial structure."
GPT_PROMPT_SYSTEM_RESPOND_LANGUAGE =""
GPT_PROMPT_SYSTEM_RESPOND_STYLE =""
GPT_PROMPT_SYSTEM_ROLE_EXPLANATION = ("You are experienced design engineer who is working on HVAC units for metro and trams projects."
                       "Your goal is to write structured simulation report based on user input data with accordance to user document structure." )

#Aditional
TEMP_TARGET_FOLDER = r"C:\Users\Admin\Desktop\Data\temp"