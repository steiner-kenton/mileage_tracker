# Migration Guide: Google Sheets → Supabase

## 📋 Pre-Migration Checklist

### 1. Set Up Supabase Tables
- [ ] Go to your Supabase Dashboard SQL Editor
- [ ] Run the SQL schema provided earlier to create tables:
  - `mileage_dictionary`
  - `mileage_log`
  - `receipts`
- [ ] Verify tables are created in Table Editor

### 2. Get Your User ID
- [ ] Create an account in your app (or directly in Supabase)
- [ ] Go to Supabase Dashboard → Authentication → Users
- [ ] Copy your User ID (UUID format, looks like: `a1b2c3d4-e5f6-...`)
- [ ] Keep this handy for the migration script

### 3. Backup Your Data (Optional but Recommended)
- [ ] Download your Google Sheets as CSV files
- [ ] Store them in a safe location

## 🚀 Running the Migration

### Step 1: Install Dependencies
```bash
cd /Users/kentonsteiner/Documents/Repositories/mileage_tracker
source venv/bin/activate
pip install toml
```

### Step 2: Run Migration Script
```bash
python migrate_to_supabase.py
```

### Step 3: Follow Prompts
The script will ask for:
1. Confirmation to proceed
2. Your Supabase User ID (3 times - once for each table)

### Step 4: Verify Migration
Go to Supabase Dashboard → Table Editor and check:
- [ ] `mileage_dictionary` has your locations
- [ ] `mileage_log` has your trips
- [ ] `receipts` has your receipt data

## 📊 What Gets Migrated

### Mileage Dictionary
- Location names
- Location addresses
- Linked to your user ID

### Mileage Log
- Trip dates
- Start/end locations
- Start/end addresses
- Distance calculations
- Linked to your user ID

### Receipts
- Receipt dates
- Store names
- Total amounts
- Upload timestamps
- Linked to your user ID

## ⚠️ Important Notes

1. **User ID Requirement**: All data will be linked to YOUR user ID
2. **Duplicate Protection**: Locations won't be duplicated if they already exist
3. **Google Sheets Preserved**: Your original data stays in Google Sheets
4. **Date Format**: Dates are automatically converted to proper format
5. **Error Handling**: Script continues even if individual rows fail

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'toml'"
```bash
pip install toml
```

### "Table 'mileage_dictionary' does not exist"
Run the SQL schema in Supabase first

### "Invalid user ID"
Make sure you copied the full UUID from Supabase Auth Users

### Column Name Mismatches
The script handles various column name formats:
- `location_name` or `Location`
- `start_location` or `Start Location`
- etc.

## 🎯 After Migration

### Test Your Data
1. Log into your app
2. Navigate to each page:
   - Mileage Dictionary
   - Mileage Log  
   - Receipt Tracker
3. Verify your data appears correctly

### Next Steps
Once migration is successful:
1. Update app to use Supabase queries (next task)
2. Test all CRUD operations
3. Keep Google Sheets as backup for 30 days
4. Eventually remove Google Sheets dependencies

## 📞 Need Help?

If you encounter issues:
1. Check the console output for specific error messages
2. Verify your Supabase credentials in `.streamlit/secrets.toml`
3. Ensure RLS policies are set up correctly
4. Check that your user is authenticated in Supabase
