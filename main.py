from modules.textanalyser import TextAnalyser, LocationHandler
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper
from modules.instadata import InstaData
from modules.websiteanalyser import ProxyChecker
from api.api_organizer import trigger_new_process
from multiprocessing import Process, Value, Manager
import time
from datetime import datetime, timedelta
import traceback
from modules.sys_helper import CLogger
from ctypes import c_char_p, c_wchar_p

# username, password
ACCOUNTS_DATA = [
    ["", ""]
]
USERMAX = float("inf")
SLEEP_TIME = 7
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 2)
ANALYZE_PREVENTION = ("sleep reconnect proxy_reconnect", 3600 * 2.5)
DB_RECONNECT_S = 3600 * 4
GFL_FILTER = {}
# GFL_FILTER = {"category": {"$nin": ["Artist", "Art", "Photographer", "Graphic Designer", "Visual Arts"]}}
# GFL_FILTER = {"category": {"$in" ["Entrepreneur", "Public figure", "Product/service", "Real Estate Agent", "Retail company", "Local business", "Digital Creator"]}}

def initialize_scraper(allowed_to_scrape, critical_error_happened):# , error_msg, manager):
    mm = MongoManager()
    ta = TextAnalyser()
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    pc = ProxyChecker()
    lh = LocationHandler()
    dh = DataHandler(mm, ta, ls, lh)
    cl = CLogger()
    try:
        trigger_new_process()
        id = InstaData(ACCOUNTS_DATA, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, ANALYZE_PREVENTION, mm, ta, ls, dh, pc)
        cl.logstat("status", "initialized")
    except Exception as e:
        print(traceback.format_exc())
        cl.logprint(traceback.format_exc())
        cl.logstat("initilialization_error", traceback.format_exc())
        critical_error_happened = Value("d", 1)
        return
    print("INITIALIZED")

    counter = 0
    while True and counter <= 20:
        counter += 1
        if allowed_to_scrape in (1, 1.0, Value("d", 1)):
            print("STARTING SCRAPING")
            break
        else:
            print("SCRAPE READY")
            time.sleep(1)

    try:
        id.make_list(use_log=True, db_reconnect=DB_RECONNECT_S, gfl_filter=GFL_FILTER)
    except:
        cl.logprint(traceback.format_exc())
        cl.logstat("status", "offline")
        cl.logstat("runtime_error", traceback.format_exc())

class ScraperShell():
    def __init__(self):
        self.cl = CLogger()
        self.manager = Manager()
        self.allowed_to_scrape = Value("d", 0)
        self.cl.logstat("status", "offline")
        self.initialized = False
        self.running = False
        self.critical_error_happened = Value("d", 0)
        

    def initialize_scraper(self):
        if self.running:
            a = self.stop_scraper() or None
            if a != None:
                return a
        try:
            self.process = Process(target=initialize_scraper, args=(self.allowed_to_scrape, self.critical_error_happened))# , self.error_msg, self.manager))
            self.process.start()
            counter = 0
            self.cl.logstat("online_status", "initializing")
            while counter <= 20:
                print("INITIALIZING")
                counter += 1
                if self.cl.getlogstat("status") == "initialized" or self.critical_error_happened in (1, 1.0, Value("d", 1)):
                    break
                time.sleep(1)

            if self.critical_error_happened in (1, 1.0, Value("d", 1)) or self.cl.getlogstat("initilialization_error", "") != "":
                return {"sstatus": "error", "error": self.cl.getlogstat("initilialization_error")}

            self.initialized = True

            return {"status": "ok"}
        except Exception as e:
            self.cl.logprint(traceback.format_exc())
            self.cl.logstat("status", "offline")
            return {"sstatus": "error", "error": str(traceback.format_exc())}

    def start_scraper(self):
        if self.initialized:
            self.allowed_to_scrape = Value("d", 1)
            self.cl.logstat("status", "running")
            return {"sstatus": "ok"}
        else:
            return {"sstatus": "error", "error": "scraper not initialized"}

    def stop_scraper(self):
        try:
            self.process.terminate()
            self.initialized = False
            self.cl.logstat("status", "offline")
        except Exception as e:
            self.cl.logprint(traceback.format_exc())
            self.cl.logstat("status", "unknown")
            return {"sstatus": "error", "error": str(traceback.format_exc())}


