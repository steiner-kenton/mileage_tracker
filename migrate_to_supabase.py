"""
Migration script to move data from Google Sheets to Supabase
Run this once to migrate your existing data
"""
from supabase import create_client
import pandas as pd
from datetime import datetime
import sys
import os

# Add the project root to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.sheets_utils import get_sheet_data

# Load secrets
print("Loading Supabase credentials...")
try:
    import toml
    secrets_path = '.streamlit/secrets.toml'
    
    if not os.path.exists(secrets_path):
        print(f"❌ Error: {secrets_path} not found!")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    secrets = toml.load(secrets_path)
    
    if 'supabase' not in secrets:
        print("❌ Error: 'supabase' section not found in secrets.toml!")
        sys.exit(1)
    
    SUPABASE_URL = secrets['supabase']['SUPABASE_URL']
    SUPABASE_KEY = secrets['supabase'].get('SUPABASE_SERVICE_ROLE_KEY', secrets['supabase']['SUPABASE_API'])
    
    print(f"✅ Loaded credentials")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Key: {SUPABASE_KEY[:20]}...{SUPABASE_KEY[-10:]}")
    
except Exception as e:
    print(f"❌ Error loading secrets: {str(e)}")
    sys.exit(1)

# Initialize Supabase client
try:
    print("\nInitializing Supabase client...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized")
except Exception as e:
    print(f"❌ Error initializing Supabase client: {str(e)}")
    sys.exit(1)

def migrate_mileage_dictionary():
    """Migrate Mileage Dictionary from Google Sheets to Supabase"""
    print("\n📍 Migrating Mileage Dictionary...")
    
    try:
        # Get data from Google Sheets
        df = get_sheet_data("Mileage_Dictionary")
        
        if df.empty:
            print("  ⚠️  No data found in Mileage Dictionary sheet")
            return
        
        print(f"  Found {len(df)} locations to migrate")
        
        # Get current user ID (you'll need to provide this)
        user_id = input("\n  Enter your Supabase user ID (from auth.users table): ").strip()
        
        if not user_id:
            print("  ❌ User ID is required")
            return
        
        migrated = 0
        skipped = 0
        errors = []
        
        # Insert each location
        for idx, row in df.iterrows():
            try:
                # Prepare data for Supabase
                location_data = {
                    "user_id": user_id,
                    "location_name": str(row.get('location_name', row.get('Location', ''))),
                    "location_address": str(row.get('location_address', row.get('Address', '')))
                }
                
                # Check if location already exists
                existing = supabase.table('mileage_dictionary').select('*').eq(
                    'user_id', user_id
                ).eq(
                    'location_name', location_data['location_name']
                ).execute()
                
                if existing.data:
                    print(f"  ⏭️  Skipping '{location_data['location_name']}' (already exists)")
                    skipped += 1
                else:
                    # Insert new location
                    supabase.table('mileage_dictionary').insert(location_data).execute()
                    print(f"  ✅ Migrated: {location_data['location_name']}")
                    migrated += 1
                    
            except Exception as e:
                error_msg = f"Error with row {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ {error_msg}")
        
        print(f"\n  Summary: {migrated} migrated, {skipped} skipped, {len(errors)} errors")
        
    except Exception as e:
        print(f"  ❌ Error migrating Mileage Dictionary: {str(e)}")

def migrate_mileage_log():
    """Migrate Mileage Log from Google Sheets to Supabase"""
    print("\n🛣️  Migrating Mileage Log...")
    
    try:
        # Get data from Google Sheets
        df = get_sheet_data("mileage_log")
        
        if df.empty:
            print("  ⚠️  No data found in Mileage Log sheet")
            return
        
        print(f"  Found {len(df)} trips to migrate")
        
        # Get current user ID
        user_id = input("\n  Enter your Supabase user ID (same as before): ").strip()
        
        if not user_id:
            print("  ❌ User ID is required")
            return
        
        migrated = 0
        errors = []
        
        # Insert each trip
        for idx, row in df.iterrows():
            try:
                # Parse date
                date_value = row.get('date', row.get('Date', ''))
                if pd.notna(date_value):
                    if isinstance(date_value, str):
                        date_obj = pd.to_datetime(date_value).date()
                    else:
                        date_obj = date_value
                else:
                    date_obj = datetime.today().date()
                
                # Parse distance
                distance_value = row.get('distance', row.get('Distance', 0))
                if pd.notna(distance_value):
                    distance = float(distance_value)
                else:
                    distance = 0.0
                
                # Prepare data for Supabase
                trip_data = {
                    "user_id": user_id,
                    "date": str(date_obj),
                    "start_location": str(row.get('start_location', row.get('Start Location', ''))),
                    "start_address": str(row.get('start_address', row.get('Start Address', ''))),
                    "end_location": str(row.get('end_location', row.get('End Location', ''))),
                    "end_address": str(row.get('end_address', row.get('End Address', ''))),
                    "distance": distance
                }
                
                # Insert trip
                supabase.table('mileage_log').insert(trip_data).execute()
                print(f"  ✅ Migrated trip: {trip_data['start_location']} → {trip_data['end_location']} ({date_obj})")
                migrated += 1
                    
            except Exception as e:
                error_msg = f"Error with row {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ {error_msg}")
        
        print(f"\n  Summary: {migrated} migrated, {len(errors)} errors")
        
    except Exception as e:
        print(f"  ❌ Error migrating Mileage Log: {str(e)}")

def migrate_receipts():
    """Migrate Receipts from Google Sheets to Supabase"""
    print("\n🧾 Migrating Receipts...")
    
    try:
        # Get data from Google Sheets
        df = get_sheet_data("Receipts", create_if_missing=True, 
                          headers=["date", "store_name", "total", "upload_timestamp"])
        
        if df.empty:
            print("  ⚠️  No data found in Receipts sheet")
            return
        
        print(f"  Found {len(df)} receipts to migrate")
        
        # Get current user ID
        user_id = input("\n  Enter your Supabase user ID (same as before): ").strip()
        
        if not user_id:
            print("  ❌ User ID is required")
            return
        
        migrated = 0
        errors = []
        
        # Insert each receipt
        for idx, row in df.iterrows():
            try:
                # Parse date
                date_value = row.get('date', row.get('Date', ''))
                if pd.notna(date_value):
                    if isinstance(date_value, str):
                        date_obj = pd.to_datetime(date_value).date()
                    else:
                        date_obj = date_value
                else:
                    date_obj = datetime.today().date()
                
                # Parse total
                total_value = row.get('total', row.get('Total', 0))
                if pd.notna(total_value):
                    # Remove $ and convert to float
                    if isinstance(total_value, str):
                        total = float(total_value.replace('$', '').replace(',', ''))
                    else:
                        total = float(total_value)
                else:
                    total = 0.0
                
                # Prepare data for Supabase
                receipt_data = {
                    "user_id": user_id,
                    "date": str(date_obj),
                    "store_name": str(row.get('store_name', row.get('Store Name', ''))),
                    "total": total,
                    "upload_timestamp": row.get('upload_timestamp', datetime.now().isoformat())
                }
                
                # Insert receipt
                supabase.table('receipts').insert(receipt_data).execute()
                print(f"  ✅ Migrated receipt: {receipt_data['store_name']} - ${total:.2f} ({date_obj})")
                migrated += 1
                    
            except Exception as e:
                error_msg = f"Error with row {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"  ❌ {error_msg}")
        
        print(f"\n  Summary: {migrated} migrated, {len(errors)} errors")
        
    except Exception as e:
        print(f"  ❌ Error migrating Receipts: {str(e)}")

def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 Google Sheets to Supabase Migration Tool")
    print("=" * 60)
    
    print("\n⚠️  IMPORTANT: Before running this migration:")
    print("1. Make sure you've created the tables in Supabase (run the SQL from earlier)")
    print("2. Create a user account in your Supabase app (sign up)")
    print("3. Get your user ID from Supabase Dashboard > Authentication > Users")
    print("4. This script will NOT delete data from Google Sheets")
    
    proceed = input("\nReady to proceed? (yes/no): ").lower().strip()
    
    if proceed != 'yes':
        print("\n❌ Migration cancelled")
        return
    
    # Run migrations
    migrate_mileage_dictionary()
    migrate_mileage_log()
    migrate_receipts()
    
    print("\n" + "=" * 60)
    print("✅ Migration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify your data in Supabase Dashboard > Table Editor")
    print("2. Update your app code to use Supabase instead of Google Sheets")
    print("3. Keep Google Sheets as backup until you're confident in Supabase")

if __name__ == "__main__":
    main()
