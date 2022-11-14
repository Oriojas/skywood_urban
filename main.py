import os
import pyodbc
import uvicorn
import time
import datetime
import warnings
import pandas as pd
from datetime import datetime
from post import postIpfs
from get import getData
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

app = FastAPI()

ROWS = os.environ["ROWS"]
TOKEN = os.environ["TOKEN"]
SERVER = os.environ["SERVER"]
DRIVER = os.environ["DRIVER"]
DELAY = int(os.environ["DELAY"])
INSTANCE = os.environ["INSTANCE"]
DATABASE = os.environ["DATABASE"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
FOLDER_DATA = os.environ["FOLDER_DATA"]

with open('temp_data/init.txt', 'w') as f:
    f.write(str(0))

df = pd.DataFrame(columns=['CO2', 'DATE_C', 'ORIGIN'])
df.to_csv('temp_data/temp_data.csv')


@app.get('/send_data/')
async def send_data(co2: int, origin: str, token: str):
    """
    this endpoint send data ti ipfs and index in SQL database
    :param co2: co2 in ppm from sensor
    :param origin: name sensor
    :param token: token from sensor
    :return:
    """

    if token == TOKEN:

        df_co = pd.read_csv('temp_data/temp_data.csv', index_col=0)

        date_c = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        df_co = df_co.append({'CO2': co2,
                              'DATE_C': date_c,
                              'ORIGIN': origin}, ignore_index=True)

        if len(df_co) > int(ROWS):
            df_co = df_co.drop([0], axis=0)
        df_co.to_csv('temp_data/temp_data.csv')

        with open('temp_data/init.txt') as file:
            cont = file.read()

        cont = int(cont)
        cont += 1
        with open('temp_data/init.txt', 'w') as file:
            file.write(str(cont))
        print(f'counter : {cont}')

        if cont == int(ROWS):
            file_name = df_co['DATE_C'].iloc[-1]
            file_name = file_name.replace(" ", "_")
            file_name = file_name.replace(":", "_")
            print(file_name)
            temp_file = f"temp_data/{file_name}.json"
            df_co.to_json(temp_file)
            time.sleep(DELAY)
            cid, ret_url = postIpfs(file_name=str(file_name)).send_data()
            print(f'saveIpfs : {file_name}, {ret_url}')

            with pyodbc.connect(
                    'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
                with conn.cursor() as cursor:
                    count = cursor.execute(
                        f"INSERT INTO {INSTANCE} (cid, ret_url, date, time_stamp, claim) VALUES ('{cid}', '{ret_url}', '{file_name}', DEFAULT, DEFAULT);").rowcount
                    conn.commit()
                    print(f'Rows inserted: {str(count)}')

            with open('temp_data/init.txt', 'w') as file:
                file.write(str(0))

            os.remove(temp_file)

    else:
        print('Bad token')


@app.get('/last_data/')
async def last_data(token: str):
    """
    this endpoint is used to render in front
    :param token: token endpoint
    :return: 60 las data
    """
    if token == TOKEN:
        df_last = pd.read_csv("temp_data/temp_data.csv", index_col=0)
        df_last['DATE_C'] = pd.to_datetime(df_last['DATE_C'])
        df_last['DATE_C'] = df_last['DATE_C'].apply(lambda x: x.timestamp())

        json_format = jsonable_encoder(df_last.to_dict(orient="records"))
    else:
        print('Bad token')
        json_format = None

    return JSONResponse(content=json_format)


@app.get('/query_ipfs/')
async def query_ipfs(init_date: str, final_date: str):
    """
    this endpoint query in ipfs directly
    :param init_date: example 2022-11-13 22:19:44.453
    :param final_date: example 2022-11-13 22:19:44.453
    :return: json object
    """
    with pyodbc.connect(
            'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
        sql_query = f"SELECT id, cid, ret_url, [date], time_stamp, claim FROM {INSTANCE} WHERE time_stamp BETWEEN '{init_date}' AND '{final_date}'"

        df_l = pd.read_sql(sql_query, conn)
        df_l = df_l[["time_stamp", "ret_url"]]
        df_output = getData(df_index=df_l).fit()
        json_format = jsonable_encoder(df_output.to_dict(orient="records"))

    return JSONResponse(content=json_format)


@app.get('/query_drop/')
async def query_drop(token: str):
    """
    this endpoint query disposable drop
    :param token: token endpoint
    :return: int, claim
    """
    if token == TOKEN:

        with pyodbc.connect(
                'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
            sql_query = f"SELECT cid FROM {INSTANCE} WHERE claim = 0"

            df_l = pd.read_sql(sql_query, conn)
            claim = len(df_l)
    else:
        claim = None

    return claim


@app.get('/claim_drop/')
async def claim_drop(token: str, user: str):
    """
    this endpoint claim disposable drop
    :param token: token endpoint
    :param user: str
    :return: json response
    """
    if token == TOKEN:

        with pyodbc.connect(
                'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
            sql_query = f"SELECT * FROM {INSTANCE} WHERE claim = 0"

        df_l = pd.read_sql(sql_query, conn)

        claim = len(df_l)

        if claim > 0:
            with pyodbc.connect(
                    'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
                with conn.cursor() as cursor:
                    count = cursor.execute(
                        f"UPDATE {INSTANCE} SET claim = 1 WHERE claim = 0;").rowcount
                    conn.commit()
                    print(f'Claim: {str(count)}')

            file_name = f"claim_{user}_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}"
            df_l.to_json(f'temp_data/{file_name}.json')
            time.sleep(DELAY)

            cid, ret_url = postIpfs(file_name=str(file_name)).send_data()

            os.remove(f'{FOLDER_DATA}{file_name}.json')

            response = {"cid": cid,
                        "ret_url": ret_url,
                        "claim": claim}

        else:
            response = {"cid": "Bad Request",
                        "ret_url": "Bad Request",
                        "claim": "No claim available"}

    else:
        response = {"cid": "Bad Request",
                    "ret_url": "Bad Request",
                    "claim": "No claim available"}

    json_format = jsonable_encoder(response)

    return JSONResponse(content=json_format)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8088)
