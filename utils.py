import os
import xml.etree.ElementTree as et

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def get_data_from_xml() -> tuple:
    """Get first xml file in data folder and parse name and data frame"""
    data_files = [file for file in os.listdir(DATA_DIR) if '.xml' in file]
    if data_files:
        data_file_path = os.path.join(DATA_DIR, data_files.pop())
        tree = et.parse(data_file_path)
        root = tree.getroot()
        for node in root:
            if "area" in node.tag:
                name, parsed_area = _parse_area_node(node)
                prepared_data = _prepare_data(parsed_area)
                return name, prepared_data


def _parse_area_node(node) -> tuple:
    """parse data from area node and return name and data"""
    name = node.find("name").text
    measuring_points = node.findall('measuringpoint')
    points_data = list()
    for point in measuring_points:
        point_data = dict()
        point_data.update(point.attrib)
        point_data.setdefault('channels', list())
        for channel in point:
            channel_data = dict()
            channel_data.update(channel.attrib)
            channel_data.setdefault('periods', list())
            for period in channel:
                period_data = dict()
                period_data.update(period.attrib)
                period_value = int(period.find('value').text)
                period_data.update({'value': period_value})
                channel_data['periods'].append(period_data)
            point_data['channels'].append(channel_data)

        points_data.append(point_data)
    return name, points_data


def _prepare_data(data) -> pd.DataFrame:
    """prepare area data and convert to data frame"""
    prepared_data = []
    for point in data:
        for channels in point['channels']:
            prepared_dict = {'name': point['name'], 'channel_name': channels['desc']}
            periods = channels['periods']
            for index, period in enumerate(periods):
                prepared_dict.update({f'{index + 1}': period['value']})
            prepared_data.append(prepared_dict)
    df = pd.DataFrame(prepared_data)
    df.rename(columns={'name': 'Точка учета', 'channel_name': 'Канал'}, inplace=True)
    return df
