"""
Google Sheets utilities for data management
"""
import pandas as pd
import streamlit as st
from config.config import client, SPREADSHEET_ID

def append_to_gsheet(new_data, sheet_name):
    """Function to append new data to Google Sheets (Mileage_Dictionary, Mileage_Log, Receipts)"""
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)

    for _, row in new_data.iterrows():
        worksheet.append_row(row.tolist())

    st.success(f"Changes successfully submitted to {sheet_name}!")

def get_sheet_data(sheet_name, create_if_missing=False, headers=None):
    """Get data from a Google Sheet, optionally creating it if it doesn't exist"""
    try:
        worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        if create_if_missing and headers:
            # If sheet doesn't exist, create it
            try:
                spreadsheet = client.open_by_key(SPREADSHEET_ID)
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                # Add headers
                worksheet.append_row(headers)
                return pd.DataFrame(columns=headers)
            except Exception as e:
                st.error(f"Error creating {sheet_name} sheet: {str(e)}")
                return pd.DataFrame()
        else:
            st.error(f"Error accessing {sheet_name} sheet")
            return pd.DataFrame()
