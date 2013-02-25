from bitdeli.insight import insight, segment, segment_label
from bitdeli.widgets import Bar, Widget, Text
from discodb.query import Literal, Clause, Q
from itertools import imap

MAX_LABEL_LEN=32

class TokenInput(Widget):
    pass

def parse_query(query):
    def parse_clause(clause_str):
        for literal_str in clause_str.replace('=', ':').split(' OR '):
            if literal_str.startswith('NOT '):
                yield Literal(literal_str[4:], negated=True)
            else:
                yield Literal(literal_str)
    return Q(Clause(parse_clause(clause_str))
             for clause_str in query if clause_str not in ('NOT', 'OR'))

def format_query(tokens, model):

    def any_key():
        return [key[2:].decode('utf-8') for key in model[' ']]

    def is_property(token):
        for key in imap(lambda x: x.decode('utf-8'), model[' ']):
            if key[0] == 'p' and key[2:] == token:
                return True
        return False
        
    def property_values(token):
        token += ':'
        n = len(token)
        for key in imap(lambda x: x.decode('utf-8'), model):
            if key.startswith(token):
                yield key[n:]
        
    last = tokens[-1] if tokens else ''
    seclast = tokens[-2] if len(tokens) > 1 else ''
    if not last:
        return [], any_key() + ['NOT']
    elif last == 'NOT':
        return tokens, any_key()
    elif last == 'OR':
        return tokens, any_key() + ['NOT']
    elif seclast.endswith('='):
        tokens[-2] += tokens[-1]
        return tokens[:-1], any_key() + ['OR', 'NOT']
    elif last.endswith('='):
        return tokens, list(property_values(last[:-1]))
    elif seclast == 'NOT':
        tokens[-2] += ' ' + tokens[-1]
        tokens = tokens[:-1]
    elif seclast == 'OR':
        tokens[-3] += ' OR ' + tokens[-1]
        tokens = tokens[:-2]
    if is_property(last):
        tokens[-1] += '='
        return tokens, list(property_values(last))
    else:
        return tokens, any_key() + ['OR', 'NOT']

def tokeninputs(params, model):
    for k, v in sorted(params.iteritems()):
        if k.startswith('query'):
            yield format_query(v['value'], model)

def chart_data(inputs, model):
    for tokens, values in inputs:
        label = ' & '.join(tokens)
        if len(label) > MAX_LABEL_LEN:
            label = '...' + label[-MAX_LABEL_LEN:]
        yield label, len(model.query(parse_query(tokens)))
            
@insight
def view(model, params):
    inputs = [(tokens, values)
              for tokens, values in tokeninputs(params, model) if tokens] +\
             [format_query([], model)] 
    if len(inputs) > 1:
        yield Bar(id='bars',
                  size=(max(4, min(12, 2 * len(inputs))), 4),
                  label='Results',
                  data=list(chart_data(inputs[:-1], model)))
    for i, (tokens, values) in enumerate(inputs):
        yield TokenInput(id='query%.2d' % i,
                         size=(12, 1),
                         label='Query %d' % (i + 1),
                         value=tokens,
                         data=values)
    yield Text(size=(12, 2),
               label="Usage",
               data={'text': 'Query "A B" means "A and B". Also OR and NOT operators are supported.'})

{"params":{"query00":{"type":"tokeninput","value":["url_domain=git-annex.branchable.com"]},"query01":{"type":"tokeninput","value":[]}},"id":"bars","type":"bar","value":{"label":"..._domain=git-annex.branchable.com","index":"0"}}    

@segment
def segment(model, params):
    tokens = list(tokeninputs(params['params'], model))
    print 'params', params
    print 'tokens', tokens
    tokens = tokens[int(params['value']['index'])]
    return model.query(parse_query(tokens))
    
@segment_label
def label(segment, params):
    tokens = tokeninputs(params, model)[params['value']['index']]
    return 'Query: ' + ' & '.join(tokens)
    