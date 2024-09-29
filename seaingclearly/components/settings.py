

from typing import Any, Dict

class Settings: 
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, settings:Dict[str, Any] = None): 
        if not hasattr(self, '_initialized'):
            self._settings: Dict[str, Any] = settings
            self._initialized = True
    
    def getSetting(self, key:str): 
        return self._settings.get(key)