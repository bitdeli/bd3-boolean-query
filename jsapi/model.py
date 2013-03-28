from discodb import DiscoDB
from bitdeli.model import model

MAX_LEN = 64

@model
def build(profiles):
    keys = set()
    for profile in profiles:
        uid = profile.uid
        if not uid:
            continue
        fields = set()
        for tstamp, group, ip, event in profile['events']:
            e = 'e:%s' % event.pop('$event_name').encode('utf-8')
            keys.add(e)
            fields.add(e)
            for prop_name, prop_value in event.iteritems():
                p = prop_name.encode('utf-8')
                keys.add('p:%s' % p)
                fields.add('%s:%s' % (p, str(prop_value)[:MAX_LEN].encode('utf-8')))
        for field in fields:
            yield field, uid
    for key in keys:
       yield ' ', key
