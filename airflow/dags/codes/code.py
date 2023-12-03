import requests
import pandas as pd
import json
import os

# from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    DATE,
    inspect,
    insert,
)

credentials_db_mysql = os.environ.get("MYSQL_CONN_STRING")
# credentials_db_postgres = os.environ.get("PS_CONN_STRING")
credentials_db_postgres = "postgresql://postgres:postgres@db_postgres_dwh:5432/dwh"


def request_data_to_api():
    reqUrl = "http://103.150.197.96:5005/api/v1/rekapitulasi_v2/jabar/harian"
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    }
    payload = ""

    response = requests.request("GET", reqUrl, data=payload, headers=headersList)
    response = json.loads(response.text)

    return response


def json_to_df(json):
    if json["status_code"] == 200:
        df = pd.DataFrame(json["data"]["content"])
        return df
    else:
        raise Exception("need to retry request_data_to_api")


def input_df_into_db_staging_area(df, credentials):
    engine = create_engine(credentials)
    table_name = "mysql"
    df.to_sql(table_name, engine, schema=None, if_exists="replace", index=False)
    engine.dispose()


def read_db_staging_area(credentials):
    engine = create_engine(credentials)
    table_name = "mysql"
    df = pd.read_sql(table_name, engine)
    engine.dispose()
    return df


def generate_schema_dwh(credentials):
    engine = create_engine(credentials)
    metadata_obj = MetaData()
    dim_province = Table(
        "dim_province",
        metadata_obj,
        Column("province_id", Integer, primary_key=True),
        Column("province_name", String(100)),
    )

    dim_district = Table(
        "dim_district",
        metadata_obj,
        Column("district_id", Integer, primary_key=True),
        Column("province_id", Integer, ForeignKey("dim_province.province_id")),
        Column("district_name", String(100)),
    )

    dim_case = Table(
        "dim_case",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("status_name", String(20)),
        Column("status_detail", String(100)),
    )

    fact_province_daily = Table(
        "fact_province_daily",
        metadata_obj,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("province_id", Integer, ForeignKey("dim_province.province_id")),
        Column("case_id", Integer, ForeignKey("dim_case.id")),
        Column("date", DATE),
        Column("total", Integer),
    )

    fact_district_daily = Table(
        "fact_district_daily",
        metadata_obj,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("district_id", Integer, ForeignKey("dim_district.district_id")),
        Column("case_id", Integer, ForeignKey("dim_case.id")),
        Column("date", DATE),
        Column("total", Integer),
    )

    metadata_obj.create_all(engine, checkfirst=True)
    return (
        dim_province,
        dim_district,
        dim_case,
        fact_province_daily,
        fact_district_daily,
    )


def transform_raw_data(df):
    # transform table
    df = df.melt(
        id_vars=["tanggal", "kode_prov", "kode_kab", "nama_prov", "nama_kab"],
        var_name="status detail",
    ).sort_values("tanggal")
    df.columns = df.columns.str.lower()

    # remove big category
    # filter data from big category values
    df = df.loc[df["status detail"] != "CLOSECONTACT"]
    df = df.loc[df["status detail"] != "CONFIRMATION"]
    df = df.loc[df["status detail"] != "PROBABLE"]
    df = df.loc[df["status detail"] != "SUSPECT"]

    df["status name"] = df["status detail"].apply(lambda x: x.split("_")[0])
    df = df.rename(
        columns={
            "kode_prov": "province_id",
            "kode_kab": "district_id",
            "tanggal": "date",
            "value": "total",
            "nama_prov": "province_name",
            "nama_kab": "district_name",
            "status name": "status_name",
            "status detail": "status_detail",
        }
    )
    return df


def update_dim_province_table(df, credentials, schema):
    engine = create_engine(credentials)

    df_temp = pd.DataFrame()
    province_unique = df["province_id"].unique()
    for i, province in enumerate(province_unique):
        province_data = df[df["province_id"] == province].iloc[0]
        df_temp.loc[i, "province_name"] = province_data["province_name"]
        df_temp.loc[i, "province_id"] = province_data["province_id"]

    try:
        df_temp.to_sql(
            name=schema.name, con=credentials, index=False, if_exists="replace"
        )
    except Exception as e:
        print(e)
        pass


def update_dim_district_table(df, credentials, schema):
    engine = create_engine(credentials)

    df_temp = pd.DataFrame()
    district_unique = df["district_id"].unique()
    for i, district in enumerate(district_unique):
        district_data = df[df["district_id"] == district].iloc[0]
        df_temp.loc[i, "district_id"] = district_data["district_id"]
        df_temp.loc[i, "district_name"] = district_data["district_name"]
        df_temp.loc[i, "province_id"] = district_data["province_id"]

    try:
        df_temp.to_sql(
            name=schema.name, con=credentials, index=False, if_exists="replace"
        )
    except Exception as e:
        print(e)
        pass


def update_dim_case_table(df, credentials, schema):
    engine = create_engine(credentials)

    df_case = pd.DataFrame(
        columns=["status_detail"], data=sorted(df["status_detail"].unique())
    )
    df_case["status_name"] = df_case["status_detail"].apply(lambda x: x.split("_")[0])
    df_case["id"] = df_case.index

    try:
        df_case.to_sql(
            name=schema.name, con=credentials, index=False, if_exists="replace"
        )
    except Exception as e:
        print(e)
        pass
    finally:
        return df_case


def update_fact_district_daily_table(df, df_case, credentials, schema):
    engine = create_engine(credentials)

    df_temp = df.merge(df_case, on=["status_detail", "status_name"], how="left")
    df_temp = df_temp.rename(columns={"id": "case_id"})
    df_temp = df_temp[["district_id", "case_id", "date", "total"]]

    df_temp.to_sql(name=schema.name, con=credentials, index=False, if_exists="replace")


def update_fact_province_daily_table(df, df_case, credentials, schema):
    engine = create_engine(credentials)

    df_temp = df.merge(df_case, on=["status_detail", "status_name"], how="left")
    df_temp = df_temp.rename(columns={"id": "case_id"})
    df_temp = df_temp.groupby(
        [
            "date",
            "province_id",
            "case_id",
        ],
        as_index=False,
    ).agg({"total": "sum"})

    df_temp.to_sql(name=schema.name, con=credentials, index=False, if_exists="replace")
