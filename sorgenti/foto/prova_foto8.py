"""20/11/2026 prova senza rete dell'ottava ricerca foto (actions_foto8.py): con risposte finte di Wikidata controlla che
si prenda l'elemento giusto e si scartino quelli sbagliati. Uso, dalla radice del sito: python3 sorgenti/foto/prova_foto8.py"""
import os, sys, importlib.util
os.environ['NO_PUSH'] = '1'; os.environ['PROVA'] = '0'
sys.argv = ['actions_foto8.py', '0']
spec = importlib.util.spec_from_file_location('f8', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'actions_foto8.py'))
f8 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f8)

def ent(label, lat, lng, p18=None, p373=None, p31='Q16970', desc=''):
    cl = {'P31': [{'mainsnak': {'datavalue': {'value': {'id': p31}}}}],
          'P625': [{'mainsnak': {'datavalue': {'value': {'latitude': lat, 'longitude': lng}}}}]}
    if p18: cl['P18'] = [{'mainsnak': {'datavalue': {'value': p18}}}]
    if p373: cl['P373'] = [{'mainsnak': {'datavalue': {'value': p373}}}]
    return {'labels': {'it': {'value': label}}, 'aliases': {}, 'descriptions': {'it': {'value': desc}}, 'claims': cl}

CASI = []
def caso(nome, x, E, atteso):
    f8.candidati = lambda x, E=E: list(E)
    f8.entita = lambda ids, E=E: E
    f8.file_della = lambda cat, x: 'Dalla categoria.jpg'
    x = dict(x); f8.cerca(x)
    ok = x.get('file') == atteso
    CASI.append(ok); print(('ok   ' if ok else 'ERRORE ') + nome, '->', x.get('file'), x.get('via', ''))

base = {'p': 'soragna-pr--rocca-meli-lupi', 'n': 'Rocca Meli Lupi', 'com': 'Soragna', 'clat': 44.926, 'clng': 10.122}
caso('elemento giusto con P18', base, {'Q1': ent('Rocca Meli Lupi', 44.927, 10.121, p18='Rocca Meli Lupi Soragna.jpg')}, 'Rocca Meli Lupi Soragna.jpg')
caso('omonimo lontano scartato', base, {'Q2': ent('Rocca Meli Lupi', 45.9, 11.9, p18='Altra.jpg')}, None)
caso('nome diverso scartato', base, {'Q3': ent('Castello di Torrechiara', 44.927, 10.121, p18='Torrechiara.jpg')}, None)
caso('persona scartata', base, {'Q4': ent('Meli Lupi', 44.927, 10.121, p18='Ritratto.jpg', p31='Q5')}, None)
caso('stemma scartato', base, {'Q5': ent('Rocca Meli Lupi', 44.927, 10.121, p18='Stemma Meli Lupi.svg')}, None)
caso('senza P18: dalla categoria P373', base, {'Q6': ent('Rocca Meli Lupi', 44.927, 10.121, p373='Rocca Meli Lupi (Soragna)')}, 'Dalla categoria.jpg')
vic = dict(base, lat=44.9265, lng=10.1215)
caso('coordinate del luogo: entro 1,5 km', vic, {'Q7': ent('Rocca Meli Lupi', 44.930, 10.125, p18='Vicina.jpg')}, 'Vicina.jpg')
caso('coordinate del luogo: a 5 km scartato', vic, {'Q8': ent('Rocca Meli Lupi', 44.97, 10.12, p18='Lontana.jpg')}, None)
print(f'{sum(CASI)} su {len(CASI)} casi giusti')
sys.exit(0 if all(CASI) else 1)
