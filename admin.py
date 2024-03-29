from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import Event, EventContainer

from copy import deepcopy

# event_admin_fieldsets = deepcopy(PageAdmin.fieldsets)
# event_admin_fieldsets[0][1]["fields"]

class EventAdmin (PageAdmin):
    fieldsets = (
        deepcopy(PageAdmin.fieldsets[0]),
        ("Event details",{
            'fields': ('content', ('start_date','end_date'), ('start_time', 'end_time'), 'location', 'mappable_location', ('lat', 'lon'), 'speakers', 'rsvp')
        }),
        deepcopy(PageAdmin.fieldsets[1]),
    )
    def save_model(self, request, obj, form, change):
        obj.save_push_to_gcal(obj)

admin.site.register(Event, EventAdmin)
admin.site.register(EventContainer, PageAdmin)
