import configparser
import csv
import json
import logging
import platform
import signal
import sys
import time
import traceback
import zipfile
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path

import pause
import pytz
from colorama import Back, Fore, Style

if platform.system() == "Windows":
    from colorama import init
    init(convert=True)

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / 'configs' / 'mainconf.ini'
DEPS_DIR = BASE_DIR / 'dependencies'

sys.path.insert(0, str(Path(__file__).parent))


def download_dependency(url, file_name):
    try:
        import requests
        response = requests.get(url)
        (DEPS_DIR / file_name).write_bytes(response.content)
    except Exception as e:
        raise Exception(f"Error getting {file_name} from {url}") from e
    print("Successfully got", file_name)


def refresh_dependencies():
    DEPS_DIR.mkdir(exist_ok=True)
    required_files = [('FAA_Reg_DB_Latest.zip', "https://registry.faa.gov/database/ReleasableAircraft.zip")]
    for file_name, url in required_files:
        zip_path = DEPS_DIR / file_name
        if not zip_path.exists():
            print(file_name, "does not exist, downloading now")
            download_dependency(url, file_name)
        else:
            print("Already have", file_name, "deleting and redownloading")
            zip_path.unlink()
            download_dependency(url, file_name)

        with zipfile.ZipFile(DEPS_DIR / 'FAA_Reg_DB_Latest.zip', 'r') as zip_file:
            for extracted in ('MASTER.txt', 'ACFTREF.txt'):
                target = DEPS_DIR / extracted
                if target.exists():
                    target.unlink()
                zip_file.extract(extracted, str(DEPS_DIR))


def lookup_aircraft_model(model_code):
    with open(DEPS_DIR / 'ACFTREF.txt', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(filter(lambda row: row[0] != '#', f))
        for model in reader:
            if model['CODE'] == model_code:
                return model


main_config = configparser.ConfigParser()
main_config.read(CONFIG_PATH)

if main_config.getboolean('DISCORD', 'ENABLE'):
    from discord_notifier import send_discord
    send_discord("Started", main_config)


def handle_service_exit(signum, frame):
    if main_config.getboolean('DISCORD', 'ENABLE'):
        send_discord("Service Stop", main_config)
    raise SystemExit("Service Stop")


signal.signal(signal.SIGTERM, handle_service_exit)

try:
    running_count = 0
    try:
        tz = pytz.timezone(main_config.get('TIME', 'TZ'))
        current_time = datetime.now(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.UTC
        current_time = datetime.now(tz)

    search_names = json.loads(main_config.get('SEARCH', 'NAMES'))
    print("Search names", search_names)
    found_aircraft = []
    first_check = True

    while True:
        header = f"-------- {running_count} -------- {current_time.strftime('%I:%M:%S %p')} ---------------------------------------------------------------------------"
        print(Back.GREEN + Fore.BLACK + header[:100] + Style.RESET_ALL)
        if current_time.hour == 0 and current_time.minute == 0:
            running_count = 0
        start_time = time.time()
        refresh_dependencies()
        with open(DEPS_DIR / 'MASTER.txt', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(filter(lambda row: row[0] != '#', f))
            for reg in reader:
                if reg['NAME'].strip() in search_names and reg['N-NUMBER'].strip() not in found_aircraft:
                    found_aircraft.append(reg['N-NUMBER'].strip())
                    if not first_check:
                        aircraft_type = lookup_aircraft_model(reg['MFR MDL CODE'])
                        message = (
                            f"Found new reg for {reg['NAME'].strip()} "
                            f"N{reg['N-NUMBER'].strip()} a "
                            f"{aircraft_type['MFR'].strip()} {aircraft_type['MODEL'].strip()} "
                            f"https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?NNumbertxt={reg['N-NUMBER']}"
                        )
                        print(message)
                        send_discord(message, main_config)
        print(len(found_aircraft), "Current Regs in searched names")
        first_check = False
        running_count += 1
        elapsed_time = time.time() - start_time
        footer = f"-------- {running_count} -------- {current_time.strftime('%I:%M:%S %p')} ------------------------Elapsed Time- {round(elapsed_time, 3)} -------------------------------------"
        print(Back.GREEN + Fore.BLACK + footer[:100] + Style.RESET_ALL)
        now_utc = datetime.utcnow()
        next_run_time = dtime(hour=5)
        if now_utc.hour >= 5:
            next_run = datetime.combine(now_utc.date() + timedelta(days=1), next_run_time, tzinfo=timezone.utc)
        else:
            next_run = datetime.combine(now_utc.date(), next_run_time, tzinfo=timezone.utc)
        print("Sleeping till", next_run)
        pause.until(next_run)

except KeyboardInterrupt as e:
    print(e)
    if main_config.getboolean('DISCORD', 'ENABLE'):
        send_discord(f"Manual Exit: {e}", main_config)
except Exception as e:
    if main_config.getboolean('DISCORD', 'ENABLE'):
        crash_log = BASE_DIR / 'crash_latest.log'
        try:
            crash_log.unlink()
        except OSError:
            pass
        logging.basicConfig(filename=str(crash_log), filemode='w', format='%(asctime)s - %(message)s')
        logging.Formatter.converter = time.gmtime
        logging.error(e)
        logging.error(traceback.format_exc())
        send_discord(f"Error Exiting: {e}", main_config, str(crash_log))
    raise e
