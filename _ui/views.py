from django.shortcuts import render
from django.http import HttpResponse
from .ui_helper import build_params

def dashboard(request):
    
    params = {
        
    }

    return render(request, "dashboard.html", build_params("Dashboard", params))

def stdout_log(request):
    
    params = {
        "wanted_log": "stdout"
    }

    return render(request, "log.html", build_params("Stdout Log", params))

def main_log(request):
    
    params = {
        "wanted_log": "log"
    }

    return render(request, "log.html", build_params("Main Log", params))