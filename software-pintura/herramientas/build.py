import os, re, json, glob, collections, colorsys
from parse import parse_page, CACHE
DISPLAY={'mercedes-benz':'Mercedes-Benz','bmw':'BMW','gmc':'GMC','mini':'MINI','land-rover':'Land Rover','alfa-romeo':'Alfa Romeo','rolls-royce':'Rolls-Royce','aston-martin':'Aston Martin','mg-motors':'MG','ram':'Ram'}
def disp(m): return DISPLAY.get(m, m.replace('-',' ').title())
# ---------- color estimado por nombre ----------
HUE=[ # (palabras, hex)
 (['pearl white','white pearl','white diamond','diamond white','crystal white','snow white','pearl'], '#EEEDE8'),
 (['white','blanco','blanc','weiss','bianco','ivory','alabaster','arctic','glacier','polar','snow','blizzard','frost white','chalk','cloud','oxford'], '#F1F1EE'),
 (['cream','vanilla','pearl beige','champagne','cashmere','linen','oyster'], '#E2D6BC'),
 (['beige','sand','tan','desert','dune','khaki','almond','sandstone','mojave','sahara','wheat','biscuit'], '#C7B48E'),
 (['gold','topaz','golden','brass','amber','honey'], '#B8914A'),
 (['yellow','lemon','canary','sunburst','citrus','banana','gelb','amarillo'], '#E6BF1C'),
 (['orange','tangerine','mango','pumpkin','sunset','inferno','copper orange'], '#DD6420'),
 (['copper','bronze','cinnamon','rust','sienna','autumn'], '#8C5432'),
 (['brown','mocha','coffee','cocoa','espresso','chestnut','walnut','saddle','chocolate','caramel','toffee','cappuccino','umber','mahogany','java','truffle'], '#5A3D2C'),
 (['maroon','burgundy','wine','garnet','cranberry','cabernet','merlot','bordeaux','claret','sangria','port','berry','currant','plum red','dark cherry','burgundy red'], '#651626'),
 (['red','ruby','cherry','scarlet','crimson','flame','fire','rojo','rot','rosso','rouge','salsa','chili','lava','vermillion','candy apple','rallye','race'], '#B3141D'),
 (['pink','rose','magenta','fuchsia','raspberry'], '#C24A7A'),
 (['purple','violet','plum','amethyst','lavender','lilac','grape','eggplant','aubergine','mulberry','orchid'], '#4C2A68'),
 (['navy','indigo','midnight blue','dark blue','deep blue','ink','marine','admiral','nautical'], '#1C2A47'),
 (['teal','aqua','turquoise','cyan','lagoon','caribbean','surf','seafoam','mint'], '#2C8A8C'),
 (['blue','sapphire','cobalt','azure','sky','ocean','sea','aegean','bleu','blau','azul','blu','denim','marina','lapis'], '#2B5199'),
 (['lime','chartreuse','kiwi'], '#86B83A'),
 (['olive','army','moss','sage','cactus','camo','jungle'], '#5E6440'),
 (['green','emerald','jade','forest','hunter','evergreen','pine','spruce','verde','grun','vert','ivy','juniper','cypress'], '#2C5E3B'),
 (['black','ebony','onyx','obsidian','jet','raven','noir','schwarz','nero','negro','sable','carbon black','phantom','shadow','midnight','night','tuxedo','licorice','caviar'], '#121315'),
 (['charcoal','graphite','gunmetal','anthracite','granite','slate','smoke','storm','thunder','iron','lead','carbon','dark gray','dark grey','magnetic','meteor','cement'], '#4C4F53'),
 (['silver','platinum','titanium','mercury','quicksilver','lunar','moon','chrome','aluminum','aluminium','steel','sterling','argent','plata','silber','pewter','nickel','tungsten','metal'], '#B1B4B7'),
 (['gray','grey','gris','grau','grigio','ash','stone','fog','mist','pebble','concrete','cinder','shale','flint','dove','harbor'], '#8A8D90'),
]
DARK=['dark','deep','midnight','night','dk ','espresso','burnt','smoked','magnetic','graphite','charcoal','gunmetal','granite','storm','thunder','shadow']
LIGHT=['light','pale','ice','frost','bright','lt ','pastel','powder','sky']
def s2l(v): return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def l2s(v):
    v=max(0,min(1,v)); return 12.92*v if v<=0.0031308 else 1.055*v**(1/2.4)-0.055
def hex2lab(h):
    r,g,b=[s2l(int(h[i:i+2],16)/255) for i in (1,3,5)]
    X=(0.4124564*r+0.3575761*g+0.1804375*b)/0.95047;Y=0.2126729*r+0.7151522*g+0.0721750*b;Z=(0.0193339*r+0.1191920*g+0.9503041*b)/1.08883
    f=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=f(X),f(Y),f(Z); return [116*fy-16,500*(fx-fy),200*(fy-fz)]
def lab2hex(L,a,b):
    fy=(L+16)/116;fx=fy+a/500;fz=fy-b/200
    fi=lambda t: t**3 if t**3>0.008856 else (t-16/116)/7.787
    X,Y,Z=0.95047*fi(fx),fi(fy),1.08883*fi(fz)
    rgb=[3.2404542*X-1.5371385*Y-0.4985314*Z,-0.9692660*X+1.8760108*Y+0.0415560*Z,0.0556434*X-0.2040259*Y+1.0572252*Z]
    return '#'+''.join('%02X'%round(l2s(v)*255) for v in rgb)
STRONG=set('white black silver gray grey red blue green yellow orange brown beige tan gold purple violet maroon burgundy pink bronze copper charcoal graphite navy teal aqua turquoise ivory cream champagne plum olive lime'.split())
def est_hex(names):
    txt=' '+re.sub(r'[^a-z ]',' ',' '.join(names[:1]).lower())+' '
    alltxt=' '+re.sub(r'[^a-z ]',' ',' '.join(names).lower())+' '
    def scan(t,strong):
        best=None
        for words,hx in HUE:
            for w in words:
                if strong and w.split()[-1] not in STRONG: continue
                for m in re.finditer(r'\b'+re.escape(w)+r'\b',t):
                    if best is None or m.start()>best[0] or (m.start()==best[0] and len(w)>best[2]): best=(m.start(),hx,len(w))
        return best
    best=scan(txt,True) or scan(alltxt,True) or scan(txt,False) or scan(alltxt,False)
    if not best: return '#9A9DA0', False
    L,a,b=hex2lab(best[1])
    first=txt
    if any(d in first for d in DARK) and L>25: L-=14
    elif any(l in first for l in LIGHT) and L<80: L+=10
    return lab2hex(L,a,b), True
def finish(names):
    t=' '.join(names).lower()
    if re.search(r'tri[\s-]?coat|tricoat|multi[\s-]?coat|3[\s-]?coat|three[\s-]?coat',t): return 'T'
    if re.search(r'pearl|mica|pearlcoat|crystal|iridescent|opal|flake|prism',t): return 'P'
    if re.search(r'metallic|\bmet\b|\bmetal|poly|metalli',t): return 'M'
    return 'S'
def find(par,x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
def build(makes):
    out={}; stats={}
    for mk in makes:
        pat={'ram':'dodge__*__*ram*.html'}.get(mk,f'{mk}__*__all-models.html')
        files=sorted(f for f in glob.glob(os.path.join(CACHE,pat)) if not open(f,errors='ignore').read(20).startswith('__HTTP'))
        if not files: continue
        GM=('chevrolet','gmc','buick','cadillac','pontiac','oldsmobile','saturn','hummer','geo')
        FCA=('dodge','ram','jeep','chrysler','plymouth','eagle')
        PAT={'toyota':[r'\d[0-9A-Z]{2}',r'[0-9A-Z]{3}'],'lexus':[r'\d[0-9A-Z]{2}',r'[0-9A-Z]{3}'],'scion':[r'\d[0-9A-Z]{2}',r'[0-9A-Z]{3}'],
             'ford':[r'[0-9A-Z]{2}'],'lincoln':[r'[0-9A-Z]{2}'],'mercury':[r'[0-9A-Z]{2}'],
             'honda':[r'[A-Z]{1,2}-?\d{2,3}[A-Z]{0,2}'],'acura':[r'[A-Z]{1,2}-?\d{2,3}[A-Z]{0,2}'],
             'volkswagen':[r'L[0-9A-Z]{3}'],'audi':[r'L[0-9A-Z]{3}'],'tesla':[r'P[A-Z]{3}'],'mercedes-benz':[r'\d{3}'],'maybach':[r'\d{3}'],'smart':[r'[A-Z0-9]{3}']}
        for m in GM: PAT[m]=[r'G[0-9A-Z]{2}',r'WA\w{3,4}']
        for m in FCA: PAT[m]=[r'P[0-9A-Z]{2}']
        pats=PAT.get(mk,[r'[0-9A-Z]{3}',r'[0-9A-Z]{2,4}'])
        raw=[]
        spread=collections.defaultdict(set)
        for fn in files:
            y=int(re.search(r'__(\d{4})__',fn).group(1))
            t=open(fn,encoding='utf-8',errors='ignore').read()
            for r in parse_page(t):
                cs=[re.sub(r'\s+',' ',c).strip().upper() for c in r['codes'] if c.strip()]
                if not cs: continue
                key=(r['names'][0].lower() if r['names'] else '')
                for c in cs: spread[c].add(key)
                raw.append((y,cs,r['names']))
        def pick(cs):
            for pt in pats:
                m=[c for c in cs if re.fullmatch(pt,c)]
                if m: return min(m,key=lambda c:(len(spread[c]),cs.index(c)))
            return min(cs,key=lambda c:(len(spread[c]),cs.index(c)))
        groups=collections.defaultdict(lambda:{'codes':collections.Counter(),'years':set(),'names':collections.Counter(),'nlast':{}})
        for y,cs,ns in raw:
            g=groups[pick(cs)]; g['years'].add(y)
            for c in cs: g['codes'][c]+=1
            for n in ns:
                g['names'][n]+=1; g['nlast'][n]=max(g['nlast'].get(n,0),y)
        primaries=set(groups)
        ents=[]
        for k,g in groups.items():
            code=k
            alias=[c for c,_ in g['codes'].most_common() if c!=code and c not in primaries][:8]
            EN=re.compile(r'\b(black|white|silver|gray|grey|red|blue|green|yellow|orange|brown|beige|gold|pearl|metallic|mica|bronze|copper|purple|maroon|burgundy|tan|charcoal|graphite)\b',re.I)
            FOREIGN=re.compile(r'\b(noir|blanc|nacre|rouge|bleu|gris|vert|schwarz|weiss|wei|silber|rot|blau|grau|nero|bianco|rosso|grigio|azul|negro|blanco|rojo|plata|metallise|metallizzato|perleffekt)\b',re.I)
            nm=sorted(g['names'],key=lambda n:(0 if EN.search(n) and not FOREIGN.search(n) else 1,-g['nlast'][n],-g['names'][n]))
            fin=finish(nm); hx,ok=est_hex(nm[:3] if nm else [''])
            ys=sorted(g['years'])
            rng=[];s0=p0=ys[0]
            for v in ys[1:]:
                if v==p0+1: p0=v; continue
                rng.append(f'{s0}-{p0}' if s0!=p0 else str(s0)); s0=p0=v
            rng.append(f'{s0}-{p0}' if s0!=p0 else str(s0))
            ents.append([code,' | '.join(nm[:4]),fin,hx,','.join(rng),' '.join(alias),1 if ok else 0])
        ents.sort(key=lambda e:e[0])
        if not ents: continue
        out[disp(mk)]=ents; stats[disp(mk)]=len(ents)
    return out,stats
if __name__=='__main__':
    makes=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'makes.txt')).read().strip().split(',')
    out,stats=build(makes)
    json.dump({'v':1,'source':'Compilado por Taller de Color a partir de listas públicas de códigos de pintura (AutomotiveTouchup.com). Solo datos: código, nombre y años. Colores en pantalla estimados por el nombre.','built':'2026-11','makes':out},open('colors.json','w'),ensure_ascii=False,separators=(',',':'))
    print(json.dumps(stats,ensure_ascii=False)); print('total',sum(stats.values()),'bytes',os.path.getsize('colors.json'))
