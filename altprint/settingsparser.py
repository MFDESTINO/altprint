import yaml

class SettingsParser:
    
    def load_from_file(self, configfname):

        with open(configfname, 'r') as f:
            params = yaml.safe_load(f)
        return params
        
