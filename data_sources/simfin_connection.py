from datetime import datetime
from typing import List
import pandas as pd
import requests
from utils.config_utils import fetch_key
from utils.files_utils import check_file


class SimFinConnection(object):
    STATEMENT_DIRECTORY = 'client_data/data/statements'
    PRICES_DIRECTORY = 'client_data/data/prices'
    name = 'SimFin'
    FILE_PREFIX = 'SF'
    URL = "https://simfin.com/api/v2/companies/"

    def __init__(self):
        self.api_key = fetch_key(self.name)

    def __repr__(self):
        return f"{self.name} API Connection"

    def get_statements(self, ticker: str,
                       statement_type: str,
                       periods: List[str],
                       fiscal_years: List[int],
                       read: bool = True):
        """
        retrieve financial statements for a certain ticker
        :param ticker: string of available ticker
        :param statement_type: pl: Profit & Loss statement, bs: Balance Sheet, cf: Cash Flow, derived: Derived figures & fundamental ratios
        :param periods: q1: First fiscal period, q2: Second fiscal period, q3: Third fiscal period, q4: Fourth fiscal period, fy: Full fiscal year.
        :param fiscal_years: list of integers for the wanted statement years retreived
        :param read: attempt to read file from disk
        :return: DataFrame containing the periods specified for the year or empty DataFrame if no data found
        """
        filename = f"{self.FILE_PREFIX}_{ticker}_{statement_type}_{''.join(periods)}_{''.join([str(y) for y in fiscal_years])}.csv"
        directory = self.STATEMENT_DIRECTORY
        if read:
            if check_file(directory=directory, file=filename):
                return pd.read_csv(f"{directory}/{filename}")

        columns = []
        output = []
        request_url = f"{self.URL}statements"
        for year in fiscal_years:
            for period in periods:
                params = {"statement": statement_type,
                          "ticker": ticker,
                          "period": period,
                          "fyear": year,
                          "api-key": self.api_key}

                request = requests.get(request_url, params)
                data = request.json()[0]

                if data['found'] and len(data['data']) > 0:
                    if len(columns) == 0:
                        columns = data['columns']
                    output += data['data']
                else:
                    print(f"api error: period {period} not found")

        df = pd.DataFrame(output, columns=columns)
        df.to_csv(f"{directory}/{filename}")
        return df

    def get_prices(self, ticker: str,
                   start: datetime,
                   end: datetime,
                   read: bool = True):

        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        filename = f"{self.FILE_PREFIX}_{ticker}_prices.csv"
        directory = self.PRICES_DIRECTORY
        if read:
            if check_file(directory=directory, file=filename):
                df = pd.read_csv(f"{directory}/{filename}")
                print(f"last date retrieved: {df.Date.max()}")
                return df.loc[(df.Date >= start) & (df.Date <= end)]

        columns = []
        output = []
        request_url = f"{self.URL}prices"

        params = {"ticker": ticker,
                  "api-key": self.api_key}

        request = requests.get(request_url, params)
        data = request.json()[0]
        currency = data['currency']
        if data['found'] and len(data['data']) > 0:
            if len(columns) == 0:
                columns = data['columns']
            output += data['data']

        df = pd.DataFrame(output, columns=columns)
        df['Currency'] = currency
        df.drop(columns=['Dividend', 'Common Shares Outstanding', 'Adj. Close', 'SimFinId'], inplace=True)
        df.set_index('Date', inplace=True)
        df.index.name = 'Date'
        df.to_csv(f"{directory}/{filename}")
        return df.loc[(df.index >= start) & (df.index <= end)]


if __name__ == '__main__':
    pass
