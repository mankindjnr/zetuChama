from sqlalchemy import create_engine, text, Table, MetaData, select, inspect
from sqlalchemy.orm import sessionmaker
import os
from .config import my_secrets
from . import db
import pymysql
import sqlalchemy

secret_3 = my_secrets.get('database_3')

new_engine = create_engine(secret_3,
                        connect_args={"ssl": {
                          "ssl_ca": "/etc/ssl/cert.pem"
                        }})


def get_tables(member_id):
    inspector = inspect(new_engine)
    table_names = inspector.get_table_names()
  
    matching_tables = []

    for table_name in table_names:
        if table_name not in ['user', 'chamas', 'manager']:
            query = None
            if table_name:
                query = text(f"SELECT COUNT(*) FROM {table_name} WHERE member_id = :member_id")
                with new_engine.begin() as connection:
                    result = connection.execute(query, {"member_id": member_id}).fetchone()

                if result[0] > 0:
                    matching_tables.append(table_name)
    
    return matching_tables
  

def get_manager(user_name):
  with new_engine.connect() as conn:
    result = conn.execute(text(f"SELECT * FROM manager WHERE username = '{user_name}'"))
    rows = []

    for row in result.all():
      rows.append(row._mapping)

    if len(rows) == 0:
      return None
    else:
      return rows


def get_member(id):
  with new_engine.connect() as conn:
    result = conn.execute(text(f"SELECT * FROM user WHERE id = {id}"))
    rows = []

    for row in result.all():
      rows.append(row._mapping)

    if len(rows) == 0:
      return None
    else:
      return [dict(row) for row in rows]


def get_chamas_by_manager(user_name):
    print(user_name)
    with new_engine.connect() as conn:
      result = conn.execute(sqlalchemy.text("SELECT * FROM chamas"))

      column_names = result.keys()

      data_list = []
      
      for row in result:
        row_dict = {}

        for column_name, value in zip(column_names, row):
          row_dict[column_name] = value 

        data_list.append(row_dict)

      filtered = [row for row in data_list if row.get("manager") == user_name]

      if len(filtered) == 0:
        return None
      else:
        return filtered
    



def get_all_chamas():
  with new_engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM chamas"))
    rows = result.all()

    if len(rows) == 0:
      return None
    else:
      column_names = result.keys()
      rows_dict = [dict(zip(column_names, row)) for row in rows]
      return rows_dict

