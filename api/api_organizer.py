from pathlib import Path
from datetime import datetime
import shutil


def trigger_new_process():
    crnt_datetime = datetime.now().strftime('%d.%m.%Y_%H:%M:%S')
    archive_path = "logs/archived/" + crnt_datetime
    Path(archive_path).mkdir(parents=True, exist_ok=True)

    shutil.move("logs/current/log.csv", archive_path + "/log.csv")
    shutil.move("logs/current/stats.json", archive_path + "/stats.json")
    shutil.move("logs/current/account_errors.json", archive_path + "/account_errors.json")
    shutil.move("logs/current/stdout.txt", archive_path + "/stdout.txt")

    with open("logs/current/log.csv", "w") as f:
        f.write("")

    with open("logs/current/stats.json", "w") as f:
        f.write("{\n\n}")

    with open("logs/current/account_errors.json", "w") as f:
        f.write("{\n\n}")
    
    with open("logs/current/stdout.txt", "w") as f:
        f.write("")

auth_error = {"status": "error", "error": "Wrong/No authentication token"}

def successful_authentication(request):
    with open("ww_resources/api_token.txt", "r", encoding="utf-8") as f:
        return request.query_params.get("auth_token") == f.read()