import json

from getpass import getpass
from mysql.connector import connect, Error

with open("storage/configs/sql.json", "r") as f:
    config = json.load(f)


show_table_query = "DESCRIBE userdata"
testez = """
INSERT INTO `userdata`
(`uid`, `comanda`, `argumente`) 
VALUES
('550776915720536085', 'stats', 'agape')
"""
try:
    with connect(host=config["host"], user=config["user"], password=config["password"], database=config["database"] + 'sampstats') as connection:
        with connection.cursor() as cursor:
            cursor.execute(testez)
            connection.commit()
            print("[+] SQL: OK")
            cursor.execute(show_table_query)
            result = cursor.fetchall()
            for row in result:
                print(row)
            connection.commit()

except Error as e:
    print(e)