from PySmartSkies import DIS_API, Session
from .PayloadModels import ControllerPayload
import tempfile
import logging
import json

class WeatherDataProvider():
    def __init__(self, controller_payload: ControllerPayload):
        self.__controller_payload = controller_payload
        self.__dis_api = DIS_API(Session.with_tokens(controller_payload.dis_auth_token, controller_payload.dis_refresh_token, None))
        self.__logger = logging.getLogger()
        self.__virtual_file = None

    def __get_local_weather_data(self):
        weather_data_f = None
        try:
            if self.__controller_payload.weather_data_filepath.endswith('.json'):
                raise Exception('Weather data can only be read from local json files')
            weather_data_f = open(self.__simulator_payload.weather_data_filepath)
            if self.__controller_payload.weather_data_filepath is not None:
                weather_data_f = open(self.__controller_payload.weather_data_filepath)
                weather_data = weather_data_f.read()
                virtual_file = self.__create_virtual_file_with_data(weather_data)
                return virtual_file
        except Exception as _:
            self.__logger.warn("No local weather file loaded")
        finally:
            if weather_data_f is not None:
                weather_data_f.close()
        self.__logger.warn("Local weather data unavailable.")

    def __get_remote_weather_data(self):
        try:
            weather_data = {
                'wind': [],
                'temperature': []
            }

            for lat, lon, _ in self.__controller_payload.waypoints:
                self.__logger.info(f'Requesting weather for lat: {lat} lon: {lon}')
                data = self.__dis_api.get_weather_data(lat, lon)
                if data:
                    temp, wind = data['temperature'], data['wind_vector']
                    weather_data['wind'].append(wind)
                    weather_data['temperature'].append(temp)
                else:
                    raise Exception('AWARE weather endpoint returned with a non 2xx status code.')
            print(json.dumps(weather_data))
            return self.__create_virtual_file_with_data(json.dumps(weather_data))
        except Exception as e:
            self.__logger.warn(e)
        self.__logger.warn("Remote weather data (AWARE) unavailable.")
        return None

    def __create_virtual_file_with_data(self, data: str):
        try:
            self.__virtual_weather_file = tempfile.NamedTemporaryFile(mode="r+", encoding='utf-8')
            self.__virtual_weather_file.write(data)
            self.__virtual_weather_file.seek(0)
            return self.__virtual_weather_file
        except Exception as e:
            self.__logger.warn("Error in creating virtual file for weather data.")
            self.__logger.warn(e)
    
    def __get_weather_data_virtual_file(self):
        if self.__controller_payload.weather_data_filepath is None:
            return self.__get_remote_weather_data()
        return self.__get_local_weather_data()

    def get_weather_data_filepath(self):
        if not self.__virtual_file:
            self.__virtual_file = self.__get_weather_data_virtual_file()
        return self.__virtual_file.name if self.__virtual_file is not None else None

    def close(self):
        if self.__virtual_file:
            self.__virtual_file.close()