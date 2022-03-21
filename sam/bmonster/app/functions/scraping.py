import json
import urllib.parse
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

import requests
from bs4 import BeautifulSoup

from ..constants import StudioList
from ..models import Performer, Program, Schedule, dynamodb_migrate
from ..schemas import ScheduleResponse

JST = timezone(timedelta(hours=9))
BASE_URL = "https://www.b-monster.jp"
PAGE_PATH = "reserve/"
URL = urllib.parse.urljoin(BASE_URL, PAGE_PATH)


def lambda_handler(event, context):
    dynamodb_migrate()
    res = main()
    return {
        "statusCode": 200,
        "body": json.dumps(res)
    }


@dataclass
class ScrapingItem:
    performer: str
    vol: str
    studio: str
    start_datetime: datetime


def scraping(studio_code: str,
             studio_name: str,
             now: datetime = datetime.now(JST)) -> List[ScrapingItem]:
    item_list: List[ScrapingItem] = []

    # HTML取得
    r = requests.get(URL, params={"studio_code": studio_code})
    try:
        r.raise_for_status()
    except Exception as e:
        raise e

    # HTML解析
    soup = BeautifulSoup(r.text, features="html.parser")
    week = soup.select("body div#scroll-box div.grid div.flex-no-wrap")
    date = now
    for day in week:
        panels = day.select("li.panel")
        for panel in panels:
            time = panel.select("p.tt-time")
            performer = panel.select("p.tt-instructor")
            program = panel.select("p.tt-mode")

            if time and performer and program:
                # プログラム開始時間（HH:MM）
                hour = int(time[0].text[:2])
                minute = int(time[0].text[3:5])
                # パフォーマー
                performer = performer[0].text
                # プログラム名（リミテッド表記を削除）
                program = program[0]["data-program"]
                program = program if "(l)" not in program else program[:-3]
                # パフォーマー名またはプログラム名が未定の場合はスキップ
                if not performer or not program:
                    continue

                item_list.append(ScrapingItem(
                    performer,
                    program,
                    studio_name,
                    datetime(year=date.year, month=date.month, day=date.day, hour=hour, minute=minute, tzinfo=JST)
                ))

        date += timedelta(days=1)

    return item_list


def main() -> List[dict]:
    # スクレイピング実行して最新のレスケ一覧取得
    item_list: List[ScrapingItem] = []
    for studio in StudioList.__members__.values():
        item_list += scraping(studio.value, studio.name)

    ProgramKey = namedtuple('ProgramKey', 'performer vol')

    # レスケを解析してパフォーマー一覧とプログラム一覧を取得
    performer_name_set: set = {item.performer for item in item_list}
    performer_list: List[Performer] = [Performer(performer_name) for performer_name in performer_name_set]
    program_set: set = {ProgramKey(item.performer, item.vol) for item in item_list}
    program_list: List[Program] = [Program(key.performer, key.vol) for key in program_set]

    with Performer.batch_write() as batch:
        for performer in performer_list:
            batch.save(performer)
    with Program.batch_write() as batch:
        for program in program_list:
            batch.save(program)

    # レスケ解析
    schedule_dict = {}
    for item in item_list:
        key = ProgramKey(performer=item.performer, vol=item.vol)
        if not schedule_dict.get(key):
            schedule_dict[key] = [{"studio": item.studio, "startDatetime": item.start_datetime.isoformat()}]
        else:
            schedule_dict[key].append({"studio": item.studio, "startDatetime": item.start_datetime.isoformat()})
    schedule_list: List[Schedule] = [
        Schedule(performer=key.performer, vol=key.vol, schedule_list=value) for key, value in schedule_dict.items()
    ]

    with Schedule.batch_write() as batch:
        for schedule in schedule_list:
            batch.save(schedule)

    return [ScheduleResponse.from_orm(schedule).dict() for schedule in schedule_list]
