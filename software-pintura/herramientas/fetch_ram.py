import json,os,sys
sys.argv=['x']
from fetchlib import get, CACHE
for y in range(1990,2026):
    ms=json.load(open(os.path.join(CACHE,f'models__dodge__{y}.json')))
    for m in ['ram','ram-truck','new-ram-truck','ram-pickup']:
        if m in ms: get(f'dodge/{y}/{m}/')
print('RAMDONE',flush=True)
