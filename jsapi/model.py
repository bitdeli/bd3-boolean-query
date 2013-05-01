from urlparse import urlparse
from itertools import chain
from discodb import DiscoDB
from bitdeli.model import model

MAX_LEN = 64

def get_event_name(event):
    name = event.get('$event_name')
    if name == '$dom_event':
        name = event.get('$event_label')
    elif name == '$pageview':
        name = 'viewed %s' % urlparse(event.get('$page', '')).path
    if name:
        return name[:MAX_LEN]

@model
def build(profiles):
    keys = set()
    for profile in profiles:
        uid = profile.uid
        if not uid:
            continue
        fields = set()
        source_events = chain(profile.get('events', []),
                              profile.get('$pageview', []),
                              profile.get('$dom_event', []))
        for tstamp, group, ip, event in source_events:
            event_name = get_event_name(event)
            if event_name:
                event_name = event_name.encode('utf-8')
                keys.add('e:' + event_name)
                fields.add(event_name)
            real_name = event.pop('$event_name', None)
            if real_name == '$dom_event':
                # Do not read properties from DOM events
                continue
            for prop_name, prop_value in event.iteritems():
                p = prop_name.encode('utf-8')
                keys.add('p:%s' % p)
                fields.add('%s:%s' % (p, str(prop_value)[:MAX_LEN].encode('utf-8')))
        for field in fields:
            yield field, uid
    for key in keys:
       yield ' ', key
