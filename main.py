import os
import pyodbc
import uvicorn
import time
import pandas as pd
from datetime import datetime
from post import postIpfs
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

SERVER = os.environ["SERVER"]
INSTANCE = os.environ["INSTANCE"]
DATABASE = os.environ["DATABASE"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
DRIVER = os.environ["DRIVER"]
TOKEN = os.environ["TOKEN"]
ROWS = os.environ["ROWS"]

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

        date_c = datetime.today().strftime('%Y-%m-%d_%H-%M')

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
            print(file_name)
            temp_file = f"temp_data/{file_name}.json"
            df_co.to_json(temp_file)
            time.sleep(30)
            cid, ret_url = postIpfs(file_name=str(file_name)).send_data()
            print(f'saveIpfs : {file_name}, {ret_url}')

            with pyodbc.connect(
                    'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
                with conn.cursor() as cursor:
                    count = cursor.execute(
                        f"INSERT INTO {INSTANCE} (cid, ret_url, date, time_stamp) VALUES ('{cid}', '{ret_url}', '{file_name}', DEFAULT);").rowcount
                    conn.commit()
                    print(f'Rows inserted: {str(count)}')

            with open('temp_data/init.txt', 'w') as file:
                file.write(str(0))

            os.remove(temp_file)

    else:
        print('Bad token')


@app.get('/last_data/')
async def last_data(token: str):

    if token == TOKEN:
        df_last = pd.read_csv("temp_data/temp_data.csv", index_col=0)
        json_last = df_last.to_json()
        json_format = jsonable_encoder(json_last)
    else:
        print('Bad token')
        json_format = None

    return JSONResponse(content=json_format)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8088)
