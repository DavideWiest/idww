import requests
from modules.sys_helper import CLogger

API_KEY = "96124839-5566-47b0-a943-d8299839bd62"

class EmailValidator():
    def __init__(self):
        self.api_key = API_KEY
        self.cl = CLogger()


    def is_valid(self, email):
        response = requests.get("https://isitarealemail.com/api/email/validate", params = {"email": email}).json()
        if "status" in response:
            return response["status"] == "valid"
        else:
            self.cl.logprint("----> CRITICAL ERROR: REALEMAIL API NOT WORKING. Response:" + str(response) + "")
            return True
