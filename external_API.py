import fire
import os ,sys ,pathlib
sys.path.append(os.getcwd())
from typing import List,Dict,Union,Optional
import requests,re
from datetime import datetime

from Config.external_API import Info as external_API
stocknames_API_urls=external_API.stocknames

from tools import normalize_text


class StockName_API_Base():

    def __init__(self,API_urls=stocknames_API_urls.HK):
        self.Chi_API_url=API_urls.Chi
        self.Eng_API_url=API_urls.Eng


    def get_requests(self,url)->Union[str,None]:
        API_resp = requests.get(url)
        API_status_code = API_resp.status_code
        if API_status_code == 200:
            return API_resp.content.decode('utf-8')
        else:
            print(API_status_code, 'Error from API: ',url)
            return None

    def get_stocknames_bylanguage(self,lang:str='chinese')->Union[Dict,None]:
        assert lang.lower() in ['chinese','chi','english','eng']
        API_url = self.Chi_API_url if lang.lower() in ['chinese', 'chi'] else self.Eng_API_url
        api_content = self.get_requests(API_url)

        if api_content is None :
            return None
        else:
            API_data = api_content.split('\n')[3:]
            StockNames = {}
            for i in API_data:
                if lang.lower() in ['chinese','chi']:
                    name, code = i.split(',')
                else:
                    code, name = i.split(',')


                name=normalize_text(name.replace(' ',''))
                name = re.sub('\-\w{1,2}$','',name)
                StockNames[code] = name

            return StockNames


    def get_stocknames_bymarket(self)->Union[Dict,None]:
        Chi_data=self.get_stocknames_bylanguage(lang='Chinese')
        Eng_data=self.get_stocknames_bylanguage(lang='English')

        if Chi_data is None or Eng_data is None:
            return None
        raw_data=[]
        for id,name in Chi_data.items():
            market=id.split('.')[0] if re.search('\.',id) else 'HK'
            id = id.split('.')[1] if re.search('\.', id) else id
            name = Eng_data.get(id,None) if name in [None,'',' '] else name

            raw_data.append({'code':id,'market':market,'name':name})

        return raw_data

def get_stocknames(market:Optional[str]='ALL'):
    assert market.upper() in ['HK', 'HONGKONG', 'SH', 'SHANGHAI', 'SZ', 'SHENZHEN', 'ALL']

    if market.upper() in ['HK', 'HONGKONG']:
        return StockName_API_Base(API_urls=stocknames_API_urls.HK).get_stocknames_bymarket()

    elif market.upper() in ['SH', 'SHANGHAI']:
        return StockName_API_Base(API_urls=stocknames_API_urls.Shanghai).get_stocknames_bymarket()

    elif market.upper() in ['SZ', 'SHENZHEN']:
        return StockName_API_Base(API_urls=stocknames_API_urls.Shenzhen).get_stocknames_bymarket()
    else:
        HK=StockName_API_Base(API_urls=stocknames_API_urls.HK).get_stocknames_bymarket()
        SH = StockName_API_Base(API_urls=stocknames_API_urls.Shanghai).get_stocknames_bymarket()
        SZ = StockName_API_Base(API_urls=stocknames_API_urls.Shenzhen).get_stocknames_bymarket()
        ALL = HK + SH + SZ
        return ALL


if __name__=='__main__':
    fire.Fire({'stocknames':get_stocknames})