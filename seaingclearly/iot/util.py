import platform
import socket
import uuid

import netifaces

class DeviceInfo(): 
    def __init__(self, uuid_namespace: uuid.UUID):
        self.device_name = platform.node()
        self.ip_address = self._getIPAddress()
        self.os_info = platform.system()
        self.machine_info = platform.machine()
        self.mac_address = self._getMACAddress()
        self.device_uuid = str(uuid.uuid5(uuid_namespace, self.device_name + self.mac_address))

    def _getIPAddress(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.254.254.254', 1))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '127.0.0.1'
        finally:
            s.close()
        return ip_address

    def _getMACAddress(self):
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            ifaddresses = netifaces.ifaddresses(interface)
            if netifaces.AF_LINK in ifaddresses:
                mac_address = ifaddresses[netifaces.AF_LINK][0]['addr']
                if mac_address:
                    return mac_address
        return None

    def to_dict(self): 
        return {
            "device_name": self.device_name,
            "ip_address": self.ip_address,
            "os_info": self.os_info,
            "machine_info": self.machine_info,
            "mac_address": self.mac_address,
            "uuid": self.device_uuid
        }