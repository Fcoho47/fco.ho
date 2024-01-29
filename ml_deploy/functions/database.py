#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import warnings
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')


import pymysql, os
import pandas as pd
from datetime import datetime


DB_NAME = os.environ.get('DATABASE_DATABASE')
DB_USER = os.environ.get('DATABASE_USER')
DB_PASS = os.environ.get('DATABASE_PASSWORD')

DB_HOST = os.environ.get('DATABASE_HOST')
DB_PORT = os.environ.get('DATABASE_PORT')


class SolarityDB:
    def __init__(self, db_name=DB_NAME):
        self.connection = pymysql.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=db_name, port=int(DB_PORT), connect_timeout=5)
           
    def reconnect(self):
        self.connection.close()
        self.__init__()

    def close_connection(self):
        self.connection.close()

    def query_raw(self, sql_query: str):
        self.connection.ping(reconnect=True)  
        with self.connection.cursor() as cursor:
            cursor.execute(sql_query)
        self.connection.commit()

    def query_to_df(self, sql_query: str):
        self.connection.ping(reconnect=True)  
        sql_df = pd.read_sql(sql_query, con=self.connection)
        return sql_df

    def query_timeseries(self, table: str, fields: list[str], identifiers: tuple[str, list], 
                        datetime_name: str, start: str, end: str, order_fields: list[str] = [],
                        where_clauses = []):
        """ Retorna dataframe con datos de series de tiempo desde la base de datos 

        Args:
            table (str): Nombre de la tabla de la BD.
            fields (list[str]): Lista de columnas a consultar de la tabla.
            identifiers (tuple[str, list]): Tupla de la forma (nombre del identificador, identificadores a buscar). Ejemplo: ('id_planta', [12, 16]).
            datetime_name (str): Nombre de la columna que contiene las fechas.
            start (str): Fecha desde la que se extraen datos.
            end (str): Fecha hasta la se extraen los datos.
            order_fields (list[str], optional): Lista con campos con los cuales Defaults to [].
            where_clauses (list[str], optional): Lista con camp. Defaults to []
        Returns:
            pd.Dataframe: Serie de tiempo 
        """

        identifiers_list = ",".join([str(value) for value in identifiers[1]])
        fields_list = ",".join(fields)

        query = f"SELECT {fields_list} FROM {table} WHERE {identifiers[0]} IN ({identifiers_list}) AND {datetime_name} >= '{start}' and {datetime_name} <= '{end}'"
        
        if where_clauses:
            for clause in where_clauses: 
                query += f'AND {clause[0]} {clause[1]} {clause[2]} '
        
        if order_fields:
            query += f" ORDER BY {','.join(order_fields)}"

        return self.query_to_df(query)

    def query_timeseries_without_identifiers(self, table: str, fields: list[str], datetime_name: str, start: str, end: str, order_fields: list[str] = []):
        """ Retorna dataframe con datos de series de tiempo desde la base de datos 

        Args:
            table (str): Nombre de la tabla de la BD.
            fields (list[str]): Lista de columnas a consultar de la tabla.
            identifiers (tuple[str, list]): Tupla de la forma (nombre del identificador, identificadores a buscar). Ejemplo: ('id_planta', [12, 16]).
            datetime_name (str): Nombre de la columna que contiene las fechas.
            start (str): Fecha desde la que se extraen datos.
            end (str): Fecha hasta la se extraen los datos.
            order_fields (list[str], optional): Lista con campos con los cuales Defaults to [].

        Returns:
            pd.Dataframe: Serie de tiempo 
        """

        fields_list = ",".join(fields)

        query = f"SELECT {fields_list} FROM {table} WHERE {datetime_name} >= '{start}' and {datetime_name} <= '{end}'"
        if order_fields:
            query += f" ORDER BY {','.join(order_fields)}"

        return self.query_to_df(query)

    def query_table(self, table: str, fields: list[str], identifiers: tuple[str, list], 
                    order_fields: list[str] = [], other_conditions=[]):

        identifiers_list = ",".join([str(value) for value in identifiers[1]])
        fields_list = ",".join(fields)

        ### Adición de otras condiciones
        additional_where_clasues = ""
        if other_conditions:
            for condition in other_conditions:
                clause, column, operator, values = condition

                if clause.lower() == 'where':
                    additional_where_clasues += f"\nAND {column} {operator} {values}"

        ## Creación de query definitiva
        query = f"SELECT {fields_list} FROM {table} WHERE {identifiers[0]} IN ({identifiers_list}) {additional_where_clasues}\n"
        if order_fields:
            query += f" ORDER BY {','.join(order_fields)}"

        return self.query_to_df(query)



    def upload_df_to_DB(self, dataframe: pd.DataFrame, table: str, chunksize: int = 1000, duplicate_keys_clause: str = ""):
        n_data = len(dataframe.index)
        remaining_rows = n_data

        fields = ', '.join(dataframe.columns)

        if duplicate_keys_clause == "":
            on_duplicate_keys = ', '.join(
                list(map(lambda field: f"{field} = VALUE({field})", dataframe.columns)))
        else:
            on_duplicate_keys = duplicate_keys_clause

        iteration = 0
        while remaining_rows >= 0:
            start_idx = iteration*chunksize
            if remaining_rows > chunksize:
                end_idx = start_idx + chunksize
            else:
                end_idx = start_idx + remaining_rows

            # Obtener valores del chunk
            updating_df = dataframe[start_idx:end_idx]

            values = []
            for _, row in updating_df.iterrows():
                values.append(f'({", ".join(list(row))})')

            # Construir y ejecutar SQL Query
            sql = f"INSERT INTO {table} ({fields}) VALUES {','.join(values)} ON DUPLICATE KEY UPDATE {on_duplicate_keys}"            
            
            self.query_raw(sql)

            remaining_rows -= chunksize
            iteration += 1


    def update_single_column(self, dataframe: pd.DataFrame, table: str, chunksize: int = 1000):
        n_data = len(dataframe.index)
        remaining_rows = n_data
        fields = ', '.join(dataframe.columns)


        iteration = 0
        while remaining_rows >= 0:
            start_idx = iteration*chunksize
            if remaining_rows > chunksize:
                end_idx = start_idx + chunksize
            else:
                end_idx = start_idx + remaining_rows

            # Obtener valores del chunk
            updating_df = dataframe[start_idx:end_idx]

            values = []
            for _, row in updating_df.iterrows():
                values.append(f'({", ".join(list(row))})')

            # Construir y ejecutar SQL Query
            #sql = f"UPDATE {table} SET ({fields}) VALUES {','.join(values)} ON DUPLICATE KEY UPDATE {on_duplicate_keys}"
            sql = ''
            self.query_raw(sql)

            remaining_rows -= chunksize
            iteration += 1


    def format_dataframe_to_DB_upload(  self, dataframe: pd.DataFrame, float_headers: list=[], int_headers:list=[], str_headers: list = [],
                                        index_name: str='fecha', datetime_index: bool=False, time_format: str='%Y-%m-%d %H:%M:%S'):
        output_df = dataframe.copy()

        if datetime_index:
            output_df[index_name] = output_df.index
            # Transformar datos a strings para subir a base de datos
            output_df[index_name] = output_df[index_name].apply(
                lambda timestamp: "'" + datetime.strftime(timestamp, time_format) + "'")

        for header in str_headers:
            output_df[header] = output_df[header].apply(
                lambda valor: "'" + valor + "'")   

        for header in float_headers:
            output_df[header] = output_df[header].apply(
                lambda valor: "{:.8f}".format(valor))
        for header in int_headers:
            output_df[header] = output_df[header].apply(
                lambda valor: "{:.0f}".format(valor))

        output_df = output_df.reset_index(drop=True)
        return output_df


    """
    def getSolcastData(self, id_planta: int, start: str, end: str, radiation_table: str):
        # Query de datos de solcast
        solcastProyQuery = SOLCAST_DATA_QUERY_TEMPLATE.format(id_planta=id_planta,
                                                              table_name=radiation_table,
                                                              start_datetime=start,
                                                              end_datetime=end)
        solcastData = self.query_to_df(solcastProyQuery)
        solcastData.index = pd.DatetimeIndex(solcastData['period_end'])
        del solcastData['period_end']
        return solcastData
    """


#Necesito crear una función que me permita crear una nueva tabla vacía en la base de datos

    def create_new_table(self, table_name: str, columns: list, primary_key: str):
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE {table_name} ({columns_str}, PRIMARY KEY ({primary_key}))"
        self.query_raw(query)
        


