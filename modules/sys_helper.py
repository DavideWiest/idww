from datetime import datetime
import json

class CLogger():
    def __init__(self):
        pass

    def logprint(self, string):
        with open("logs/current/stdout.txt", "a", encoding="utf-8") as f:
            f.write("\n" + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " --- " + string + "\n!---!\n")

    def getlogstat(self, var, default=None):
        with open("logs/current/stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)
        
        return stats.get(var, default)

    def logstat(self, var, val, mode="overwrite"):
        with open("logs/current/stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)

        if var in stats:
            if mode == "increment":
                stats[var] += val
            else:
                stats[var] = val
        else:
            stats[var] = val
        
        if var == "status" and val == "offline" and "online_status" in stats:
            del stats["online_status"]

        with open("logs/current/stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4)

    def log_account_exit(self, username, errdict):
        with open(f"logs/current/account_errors.json", "r", encoding="utf-8") as f:
            logfile = json.load(f)

        logfile[username] = errdict

        with open(f"logs/current/account_errors.json", "w", encoding="utf-8") as f:
            json.dump(logfile, f, indent=4)


class LoginFailure_cl_Primary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl - " + message

    def __str__(self):
        return self.message
    
class LoginFailure_cl_Secondary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl - " + message
    
    def __str__(self):
        return self.message

class LoginFailure_cl_Generic(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message


class LoginFailure_cl2_Secondary(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message

class LoginFailure_cl2_Generic(Exception):
    def __init__(self, message):
        self.message = f"[{datetime.now().strftime('%d-%m-%Y, %H:%M:%S')}] Error for cl2 - " + message
    
    def __str__(self):
        return self.message

def get_full_class_name(obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + '.' + obj.__class__.__name__
