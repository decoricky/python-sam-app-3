import json
import urllib.parse
from datetime import timedelta, timezone
from typing import List

from ..models import ProgramReview, Program
from ..schemas import ProgramRequest, ProgramReviewResponse, ProgramReviewCreateUpdateRequest

JST = timezone(timedelta(hours=9))


def lambda_handler(event, context):
    http_method = event['httpMethod']
    headers = event['headers']
    query_params = event['queryStringParameters'] or {}
    body = event['body']

    if http_method == 'GET':
        response = get(ProgramRequest(**query_params))

    elif http_method == 'POST' and headers.get('Content-Type') == 'application/json':
        body = json.loads(body)
        response = post(ProgramReviewCreateUpdateRequest(**body))

    elif http_method == 'POST' and headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        # APIGWの場合はbase64でencodeされているのでdecodeが必要
        # import base64
        # body = base64.b64decode(body).decode()
        body = urllib.parse.parse_qs(body)
        response = post(ProgramReviewCreateUpdateRequest(
            performer=body['performer'][0],
            vol=body['vol'][0],
            star=body['star'][0]
        ))

    else:
        response = {}

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


def get(req: ProgramRequest) -> List[dict]:
    if req.performer and req.vol:
        try:
            item_list = [ProgramReview.get(req.performer, req.vol)]
        except ProgramReview.DoesNotExist:
            item_list = []
    elif req.performer:
        item_list = ProgramReview.query(req.performer)
    else:
        item_list = ProgramReview.scan()

    return [ProgramReviewResponse.from_orm(item).dict() for item in item_list]


def post(req: ProgramReviewCreateUpdateRequest) -> dict:
    try:
        Program.get(req.performer, req.vol)
    except ProgramReview.DoesNotExist:
        return {}

    try:
        item = ProgramReview.get(req.performer, req.vol)
        item.star = req.star
    except ProgramReview.DoesNotExist:
        item = ProgramReview(**req.dict())

    item.save()
    return ProgramReviewResponse.from_orm(item).dict()
