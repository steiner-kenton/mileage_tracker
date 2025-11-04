"""
Fix receipt totals that got zeroed out during migration
"""
from supabase import create_client
import pandas as pd
import toml
from src.utils.sheets_utils import get_sheet_data

# Load Supabase credentials
secrets = toml.load('.streamlit/secrets.toml')
SUPABASE_URL = secrets['supabase']['SUPABASE_URL']
SUPABASE_KEY = secrets['supabase'].get('SUPABASE_SERVICE_ROLE_KEY', secrets['supabase']['SUPABASE_API'])

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get user ID
user_id = input("Enter your Supabase user ID: ").strip()

print("\n📊 Checking receipt totals...")

# Get receipts from Supabase
supabase_receipts = supabase.table('receipts').select('*').eq('user_id', user_id).execute()

if not supabase_receipts.data:
    print("❌ No receipts found in Supabase")
else:
    print(f"\n✅ Found {len(supabase_receipts.data)} receipts in Supabase")
    
    # Check for zero totals
    zero_totals = [r for r in supabase_receipts.data if r['total'] == 0.0 or r['total'] == 0]
    
    if zero_totals:
        print(f"⚠️  Found {len(zero_totals)} receipts with $0.00 total")
        
        # Try to get original data from Google Sheets
        print("\n📄 Fetching original data from Google Sheets...")
        try:
            sheets_data = get_sheet_data("Receipts", create_if_missing=True, 
                                        headers=["date", "store_name", "total", "upload_timestamp"])
            
            print(f"✅ Found {len(sheets_data)} receipts in Google Sheets")
            print("\nGoogle Sheets data sample:")
            print(sheets_data.head())
            print(f"\nColumn names: {sheets_data.columns.tolist()}")
            print(f"\nData types:\n{sheets_data.dtypes}")
            
            # Show a few total values
            if 'total' in sheets_data.columns:
                print(f"\nSample totals: {sheets_data['total'].head().tolist()}")
            
            # Ask if user wants to re-migrate
            fix = input("\nWould you like to re-migrate the receipts with correct totals? (yes/no): ").lower().strip()
            
            if fix == 'yes':
                print("\n🔧 Fixing receipt totals...")
                fixed = 0
                
                for idx, row in sheets_data.iterrows():
                    try:
                        # Get store name and date to match
                        store_name = str(row.get('store_name', row.get('Store Name', '')))
                        date_value = str(pd.to_datetime(row.get('date', row.get('Date', ''))).date())
                        
                        # Parse total properly
                        total_value = row.get('total', row.get('Total', 0))
                        if pd.notna(total_value) and total_value != '':
                            if isinstance(total_value, str):
                                # Remove $ and commas
                                total = float(total_value.replace('$', '').replace(',', '').strip())
                            else:
                                total = float(total_value)
                        else:
                            total = 0.0
                        
                        print(f"\n  Store: {store_name}, Date: {date_value}, Total: ${total:.2f}")
                        
                        # Find matching receipt in Supabase
                        matching = [r for r in supabase_receipts.data 
                                  if r['store_name'] == store_name and r['date'] == date_value]
                        
                        if matching and total > 0:
                            receipt_id = matching[0]['id']
                            
                            # Update the total
                            supabase.table('receipts').update({'total': total}).eq('id', receipt_id).execute()
                            print(f"  ✅ Updated receipt {receipt_id}: ${total:.2f}")
                            fixed += 1
                        elif total == 0:
                            print(f"  ⏭️  Skipping - total is 0 in Google Sheets too")
                        else:
                            print(f"  ⚠️  No matching receipt found in Supabase")
                            
                    except Exception as e:
                        print(f"  ❌ Error: {str(e)}")
                
                print(f"\n✅ Fixed {fixed} receipts!")
            
        except Exception as e:
            print(f"❌ Error accessing Google Sheets: {str(e)}")
    else:
        print("✅ All receipts have non-zero totals")
        for r in supabase_receipts.data[:5]:
            print(f"  {r['store_name']}: ${r['total']:.2f}")
