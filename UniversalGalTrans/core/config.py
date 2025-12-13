import configparser
import os

class ConfigManager:
    _instance = None

    def __new__(cls, config_path="config.ini"):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._init_config(config_path)
        return cls._instance

    def _init_config(self, config_path):
        self.config = configparser.ConfigParser()

        # Load defaults
        self.defaults = {
            "General": {
                "OPENAI_API_KEY": "sk-mock-key",
                "OPENAI_BASE_URL": "https://api.openai.com/v1",
                "MODEL": "gpt-3.5-turbo",
                "DEBOUNCE_TIME": "0.3"
            },
            "Server": {
                "HOST": "localhost",
                "PORT": "5000"
            },
            "Display": {
                "FONT_FAMILY": "Microsoft YaHei",
                "FONT_SIZE": "16",
                "TEXT_COLOR": "white",
                "BG_COLOR": "black",
                "OPACITY": "0.8",
                "WINDOW_WIDTH": "800",
                "WINDOW_HEIGHT": "150",
                "X_POS": "100",
                "Y_POS": "600"
            }
        }

        # If config file exists, read it
        if os.path.exists(config_path):
            self.config.read(config_path, encoding='utf-8')

        # Look in parent dir too (for dev env vs dist env)
        elif os.path.exists(os.path.join("..", config_path)):
             self.config.read(os.path.join("..", config_path), encoding='utf-8')

    def get(self, section, key, fallback=None):
        # 1. Try Config File
        if self.config.has_option(section, key):
            return self.config.get(section, key)

        # 2. Try Defaults
        if section in self.defaults and key in self.defaults[section]:
            return self.defaults[section][key]

        return fallback

    def get_int(self, section, key, fallback=0):
        try:
            return int(self.get(section, key, fallback))
        except:
            return fallback

    def get_float(self, section, key, fallback=0.0):
        try:
            return float(self.get(section, key, fallback))
        except:
            return fallback

# Global instance helper
def get_config():
    # Attempt to find config.ini in current working dir
    return ConfigManager("config.ini")
