import os
from datetime import datetime, timedelta, timezone

from pynamodb.attributes import ListAttribute, TTLAttribute, UnicodeAttribute, NumberAttribute
from pynamodb.models import Model

JST = timezone(timedelta(hours=9))


class BaseMeta:
    region = os.getenv('REGION')
    host = os.getenv('DYNAMODB_HOST') or None
    billing_mode = os.getenv('BILLING_MODE')


class PerformerIndex(Model):
    class Meta(BaseMeta):
        table_name = 'performer'

    name = UnicodeAttribute(hash_key=True)

    def __str__(self):
        return self.name


class Performer(PerformerIndex):
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=31))


class ProgramIndex(Model):
    class Meta(BaseMeta):
        table_name = 'program'

    performer = UnicodeAttribute(hash_key=True)
    vol = UnicodeAttribute(range_key=True)


class Program(ProgramIndex):
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=31))


class ScheduleIndex(Model):
    class Meta(BaseMeta):
        table_name = 'schedule'

    performer = UnicodeAttribute(hash_key=True)
    vol = UnicodeAttribute(range_key=True)


class Schedule(ScheduleIndex):
    schedule_list = ListAttribute()
    ttl = TTLAttribute(default=datetime.now(JST) + timedelta(days=1))


class ProgramReviewIndex(Model):
    class Meta(BaseMeta):
        table_name = 'program_review'

    performer = UnicodeAttribute(hash_key=True)
    vol = UnicodeAttribute(range_key=True)


class ProgramReview(ProgramIndex):
    star = NumberAttribute()


def dynamodb_migrate():
    if not PerformerIndex.exists():
        PerformerIndex.create_table()

    if not ProgramIndex.exists():
        ProgramIndex.create_table()

    if not ScheduleIndex.exists():
        ScheduleIndex.create_table()

    if not ProgramReviewIndex.exists():
        ProgramReviewIndex.create_table()
