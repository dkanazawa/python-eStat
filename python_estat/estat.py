import json
import urllib.parse
import urllib.request
from IPython import get_ipython
from IPython.display import display

import pandas as pd
import numpy as np


API_VERSION = "3.0"
p_id = {"appId": ""}


def is_env_notebook():
    """Determine wheather is the environment Jupyter Notebook"""
    if 'get_ipython' not in globals():
        # Python shell
        return False
    env_name = get_ipython().__class__.__name__
    if env_name == 'TerminalInteractiveShell':
        # IPython shell
        return False
    # Jupyter Notebook
    return True


def set_appid(filename):
    global p_id
    with open(filename) as f:
        p_id = json.load(f)


def get_api_return_val(param, url):
    param.update(p_id)
    url += urllib.parse.urlencode(param)
    with urllib.request.urlopen(url) as response:
        return response.read()


def get_list(param, form='df'):
    url = 'http://api.e-stat.go.jp/rest/' + API_VERSION + '/app/json/getStatsList?'
    res = get_api_return_val(param, url).decode()
    if ('statsNameList', 'Y') in param.items():
        d = pd.json_normalize(json.loads(res)['GET_STATS_LIST']['DATALIST_INF']['LIST_INF'])
        if form in ['df', 'dfall']:
            return d
        else:
            return res
    else:
        d = pd.json_normalize(json.loads(res)['GET_STATS_LIST']['DATALIST_INF']['TABLE_INF'])
        if form == 'df':
            return d[['STAT_NAME.@code', 'STAT_NAME.$', 'STATISTICS_NAME', '@id', 'TITLE.$']]
        elif form == 'dfall':
            return d
        else:
            return res


def get_rowdata(param):
    url = 'http://api.e-stat.go.jp/rest/' + API_VERSION + '/app/json/getStatsData?'
    res = get_api_return_val(param, url).decode()
    res_json = json.loads(res)
    for class_item in res_json['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']:
#        print(type(class_item['@id']))
        print(class_item['@id'] + ':' + class_item['@name'])
        if is_env_notebook():
            display(pd.json_normalize(class_item['CLASS']))
        else:
            print(pd.json_normalize(class_item['CLASS']))
    return pd.json_normalize(res_json['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE'])


def get_data(param):
    url = 'http://api.e-stat.go.jp/rest/' + API_VERSION + '/app/json/getStatsData?'
    res = get_api_return_val(param, url).decode()
    res_json = json.loads(res)
    df = pd.json_normalize(res_json['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE'])
    for class_item in res_json['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']:
        classdf = pd.json_normalize(class_item['CLASS'])
        df = df.merge(classdf,
                left_on = '@' + class_item['@id'],
                right_on = '@code',
                suffixes = ('', '_' + class_item['@id']),
                validate = 'many_to_one')
        df = df.rename(columns = {'@name': class_item['@name'] + '_' + class_item['@id'] })
    df.columns = df.columns.str.replace('@', '')
    df = df.rename(columns = {'$': 'value'})
    # replace specific value to NaN
    df.value.replace(['-','ÅE', '•'], np.nan, inplace=True)
    # change dtypes
    for col in df.columns:
        try:
            df = df.astype({col: int}, copy=False)
        except:
            try:
                df = df.astype({col: float}, copy=False)
            except:
                try:
                    df = df.astype({col: 'datatime64'}, copy=False)
                except:
                    pass
        
    return df

