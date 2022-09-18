from dataclasses import dataclass
from typing import List, Union, Optional
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
from modules.sys_helper import CLogger

cl = CLogger()

@dataclass
class Link:
    url : Optional[str]
    
@dataclass
class LinktreeUser:
    username : str
    url : Optional[str]
    avatar_image : Optional[str]
    id : int
    tier : str
    is_active : bool
    description : Optional[str]
    created_at: int
    updated_at: int
    links : List[tuple]

class Linktree(object):
    async def _fetch(self, url : str,
                     method : str = "GET", 
                     headers : dict = {}, 
                     data : dict = {}) -> tuple[aiohttp.ClientSession, aiohttp.ClientSession]:
        
        session = aiohttp.ClientSession(headers= headers)
        resp = await session.request(method = method ,url = url, json = data)
        return session, resp
                    
    async def getSource(self, url : str):
        session, resp = await self._fetch(url)
        content = await resp.text()
        await session.close()
        return content
            
    async def getUserInfoJSON(self, source = None,  url : Optional[str] = None, username : Optional[str] = None):            
        if url is None and username:
            url = f"https://linktr.ee/{username}"

        if source is None and url:
            source = await self.getSource(url)

        soup = BeautifulSoup(source, 'html.parser')
        attributes = {"id":"__NEXT_DATA__"}
        user_info = soup.find('script', attrs=attributes)
        user_data = json.loads(user_info.contents[0])["props"]["pageProps"]
        return user_data

    async def uncensorLinks(self, account_id : int, link_ids : Union[List[int], int]):
        if isinstance(link_ids, int):
            link_ids = [link_ids]
        
        headers = {"origin": "https://linktr.ee",
                   "referer": "https://linktr.ee",
                   "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"}
        
        data = {"accountId": account_id, 
                   "validationInput": {"acceptedSensitiveContent": link_ids},
                 "requestSource": {"referrer":None}}
        
        url = "https://linktr.ee/api/profiles/validation/gates"
        session, resp = await self._fetch(method = "POST", url = url, headers = headers, data= data)
        
        json_resp = await resp.json()
        await session.close()
        
        _links = json_resp["links"]
        
        links = []
        for _link in _links:
            links.append((_link["title"], _link["url"]))
        return links
    
    async def getUserLinks(self, username : Optional[str] = None, data : Optional[dict] = None):
        if data is None and username:
            data = await self.getUserInfoJSON(username= username)
            
        user_id = data["account"]["id"]
        _links = data["links"]
    
        links = []
        censored_links_ids = []
        
        for _link in _links:
            id = int(_link["id"])
            url = _link["url"]
            locked = _link["locked"]

            link = url
            if _link["type"] == "COMMERCE_PAY":
                continue
            
            if url is None and locked is True:
                censored_links_ids.append(id)
                continue
            links.append(link)

        uncensored_links = await self.uncensorLinks(account_id= user_id, 
                                                    link_ids= censored_links_ids)
        links.extend(uncensored_links)
        
        return links

    async def getLinktreeUserInfo(self, url : Optional[str] = None, username : Optional[str] = None)-> LinktreeUser:
        if url is None and username is None:
            cl.logprint("ERROR in getLinktreeUserInfo: url must be given")
            return

        JSON_INFO = await self.getUserInfoJSON(url = url, username= username)

        account = JSON_INFO["account"]
        username = account.get("username", None)
        avatar_image = account.get("profilePictureUrl", None)
        id = account.get("id", None)
        tier  = account.get("tier", None)
        is_active = account.get("is_active", None)
        created_at = account.get("created_at", None)
        updated_at = account.get("updated_at", None)
        description = account.get("description", None)

        links = await self.getUserLinks(data= JSON_INFO)
        
        return LinktreeUser(username = username,
                            url = url,
                            avatar_image= avatar_image,
                            id = id,
                            tier = tier,
                            is_active = is_active,
                            created_at = created_at,
                            updated_at = updated_at,
                            description = description,
                            links = links)

    
async def main(url):
    linktree = Linktree()
    user_info = await linktree.getLinktreeUserInfo(url, username=None)
    
    userobj = {}
    userobj["username"] = user_info.username
    userobj["avatar_image"] = user_info.avatar_image
    userobj["tier"] = user_info.tier
    userobj["is_active"] = user_info.is_active
    userobj["description"] = user_info.description
    userobj["created_at"] = user_info.created_at
    userobj["updated_at"] = user_info.updated_at
    userobj["links"] = user_info.links

    return userobj

class LinktreeScraper:
    def __init__(self, ta, vd):
        self.ta = ta
        self.vd = vd
        pass

    def get_linktree(self, url):
        loop = asyncio.get_event_loop()
        userobj = loop.run_until_complete(main(url))
        return userobj

    def get_linktreedata(self, data, link):

        data["linktreedata"] = self.get_linktree(link)
        for link in data["linktreedata"]["links"]:
            data["links"][link] = 1 if self.vd.is_valuable_domain(link) else 0

        data["linktreedata"]["description_original"] = data["linktreedata"]["description"]
        data["linktreedata"]["description_normalized"] = None

        if data["linktreedata"]["description"] not in ("", None):
            data["linktreedata"]["description_normalized"] = self.ta.normalize_all(data["linktreedata"]["description"])
            data["linktreedata"]["description_normalized"] = self.ta.parse_direct_chars(data["linktreedata"]["description"])

        return data
