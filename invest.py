import os
import csv
import datetime
import logging
import tempfile
import json
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
from typing import List, Dict

import boto3
from botocore.config import Config
from tinkoff.invest import Client
import gspread
from google.oauth2.service_account import Credentials


def get_env_variable(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def build_date_range(days_back: int) -> tuple[datetime.datetime, datetime.datetime]:
    now = datetime.datetime.now()
    start_dt = now - datetime.timedelta(days=days_back)
    return start_dt, now


def _money_to_decimal_str(money_obj: object) -> str:
    try:
        units = getattr(money_obj, "units", 0)
        nano = getattr(money_obj, "nano", 0)
        sign = 1
        if units < 0 or nano < 0:
            sign = -1
        total = (Decimal(abs(units)) + (Decimal(abs(nano)) / Decimal(1_000_000_000))) * sign
        # Format to two decimals as plain string to avoid scientific notation in Sheets
        return str(total.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP))
    except Exception:
        return str(money_obj)


def _rus_operation_type(op_type: object) -> str:
    name = getattr(op_type, "name", str(op_type))
    mapping = {
        "OPERATION_TYPE_BUY": "Покупка ценных бумаг",
        "OPERATION_TYPE_SELL": "Продажа ценных бумаг",
        "OPERATION_TYPE_BROKER_FEE": "Комиссия брокера",
        "OPERATION_TYPE_SERVICE_FEE": "Удержание комиссии",
        "OPERATION_TYPE_TAX": "Удержание налога",
        "OPERATION_TYPE_TAX_DIVIDEND": "Налог на дивиденды",
        "OPERATION_TYPE_DIVIDEND": "Выплата дивидендов",
        "OPERATION_TYPE_COUPON": "Выплата купона",
        "OPERATION_TYPE_INPUT": "Ввод денежных средств",
        "OPERATION_TYPE_OUTPUT": "Вывод денежных средств",
        "OPERATION_TYPE_OPTION_EXPIRATION": "Экспирация опциона",
        "OPERATION_TYPE_WRITE_OFF_MONEY": "Списание средств",
        "OPERATION_TYPE_PAY_IN": "Пополнение",
        "OPERATION_TYPE_PAY_OUT": "Вывод",
    }
    return mapping.get(name, name)


def _rus_operation_state(state: object) -> str:
    name = getattr(state, "name", str(state))
    mapping = {
        "OPERATION_STATE_EXECUTED": "Проведена",
        "OPERATION_STATE_DECLINED": "Отклонена",
        "OPERATION_STATE_PROGRESS": "В обработке",
    }
    return mapping.get(name, name)


def fetch_operations(invest_token: str, days_back: int) -> List[Dict[str, str]]:
    start_date, end_date = build_date_range(days_back)
    logging.info("Fetching operations from %s to %s", start_date, end_date)

    with Client(invest_token) as client:
        accounts = client.users.get_accounts().accounts
        if not accounts:
            raise RuntimeError("No Tinkoff Invest accounts available for the token")

        account_id = accounts[0].id
        operations = client.operations.get_operations(
            account_id=account_id,
            from_=start_date,
            to=end_date,
        )

        rows: List[Dict[str, str]] = []
        msk = ZoneInfo("Europe/Moscow")
        for op in operations.operations:
            # Try common identifiers; fall back to a hash of fields if missing
            op_id = (
                getattr(op, "id", None)
                or getattr(op, "operation_id", None)
                or getattr(op, "trade_id", None)
            )
            if not op_id:
                fingerprint = (
                    f"{getattr(op, 'date', '')}|{getattr(op, 'type', '')}|"
                    f"{getattr(op, 'currency', '')}|{getattr(op, 'payment', '')}|"
                    f"{getattr(op, 'status', '')}|{getattr(op, 'description', '')}"
                )
                op_id = str(abs(hash(fingerprint)))

            raw_dt = getattr(op, "date", None)
            if isinstance(raw_dt, datetime.datetime):
                try:
                    local_dt = raw_dt.astimezone(msk)
                except Exception:
                    local_dt = raw_dt
                date_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(raw_dt)

            amount_str = _money_to_decimal_str(getattr(op, "payment", None))
            action_ru = _rus_operation_type(getattr(op, "type", ""))
            status_ru = _rus_operation_state(getattr(op, "status", ""))

            rows.append(
                {
                    "operation_id": str(op_id),
                    "date_msk": date_str,
                    "action": action_ru,
                    "amount": amount_str,
                    "currency": str(getattr(op, "currency", "")),
                    "status": status_ru,
                    "description": str(getattr(op, "description", "")),
                }
            )

        logging.info("Fetched %d operations", len(rows))
        return rows


def write_csv(filepath: str, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "operation_id",
        "date_msk",
        "action",
        "amount",
        "currency",
        "status",
        "description",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def upload_to_yandex_s3(filepath: str, bucket_name: str, access_key: str, secret_key: str) -> None:
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url="https://storage.yandexcloud.net",
        region_name="ru-central1",
        config=Config(signature_version="s3v4"),
    )
    s3.upload_file(filepath, bucket_name, os.path.basename(filepath))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Required env vars
    invest_token = get_env_variable("INVEST_TOKEN")
    ya_access_key = get_env_variable("YA_ACCESS_KEY")
    ya_secret_key = get_env_variable("YA_SECRET_KEY")
    bucket_name = get_env_variable("BUCKET_NAME")

    # Optional params
    days_back_str = os.environ.get("DAYS_BACK", "1000")
    try:
        days_back = max(1, int(days_back_str))
    except ValueError:
        raise RuntimeError("DAYS_BACK must be an integer")

    now = datetime.datetime.now()
    date_suffix = now.strftime("%Y-%m-%d_%H-%M")
    filename = f"operations_{date_suffix}.csv"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    try:
        rows = fetch_operations(invest_token, days_back)
        write_csv(filepath, rows)
        upload_to_yandex_s3(filepath, bucket_name, ya_access_key, ya_secret_key)
        logging.info("Upload finished successfully: %s -> bucket %s", filepath, bucket_name)

        # Also publish stable aliases for Apps Script consumption
        try:
            session = boto3.session.Session()
            s3_client = session.client(
                service_name="s3",
                aws_access_key_id=ya_access_key,
                aws_secret_access_key=ya_secret_key,
                endpoint_url="https://storage.yandexcloud.net",
                region_name="ru-central1",
                config=Config(signature_version="s3v4"),
            )
            # 1) Upload same CSV under a stable key
            stable_key = "operations_latest.csv"
            s3_client.upload_file(filepath, bucket_name, stable_key)

            # 2) Upload latest.json with the exact object key
            latest_info_path = os.path.join(tempfile.gettempdir(), "latest.json")
            with open(latest_info_path, "w", encoding="utf-8") as jf:
                jf.write(json.dumps({"key": os.path.basename(filepath)}, ensure_ascii=False))
            s3_client.upload_file(latest_info_path, bucket_name, "latest.json")
            logging.info("Published aliases: %s and latest.json", stable_key)
        except Exception as alias_exc:  # noqa: BLE001
            logging.exception("Failed to publish aliases: %s", alias_exc)

        # Optional: Google Sheets export when env is provided
        gs_creds_json = os.environ.get("GSHEETS_SERVICE_ACCOUNT_JSON", "")
        gs_spreadsheet = os.environ.get("GSHEETS_SPREADSHEET", "")
        gs_worksheet = os.environ.get("GSHEETS_WORKSHEET", "") or "Sheet1"
        if gs_creds_json and gs_spreadsheet:
            try:
                logging.info("Appending %d rows to Google Sheets: %s / %s", len(rows), gs_spreadsheet, gs_worksheet)
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
                service_account_info = json.loads(gs_creds_json)
                creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
                gc = gspread.authorize(creds)
                sh = gc.open(gs_spreadsheet)
                try:
                    ws = sh.worksheet(gs_worksheet)
                except gspread.WorksheetNotFound:
                    ws = sh.add_worksheet(title=gs_worksheet, rows=1000, cols=10)

                # Ensure header row
                header = ["date", "type", "currency", "payment", "status", "description"]
                current_values = ws.get_values("1:1")
                if not current_values or current_values[0] != header:
                    ws.update("1:1", [header])

                # Append data rows
                if rows:
                    values = [[r.get(k, "") for k in header] for r in rows]
                    ws.append_rows(values, value_input_option="RAW")
                logging.info("Google Sheets append complete")
            except Exception as gexc:  # noqa: BLE001
                logging.exception("Google Sheets export failed: %s", gexc)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to fetch and upload operations: %s", exc)
        raise


if __name__ == "__main__":
    main()


