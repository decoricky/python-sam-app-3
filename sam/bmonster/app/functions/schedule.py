import json
from datetime import timedelta, timezone
from typing import List

from ..models import Schedule
from ..schemas import ProgramRequest, ScheduleResponse

JST = timezone(timedelta(hours=9))


def lambda_handler(event, context):
    http_method = event['httpMethod']
    headers = event['headers']
    query_params = event['queryStringParameters'] or {}

    if http_method == 'GET':
        response = get(ProgramRequest(**query_params))

    else:
        response = {}

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


def get(req: ProgramRequest) -> List[dict]:
    if req.performer and req.vol:
        try:
            schedule_list = [Schedule.get(req.performer, req.vol)]
        except Schedule.DoesNotExist:
            schedule_list = []
    elif req.performer:
        schedule_list = Schedule.query(req.performer)
    else:
        schedule_list = Schedule.scan()

    return [ScheduleResponse.from_orm(schedule).dict() for schedule in schedule_list]
