import os
import xml.etree.ElementTree as et
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def get_xml_data_file():
    """Get first xml file in data folder and parse to data frame"""
    data_files = [file for file in os.listdir(DATA_DIR) if '.xml' in file]
    if data_files:
        data_file_path = os.path.join(DATA_DIR, data_files.pop())
        tree = et.parse(data_file_path)
        root = tree.getroot()
        for node in root:
            if "area" in node.tag:
                parsed_area = _parse_area_node(node)
                prepared_data = _prepare_data(parsed_area)
                return prepared_data


def _parse_area_node(node) -> dict:
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
    return {'name': name, 'data': points_data}


def _prepare_data(data) -> pd.DataFrame:
    """prepare area data and convert to data frame"""
    df = pd.DataFrame(data['data'], columns=['name', 'channels'])
    for channel_data in df['channels']:
        _calculate_consuming(channel_data)
        break


def _calculate_consuming(channel_data) -> pd.DataFrame:
    """calculate consuming for each measuring point
        01, 03 - input
        02, 04 - output
    """
    points = {'input': [], 'output': []}
    for channel in channel_data:
        periods = channel['periods']
        if int(channel['code']) % 2:
            points['input'].append(periods)
        else:
            points['output'].append(periods)

    for _, point in points.items():
        data = _sum_dict_values(point, 'value')
        print(data)


def _sum_dict_values(data, key) -> list:
    """sum by 'value' key from measuring point"""
    computed_data = list()
    first_dict = data.pop()
    second_dict = data.pop()
    for index, item in enumerate(first_dict):
        item_two = second_dict[index]
        if item['start'] == item_two['start'] and item['end'] == item_two['end']:
            items_value_sum = item[key] + item_two[key]
            item.update({key: items_value_sum})
            computed_data.append(item)
        else:
            raise Exception(f'Error when sum dict {item} and {item_two}')
    return computed_data


get_xml_data_file()
