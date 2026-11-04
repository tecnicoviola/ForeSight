"""
Inspection script for UCI Online Retail II dataset.
Verifies sheets, columns, record counts, nulls, and anomalies.
"""

import time
import openpyxl
import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "online_retail_II.xlsx"


def inspect():
    print(f"Loading workbook sheets from {DATA_FILE}...")
    t0 = time.time()
    wb = openpyxl.load_workbook(DATA_FILE, read_only=True)
    sheet_names = wb.sheetnames
    print(f"Sheets found ({len(sheet_names)}): {sheet_names}")
    wb.close()

    total_records = 0
    sheet_stats = []

    for sheet in sheet_names:
        print(f"\n--- Inspecting Sheet: {sheet} ---")
        df_sheet = pd.read_excel(DATA_FILE, sheet_name=sheet)
        n_rows, n_cols = df_sheet.shape
        total_records += n_rows
        print(f"Shape: {n_rows:,} rows, {n_cols} columns")
        print("Columns & Types:")
        for col, dtype in zip(df_sheet.columns, df_sheet.dtypes):
            null_count = df_sheet[col].isna().sum()
            print(f"  - {col}: {dtype} | Missing: {null_count:,} ({null_count/n_rows*100:.2f}%)")

        cancellations = df_sheet["Invoice"].astype(str).str.startswith("C").sum()
        neg_qty = (df_sheet["Quantity"] <= 0).sum()
        zero_or_neg_price = (df_sheet["Price"] <= 0).sum()
        dup_count = df_sheet.duplicated().sum()

        print(f"Cancellation invoices (Invoice starts with 'C'): {cancellations:,}")
        print(f"Non-positive quantity (<= 0): {neg_qty:,}")
        print(f"Non-positive price (<= 0): {zero_or_neg_price:,}")
        print(f"Duplicate rows: {dup_count:,}")
        print(f"InvoiceDate range: {df_sheet['InvoiceDate'].min()} to {df_sheet['InvoiceDate'].max()}")
        print(f"Unique Countries: {df_sheet['Country'].nunique():,}")
        print(f"Unique Customers: {df_sheet['Customer ID'].nunique():,}")
        print(f"Unique StockCodes: {df_sheet['StockCode'].nunique():,}")

        sheet_stats.append({
            "sheet": sheet,
            "rows": n_rows,
            "cancellations": cancellations,
            "neg_qty": neg_qty,
            "non_pos_price": zero_or_neg_price,
            "duplicates": dup_count,
            "min_date": str(df_sheet['InvoiceDate'].min()),
            "max_date": str(df_sheet['InvoiceDate'].max())
        })

    print(f"\n==========================================")
    print(f"TOTAL RECORDS ACROSS ALL SHEETS: {total_records:,}")
    print(f"Total inspection time: {time.time() - t0:.2f}s")
    print(f"==========================================")


if __name__ == "__main__":
    inspect()

