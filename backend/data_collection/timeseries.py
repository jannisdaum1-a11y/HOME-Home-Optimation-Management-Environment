import pandas as pd

from .config import get_config

class TimeSeries():
    def __init__(self, data:pd.DataFrame|str):

        active_config = get_config()
        if isinstance(data, str):
            data = pd.read_csv(data)

        start_time = active_config.start_date
        end_time = active_config.end_date
        timestep = active_config.timestep

        # Resample available data to timedelt if necessary
        if(all([isinstance(index, pd.Timestamp) for index in data.index])):
            if not (data.index[1]-data.index[0] == timestep):
                data.resample(rule=timestep).interpolate()

        #Genererate identical indices
        indexes = pd.date_range(start=start_time, end=end_time-timestep,freq=timestep)

        if len(data)<len(indexes):
            Warning("Timeseries length does not match, try to expand")
            #Repeat data until long enough
            while len(data)<len(indexes):
                data = pd.concat([data, data], axis=0)

        # Cut unnecessary data
        if len(data)>len(indexes):
            data = data.iloc[:len(indexes)]

        # Set indexes
        if len(indexes)==len(data):
            data.index = indexes
        else:
            ValueError("Timeseries length does not match. Rescaling failed!")

        self.data = data
        return