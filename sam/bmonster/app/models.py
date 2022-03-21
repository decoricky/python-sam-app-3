from datetime import datetime, timedelta, timezone

from pynamodb.attributes import ListAttribute, TTLAttribute, UnicodeAttribute
from pynamodb.models import Model

JST = timezone(timedelta(hours=9))


class BaseMeta:
    region = 'ap-northeast-1'
    host = "http://dynamodb:8000"
    aws_access_key_id = 'access_key_id'
    aws_secret_access_key = 'secret_access_key'
    billing_mode = 'PAY_PER_REQUEST'


class Performer(Model):
    class Meta(BaseMeta):
        table_name = 'performer'

    name = UnicodeAttribute(hash_key=True)
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=31))

    def __str__(self):
        return self.name


class Program(Model):
    class Meta(BaseMeta):
        table_name = 'program'

    performer = UnicodeAttribute(hash_key=True)
    vol = UnicodeAttribute(range_key=True)
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=31))


class Schedule(Model):
    class Meta(BaseMeta):
        table_name = 'schedule'

    performer = UnicodeAttribute(hash_key=True)
    vol = UnicodeAttribute(range_key=True)
    schedule_list = ListAttribute()
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=1))


def dynamodb_migrate():
    if not Performer.exists():
        Performer.create_table()

    if not Program.exists():
        Program.create_table()

    if not Schedule.exists():
        Schedule.create_table()
