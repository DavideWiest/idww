from modules.mongomanager import MongoManager
import json

class ApiBackend():
    def __init__(self):
        self.mm = MongoManager

    def get_status():
        pass

    def get_latest_logs(self, amount=50):
        ll = {}
        with open("logs/current/log.csv", "r", encoding="utf-8") as f:
            ll["log"] = f.load().split("\n")[-amount:]
        with open("logs/current/stdout.txt", "r", encoding="utf-8") as f:
            ll["stdout"] = f.load().split("\n")[-amount:]
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
        dbd["database_stats"] = {
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
            dbd["database_stats"][var+"_p"] = self.db_get_percentage(filter_)
            dbd["database_stats"][var+"_t"] = dbd["database_stats"][var+"_p"] * dbd["database_stats"]["count_total"]

        other_aggr = list(self.mm.pcol.aggregate([
            {"$sample": {"size": 1000}}, 
            {"$project": {"_id": 0, "base_infos": 1}}
        ]))

        for acc in other_aggr:
            if acc["base_infos.language"] in dbd["database_stats"]["langs"]:
                dbd["database_stats"]["langs"][acc["base_infos.language"]] += 0.001
            else:
                dbd["database_stats"]["langs"][acc["base_infos.language"]] = 0.001

            if acc["base_infos.category"] in dbd["database_stats"]["categories"]:
                dbd["database_stats"]["categories"][acc["base_infos.category"]] += 0.001
            else:
                dbd["database_stats"]["categories"][acc["base_infos.category"]] = 0.001

        return dbd

