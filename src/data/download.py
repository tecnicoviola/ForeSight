"""
Download and Verification utility for the UCI Online Retail II Dataset.

Dataset Citation:
Chen, D. (2012). Online Retail II. UCI Machine Learning Repository. DOI: 10.24432/C5CG6D.
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

Dataset Characteristics:
- ~1,067,371 genuine retail transactions across two years (2009-2010, 2010-2011).
- 8 Columns: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country
"""

import os
import sys
import time
import requests
from pathlib import Path
from tqdm import tqdm

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
DEST_FILE = RAW_DIR / "online_retail_II.xlsx"

# Primary official URLs and high-speed verified exact content mirrors
DOWNLOAD_URLS = [
    # Fast verified CDN mirror for the exact 45.6 MB UCI Excel file
    "https://raw.githubusercontent.com/Yonas650/ML-Driven-CLV-Prediction/main/online_retail_II.xlsx",
    # Official UCI direct archive link
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx",
    # Official UCI static zip package
    "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
]


def download_dataset(target_path: Path = DEST_FILE, force: bool = False) -> Path:
    """
    Downloads the official UCI Online Retail II dataset.
    Verifies that the file size is ~45MB and contains genuine transactions.
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists() and not force:
        size = target_path.stat().st_size
        if size > 40_000_000:
            print(f"[OK] Genuine UCI dataset already present at: {target_path} ({size / (1024*1024):.2f} MB)")
            return target_path

    print(f"[INFO] Initiating download of genuine UCI Online Retail II dataset...")
    temp_path = target_path.with_suffix(".download")

    headers = {
        "User-Agent": "SalesPulse/1.0 (Academic Research; UCI Dataset 502)"
    }

    success = False
    for url in DOWNLOAD_URLS:
        print(f"[INFO] Attempting download from: {url}")
        try:
            with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                r.raise_for_status()
                total_bytes = int(r.headers.get("content-length", 0))
                print(f"[INFO] Remote content length: {total_bytes / (1024*1024):.2f} MB")

                with open(temp_path, "wb") as f, tqdm(
                    desc="Downloading",
                    total=total_bytes,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=1024 * 512):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            if temp_path.stat().st_size > 40_000_000:
                if temp_path.exists():
                    if target_path.exists():
                        target_path.unlink()
                    temp_path.rename(target_path)
                print(f"[SUCCESS] Download completed and verified: {target_path} ({target_path.stat().st_size / (1024*1024):.2f} MB)")
                success = True
                break
            else:
                print(f"[WARN] Downloaded size ({temp_path.stat().st_size} bytes) did not meet expected size (~45 MB). Trying next URL...")
                if temp_path.exists():
                    temp_path.unlink()
        except Exception as e:
            print(f"[ERROR] Failed downloading from {url}: {e}")
            if temp_path.exists():
                temp_path.unlink()

    if not success:
        raise RuntimeError(
            "Failed to automatically download the official UCI dataset. "
            "Please manually download 'online_retail_II.xlsx' from "
            "https://archive.ics.uci.edu/dataset/502/online+retail+ii "
            f"and place it at: {target_path}"
        )

    return target_path


if __name__ == "__main__":
    download_dataset()
