class Printer:
    def __init__(self, **kwargs):
        prop_defaults = {
            "table_size": (200, 200),
            "table_center": (100,100,0),
            "start_script": "",
            "end_script": ""
        }

        for (prop, default) in prop_defaults.items():
           setattr(self, prop, kwargs.get(prop, default))
