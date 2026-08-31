from datetime import datetime, timedelta
class Config():
    def __init__(self, start_date, end_date, lat, lon, ens_cost,timestep=15, formulate_binary=False, wacc=0, expansion_investment_limit=20000, **kwargs):
        self.start_date = datetime.strptime(start_date, "%d.%m.%Y %H.%M")
        self.end_date = datetime.strptime(end_date, "%d.%m.%Y %H.%M")
        self.timestep = timedelta(minutes=timestep)
        self.lat = lat
        self.lon = lon

        self.wacc = wacc
        self.investment_limit = expansion_investment_limit
        self.formulate_binary = formulate_binary

        self.ens_cost = ens_cost


config = None


def set_config(cfg):
    global config
    config = cfg


def get_config():
    return config




