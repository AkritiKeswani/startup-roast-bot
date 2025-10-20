import json, sys
def jlog(**kv): print(json.dumps(kv), flush=True, file=sys.stdout)