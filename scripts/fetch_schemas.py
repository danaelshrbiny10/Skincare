import json, pathlib, urllib.request, urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent/'schemas'
BASE='https://raw.githubusercontent.com/microsoft/json-schemas/main/'
seen=set()
def fetch(path):
    path=path.split('#')[0]
    if not path or path in seen:return
    seen.add(path)
    dest=ROOT/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): s=json.loads(dest.read_text())
    else:
        data=urllib.request.urlopen(BASE+path,timeout=30).read()
        dest.write_bytes(data); s=json.loads(data)
    def walk(x):
        if isinstance(x,dict):
            r=x.get('$ref','')
            if r and not r.startswith('#') and not r.startswith('http'):
                fetch(urllib.parse.urljoin(path,r))
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(s)
for p in ['visualContainer/2.1.0/schema.json','visualConfiguration/2.1.0/schema-embedded.json','page/1.0.0/schema.json','pagesMetadata/1.0.0/schema.json','report/1.0.0/schema.json']:
    fetch('fabric/item/report/definition/'+p)
print('Downloaded',len(seen),'Microsoft schemas')
