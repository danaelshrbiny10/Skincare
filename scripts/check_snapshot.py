from pathlib import Path
import json,base64,zlib,re
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'portfolio/PowerBI/Beauty.SemanticModel/model.bim').read_text(encoding='utf-8'))
tables={}
for t in m['model']['tables']:
    s=t['partitions'][0]['source']['expression'][1]
    payload=s.split('FromText("')[1].split('"')[0]
    rows=json.loads(zlib.decompress(base64.b64decode(payload),-15))
    tables[t['name']]=rows
    print(t['name'],len(rows))
assert len(tables['Products'])==1000
assert len(tables['Ingredient occurrences'])==17442
product_ids={r['Product ID'] for r in tables['Products']}
ingredient_ids={r['Ingredient ID'] for r in tables['Ingredients']}
assert len(product_ids)==len(tables['Products'])
assert len(ingredient_ids)==len(tables['Ingredients'])
for r in tables['Ingredient occurrences']:
    assert r['Product ID'] in product_ids and r['Ingredient ID'] in ingredient_ids
assert all(r['Product ID'] in product_ids for r in tables['Product functions'])
print('Embedded snapshots and foreign keys reconciled successfully')
