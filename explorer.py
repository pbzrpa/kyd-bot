import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from localsettings import BASE_API, BASE_EXP_API

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Explorer:
    _base_api = BASE_API
    _base_ext_api = BASE_EXP_API

    def _get_data(self, base, endpoint):
        try:
            data = requests.get('{}{}'.format(base, endpoint), verify = False, timeout = 10).json()
        except Exception:
            raise Exception('Could not get details from explorer')
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
