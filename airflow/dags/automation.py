

# only uncomment for testing purpose
from code import *


(
    dim_province,
    dim_district,
    dim_case,
    fact_province_daily,
    fact_district_daily,
) = generate_schema_dwh(credentials_db_postgres)
response = request_data_to_api()
df = json_to_df(response)
input_df_into_db_staging_area(df, credentials_db_mysql)
df = read_db_staging_area(credentials_db_mysql)
df = transform_raw_data(df)
update_dim_province_table(df, credentials_db_postgres, dim_province)
update_dim_district_table(df, credentials_db_postgres, dim_district)
df_case = update_dim_case_table(df, credentials_db_postgres, dim_case)
update_fact_district_daily_table(
    df, df_case, credentials_db_postgres, fact_district_daily
)
update_fact_province_daily_table(
    df, df_case, credentials_db_postgres, fact_province_daily
)
