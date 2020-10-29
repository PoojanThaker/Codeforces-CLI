import psycopg2
from Scrapper.constants import *
import pandas as pd


class DatabaseConnect:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=PASSWORD)
            self.cur = self.conn.cursor()
            # For the first time, implement table
            # self.cur.execute("""CREATE TABLE problems(
            #                                 id text PRIMARY KEY NOT NULL,
            #                                 url text NOT NULL,
            #                                 platform text,
            #                                 metadata json,
            #                                 statement json)"""
            #                     )
            # self.conn.commit()
            self.check_problems_table_exist()
        except Exception as e:
            print("Database connection failed due to the following issue: {}".format(e))

    def check_problems_table_exist(self):
        sql = """
                SELECT "table_name","column_name", "data_type", "table_schema"
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE "table_schema" = 'public'
                ORDER BY table_name
                """
        info = pd.read_sql(sql, con=self.conn)
        df = info[info.table_name == 'problems']
        df = df.column_name.isin(['id', 'url', 'platform', 'metadata', 'statement']).all()
        assert df, "The table \'problems\' does not exist in the database."

    def put_problems(self, problem):
        sql = """ INSERT INTO problems(id, url, platform, metadata, statement)
                    VALUES (%s, %s, %s, %s, %s) RETURNING *;"""
        self.cur.execute(sql, (problem.id, problem.url, problem.platform, problem.metadata, problem.statement))
        self.conn.commit()