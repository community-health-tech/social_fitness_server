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
        fitbit_devices_list = list(fitbit_device)

        if not fitbit_devices_list:
            raise ValueError(f"No Fitbit device found matching version: {device_version}")
        return fitbit_devices_list[0]
        
    @staticmethod
    def get_datetime(datetime_string):
        return parser.parse(datetime_string + " EST")
    