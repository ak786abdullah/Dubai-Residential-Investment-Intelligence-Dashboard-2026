# -------------------------------------------------------------------------------------------------
# -----------------phase 1: data extraction and loading-----------------
# -------------------------------------------------------------------------------------------------







# Import necessary libraries
import pandas as pd
import numpy as np
import os
import time
import requests
from sqlalchemy import create_engine ,inspect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# Step 1: Credentials and Endpoints
# ---------------------------------------------------------
CLIENT_ID = os.getenv("DLD_CLIENT_ID") # Provided by the integration team and stored securely in .env file
CLIENT_SECRET = os.getenv("DLD_CLIENT_SECRET")  # Provided by the integration team and stored securely in .env file
APP_IDENTIFIER = os.getenv("DLD_APP_IDENTIFIER") # Provided by the integration team and stored securely in .env file

TOKEN_URL = "https://stg-apis.data.dubai/secure/ssis/dubaiai/gatewaytoken/1.0.0/getAccessToken"
DATA_URL = "https://stg-apis.data.dubai/open/dld/dld_transactions-open-api"
MASTER_FILE = "dld_transactions_2024_onwards.csv" 

# ---------------------------------------------------------
# Step 2: Request the Bearer Token according to the API's specifications
# ---------------------------------------------------------
def get_token():
    headers = {
        "Content-Type": "application/json",
        "x-DDA-SecurityApplicationIdentifier": APP_IDENTIFIER
    }
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            return response.json().get("access_token")
        except ValueError:
            return None
    return None

# ---------------------------------------------------------
# Step 2: Extraction with Auto-Refresh Logic - Fetch only new records since the last sync 
# ---------------------------------------------------------
def sync_new_data_only(initial_token):
    # Setup our active token and track exactly when it was minted
    active_token = initial_token
    token_mint_time = time.time()

    # We will trigger a refresh after 50 minutes (50 * 60 seconds) to be safe
    SAFE_LIFESPAN_SECONDS = 3000

    headers = {
        "Authorization": f"Bearer {active_token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Connection": "keep-alive"
    }
    
    DATE_COLUMN = "instance_date"
    
    # 1. Establish the Watermark (The maximum date we already possess)
    if os.path.exists(MASTER_FILE):
        print(f"Reading existing database: {MASTER_FILE}...")
        existing_df = pd.read_csv(MASTER_FILE, usecols=[DATE_COLUMN])
        existing_df[DATE_COLUMN] = pd.to_datetime(existing_df[DATE_COLUMN])
        
        last_known_date = existing_df[DATE_COLUMN].max()
        print(f"Database is currently synced up to: {last_known_date}")
    else:
        # If no file exists, we default to the historical cutoff
        print(f"No existing database found. Defaulting to historical cutoff: 2024-01-01")
        last_known_date = pd.Timestamp('2024-01-01')

    page = 1
    keep_fetching = True
    new_records_added = 0
    
    print("Pinging API for new records...")
    
    while keep_fetching:
        params = {
            "page": page,
            "pageSize": 1000, 
            "order_by": DATE_COLUMN,
            "order_dir": "desc" # Pull newest records first
        }
        
        response = requests.get(DATA_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            records = response.json().get("results", [])
            if not records:
                break
                
            page_df = pd.DataFrame(records)
            page_df[DATE_COLUMN] = pd.to_datetime(page_df[DATE_COLUMN])
            
            # Find the oldest date on this specific API page
            oldest_date_in_page = page_df[DATE_COLUMN].min()
            
            # 2. Isolate ONLY the strictly new records by applying a boolean mask
            new_data_mask = page_df[DATE_COLUMN] > last_known_date
            strictly_new_df = page_df[new_data_mask]
            
            # 3. Append only the new records directly to the CSV
            if not strictly_new_df.empty:
                if not os.path.exists(MASTER_FILE):
                    strictly_new_df.to_csv(MASTER_FILE, index=False)
                else:
                    strictly_new_df.to_csv(MASTER_FILE, mode='a', header=False, index=False)
                
                new_records_added += len(strictly_new_df)
                print(f"Page {page}: Appended {len(strictly_new_df)} new records.")
            
            # 4. The Logic Break: If the oldest date on this page overlaps with our history, STOP.
            if oldest_date_in_page <= last_known_date:
                print("Overlap detected with existing historical data. Sync complete.")
                keep_fetching = False
            else:
                page += 1
                time.sleep(1.5) # Respect the rate limit
                
        else:
            print(f"Failed on page {page}. Status Code: {response.status_code}")
            break

    print(f"\n--- SYNC SUMMARY ---")
    print(f"Total new records added: {new_records_added}")

# --- Main Execution ---
if __name__ == "__main__":
    access_token = get_token()

    if access_token:
        print("Token secured! Initiating Delta Sync...")
        sync_new_data_only(access_token)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# STEP 3: After the new data is fetched and stored in the CSV file, we will read it into a pandas dataframe for the next phase of the pipeline which is data cleansing and transformation.
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# read the raw data files into a pandas dataframe and the lookup tables into separate dataframes
data=pd.read_csv("dld_transactions_2024_onwards.csv")
data1=pd.read_csv("lkp_areas.csv") 
data2=pd.read_csv("lkp_property_sub_types.csv")
data3=pd.read_csv("lkp_property_types.csv")
data4=pd.read_csv("lkp_statuses.csv")
data5=pd.read_csv("lkp_procedures.csv")

print(f"\n===phase 1 complete: data extracted and loaded into pandas dataframe===")




# ------------------------------------------------------------------------------------------------- 
# -------------------------phase 2: data cleansing and transformation------------------------------
# -------------------------------------------------------------------------------------------------







# -----------------------------------------------------------------------------------------------------------------------------
# step 1: DROP ARABIC COLUMNS , OTHER UNNECESSARY COLUMNS , RENAMING COLUMNS and FILTER FOR RESIDENTIAL AND SALES PROPERTIES ONLY
# ------------------------------------------------------------------------------------------------------------------------------

# I dropped the Arabic columns , the columns related to the number of parties involved and load_timestamp column because they are not relevant to our analysis.
# I also dropped the rent_value and meter_rent_price columns because they are empty. 
# I dropped area_name_en,property_sub_type_en,reg_type_en,procedure_name_en ,property_type_en because we have lookup tables for them.
data.drop(columns=['trans_group_ar','procedure_name_ar','procedure_name_en','property_sub_type_ar','property_sub_type_en','property_usage_ar','reg_type_ar','reg_type_en','area_name_ar','building_name_ar','project_name_ar','master_project_ar','nearest_landmark_ar','nearest_metro_ar','nearest_mall_ar','rooms_ar','property_type_ar','property_type_en','no_of_parties_role_1','no_of_parties_role_2','no_of_parties_role_3','load_timestamp','rent_value','meter_rent_price','area_name_en'], inplace=True) 

# FILTER FOR RESIDENTIAL AND SALES PROPERTIES ONLY
data = data[(data['property_usage_en'] == 'Residential') & (data['rooms_en'].isin(['Shop', 'Office']) == False) & (data['trans_group_en'] == 'Sales')] # FILTER FOR RESIDENTIAL PROPERTIES and sales , EXCLUDE SHOPS AND OFFICES

# we filtered for sales property now we can drop the trans_group_en, trans_group_id, property_usage_en columns because they will be the same for all rows
data.drop(columns=['trans_group_en','trans_group_id','property_usage_en'], inplace=True)

# RENAME COLUMNS
data.rename(columns={'property_type_en':'property_type','reg_type_id':'status_id','building_name_en':'building_name','project_name_en':'project_name','master_project_en':'master_project','nearest_landmark_en':'nearest_landmark','nearest_metro_en':'nearest_metro','nearest_mall_en':'nearest_mall','instance_date':'transaction_date','actual_worth':'price','rooms_en':'rooms'}, inplace=True) 

# ------------------------------------------------------------------------------------------------
# STEP 2: DROP DUPLICATES  CHANGE DATA TYPES AND HANDLE MISSING VALUES
# ------------------------------------------------------------------------------------------------

# drop duplicates
data = data.drop_duplicates(subset=['transaction_id']) # transaction_id is a unique identifier for each transaction, so we drop duplicates based on it to ensure data integrity.

# CHANGE OTHER COLUMNS DATA TYPES
# Convert id columns to smallest nullable integer dtypes and boolean flags in one pass
data = data.astype({
    'procedure_id': 'UInt16',
    'area_id': 'UInt16',
    'property_type_id': 'UInt8',
    'property_sub_type_id': 'UInt8',
    'project_number': 'UInt16',
    'has_parking': 'boolean',
    'status_id': 'boolean'
})


# fill NaN in property_sub_type_id with 6(Residential Land) where property_type_id == 1 (Land)  Becouse we have only residential data so, we impute "residential land" as  property_sub_type of "land"
mask = (data['property_type_id'] == 1) & data['property_sub_type_id'].isna()
data.loc[mask, 'property_sub_type_id'] = 6

# fill NaN in property_sub_type_id with 4 where property_type_id == 4 (Villa) Becouse "Villa" has same property_type and property_sub_type
mask = (data['property_type_id'] == 4) & data['property_sub_type_id'].isna()
data.loc[mask, 'property_sub_type_id'] = 4 

# fill NAN in rooms with "land" where property_type_id is 1 (Land) becouse land has no rooms
mask = data['property_type_id'] == 1 & data['rooms'].isna()
data.loc[mask, 'rooms'] = 'land'

# fill NaN in property_sub_type_id with 5 (Residential Building) where property_type_id == 2 (Building) Becouse we have only residential data so, we impute "residential building" as  property_sub_type of "building"
mask = (data['property_type_id'] == 2) & data['property_sub_type_id'].isna()
data.loc[mask, 'property_sub_type_id'] = 5 

# fill NaN in project_number with 0 because it has no project (it is an independent property) and project_number is a numerical column so we impute it with 0 instead of "Independent Property"
data['project_number']=data['project_number'].fillna(0) 

# fill NaN in project_name with "Independent Property" because it is not part of any project
data['project_name']=data['project_name'].fillna('Independent Property') 

# fill NaN in master_project with "Independent Property" because it is not part of any master project
data['master_project']=data['master_project'].fillna('Independent Property')

# we impute "Villa" as building_name where property_type_id == 4 (Villa) becouse villa is not a building
mask = (data['property_type_id'] == 4) & data['building_name'].isna()
data.loc[mask, 'building_name'] = 'Villa'

# we impute "empty land" as building_name where property_type_id == 1 (Land) becouse land has no building
mask = (data['property_type_id'] == 1) & data['building_name'].isna()
data.loc[mask, 'building_name'] = 'empty land' 

# we impute "Independent Building" as building_name where property_type_id == 2 (Building) becouse it's a type of building
mask = (data['property_type_id'] == 2) & data['building_name'].isna()
data.loc[mask, 'building_name'] = 'Independent Building' 

# we impute "whole building" as rooms where property_type_id == 2 (Building)
mask = (data['property_type_id'] == 2) & data['rooms'].isna()
data.loc[mask, 'rooms'] = 'whole building' 


# we will impute the missing values in rooms column for villas and units using the median area of each room category for villas and units respectively.
# We will use a mathematical function to find the nearest room category based on the area of the property.

# 1. Isolate the data where we actually know the villa sizes and room counts
known_villas = data[(data['property_type_id'] == 4) & (data['rooms'].notna())]

# 2. Calculate the median area for each room category within Villas
villa_room_medians = known_villas.groupby('rooms')['procedure_area'].median()

# 3. Create a mathematical function to find the nearest room category
def get_closest_room(area_value, median_series):
    # Calculate the absolute mathematical distance between the specific area and all medians
    differences = abs(median_series - area_value)
    # Return the index (the room category string) with the smallest distance
    return differences.idxmin()

# 4. Create a mask for the rows we need to fix
missing_villas_mask = (data['property_type_id'] == 4) & (data['rooms'].isna())

# 5. Apply the function only to the missing rows
data.loc[missing_villas_mask, 'rooms'] = data.loc[missing_villas_mask, 'procedure_area'].apply(
    lambda x: get_closest_room(x, villa_room_medians)
)

# repeat this exact same logic for missing 'Unit's rooms' rows as well 
known_units = data[(data['property_type_id'] == 3) & (data['rooms'].notna())]
unit_room_medians = known_units.groupby('rooms')['procedure_area'].median()

missing_units_mask = (data['property_type_id'] == 3) & (data['rooms'].isna())
data.loc[missing_units_mask, 'rooms'] = data.loc[missing_units_mask, 'procedure_area'].apply(
    lambda x: get_closest_room(x, unit_room_medians)
) 

# -------------------------------------------------------------------------------------------------
# step 3: STANDARIZE COLUMNS,FEATURE ENGINEERING AND CREATE NEW COLUMNS
# --------------------------------------------------------------------------------------------------

# remove "B/R" if it exists, then strip whitespace 
# It use regex=False by default to ensure it treats "B/R" as a literal string and not a regex pattern.
data['rooms']=data['rooms'].str.replace("B/R",'').str.strip() 

# single room is 1
data['rooms']=data['rooms'].replace('Single Room','1')

# strip whitespace and capitalize first letter of each word in rooms column
data['rooms']=data['rooms'].str.strip().str.title() # capitalize first letter of each word


# create a new column has_nearest_metro that is True if nearest_metro is not null and False if it is null
data['has_nearest_metro']=data['nearest_metro'].apply(lambda x: True if x is not np.nan else False)
# drop nearest_metro column because we have the new column has_nearest_metro that contains the same information in a more useful format
data.drop(columns=['nearest_metro'], inplace=True) 

# create a new column has_nearest_landmark that is True if nearest_landmark is not null and False if it is null
data['has_nearest_landmark']=data['nearest_landmark'].apply(lambda x: True if x is not np.nan else False)
# drop nearest_landmark column because we have the new column has_nearest_landmark that contains the same information in a more useful format
data.drop(columns=['nearest_landmark'], inplace=True)

# create a new column has_nearest_mall that is True if nearest_mall is not null and False if it is null
data['has_nearest_mall']=data['nearest_mall'].apply(lambda x: True if x is not np.nan else False)
# drop nearest_mall column because we have the new column has_nearest_mall that contains the same information in a more useful format
data.drop(columns=['nearest_mall'], inplace=True)  


# procedure_area is given in square meters, we will convert it to square feet by multiplying it by 10.7639, then round to 2 decimal places
data['property_size_sqft'] = (data['procedure_area'] * 10.7639).round(2) # convert area from square meters to square feet by multiplying by 10.7639
# drop the original procedure_area column because we have the new property_size_sqft column that contains the same information in a more useful format
data.drop(columns=['procedure_area'], inplace=True) 

# create a new column for price per square foot by dividing price by area and rounding to 2 decimal places
data['price_per_sqft'] = (data['price'] / data['property_size_sqft']).round(2) 
# drop meter_price column because we have the new price_per_sqft column that contains the same information in a more useful format
data.drop(columns=['meter_sale_price'], inplace=True)

# --------------------------------------------------------------------------------------------
# STEP 4: HANDLE OUTLIERS AND MARKET ANOMALIES IN PRICE PER SQUARE FOOT BY PROPERTY TYPE
# --------------------------------------------------------------------------------------------

def run_real_estate_pipeline(
    df,
    amount_col='price',
    area_col='property_size_sqft',
    price_col='price_per_sqft',
    type_col='property_type_id',
    type_map=None,
    area_unit='sqft'
):
    """
    Executes a 3-step real estate data cleansing pipeline
    tuned for your dataframe structure.
    - amount_col: total price of the property column
    - area_col: property area column
    - price_col: price per sqft column
    - type_col: property type identifier column
    - type_map: mapping from type ids to labels if needed
    - area_unit: 'sqft' when area_col is already sqft, 'sqm' when area_col is sqm
    """
    print("=== Starting Real Estate Data Cleansing Pipeline ===\n")
    df_working = df.copy()
    initial_rows = len(df_working)

    if type_map is None:
        type_map = {1: 'Land', 2: 'Building', 3: 'Unit', 4: 'Villa'}

    market_limits = {
        'Unit': (300, 15000),
        'Villa': (400, 10000),
        'Land': (50, 5000),
        'Building': (300, 5000)
    }

    if df_working[type_col].dtype == object:
        df_working['_property_type_label'] = df_working[type_col]
    else:
        df_working['_property_type_label'] = df_working[type_col].map(type_map)

    valid_records = []
    recovered_count = 0
    dropped_count = 0

    for prop_name, (min_limit, max_limit) in market_limits.items():
        group_mask = df_working['_property_type_label'] == prop_name
        df_group = df_working[group_mask].copy()

        if df_group.empty:
            continue

        is_too_low = df_group[price_col] < min_limit
        is_too_high = df_group[price_col] > max_limit
        is_error = is_too_low | is_too_high | df_group[price_col].isna()

        df_group_valid = df_group[~is_error].copy()
        df_group_errors = df_group[is_error].copy()
        total_errors_in_group = len(df_group_errors)

        df_recovered = pd.DataFrame()

        if not df_group_errors.empty:
            can_recalculate = (amount_col in df_group_errors.columns) and (area_col in df_group_errors.columns)

            if can_recalculate:
                valid_area_mask = (df_group_errors[area_col] > 0) & df_group_errors[area_col].notna()
                df_to_recalc = df_group_errors[valid_area_mask].copy()

                if area_unit == 'sqm':
                    df_to_recalc[price_col] = df_to_recalc[amount_col] / (df_to_recalc[area_col] * 10.764)
                else:
                    df_to_recalc[price_col] = df_to_recalc[amount_col] / df_to_recalc[area_col]

                now_valid_mask = (df_to_recalc[price_col] >= min_limit) & (df_to_recalc[price_col] <= max_limit)
                df_recovered = df_to_recalc[now_valid_mask]

                if not df_recovered.empty:
                    df_group_valid = pd.concat([df_group_valid, df_recovered])

        recovered_count += len(df_recovered)
        dropped_count += total_errors_in_group - len(df_recovered)
        valid_records.append(df_group_valid)

    if not valid_records:
        print("Pipeline Halt: No valid property types found matching target criteria.")
        return pd.DataFrame()

    df_validated = pd.concat(valid_records).reset_index(drop=True)

    def cap_group_outliers(group_series):
        Q1 = group_series.quantile(0.25)
        Q3 = group_series.quantile(0.75)
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        return group_series.clip(lower=lower_fence, upper=upper_fence)

    df_validated[f'{price_col}_capped'] = df_validated.groupby('_property_type_label')[price_col].transform(cap_group_outliers)
    capped_count = (df_validated[price_col] != df_validated[f'{price_col}_capped']).sum()

    print(f"1. Rows Analyzed:         {initial_rows}")
    print(f"2. Rows Forensically Saved: {recovered_count}")
    print(f"3. Broken Rows Excluded:   {dropped_count}")
    print(f"4. Valid Rows Remaining:   {len(df_validated)}")
    print(f"5. Luxury Outliers Capped: {capped_count}")

    df_validated.drop(columns=['_property_type_label'], inplace=True)
    return df_validated

data= run_real_estate_pipeline(data, amount_col='price', area_col='property_size_sqft', price_col='price_per_sqft', type_col='property_type_id')

print(f"\n=== phase 2 complete : data Cleaned And Transformed")


# -------------------------------------------------------------------------------------------------
# ----------------phase 3: loading the cleaned data into a MySQL database-----------------
# -------------------------------------------------------------------------------------------------



# We will use SQLAlchemy to connect to the MySQL database and load the cleaned data into it.
# We will also check if the lookup tables already exist in the database before loading them to avoid
db_password = os.getenv("MYSQL_PASSWORD")
connection_string = f"mysql+pymysql://root:{db_password}@localhost/real_estate_db"
engine = create_engine(connection_string) 

# 1. Load the main daily transaction data (Replace the database table with the newly cleansed master dataset)
print("Loading daily transaction data...")
data.to_sql('cleaned_residential_real_estate_sale_data', con=engine, if_exists='replace', index=False)

# 2. Check and load Lookup Tables conditionally
print("Checking lookup tables...")

# Create an inspector object to look at the database schema
inspector = inspect(engine)

# Map your lookup table names to their respective DataFrames
lookup_mapping = {
    'lkp_areas': data1,
    'lkp_property_sub_types': data2,
    'lkp_property_types': data3,
    'lkp_statuses': data4,
    'lkp_procedures': data5
}

# Loop through the mapping and only upload if the table is missing
for table_name, df in lookup_mapping.items():
    if not inspector.has_table(table_name):
        print(f" -> Table '{table_name}' not found. Uploading...")
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    else:
        print(f" -> Table '{table_name}' already exists. Skipping upload.")

print("\nPhase 3 Complete: Data successfully loaded into MySQL database!")