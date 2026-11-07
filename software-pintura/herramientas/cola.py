"""Fila de marcas: 3 descargas a la vez; salta las marcas ya terminadas (.done)."""
import os, subprocess, time
HERE=os.path.dirname(os.path.abspath(__file__))
COLA=('chrysler hyundai kia volkswagen mazda subaru mitsubishi buick cadillac lincoln '
      'lexus acura infiniti bmw mercedes-benz audi tesla volvo mini land-rover jaguar porsche '
      'pontiac saturn mercury oldsmobile scion hummer plymouth isuzu suzuki fiat alfa-romeo saab smart '
      'eagle geo genesis polestar rivian daewoo').split()
def done(m): return os.path.exists(os.path.join(HERE,'resultados',f'{m}.done'))
def busy(m):
    return subprocess.run(['pgrep','-f',f'fetch_models.py.*{m}'],capture_output=True).returncode==0
run={}
while True:
    for m,p in list(run.items()):
        if p.poll() is not None: del run[m]
    activos=len(run)+sum(1 for m in COLA if busy(m) and m not in run)
    pend=[m for m in COLA if not done(m) and not busy(m) and m not in run]
    while activos<3 and pend:
        m=pend.pop(0)
        run[m]=subprocess.Popen(['python3','fetch_models.py',m],cwd=HERE,env=dict(os.environ,DELAY='1.0'),
                                stdout=open(os.path.join(HERE,f'cola_{m}.log'),'a'),stderr=subprocess.STDOUT)
        activos+=1
    if not pend and not run and not any(busy(m) for m in COLA): print('COLA_FIN',flush=True); break
    time.sleep(30)
