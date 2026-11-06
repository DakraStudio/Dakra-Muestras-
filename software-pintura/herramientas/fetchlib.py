import os, sys, time, re, json, urllib.request, urllib.error
BASE='https://www.automotivetouchup.com/touch-up-paint/'
CACHE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache')
os.makedirs(CACHE,exist_ok=True)
UA='Mozilla/5.0 (compatible; TallerDeColor-research/1.0)'
DELAY=float(os.environ.get('DELAY','0.9'))
def get(path):
    fn=os.path.join(CACHE,path.strip('/').replace('/','__')+'.html')
    if os.path.exists(fn): return open(fn,encoding='utf-8',errors='ignore').read()
    for attempt in range(4):
        try:
            req=urllib.request.Request(BASE+path,headers={'User-Agent':UA})
            with urllib.request.urlopen(req,timeout=40) as r:
                t=r.read().decode('utf-8','ignore')
            open(fn,'w',encoding='utf-8').write(t); time.sleep(DELAY); return t
        except urllib.error.HTTPError as e:
            open(fn,'w').write(f'__HTTP{e.code}__'); time.sleep(DELAY); return f'__HTTP{e.code}__'
        except Exception as e:
            time.sleep(2**attempt*2)
    return ''
