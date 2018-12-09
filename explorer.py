import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Explorer:
    _base_api = 'https://explorer.kydcoin.io/api/'
    _base_ext_api = 'http://209.250.244.184/ext/'

    def _get_data(self, base, endpoint):
        try:
            data = requests.get('{}{}'.format(base, endpoint), verify = False, timeout = 10).json()
        except Exception as e:
            print("Explorer", e)
            data = None
        return data

    def _get_api_data(self, endpoint):
        return self._get_data(self._base_api, endpoint)

    def _get_ext_data(self, endpoint):
        return self._get_data(self._base_ext_api, endpoint)

    def get_block_count(self):
        return self._get_api_data('getblockcount')

    def get_mn_data(self):
        return self._get_api_data('getmasternodecount')

    def get_current_supply(self):
        return self._get_ext_data('getmoneysupply')
