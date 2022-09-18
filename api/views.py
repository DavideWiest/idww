from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.api_backend import ApiBackend
from api.api_organizer import successful_authentication, auth_error
from .datamanager import UrlQueryManager, BadRequestError
# import os
# import sys
# import inspect

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir) 

from main import ScraperShell

ss = ScraperShell()
ab = ApiBackend()

@api_view(["GET"])
def initialize_scraper(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ss.initialize_scraper()
    return Response(resp)

@api_view(["GET"])
def start_scraper(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ss.start_scraper()
    return Response(resp)

@api_view(["GET"])
def stop_scraper(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ss.stop_scraper()
    return Response(resp)

@api_view(["GET"])
def scraper_stats(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ab.get_scraperstats()
    return Response(resp)

@api_view(["GET"])
def database_stats(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ab.get_dbdstats()
    return Response(resp)

@api_view(["GET"])
def latest_logs(request):
    if not successful_authentication(request):
        return Response(auth_error)
    resp = ab.get_latest_logs()
    return Response(resp)