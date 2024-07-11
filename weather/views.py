import requests
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseBadRequest
from .models import City
from .forms import CityForm

MAX_CITIES_TO_STORE = 5  # Максимальное количество городов для хранения в сессии

def index(request):
    appid = 'f983a96246b09afeef8e176b7d6d859d'
    url_template = 'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={appid}'
    
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']
            
            # Получаем или создаем список городов из сессии
            cities = request.session.get('cities', [])
            
            # Добавляем новый город в начало списка
            cities.insert(0, city_name)
            
            # Обрезаем список до MAX_CITIES_TO_STORE элементов
            cities = cities[:MAX_CITIES_TO_STORE]
            
            # Сохраняем обновленный список в сессии
            request.session['cities'] = cities
            
            try:
                city_info_list = []
                for city_name in cities:
                    url = url_template.format(city=city_name, appid=appid)
                    res = requests.get(url)
                    res.raise_for_status()  # Проверяем наличие HTTP ошибок
                    weather_data = res.json()
                    
                    city_info = {
                        'city': city_name,
                        'temp': weather_data["main"]["temp"],
                        'icon': weather_data["weather"][0]["icon"]
                    }
                    
                    city_info_list.append(city_info)
                
                context = {'all_info': city_info_list, 'form': form}
                return render(request, 'weather/index.html', context)
            
            except requests.exceptions.HTTPError as http_err:
                error_message = f'HTTP error occurred: {http_err}'
            except Exception as err:
                error_message = f'Error occurred: {err}'
            
            # Если город не найден или произошла ошибка, выводим сообщение об ошибке
            context = {'error': error_message, 'form': form}
            return render(request, 'weather/index.html', context)
        else:
            # Если форма не прошла валидацию, возвращаем ошибку 400 (BadRequest)
            return HttpResponseBadRequest("Invalid form data")
    
    else:
        form = CityForm()
        
        # Получаем список городов из сессии, если он есть
        cities = request.session.get('cities', [])
        
        city_info_list = []
        try:
            for city_name in cities:
                url = url_template.format(city=city_name, appid=appid)
                res = requests.get(url)
                res.raise_for_status()  # Проверяем наличие HTTP ошибок
                weather_data = res.json()
                
                city_info = {
                    'city': city_name,
                    'temp': weather_data["main"]["temp"],
                    'icon': weather_data["weather"][0]["icon"]
                }
                
                city_info_list.append(city_info)
            
            context = {'all_info': city_info_list, 'form': form}
        
        except requests.exceptions.HTTPError as http_err:
            error_message = f'HTTP error occurred: {http_err}'
            context = {'error': error_message, 'form': form}
        except Exception as err:
            error_message = f'Error occurred: {err}'
            context = {'error': error_message, 'form': form}
    
    return render(request, 'weather/index.html', context)
