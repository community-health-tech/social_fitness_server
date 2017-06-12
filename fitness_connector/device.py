from dateutil import parser

FITBIT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

class Device:
   
    def __init__(self, fitbit, account):
        self._device = self._get_fitbit_device(fitbit, account.device_version)
        self.id = self._device["id"]
        self.device_version = self._device["deviceVersion"]
        self.last_sync_time = self.get_datetime(self._device["lastSyncTime"])
        
    @staticmethod
    def _get_fitbit_device(fitbit, device_version):
        fitbit_device = filter(
            lambda x: x["deviceVersion"] == device_version,
            fitbit.get_devices())
        fitbit_device = list(fitbit_device)[0]
        return fitbit_device
        
    @staticmethod
    def get_datetime(datetime_string):
        return parser.parse(datetime_string + " EST")
    