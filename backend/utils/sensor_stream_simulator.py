import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Generator, List, Iterable
from backend.dao.measurements_dao import MeasurementsDAO
from backend.dao.weather_dao import WeatherDAO


def _measurements_and_weather_to_full_packet(
    measurements: Iterable,
    weather_list: Iterable,
    plant_id: str,
) -> List[tuple]:
    
    weather_dict = {
        (w.timestamp, w.plant_id): w
        for w in weather_list
    }

    full_packets = []

    for measure in measurements:
        key = (measure.timestamp, plant_id)

        if key not in weather_dict:
            continue

        w = weather_dict[key]
        weather_info = {
            "AMBIENT_TEMPERATURE": w.ambient_temperature,
            "MODULE_TEMPERATURE": w.module_temperature,
            "IRRADIATION": w.irradiation,
        }

        full_packets.append(
            (
                weather_info,
                measure.ac_power,
                measure.timestamp,
                measure.panel_id,
            )
        )

    return full_packets


def weather_stream_simulator(
        interval_s: int = 1, data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", 
        start_time: datetime = None, end_time: datetime = None
) -> Generator[Tuple[dict, float, datetime, str], None, None]:
    
    weather_dao = WeatherDAO(data_directory=data_directory)

    weathers = weather_dao.get_weather_measurements_by_plant_id_and_time_range(plant_id=plant_id,  start_time=start_time, end_time=end_time)
        
    for packet in weathers:
        yield packet
        if interval_s != 0:
            time.sleep(interval_s)


def panel_stream_simulator(interval_s: int = 1, data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", 
        start_time: datetime = None, end_time: datetime = None
) -> Generator[Tuple[dict, float, datetime, str], None, None]:
    
    measurements_dao = MeasurementsDAO(data_directory=data_directory)
            
    measurements = measurements_dao.get_panel_measurements_by_plant_id_and_time_range(plant_id=plant_id, start_time=start_time, end_time=end_time)

    for packet in measurements:
        yield packet
        if interval_s != 0:
            time.sleep(interval_s)


def full_packet_stream_simulator(
        interval_s: int = 1, data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", panel_id: str = None, 
        start_time: datetime = None, end_time: datetime = None
) -> Generator[Tuple[dict, float, datetime, str], None, None]:
    
    measurement_dao = MeasurementsDAO (data_directory=data_directory)
    weather_dao = WeatherDAO(data_directory=data_directory)

    full_packets = []
    measurements = []
    weathers = []

    
    if panel_id is None:
        measurements = measurement_dao.get_panel_measurements_by_plant_id_and_time_range(plant_id, start_time=start_time, end_time=end_time)
        weathers = weather_dao.get_weather_measurements_by_plant_id_and_time_range(plant_id=plant_id, start_time=start_time, end_time=end_time)
    else:
        measurements = measurement_dao.get_panel_measurements_by_panel_id_and_time_range(plant_id=plant_id, panel_id=panel_id, start_time=start_time, end_time=end_time)
        weathers = weather_dao.get_weather_measurements_by_plant_id_and_time_range(plant_id, start_time=start_time, end_time=end_time)

    full_packets = _measurements_and_weather_to_full_packet(
        measurements=measurements,
        weather_list=weathers,
        plant_id=plant_id,
    )   

    for packet in full_packets:
        yield packet
        if interval_s != 0:
            time.sleep(interval_s)


def load_historical_data(
        data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", 
        end_time: datetime = None
) -> List[Tuple[Dict[str, Any], float, datetime, str]]:
    
    measurement_dao = MeasurementsDAO (data_directory=data_directory)
    weather_dao = WeatherDAO(data_directory=data_directory)

    full_packets = []
    measurements = []
    weathers = []

    if end_time is None:
        measurements = measurement_dao.get_all_panel_measurements_by_plant_id(plant_id)
        weathers = weather_dao.get_all_weather_measurements_by_plant_id(plant_id)

    else:
        measurements = measurement_dao.get_panel_measurements_by_plant_id_and_time_range(plant_id, end_time=end_time, start_time=None)
        weathers = weather_dao.get_weather_measurements_by_plant_id_and_time_range(plant_id=plant_id, end_time=end_time, start_time = None)

    
    full_packets = _measurements_and_weather_to_full_packet(
        measurements=measurements,
        weather_list=weathers,
        plant_id=plant_id,
    )
   
    return full_packets


def load_future_weather_data(
        data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", 
        end_time: datetime = None,
        start_time: datetime = None,
) -> List[Tuple[Dict[str, Any], datetime, str]]:
    
    measurement_dao = MeasurementsDAO (data_directory=data_directory)
    weather_dao = WeatherDAO(data_directory=data_directory)

    full_packets = []
    measurements = []
    weathers = []


    if start_time is None and end_time is None:
        measurements = measurement_dao.get_all_panel_measurements_by_plant_id(plant_id)
        weathers = weather_dao.get_all_weather_measurements_by_plant_id(plant_id)

    else:
        if end_time is None:
            end_time = datetime.max
        if start_time is None:
            start_time = datetime.max
        measurements = measurement_dao.get_panel_measurements_by_plant_id_and_time_range(plant_id, end_time=end_time, start_time=start_time)
        weathers = weather_dao.get_weather_measurements_by_plant_id_and_time_range(plant_id=plant_id, end_time=end_time, start_time = start_time)


    full_packets = _measurements_and_weather_to_full_packet(
        measurements=measurements,
        weather_list=weathers,
        plant_id=plant_id,
    )
   
    return full_packets





#for i, packet in enumerate(full_packet_stream_simulator()):
#    print(i)
#for i, packet in enumerate(weather_stream_simulator()):
#    print(i)
#s = "2020-06-15 12:00:00"
#start_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
#for i, packet in enumerate(load_future_weather_data(start_time=start_time)):
#    print(f"\r\nMeteo {i}: timestamp= {packet[2]}")
#    print(packet)
