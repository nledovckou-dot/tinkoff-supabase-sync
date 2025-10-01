import os
import csv
import json
import logging
import tempfile
from typing import List

import boto3
from botocore.config import Config
import gspread
from google.oauth2.service_account import Credentials


def get_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing environment variable: {name}")
    return v


def list_csv_objects(s3, bucket: str) -> List[dict]:
    paginator = s3.get_paginator("list_objects_v2")
    csv_objects: List[dict] = []
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            key: str = obj["Key"]
            if key.lower().endswith(".csv"):
                csv_objects.append(obj)
    return csv_objects


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Yandex S3 params
    access_key = get_env("YA_ACCESS_KEY")
    secret_key = get_env("YA_SECRET_KEY")
    bucket = get_env("BUCKET_NAME")

    # Google Sheets params
    gs_creds_json = get_env("GSHEETS_SERVICE_ACCOUNT_JSON")
    spreadsheet = get_env("GSHEETS_SPREADSHEET")
    worksheet = os.environ.get("GSHEETS_WORKSHEET", "Sheet1")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url="https://storage.yandexcloud.net",
        region_name="ru-central1",
        config=Config(signature_version="s3v4"),
    )

    # find latest CSV by LastModified
    objs = list_csv_objects(s3, bucket)
    if not objs:
        logging.info("No CSV files found in bucket %s", bucket)
        return
    latest = max(objs, key=lambda o: o["LastModified"])  # type: ignore[arg-type]
    key = latest["Key"]
    logging.info("Latest CSV in bucket: %s", key)

    # download to temp
    local = os.path.join(tempfile.gettempdir(), os.path.basename(key))
    s3.download_file(bucket, key, local)
    logging.info("Downloaded to %s", local)

    # authorize Google Sheets
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    service_account_info = json.loads(gs_creds_json)
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open(spreadsheet)
    try:
        ws = sh.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet, rows=1000, cols=10)

    # read CSV and append
    with open(local, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        logging.info("CSV is empty, nothing to append")
        return

    header = rows[0]
    if not ws.get_values("1:1"):
        ws.update("1:1", [header])
        data_rows = rows[1:]
    else:
        data_rows = rows[1:] if rows[0] == ws.get_values("1:1")[0] else rows

    if data_rows:
        ws.append_rows(data_rows, value_input_option="RAW")
        logging.info("Appended %d rows to %s / %s", len(data_rows), spreadsheet, worksheet)
    else:
        logging.info("No data rows to append")


if __name__ == "__main__":
    main()


