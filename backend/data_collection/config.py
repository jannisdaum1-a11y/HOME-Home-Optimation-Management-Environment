from datetime import datetime, timedelta
class Config():
    def __init__(self, start_date, end_date, lat, lon, ens_cost,timestep=15, **kwargs):
        self.start_date = datetime.strptime(start_date, "%d.%m.%Y %H.%M")
        self.end_date = datetime.strptime(end_date, "%d.%m.%Y %H.%M")
        self.timestep = timedelta(minutes=timestep)
        self.lat = lat
        self.lon = lon

        self.p_grid_max = kwargs.get("p_grid_max", 10000)  # Maximum grid power in Watts
        self.p_grid_min = kwargs.get("p_grid_min", -10000)  # Minimum grid power in Watts (negative for export)

        self.wacc = kwargs.get("wacc", 0) or 0
        self.formulate_binary = kwargs.get("formulate_binary", True)

        self.ens_cost = ens_cost


config = None


def set_config(cfg):
    global config
    config = cfg


def get_config():
    return config




