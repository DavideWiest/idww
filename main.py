from modules.textanalyser import TextAnalyser, LocationHandler
from modules.mongomanager import MongoManager
from modules.linktreescraper import LinktreeScraper
from modules.datahandler import DataHandler, isValDomainWrapper
from modules.instadata import InstaData
from modules.websiteanalyser import ProxyChecker
from api.api_organizer import trigger_new_process
from multiprocessing import Process, Value
import time
import traceback
from modules.sys_helper import CLogger

# username, password
ACCOUNTS_DATA = [
    ["seauser565", "seauser656"]
]
USERMAX = float("inf")
SLEEP_TIME = 7
LONG_SLEEP_TIME = (3600 * 0.5, 3600 * 2)
ANALYZE_PREVENTION = ("sleep reconnect proxy_reconnect", 3600 * 2.5)
GFL_FILTER = {"category": {"$nin": ["Artist", "Art", "Photographer", "Graphic Designer", "Visual Arts"]}}
DB_RECONNECT_S = 3600 * 4
# GFL_FILTER = {"category": {"$in" ["Entrepreneur", "Public figure", "Product/service", "Real Estate Agent", "Retail company", "Local business", "Digital Creator"]}}

def initialize_scraper(allowed_to_scrape):
    mm = MongoManager()
    ta = TextAnalyser()
    vd = isValDomainWrapper()
    ls = LinktreeScraper(ta, vd)
    pc = ProxyChecker()
    lh = LocationHandler()
    dh = DataHandler(mm, ta, ls, lh)

    id = InstaData(ACCOUNTS_DATA, USERMAX, SLEEP_TIME, LONG_SLEEP_TIME, ANALYZE_PREVENTION, mm, ta, ls, dh, pc)
    trigger_new_process()

    while True:
        if allowed_to_scrape in (1, 1.0):
            break
        else:
            time.sleep(1)

    id.make_list(use_log=True, db_reconnect=DB_RECONNECT_S, gfl_filter=GFL_FILTER)



class ScraperShell():
    def __init__(self):
        self.cl = CLogger()
        self.allowed_to_scrape = Value("d", 0)
        print(self.cl.getlogstat("aa"))
        self.cl.logstat("status", "offline")

    def initialize_scraper(self):
        try:
            self.process = Process(target=initialize_scraper, args=(self.allowed_to_scrape))
            self.process.start()
            self.cl.logstat("status", "initialized")
            return {"status": "ok"}
        except Exception as e:
            self.cl.logstat("status", "offline")
            return {"status": "error", "error": str(traceback.format_exc())}

    def run_scraper(self):
        self.allowed_to_scrape = Value("d", 1)
        self.cl.logstat("status", "running")
        return {"status": "ok"}

    def stop_scraper(self):
        try:
            self.process.terminate()
            self.cl.logstat("status", "offline")
        except Exception as e:
            self.cl.logstat("status", "unknown")
            return {"status": "error", "error": str(traceback.format_exc())}


