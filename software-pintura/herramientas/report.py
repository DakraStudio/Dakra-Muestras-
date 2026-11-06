import json,collections
d=json.load(open('colors.json'))
rows=[];tot=0;est=0
for mk,arr in sorted(d['makes'].items()):
    ys=[int(r.split('-')[0]) for e in arr for r in e[4].split(',')]+[int(r.split('-')[-1]) for e in arr for r in e[4].split(',')]
    fin=collections.Counter(e[2] for e in arr); nohue=sum(1 for e in arr if not e[6])
    rows.append((mk,len(arr),min(ys),max(ys),fin['S'],fin['M'],fin['P'],fin['T'],nohue)); tot+=len(arr); est+=nohue
lines=['| Marca | Códigos | Años | Sólidos | Metálicos | Perlados | Tricapa | Sin tono en el nombre |','|---|---:|---|---:|---:|---:|---:|---:|']
for r in rows: lines.append(f'| {r[0]} | {r[1]:,} | {r[2]}–{r[3]} | {r[4]:,} | {r[5]:,} | {r[6]:,} | {r[7]:,} | {r[8]:,} |')
lines.append(f'| **Total** | **{tot:,}** | | | | | | **{est:,}** |')
print('\n'.join(lines)); print(); print('MAKES',len(rows),'TOTAL',tot)
