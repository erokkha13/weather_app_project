from flask import Flask, jsonify, request
import requests
import json

API_KEY = 'p07sBsqPqoJpUfGH0X1Ork6pJTMQk1EX'

def get_location_key(latitude, longitude):
    url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
    params = {
        'apikey': API_KEY,
        'q': f'{latitude},{longitude}',
        'language': 'ru-ru'
    }
    response = requests.get(url, params=params)
    data = response.json()
    location_key = data['Key']
    return location_key

def get_current_weather(location_key):
    url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    params = {
        'apikey': API_KEY,
        'language': 'ru-ru',
        'details': 'true'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data[0]

def extract_weather_parameters(weather_data, forecast_data):
    temperature = weather_data['Temperature']['Metric']['Value']
    humidity = weather_data['RelativeHumidity']
    wind_speed = weather_data['Wind']['Speed']['Metric']['Value']
    rain_probability = forecast_data['DailyForecasts'][0]['Day']['PrecipitationProbability']

    data = {
        'temperature(celsius)': temperature,
        'humidity(percent)': humidity,
        'wind_speed(km_per_hour)': wind_speed,
        'rain_probability(percent)': rain_probability
    }

    return data

def get_forecast(location_key):
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}'
    params = {
        'apikey': API_KEY,
        'language': 'ru-ru',
        'details': 'true',
        'metric': 'true'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def extract_rain_probability(forecast_data):
    rain_probability = forecast_data['DailyForecasts'][0]['Day']['PrecipitationProbability']
    return rain_probability

def check_bad_weather(weather_parameters):
    temperature = weather_parameters['temperature(celsius)']
    wind_speed = weather_parameters['wind_speed(km_per_hour)']
    rain_probability = weather_parameters['rain_probability(percent)']

    if temperature < 0 or temperature > 35:
        return 'Плохие погодные условия'
    elif wind_speed > 50:
        return 'Плохие погодные условия'
    elif rain_probability > 70:
        return 'Плохие погодные условия'
    else:
        return 'Хорошие погодные условия'

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/weather')
def weather():
    try:
        latitude = request.args.get('широта(latitude)',default=55.768740, type=float)
        longitude = request.args.get('долгота(longitude)',default=37.588835, type=float)
        location_key = get_location_key(latitude, longitude)
        current_weather = get_current_weather(location_key)
        forecast = get_forecast(location_key)
        weather_parameters = extract_weather_parameters(current_weather, forecast)
        weather_condition = check_bad_weather(weather_parameters)
        result = {
            'weather_parameters': weather_parameters,
            'weather_condition': weather_condition
        }
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Произошла ошибка: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

