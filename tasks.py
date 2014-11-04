from __future__ import absolute_import
from celery import shared_task
from gcalsync.sync import Synchronizer
from gcalsync.transformation import BaseTransformer
from mezzanine_events.models import Event
from mezzanine.conf import settings
from rfc3339 import parse_date
from mezzanine.generic.models import Keyword

class EventTransformer(BaseTransformer):
    model = Event

    def transform(self, event_data):
        if not self.validate(event_data):
            return False
        res = {
            'title': event_data['summary'],
            'location': event_data['location'],
            'gcal_url': event_data['htmlLink'],
            'gcal_id': event_data['id'],
            'gcal_etag': event_data['etag']
        }
        if 'dateTime' in event_data['start']:
            start_datetime = self.parse_datetime(event_data['start']['dateTime'])
            res['start_date']= start_datetime.date()
            res['start_time']= start_datetime.time()

        elif 'date' in event_data['start']:
            res['start_date']= parse_date(event_data['start']['date'])

        if 'dateTime' in event_data['end']:
            end_datetime = self.parse_datetime(event_data['end']['dateTime'])
            res['end_date']= end_datetime.date()
            res['end_time']= end_datetime.time()

        elif 'date' in event_data['end']:
            res['end_date'] = parse_date(event_data['end']['date'])

        if 'description' in event_data:
            res['content'] = event_data['description']

        if 'extendedProperties' in event_data:
            if 'private' in event_data['extendedProperties']:
                if 'X-MOZ-CATEGORIES' in event_data['extendedProperties']['private']:
                    res['keywords_string'] = event_data['extendedProperties']['private']['X-MOZ-CATEGORIES']
                    res['keywords'] = []
                    for keyword_string in res['keywords_string'].split(","):
                        res['keywords'].append(Keyword.objects.get_or_create(title=keyword_string)[0].id)

        return res

@shared_task(ignore_result=True)
def transform():
    synchronizer = Synchronizer(calendar_id=settings.GCALSYNC_CALENDAR, transformer=EventTransformer())
    synchronizer.sync()

