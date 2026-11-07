"""Descarga por modelo: muestrea cada 4 años y completa solo donde el modelo existe.
Guarda solo datos (códigos y nombres) en resultados/<marca>.jsonl."""
import os, sys, json, time, glob, re, collections, urllib.request, urllib.error
from parse import parse_page
HERE=os.path.dirname(os.path.abspath(__file__))
CACHE=os.path.join(HERE,'cache'); OUT=os.path.join(HERE,'resultados'); os.makedirs(OUT,exist_ok=True)
BASE='https://www.automotivetouchup.com/touch-up-paint/'; UA='Mozilla/5.0 (compatible; TallerDeColor-research/1.0)'
DELAY=float(os.environ.get('DELAY','1.0'))
VMAX=53600  # los años que no existen usan vehículos 'virtuales' con número alto
def fetch(path):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE+path,headers={'User-Agent':UA}),timeout=45) as r: t=r.read().decode('utf-8','ignore')
            time.sleep(DELAY); return t
        except urllib.error.HTTPError as e:
            time.sleep(DELAY); return None
        except Exception: time.sleep(3*(a+1))
    return None
def run(mk):
    fn=os.path.join(OUT,f'{mk}.jsonl'); done={}
    if os.path.exists(fn):
        for l in open(fn):
            d=json.loads(l)
            if 'v' in d: done[(d['m'],d['y'])]=d
    out=open(fn,'a')
    def get(m,y):
        if (m,y) in done: return done[(m,y)]
        t=fetch(f'{mk}/{y}/{m}/'); rows=[] if t is None else [[r['codes'],r['names']] for r in parse_page(t)]
        vm=re.search(r'vehicle=(\d+)',t or ''); v=int(vm.group(1)) if vm else 0
        d={'m':m,'y':y,'v':v,'r':rows if 0<v<VMAX else [],'ok':t is not None}; done[(m,y)]=d; out.write(json.dumps(d,ensure_ascii=False)+'\n'); out.flush(); return d
    models=set()
    for f in glob.glob(os.path.join(CACHE,f'models__{mk}__*.json')): models|=set(json.load(open(f)))
    models=sorted(models-{'all-models'})
    years=[y for y in range(1990,2026) if os.path.exists(os.path.join(CACHE,f'{mk}__{y}__all-models.html'))]
    if not years: print('skip',mk,flush=True); return
    probe=sorted(set(years[::4]+[years[-1]]))
    for m in models:
        for y in probe: get(m,y)
    valid=lambda d: d['ok'] and 0<d['v']<VMAX and d['r']
    for m in models:
        vy=[y for y in probe if valid(done[(m,y)])]
        need=set()
        for y in vy: need|={x for x in range(y-3,y+4) if x in years}
        for y in sorted(need): get(m,y)
    print('done',mk,len(done),flush=True); open(os.path.join(OUT,f'{mk}.done'),'w').write(str(len(done)))
for mk in sys.argv[1].split(','): run(mk)
print('ALLDONE',flush=True)
