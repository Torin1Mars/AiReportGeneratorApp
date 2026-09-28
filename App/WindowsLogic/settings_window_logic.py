

class SettingsWindowLogic:
    def __init__(self, key:str , aiModelName:str, reportStyle:str):
        self.ai_api_key = key
        self.current_ai_model_name = aiModelName
        self.current_report_style = reportStyle
