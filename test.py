import simplejson as json

print(json.loads(json.dumps({'a': True})))
