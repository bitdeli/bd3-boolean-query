from discodb import DiscoDB
from bitdeli.model import model


MAX_LEN = 64

@model
def items(profiles):
    for profile in profiles:
        uid = profile.uid
        for event in profile['events']:
            event = event.encode('utf-8')
            yield event, uid
            yield ' ', 'e:%s' % event
        for prop_name, prop_values in profile['properties'].iteritems():
            prop_name = prop_name.encode('utf-8') 
            yield ' ', 'p:%s' % prop_name
            for prop_value in prop_values:
                yield '%s:%s' % (prop_name, prop_value[:MAX_LEN].encode('utf-8')),\
                      uid
                
