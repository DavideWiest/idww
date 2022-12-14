from modules.mongomanager import MongoManager
import json

class ApiBackend():
    def __init__(self):
        self.mm = MongoManager()

    def get_status():
        pass

    def get_latest_logs(self, amount=30):
        ll = {}
        with open("logs/current/log.csv", "r", encoding="utf-8") as f:
            ll["log"] = f.read().split("\n")[-amount:]
        ll_log2 = []
        for a in ll["log"]:
            try:
                ll_log2.append([a.split(",")[3].replace("\n", ""), a.replace(a.split(",")[3] + ",", "")])
            except:
                ll_log2.append(["???", a])
        ll["log"] = ll_log2

        # ll["log"] = [[a.split(",")[3].replace("\n", ""), a.replace(a.split(",")[3] + ",", "")] for a in ll["log"]]
        
        with open("logs/current/stdout.txt", "r", encoding="utf-8") as f:
            ll["stdout"] = f.read().split("\n!---!\n")[-amount:]
        ll["stdout"] = [[a.split(" --- ")[0].replace("\n", ""), a.replace(a.split(" --- ")[0], "")] for a in ll["stdout"]]
        with open("logs/current/stats.json", "r", encoding="utf-8") as f:
            ll["stats"] = json.load(f)
        with open("logs/current/account_errors.json", "r", encoding="utf-8") as f:
            ll["account_errors"] = json.load(f)

        return ll

    def db_get_percentage(self, doc_filter):
        filtered_docs = list(self.mm.pcol.aggregate([
            {"$sample": {"size": 1000}}, 
            {"$match": doc_filter}, 
            {"$project": {"_id": 0, "insta_id": 1}}
        ]))

        return len(filtered_docs) / 1000

    def get_scraperstats(self):
        with open("logs/current/stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)

        if stats["status"] == "running":
            with open("logs/current/log.csv", "r", encoding="utf-8") as f:
                stats["lastest_scraper_status"] = f.load().split("\n")[-1].split(",")[0]
        else:
            stats["lastest_scraper_status"] = "none"
        
        return stats
    
    def get_dbdstats(self):
        dbd = {}
        dbd = {
            "count_total": self.mm.pcol.estimated_document_count()
        }

        filter_var_map = {
            "email": {"credentials.email": {"$nin": ["", "None"]}},
            "domain": {"credentials.domain": {"$nin": ["", "None"]}},
            "link": {"credentials.link": {"$nin": ["", "None"]}},
            "phone": {"credentials.phone": {"$nin": ["", "None"]}},
            "high_value_profile": {"classification_level": {"$gt": 2}},
            "applicable": {"applicable": True},
            "business": {"base_infos.is_business": True},
            "private": {"social_profiles.instagram.is_private": True},
            "influencer": {"social_profiles.instagram.stats.follower_count": {"lt": 10000}},
            "location": {"location.lat": {"ne": 0}},
            "male": {"base_infos.gender": "male"},
            "female": {"base_infos.gender": "female"},
            "androgynous": {"base_infos.gender": "androgynous"}
        }

        for var, filter_ in filter_var_map.items():
            dbd[var+"_p"] = self.db_get_percentage(filter_)
            dbd[var+"_t"] = dbd[var+"_p"] * dbd["count_total"]

        other_aggr = list(self.mm.pcol.aggregate([
            {"$sample": {"size": 1000}}, 
            {"$project": {"_id": 0, "base_infos": 1}}
        ]))

        dbd["langs"] = {}
        dbd["categories"] = {}

        for acc in other_aggr:
            if "base_infos" not in acc:
                continue

            if acc["base_infos"]["language"] in dbd["langs"]:
                dbd["langs"][acc["base_infos"]["language"]] += 0.001
            else:
                dbd["langs"][acc["base_infos"]["language"]] = 0.001

            if acc["base_infos"]["category"] in dbd["categories"]:
                dbd["categories"][acc["base_infos"]["category"]] += 0.001
            else:
                dbd["categories"][acc["base_infos"]["category"]] = 0.001

        return dbd

