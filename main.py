from modules.textanalyser import TextAnalyser, LocationHandler
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper
from modules.instadata import InstaData
from modules.websiteanalyser import ProxyChecker
from api.api_organizer import trigger_new_process
from multiprocessing import Process, Value
import time
from datetime import datetime, timedelta
import traceback
from modules.sys_helper import CLogger

# username, password
ACCOUNTS_DATA = [
    ["seauser565", "seauser656"],
    ["stefaniebuddzusvoi1", "Y95L5VMME2"]
]
USERMAX = float("inf")
SLEEP_TIME = 7
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 2)
ANALYZE_PREVENTION = ("sleep reconnect proxy_reconnect", 3600 * 2.5)
GFL_FILTER = {"category": {"$nin": ["Artist", "Art", "Photographer", "Graphic Designer", "Visual Arts"]}}
DB_RECONNECT_S = 3600 * 4
# GFL_FILTER = {"category": {"$in" ["Entrepreneur", "Public figure", "Product/service", "Real Estate Agent", "Retail company", "Local business", "Digital Creator"]}}

def initialize_scraper(allowed_to_scrape, successful_initialization):
    mm = MongoManager()
    ta = TextAnalyser()
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    pc = ProxyChecker()
    lh = LocationHandler()
    dh = DataHandler(mm, ta, ls, lh)

    trigger_new_process()
    id = InstaData(ACCOUNTS_DATA, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, ANALYZE_PREVENTION, mm, ta, ls, dh, pc)
    successful_initialization = Value("d", 0)
    print(5)

    dt_new_process = datetime.now()

    while True and timedelta(datetime.now(), dt_new_process).total_seconds() > 3600 * 4:
        if allowed_to_scrape in (1, 1.0):
            print("allowed to scrape")
            break
        else:
            print("not allowed to scrape")
            time.sleep(1)

    id.make_list(use_log=True, db_reconnect=DB_RECONNECT_S, gfl_filter=GFL_FILTER)



class ScraperShell():
    def __init__(self):
        self.cl = CLogger()
        self.allowed_to_scrape = Value("d", 0)
        self.cl.logstat("status", "offline")
        self.initialized = False
        self.successful_initialization = Value("d", 0)

    def initialize_scraper(self):
        try:
            self.process = Process(target=initialize_scraper, args=(self.allowed_to_scrape, self.successful_initialization))
            self.process.start()
            counter = 0
            while counter <= 30:
                print(counter)
                counter += 1
                if self.successful_initialization in (1, 1.0):
                    break
                time.sleep(0.5)
            if self.successful_initialization not in (1, 1.0):
                return {"sstatus": "error", "error": "unknown error"}

            self.initialized = True
            self.cl.logstat("status", "initialized")
            return {"status": "ok"}
        except Exception as e:
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
            self.cl.logstat("status", "unknown")
            return {"sstatus": "error", "error": str(traceback.format_exc())}


