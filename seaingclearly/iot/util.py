import platform
import socket
import uuid

import netifaces

class DeviceInfo(): 
    """
    A class to gather and represent information about a device, including its name, IP address, 
    operating system, machine architecture, MAC address, and a generated UUID.

    Attributes:
        device_name (str): The name of the device (hostname).
        ip_address (str): The IP address of the device.
        os_info (str): The operating system information of the device.
        machine_info (str): The machine architecture information.
        mac_address (str): The MAC address of the device.
        device_uuid (str): A UUID generated from the device's name and MAC address.
    """

    def __init__(self, uuid_namespace: uuid.UUID):
        """
        Initializes the DeviceInfo object by gathering device-specific details.

        Args:
            uuid_namespace (uuid.UUID): The namespace UUID used to generate a unique device UUID.
        
        Sets the following attributes:
            device_name (str): The hostname of the device.
            ip_address (str): The IP address of the device.
            os_info (str): The operating system of the device.
            machine_info (str): The machine architecture of the device.
            mac_address (str): The MAC address of the device.
            device_uuid (str): A unique UUID generated for the device.
        """

        self.device_name = platform.node()
        self.ip_address = self._getIPAddress()
        self.os_info = platform.system()
        self.machine_info = platform.machine()
        self.mac_address = self._getMACAddress()
        self.device_uuid = str(uuid.uuid5(uuid_namespace, self.device_name + self.mac_address))

    def _getIPAddress(self):
        """
        Retrieves the device's IP address by attempting a socket connection.

        Returns:
            str: The IP address of the device, or '127.0.0.1' if it cannot be determined.
        """

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
        """
        Retrieves the first available MAC address from the network interfaces.

        Returns:
            str: The MAC address of the device, or None if it cannot be determined.
        """

        interfaces = netifaces.interfaces()
        for interface in interfaces:
            ifaddresses = netifaces.ifaddresses(interface)
            if netifaces.AF_LINK in ifaddresses:
                mac_address = ifaddresses[netifaces.AF_LINK][0]['addr']
                if mac_address:
                    return mac_address
        return None

    def to_dict(self): 
        """
        Converts the DeviceInfo object to a dictionary representation.

        Returns:
            dict: A dictionary containing the device's information, including name, IP address, 
                  operating system, machine architecture, MAC address, and UUID.
        """
        
        return {
            "device_name": self.device_name,
            "ip_address": self.ip_address,
            "os_info": self.os_info,
            "machine_info": self.machine_info,
            "mac_address": self.mac_address,
            "uuid": self.device_uuid
        }