import requests
import urllib.request
import socket
import urllib.error
from modules.sys_helper import CLogger
from urllib import request as urlrequest


socket.setdefaulttimeout(180)

class ProxyChecker:
    def __init__(self):
        self.cl = CLogger()

    def is_bad_proxy(self, proxy):    
        try:
            proxy_handler = urllib.request.ProxyHandler({'https': proxy})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            req=urllib.request.Request('https://www.google.com')  # change the URL to test here
            sock=urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:
            return True
        return False

    def is_bad_proxy2(self, proxy):
        try:
            req = urlrequest.Request("https://google.com")
            req.set_proxy(proxy, 'http')
            response = urlrequest.urlopen(req)
            # urllib.request.urlopen(
            #     "https://google.com",
            #     proxies={'http': proxy}
            # )
        except IOError:
            return True
        else:
            return False

    def get_valid_proxies(self, max_proxies=float("inf"), print_status=True):
        with open("resources/proxies.csv", "r") as f:
            f = f.read().split("\n")
        
        proxylist = {}
        if f in ([], "", [""]):
            return proxylist
        
        for index, proxydata in enumerate(f):
            url, port, a1, a2, a3 = proxydata.split(",")
            if not self.is_bad_proxy(f"http://{url}:{port}") and index <= max_proxies:
                proxylist[f"http://{url}:{port}"] = float(a2) * float(a3) / float(a1)

        if print_status:
            self.cl.logprint(f"PROXIES CHECKED: {len(proxylist)} SUCCEEDED | {len(f)-len(proxylist)} FAILED")

        proxylist_sorted = {k: v for k, v in sorted(proxylist.items(), key=lambda item: item[1], reverse=True)}
        return proxylist_sorted

class WebsiteAnalyser:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        self.user_agent_header = {"User-agent": self.user_agent}
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Custom user agent'})

        self.url_regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


    def check_url_up(self, url, check_status_code=True):
        try:
            request = self.session.get(url, headers=self.user_agent_header)
            if check_status_code:
                if request.status_code > 199 and request.status_code < 300:
                    return request.url
                else:
                    return False
            else:
                request.url
        except:
            return False

    def get_domainname(self, url_or_mail):
        domain = url_or_mail
        try:
            domain = domain.split("//")[1]
        except:
            pass

        try:
            domain = domain.split("www.")[1]
        except:
            pass

        return domain

    def _avoid_duplicate_urls(self, urllist):
        urllist2 = []
        for _url in urllist:
            if not any([url3.endswith(self.get_domainname(_url)) for url3 in urllist2]):
                urllist2.append(_url)

        return urllist2

    def _has_subroute(self, url):
        checkingurl = url
        if "?" in checkingurl:
            checkingurl = checkingurl.split("?")[0]
        if checkingurl[-1] == "/":
            checkingurl = checkingurl[:-1]
        if "://" in checkingurl:
            checkingurl = checkingurl.replace("://", "")


        return "/" in checkingurl

    def sanitizeurls(self, urls, must_be_unique=True, subroutes_allowed=False, must_have_subroutes=False):
        if must_have_subroutes:
            subroutes_allowed = True
        
        urls2 = []
        for url in urls:
            result = self.check_url_up(url)
            if result != False:
                urls2.append(result)
                continue
            
            if not url.startswith("https://"):
                result = self.check_url_up("https://" + url)
                if result != False:
                    urls2.append(result)
                    continue
            
            elif not url.startswith("http://"):
                result = self.check_url_up("http://" + url)
                if result != False:
                    urls2.append(result)
                    continue

            if "www." in url:
                if not url.startswith("https://"):
                    result = self.check_url_up("https://" + url.replace("www.", ""))
                    if result != False:
                        urls2.append(result)
                        continue

                elif not url.startswith("http://"):
                    result = self.check_url_up("http://" + url.replace("www.", ""))
                    if result != False:
                        urls2.append(result)
                        continue
                        
                else:
                    result = self.check_url_up(url.replace("www.", ""))
                    if result != False:
                        urls2.append(result)
                        continue
                
        if must_be_unique:
            urls3 = self._avoid_duplicate_urls(urls2)
        else:
            urls3 = urls2

        if not subroutes_allowed:
            for _url in urls3:
                if self._has_subroute(_url):
                    urls3.remove(_url)

        if must_have_subroutes:
            for _url in urls3:
                if not self._has_subroute(_url):
                    urls3.remove(_url)
            
        return urls3