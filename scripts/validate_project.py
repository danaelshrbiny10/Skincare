from pathlib import Path
import json, jsonschema, sys
ROOT=Path(__file__).resolve().parents[1]
schemas=ROOT/'scripts/schemas'
def validate(path):
    data=json.loads(path.read_text(encoding='utf-8'))
    url=data.get('$schema')
    if not url:return
    local=schemas/url.split('json-schemas/')[1]
    schema=json.loads(local.read_text())
    store={}
    for p in schemas.rglob('*.json'):
        s=json.loads(p.read_text()); store['https://developer.microsoft.com/json-schemas/'+p.relative_to(schemas).as_posix()]=s
    resolver=jsonschema.RefResolver(base_uri=url,referrer=schema,store=store)
    errors=list(jsonschema.Draft7Validator(schema,resolver=resolver).iter_errors(data))
    for e in errors: print(path.relative_to(ROOT),list(e.absolute_path),e.message)
    return len(errors)
project=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'portfolio/Beauty_Studio'
files=list((project/'Beauty.Report/definition').rglob('*.json'))
n=sum(validate(p) or 0 for p in files)
print(f'{len(files)} report definition files checked; {n} schema errors')
assert n==0
