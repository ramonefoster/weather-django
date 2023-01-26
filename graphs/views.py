from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import connections
from django.contrib import messages
from django.urls import reverse
import pandas as pd
from plotly.offline import plot
import plotly.graph_objs as go
from .plot import *
import calendar

def index(request):
    list_years = []
    list_month = {}
    types = ['temperature', 'humidity', 'solar-radiation', 'uv-dose', 'wind-speed', 'wind-rose', 'bar', 'wind']

    for year in range(2006,2023):
        list_years.append(year)
    
    for month in range(1,13):
        month_name = calendar.month_name[month]
        list_month[month_name] = month
    
    print(list_month)
    context = {'list_years': list_years, 'list_month': list_month, 'elements': types}
    return render(
        request,
        'graphs/index.html',
        context= context)

def windPage(year, month):
    if isinstance(month, int) and isinstance(year, int):
        page_name = "Wind in " + calendar.month_name[month] + " " + str(year)
        if 1<=month<=12:
            if month < 10:
                month = '0' + str(month)
            try:
                wind = plot_wind(str(year), str(month), False) 
                error = False
            except:
                wind = None
                error = True   
        elif month == 0:            
            wind = None
            error = True    
    elif not isinstance(month, int) and isinstance(year, int):
        try:
            wind = plot_wind(str(year), '', True)
            error = False
        except:
            wind = None
            error = True
        page_name = "Wind in " + str(year)
    else:
        wind = None
        error = True
    
    context = { 'graph_data': wind,
                'page_name': page_name,
                'error': error
                 }
    
    return context

def graphPage(request, typegraph, year, month):
    types = ['temperature', 'humidity', 'solar-radiation', 'uv-dose', 'wind-speed', 'bar', 'wind-rose']
    if typegraph in types:
        if typegraph == 'wind-rose':
            context = windPage(year, month)
        else:
            element = typegraph.capitalize()
            if isinstance(month, int) and isinstance(year, int):
                if 1<=month<=12:
                    page_name = element + " in " + calendar.month_name[month] + " " + str(year)
                    if month < 10:
                        month = '0' + str(month)
                    try:
                        plt = plot_general(str(year), str(month), element, False)  
                        error = False    
                    except:
                        plt = None
                        error = True
                elif month == 0:
                    page_name = typegraph.capitalize()+ " in " + str(year)
                    try:
                        plt = plot_general(str(year), '', element, True)
                        error = False
                    except:
                        plt = None
                        error = True
                else:
                    page_name = ''
                    plt = None
                    error = True
            elif not isinstance(month, int) and isinstance(year, int):
                try:
                    plt = plot_general(str(year), '', element, True)
                    error = False
                except:
                    plt = None
                    error = True
                page_name = typegraph.capitalize()+ " in " + str(year)
                
            else:
                return Http404

            context = { 'graph_data': plt,
                    'page_name': page_name,
                    'error': error
                    } 
    else:
        return Http404
    
    
    
    return render(
        request,
        'graphs/graphs.html',
        context= context)

