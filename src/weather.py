import requests
from datetime import datetime
from pprint import pprint
from uszipcode import SearchEngine as zip_search_engine

class Weather:
    def __init__(self,zipcode):
        self.zipcode = zipcode
        # Used for global requests settings such as proxy configs
        self.requests_settings = {}
        self.root_url = 'https://api.weather.gov'
        if not self._test_api():
            raise Exception(f'NWS Weather API at {self.root_url} is currently down')

        with zip_search_engine() as zipsearch:
            zipcode_obj = zipsearch.by_zipcode(zipcode)
        if zipcode_obj.zipcode is None:
            raise Exception(f'Zipcode {zipcode} not found')

        self.lat = zipcode_obj.lat
        self.long = zipcode_obj.lng
        self.entry_data = self.weather_entry()
        self.radar_station = self.entry_data['properties']['radarStation']
        self.time_zone = self.entry_data['properties']['timeZone']
        self.geo_id = self.entry_data['properties']['cwa']
        self.weather_zone = self.entry_data['properties']['forecastZone'].split('/')[-1]
        self.radar_station = self.entry_data['properties']['radarStation']
        self.radar_url = f"https://radar.weather.gov/radar.php?rid={self.radar_station[1:]}"
        self.active_alerts = self.get_alerts()

    def _get(self,url=''):
        if url.startswith("http"):
            return requests.get(f'{url}',**self.requests_settings)
        else:
            return requests.get(f'{self.root_url}{url}',**self.requests_settings)
        
    def _test_api(self):
        r = self._get()
        if r.status_code == 200:
            if r.json()['status'] == 'OK':
                return True
            else:
                return False
        else:
            raise Exception(f'API call failed with error {r.status_code}')

    def weather_entry(self):
        r = self._get(f'/points/{self.lat},{self.long}')
        if r.status_code != 200: raise Exception(f'API call failed with error {r.status_code}')
        return r.json()

    def get_alerts(self):
        r = self._get(f'/alerts/active/zone/{self.weather_zone}')
        return r.json()

    def alerts_text(self):
        if 'features' in self.active_alerts.keys() \
        and len(self.active_alerts.get('features')) > 0:
            alerts = []
            for feature in self.active_alerts['features']:
                alert_id = feature['properties']['id']
                areas = feature['properties']['areaDesc']
                event = feature['properties']['event']
                sender = feature['properties']['senderName']
                headline = feature['properties']['headline']
                description = feature['properties']['description']
                msg = f"""\
__Active Alert__:
{event}
__ID__: {alert_id}
__Sender__: {sender}
__Areas of impact__: {areas}
__Message__:
{headline}
{description}
"""
                alerts.append(msg)
            #return '\n\n'.join(alerts)
            return self.active_alerts
        return "No active alerts"

    def weekly_forecast(self):
        r = self._get(self.entry_data['properties']['forecast'])
        return r.json()
    
    def weekly_forecast_text(self):
        response = []
        weekly_forecast = self.weekly_forecast()
        for period in weekly_forecast['properties']['periods']:
            response.append(f"""\
**{period['name']}**
**{period['shortForecast']}** with a temperature of **{period['temperature']}** and wind speed of **{period['windSpeed']} {period['windDirection']}**

""")
        return ''.join(response)


    def weekly_forecast_jupyter(self):
        from IPython.display import Image
        show = []
        weekly_forecast = self.weekly_forecast()
        for period in weekly_forecast['properties']['periods']:
            show.append(Image(url=period['icon']))
            show.append(f"{period['name']} it will be {period['shortForecast']} with a temperature of {period['temperature']} and wind speed of {period['windSpeed']} {period['windDirection']}")
        display(*show)

    
    def hourly_forecast(self):
        r = self._get(self.entry_data['properties']['forecastHourly'])
        return r.json()

    def hourly_forecast_text(self):
        show = []
        hourly_forecast = self.hourly_forecast()
        for period in hourly_forecast['properties']['periods']:
            str_date = period['startTime'][0:10]
            str_time = period['startTime'][11:19]
            str_tz = period['startTime'][19:]

            str_final = f'{str_date} {str_time}'
            str_fmt = '%Y-%m-%d %H:%M:%S'

            forecast_dto = datetime.strptime(str_final,str_fmt)
            forescast_time = forecast_dto.strftime('%a %I:%M %p')
            show.append(f"**{forescast_time}** it will be **{period['shortForecast']}** with a temperature of **{period['temperature']}** and wind speed of **{period['windSpeed']} {period['windDirection']}**")
        return '\n\n'.join(show)

    def hourly_forecast_jupyter(self):
        from IPython.display import Image
        show = []
        hourly_forecast = self.hourly_forecast()
        for period in hourly_forecast['properties']['periods']:
            str_date = period['startTime'][0:10]
            str_time = period['startTime'][11:19]
            str_tz = period['startTime'][19:]

            str_final = f'{str_date} {str_time}'
            str_fmt = '%Y-%m-%d %H:%M:%S'

            forecast_dto = datetime.strptime(str_final,str_fmt)
            forescast_time = forecast_dto.strftime('%a %I:%M %p')

            show.append(Image(url=period['icon']))
            show.append(f"{forescast_time} it will be {period['shortForecast']} with a temperature of {period['temperature']} and wind speed of {period['windSpeed']} {period['windDirection']}")

        display(*show)
