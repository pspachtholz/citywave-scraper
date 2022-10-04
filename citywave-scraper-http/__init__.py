import json
import logging
import requests

from datetime import datetime, timedelta

import azure.functions as func

log = logging.getLogger(__name__)


def main(mytimer: func.TimerRequest, outputblob: func.Out[str]) -> None:
    logging.info('Python HTTP trigger function processed a request.')
    if mytimer.past_due:
        log.warning('The timer is past due!')

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_week = today + timedelta(days=7)

    log.info(f"Scraping for {today} until {next_week}")
    url = f"https://partner.venuzle.de/citywave-regensburg/sharedbookings/1/bookableevents/ajax/?start={today.isoformat()}&end={next_week.isoformat()}"
    log.info(f"Url: {url}")

    resp = requests.get(url)

    if not resp.ok:
        raise Exception(f"Could not get response from url: {url}")

    slots = resp.json()

    if not slots:
        raise Exception("No slots found")
    
    for slot in slots:
        slot["harvest_date"] = str(datetime.now())

    json_str = json.dumps(slots)

    outputblob.set(json_str)