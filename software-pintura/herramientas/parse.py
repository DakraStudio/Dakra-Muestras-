import re, html, os, json
CACHE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache')
ROW=re.compile(r'<tr data-color-result-id="(\d+)">(.*?)</tr>',re.S)
def parse_page(t):
    out=[]
    for rid,r in ROW.findall(t):
        cp=re.search(r'CodePanel">(.*?)</div>',r,re.S); np_=re.search(r'NamePanel">(.*?)</div>',r,re.S)
        codes=[html.unescape(c).strip() for c in re.findall(r'>([^<>]+)</a>',cp.group(1))] if cp else []
        alt=re.search(r'alt="([^"]*)"',r)
        altcodes=[html.unescape(c).strip() for c in alt.group(1).split(',')] if alt else []
        names=[html.unescape(n).strip() for n in re.findall(r'<span>([^<]*)</span>',np_.group(1))] if np_ else []
        codes=[c for c in codes if c]; 
        allc=[]
        for c in codes+altcodes:
            if c and c not in allc: allc.append(c)
        out.append({'id':rid,'codes':allc,'names':[n for n in names if n]})
    return out
if __name__=='__main__':
    import sys
    t=open(os.path.join(CACHE,sys.argv[1]),encoding='utf-8',errors='ignore').read()
    rows=parse_page(t); print(len(rows))
    for r in rows[:40]: print(r['codes'],r['names'])
