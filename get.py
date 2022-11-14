import warnings
import pandas as pd
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')


class getData:

    def __init__(self, df_index):

        self.df_output = pd.DataFrame()
        self.df_index = df_index[df_index["ret_url"] != "Bad Request"]
        self.list_url = list(self.df_index["ret_url"])

    def fit(self):
        df_output = self.df_output
        for url_i in self.list_url:
            try:
                df_temp = pd.read_json(url_i)
                print(url_i)
                df_output = pd.concat([df_output, df_temp])
            except:
                print("Bad request")

        return df_output
