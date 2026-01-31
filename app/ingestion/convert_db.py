import pandas as pd
import os
from sqlalchemy import create_engine

def convert_excel_to_db():
    data_dir = "data"
    excel_file = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")][0] # Grab the first excel file
    file_path = os.path.join(data_dir, excel_file)
    db_path = os.path.join(data_dir, "orders.db")
    
    print(f"Converting {excel_file} to {db_path}...")
    
    try:
        # Read Excel
        df = pd.read_excel(file_path)
        
        # Create SQLite Engine
        engine = create_engine(f"sqlite:///{db_path}")
        
        # Write to SQL (table name = 'orders')
        df.to_sql("orders", engine, if_exists="replace", index=False)
        
        print("Success! Database created.")
        print(f"Table 'orders' has {len(df)} rows.")
        
    except Exception as e:
        print(f"Error converting to DB: {e}")

if __name__ == "__main__":
    convert_excel_to_db()
