import base64
import json
import urllib.parse
from datetime import timedelta, timezone
from typing import List

from ..models import Schedule
from ..schemas import ProgramRequest, ScheduleResponse

JST = timezone(timedelta(hours=9))


def lambda_handler(event, context):
    http_method = event['httpMethod']
    headers = event['headers']
    query_params = event['queryStringParameters']
    body = event['body']
    # APIGWの場合はbase64でencodeされているのでdecodeが必要
    # body = base64.b64decode(body).decode()

    if http_method == 'GET':
        if not query_params:
            query_params = {}
        response = get(ProgramRequest(**query_params))

    elif http_method == 'POST' and headers.get('Content-Type') == 'application/json':
        body = json.loads(body)
        response = post(ProgramRequest(**body))

    elif http_method == 'POST' and headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        body = urllib.parse.parse_qs(body)
        response = post(ProgramRequest(**body))

    else:
        response = {}

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


def get(req: ProgramRequest) -> List[dict]:
    if req.performer and req.vol:
        schedule_list = [Schedule.get(req.performer, req.vol)]
    elif req.performer:
        schedule_list = Schedule.query(req.performer)
    else:
        schedule_list = Schedule.scan()

    return [ScheduleResponse.from_orm(schedule).dict() for schedule in schedule_list]


def post(req: ProgramRequest) -> dict:
    return {}
