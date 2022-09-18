import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import validators
import nltk
import unicodedata
import gender_guesser.detector as genderDetector
from modules.websiteanalyser import WebsiteAnalyser
from modules.mailhandler import EmailValidator
from geopy.geocoders import Nominatim
from modules.sys_helper import CLogger

cl = CLogger()

class LocationHandler():
    def __init__(self, proxies=[]):
        self.proxies = proxies

    def set_proxies(self, proxies):
        self.proxies = proxies
    
    def login(self):
        if self.proxies != []:
            self.locator = Nominatim(user_agent="myGeocoder", proxies=self.proxies)
        else:
            self.locator = Nominatim(user_agent="myGeocoder")

    def get_address(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        return location.address

    def get_whole_location(self, lat, long):
        coordinates = lat, long
        location = self.locator.reverse(coordinates)
        addr = location.raw
        return addr

gd = genderDetector.Detector()
wa = WebsiteAnalyser()
ev = EmailValidator()

class TextAnalyser:
    def __init__(self, languages=["english", "german"]):
        self.stopwords = []
        for lang in languages:
            for word in stopwords.words(lang):
                self.stopwords.append(word)
        self.punctuation = string.punctuation
        self.lemmatizer = WordNetLemmatizer()

    def findlinks(self, string, rfn=False):
        urls = re.findall(wa.url_regex, " " + string + " ")

        urls = wa.sanitizeurls(urls, must_have_subroutes=True)

        if rfn:
            try:
                return urls[0]
            except:
                return None
        return urls

    def finddomains(self, string, rfn=False):
        domains = re.findall(wa.url_regex, " " + string + " ")

        domains = wa.sanitizeurls(domains)

        if rfn:
            try:
                return domains[0]
            except:
                return None
        return domains

    def findemails(self, string, rfn=False):
        email_regex = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"
        emails = re.findall(email_regex, " " + string + " ")
        for email in emails:
            try:
                validators.email(email)
            except:
                emails.remove(email)
            
            if email.startswith("n@") or not ev.is_valid(email):
                emails.remove(email)

        if rfn:
            try:
                return emails[0]
            except:
                return None
        return emails

    def _multireplace(self, string, replace_pattern):
        for arg in replace_pattern:
            string = string.replace(arg[0], arg[1])
        return string

    def _remove_punctuation(self, string):
        replace_pattern = [(v, "") for v in self.punctuation]
        return self._multireplace(string, replace_pattern)

    def get_keywords(self, list_string_weight):
        kwdict = {}
        for string, weight in list_string_weight:
            string = self._remove_punctuation(string)
            string = self.lemmatizer.lemmatize(string)
            string = word_tokenize(string)

            kwlist = [w for w in string if not w.lower() in self.stopwords and len(w) > 1 and w.isnumeric() == False]
            for w in kwlist:
                if w in kwdict:
                    kwdict[w] = [kwdict[w][0]+weight, kwdict[w][1]+1]
                else:
                    kwdict[w] = [weight, 1]
        return kwdict

    def findnames(self, text):
        person_list = []

        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary = False)

        for subtree in sentt.subtrees(filter=lambda t: t.label() == "PERSON"):
            name = []
            person = []

            for leaf in subtree.leaves():
                person.append(leaf[0])
            if len(person) > 1:
                name = [" ".join(person[:-1]), person[-1]]
                if name not in person_list:
                    person_list.append(name)

        for name in person_list:
            if name[1].lower() in self.stopwords:
                person_list.remove(name)
        return person_list

    def normalize_all(self, text, replace_pynewline=True):
        text = unicodedata.normalize("NFKD", text)
        if replace_pynewline:
            text = text.replace("\n", " ")

        return text

    def parse_direct_chars(self, text):
        parse_chars = [
            ("[at]", "@"),
            ("[dot]", "."),
            (" at ", "@"),
            (" dot ", ".")
        ]

        for char_in, char_out in parse_chars:
            text = text.replace(char_in, char_out)

        return text

    def decode_unicode_esc(self, text):
        return str(text)

    def get_hashtags(self, text):
        hashtags = []
        for word in text.split(" "):
            if word.startswith("#"):
                hashtags.append(word[1:])
        
        return hashtags

    def get_entities(self, text):
        hashtags = []
        for word in text.split(" "):
            if word.startswith("@"):
                hashtags.append(word[1:])
        
        return hashtags

    def get_gender(self, fname, country=None):
        gender = gd.get_gender(fname, country)
        gender = "androgynous" if gender == "andy" else gender
        gender = gender.replace("mostly_", "")
        return gender