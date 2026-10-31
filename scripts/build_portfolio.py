"""Reproducible cleaning and Power BI portfolio project. Standard library only."""
from pathlib import Path
import json, csv, collections, unicodedata, re, hashlib, zlib, base64, uuid

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'portfolio'; CLEAN=OUT/'cleaned'; PROJECT=OUT/'PowerBI'
for p in [CLEAN,PROJECT]:p.mkdir(parents=True,exist_ok=True)
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def text(v):
    if v is None:return None
    v=unicodedata.normalize('NFC',str(v))
    return re.sub(r'\s+',' ',re.sub('[\u200b\u200c\u200d\ufeff]','',v)).strip()
rawpath=ROOT/'Data/beauty_data.jsonl'
raw=[json.loads(l) for l in rawpath.read_text(encoding='utf-8-sig').splitlines() if l.strip()]
assert len({r['id'] for r in raw})==len(raw),'Conflicting source IDs require review'
brand_lookup={}; ingredient_lookup={}; ingredients=[]; products=[]; occurrences=[]; functions=[]; issues=[]
names=collections.Counter((text(r['brand']).casefold(),text(r['name']).casefold()) for r in raw)
changed=0; repeated_ingredients=0
for r in raw:
    b=text(r['brand']); b=brand_lookup.setdefault(b.casefold(),b)
    tags=set(r['tags']); duplicate=names[(b.casefold(),text(r['name']).casefold())]>1
    p={'Product ID':r['id'],'Brand':b,'Product':text(r['name']),'Description':text(r['description']),
       'Ingredient count':len(r['ingredients']),'Alcohol tag':'Tagged alcohol-free' if 'alcohol-free' in tags else 'Not tagged alcohol-free',
       'Fragrance tag':'Tagged fragrance / essential oil-free' if 'fragrance & essentialoil-free' in tags else 'Not tagged fragrance / essential oil-free',
       'Known active tag':'Tagged known active amount' if 'knownamountofactive' in tags else 'Not tagged known active amount',
       'Name review':'Review repeated name' if duplicate else 'Unique brand / product name',
       'Image available':'Available' if (ROOT/'images'/r['image_name']).is_file() else 'Missing',
       'Formula size':'01 | 1–10 ingredients' if len(r['ingredients'])<=10 else '02 | 11–20 ingredients' if len(r['ingredients'])<=20 else '03 | 21–30 ingredients' if len(r['ingredients'])<=30 else '04 | 31+ ingredients'}
    products.append(p)
    if duplicate:issues.append({'Product ID':r['id'],'Issue':'Repeated brand / product name','Action':'Retained; compare formulas before merging'})
    fs=set(); used=set()
    for pos,i in enumerate(r['ingredients'],1):
        n=text(i['name']); changed+=int(n!=i['name']); key=n.casefold()
        if key not in ingredient_lookup:
            ingredient_lookup[key]=len(ingredients)+1
            ingredients.append({'Ingredient ID':ingredient_lookup[key],'Ingredient':n})
        iid=ingredient_lookup[key]
        repeated_ingredients+=int(iid in used);used.add(iid)
        c=i.get('concentration')
        if c is not None and (not isinstance(c,(int,float)) or not 0<=c<=100):
            issues.append({'Product ID':r['id'],'Issue':f'Invalid concentration at position {pos}','Action':'Numeric concentration left blank; original retained in raw source'}); c=None
        occurrences.append({'Product ID':r['id'],'Ingredient ID':iid,'Position':pos,
            'Source rating':text(i.get('rating')) or 'Unrated','Concentration':c,
            'Irritancy source':text(i.get('irritancy')),'Comedogenicity source':text(i.get('comedogenicity'))})
        fs.update(text(f) for f in i.get('functions',[]) if text(f))
    functions.extend({'Product ID':r['id'],'Function':f} for f in sorted(fs))

tables={'Products':products,'Ingredients':ingredients,'Ingredient occurrences':occurrences,'Product functions':functions}
quality=[{'Check':'Source product IDs','Result':'Pass','Count':len(products),'Detail':'All product IDs are unique; one row per source product'},
 {'Check':'Repeated brand / product names','Result':'Review','Count':sum(p['Name review']=='Review repeated name' for p in products),'Detail':'Retained as separate records; names alone do not establish duplicate formulas'},
 {'Check':'Ingredient names normalized','Result':'Cleaned','Count':changed,'Detail':'Unicode NFC; invisible characters removed; repeated whitespace collapsed'},
 {'Check':'Unrated ingredient entries','Result':'Missing metadata','Count':sum(o['Source rating']=='Unrated' for o in occurrences),'Detail':'Missing source ratings preserved as Unrated; no safety score imputed'},
 {'Check':'Concentrations not supplied','Result':'Missing metadata','Count':sum(o['Concentration'] is None for o in occurrences),'Detail':'Unknown concentration remains null, never zero'},
 {'Check':'Images unavailable locally','Result':'Coverage','Count':sum(p['Image available']=='Missing' for p in products),'Detail':'Image availability verified against images folder'},
 {'Check':'Repeated ingredients within formulas','Result':'Review','Count':repeated_ingredients,'Detail':'Occurrences retained by source position; product reach uses distinct product IDs'}]
tables['Quality checks']=quality
for name,rows in tables.items():
    with (CLEAN/(name.replace(' ','_').lower()+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with (CLEAN/'review_queue.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=['Product ID','Issue','Action']);w.writeheader();w.writerows(issues)
audit={'source':'Data/beauty_data.jsonl','source_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),
 'raw_products':len(raw),'clean_products':len(products),'brands':len(brand_lookup),'ingredient_entries':len(occurrences),
 'unique_ingredient_names':len(ingredients),'name_pair_review_groups':sum(v>1 for v in names.values()),'checks':quality,
 'rules':['Original JSONL and empty CSV are unchanged','Do not merge product names or ingredient aliases without evidence',
          'Tags describe supplied catalog labels; absent tag is not evidence of ingredient presence',
          'Source ingredient ratings are annotations, not clinical evidence or product safety scores',
          'No date, price, sales, review score or clinical outcome exists in this dataset']}
write(OUT/'cleaning_audit.json',audit)

# Portable imported semantic model: cleaned snapshots are compressed into Power Query M.
modeldir=PROJECT/'Beauty.SemanticModel'; reportdir=PROJECT/'Beauty.Report'
write(PROJECT/'Beauty.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'Beauty.Report'}}],'settings':{'enableAutoRecovery':True}})
write(modeldir/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}})
write(reportdir/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Beauty.SemanticModel'}}})
measures={
 'Products':('COUNTROWS(Products)','#,0'),
 'Brands':('DISTINCTCOUNT(Products[Brand])','#,0'),
 'Avg ingredients':('AVERAGE(Products[Ingredient count])','0.0'),
 'Alcohol-free tagged %':('DIVIDE(CALCULATE([Products], KEEPFILTERS(Products[Alcohol tag] = "Tagged alcohol-free")), [Products])','0.0%'),
 'Fragrance-free tagged %':('DIVIDE(CALCULATE([Products], KEEPFILTERS(Products[Fragrance tag] = "Tagged fragrance / essential oil-free")), [Products])','0.0%'),
 'Ingredient entries':("COUNTROWS('Ingredient occurrences')",'#,0'),
 'Ingredient product reach':("DISTINCTCOUNT('Ingredient occurrences'[Product ID])",'#,0'),
 'Distinct ingredients':("DISTINCTCOUNT('Ingredient occurrences'[Ingredient ID])",'#,0'),
 'Function product reach':("DISTINCTCOUNT('Product functions'[Product ID])",'#,0'),
 'Rated entries %':("DIVIDE(CALCULATE([Ingredient entries], KEEPFILTERS('Ingredient occurrences'[Source rating] <> \"Unrated\")), [Ingredient entries])",'0.0%'),
 'Name review records':('CALCULATE([Products], KEEPFILTERS(Products[Name review] = "Review repeated name"))','#,0'),
 'Image coverage %':('DIVIDE(CALCULATE([Products], KEEPFILTERS(Products[Image available] = "Available")),[Products])','0.0%'),
 'Top brand products':('IF(RANKX(ALLSELECTED(Products[Brand]), [Products], , DESC, DENSE) <= 10, [Products])','#,0'),
 'Top ingredient reach':('IF(RANKX(ALLSELECTED(Ingredients[Ingredient]), [Ingredient product reach], , DESC, DENSE) <= 12, [Ingredient product reach])','#,0'),
 'Top function reach':('IF(RANKX(ALLSELECTED(\'Product functions\'[Function]), [Function product reach], , DESC, DENSE) <= 10, [Function product reach])','#,0')}
modeltables=[]
for name,rows in tables.items():
    cols=[]; types=[]
    for k in rows[0]:
        vals=[r[k] for r in rows if r[k] is not None]
        typ='int64' if vals and all(isinstance(v,int) for v in vals) else 'double' if vals and all(isinstance(v,(int,float)) for v in vals) else 'string'
        cols.append({'name':k,'dataType':typ,'sourceColumn':k,'summarizeBy':'none'})
        types.append('{"'+k+'", '+('Int64.Type' if typ=='int64' else 'type number' if typ=='double' else 'type text')+'}')
    payload=base64.b64encode(zlib.compress(json.dumps(rows,ensure_ascii=False).encode())).decode()
    m=['let',f'    Source = Json.Document(Binary.Decompress(Binary.FromText("{payload}", BinaryEncoding.Base64), Compression.Deflate)),',
       '    Records = Table.FromRecords(Source),','    Typed = Table.TransformColumnTypes(Records, {'+', '.join(types)+'}, "en-US")','in','    Typed']
    # Power Query Compression.Deflate expects raw RFC1951 data rather than zlib wrapper.
    compressor=zlib.compressobj(wbits=-15); payload=base64.b64encode(compressor.compress(json.dumps(rows,ensure_ascii=False).encode())+compressor.flush()).decode()
    m[1]=f'    Source = Json.Document(Binary.Decompress(Binary.FromText("{payload}", BinaryEncoding.Base64), Compression.Deflate)),'
    t={'name':name,'columns':cols,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':m}}]}
    if name=='Products':t['measures']=[{'name':n,'expression':e,'formatString':fmt} for n,(e,fmt) in measures.items()]
    modeltables.append(t)
rels=[]
for a,b,ac,bc in [('Ingredient occurrences','Products','Product ID','Product ID'),('Ingredient occurrences','Ingredients','Ingredient ID','Ingredient ID'),('Product functions','Products','Product ID','Product ID')]:
    rels.append({'name':str(uuid.uuid5(uuid.NAMESPACE_DNS,a+b)),'fromTable':a,'fromColumn':ac,'toTable':b,'toColumn':bc,'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'})
write(modeldir/'model.bim',{'compatibilityLevel':1600,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-US','tables':modeltables,'relationships':rels,'annotations':[{'name':'PBI_ProTooling','value':'["DevMode"]'}]}})

SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
DEF=reportdir/'definition'
write(DEF/'version.json',{'$schema':SCHEMA+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
BG='#F4EDE3'; BROWN='#493123'; INK='#33251E'; ACCENT='#A8764E'; MUTED='#796554'; WHITE='#FFFCF7'
theme={'name':'Beauty | Sand & Espresso','dataColors':[BROWN,ACCENT,'#C6A17B','#8B6952','#DCC8AD','#A59B78','#BA8C73','#6D5848'],'background':BG,'foreground':INK,'tableAccent':ACCENT,
 'textClasses':{'callout':{'fontFace':'Segoe UI Semibold','color':BROWN,'fontSize':32},'title':{'fontFace':'Segoe UI Semibold','color':INK,'fontSize':13},'label':{'fontFace':'Segoe UI','color':MUTED,'fontSize':10}},
 'visualStyles':{'*':{'*':{'background':[{'show':True,'color':{'solid':{'color':WHITE}},'transparency':0}],'visualHeader':[{'show':False}],'border':[{'show':False}],'title':[{'fontColor':{'solid':{'color':INK}},'fontSize':13,'fontFamily':'Segoe UI Semibold'}]}}}}
write(OUT/'Sand_Espresso_theme.json',theme)
write(reportdir/'StaticResources/RegisteredResources/BeautyTheme.json',theme)
write(DEF/'report.json',{'$schema':SCHEMA+'report/1.0.0/schema.json','themeCollection':{'baseTheme':{'name':'CY24SU10','reportVersionAtImport':'5.59','type':'SharedResources'},'customTheme':{'name':'BeautyTheme','reportVersionAtImport':'5.59','type':'RegisteredResources'}},'layoutOptimization':'None','resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'BeautyTheme','path':'BeautyTheme.json','type':'CustomTheme'}]}],'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','defaultDrillFilterOtherVisuals':True}})
def lit(v):return {'expr':{'Literal':{'Value':('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
def prop(t,n,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':n}}
def projection(t,n,measure=False):return {'field':prop(t,n,measure),'queryRef':t+'.'+n,'nativeQueryRef':n}
counter=0
def visual(page,kind,title,x,y,w,h,roles=None,objects=None,subtitle=None):
    global counter;counter+=1;name=f'v{counter:03}'
    v={'visualType':kind,'visualContainerObjects':{
        'title':[{'properties':{'show':lit(bool(title)),'text':lit(title),'fontColor':color(INK),'fontSize':lit(13),'fontFamily':lit('Segoe UI Semibold')}}],
        'background':[{'properties':{'show':lit(True),'color':color(WHITE),'transparency':lit(0)}}],
        'border':[{'properties':{'show':lit(False),'radius':lit(12)}}],
        'visualHeader':[{'properties':{'show':lit(False)}}]}}
    if roles:v['query']={'queryState':{r:{'projections':[projection(*p) for p in ps]} for r,ps in roles.items()}}
    if objects:v['objects']=objects
    if subtitle:v['visualContainerObjects']['subTitle']=[{'properties':{'show':lit(True),'text':lit(subtitle),'fontSize':lit(9),'fontColor':color(MUTED)}}]
    d={'$schema':SCHEMA+'visualContainer/2.1.0/schema.json','name':name,'position':{'x':x,'y':y,'z':counter,'height':h,'width':w,'tabOrder':counter},'visual':v}
    write(DEF/f'pages/{page}/visuals/{name}/visual.json',d)
    return d
def textbox(page,txt,x,y,w,h,size=16,fg=INK,bg=BG):
    d=visual(page,'textbox','',x,y,w,h+14,objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':txt,'textStyle':{'fontFamily':'Segoe UI Semibold' if size>=20 else 'Segoe UI','fontSize':f'{size}pt','color':fg}}]}]}}]})
    d['visual']['visualContainerObjects']['padding']=[{'properties':{k:lit(0) for k in ['top','bottom','left','right']}}]
    d['visual']['visualContainerObjects']['background'][0]['properties']['color']=color(bg)
    write(DEF/f'pages/{page}/visuals/{d["name"]}/visual.json',d)
def card(page,m,title,x):
    return visual(page,'card',title,x,148,350,118,{'Values':[('Products',m,True)]},{'labels':[{'properties':{'color':color(BROWN),'fontSize':lit(32),'labelDisplayUnits':lit(1)}}],'categoryLabels':[{'properties':{'show':lit(False)}}]})
barstyle={'labels':[{'properties':{'show':lit(True),'color':color(INK),'fontSize':lit(10),'labelDisplayUnits':lit(1),'labelPrecision':lit(0)}}],
 'categoryAxis':[{'properties':{'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(10)}}],
 'valueAxis':[{'properties':{'showAxisTitle':lit(False),'start':lit(0),'labelColor':color(MUTED),'fontSize':lit(9)}}],
 'dataPoint':[{'properties':{'defaultColor':color(ACCENT)}}],'legend':[{'properties':{'show':lit(False)}}]}
def bar(page,title,table,category,measure,x,y,w,h):
    d=visual(page,'clusteredBarChart',title,x,y,w,h,{'Category':[(table,category,False)],'Y':[('Products',measure,True)]},barstyle)
    d['visual']['query']['sortDefinition']={'sort':[{'field':prop('Products',measure,True),'direction':'Descending'}],'isDefaultSort':True}
    write(DEF/f'pages/{page}/visuals/{d["name"]}/visual.json',d)
pages=[('overview','01  Catalog overview'),('ingredients','02  Ingredient explorer'),('quality','03  Data quality')]
write(DEF/'pages/pages.json',{'$schema':SCHEMA+'pagesMetadata/1.0.0/schema.json','pageOrder':[p for p,_ in pages],'activePageName':'overview'})
for page,title in pages:
    write(DEF/f'pages/{page}/page.json',{'$schema':SCHEMA+'page/1.0.0/schema.json','name':page,'displayName':title,'displayOption':'FitToPage','width':1520,'height':950,'objects':{'background':[{'properties':{'color':color(BG),'transparency':lit(0)}}]}})
    textbox(page,'BEAUTY  /  CATALOG INTELLIGENCE',32,20,1000,28,11,MUTED)
    textbox(page,title[4:],32,51,1100,64,32,BROWN)
    textbox(page,'PRODUCT & FORMULATION PORTFOLIO',1130,24,358,28,10,MUTED)
    textbox(page,'Supplied catalog snapshot  •  Product-level exploration',32,112,1050,25,11,MUTED)
    textbox(page,'Catalog labels and source annotations only. No sales, dates, prices or clinical outcomes are supplied.',32,908,1456,28,10,MUTED)

for m,t,x in [('Products','Products in catalog',32),('Brands','Brands represented',400),('Avg ingredients','Average ingredients / product',768),('Fragrance-free tagged %','Fragrance / oil-free tagged',1136)]:card('overview',m,t,x)
bar('overview','Brands by product count · top 10 ranks','Products','Brand','Top brand products',32,286,720,330)
bar('overview','Formula size distribution','Products','Formula size','Products',768,286,720,330)
bar('overview','Alcohol-free catalog tags','Products','Alcohol tag','Products',32,636,720,230)
visual('overview','slicer','Explore a brand',768,636,350,230,{'Values':[('Products','Brand',False)]},{'data':[{'properties':{'mode':lit('Dropdown')}}]})
visual('overview','slicer','Fragrance / oil-free tag',1136,636,352,230,{'Values':[('Products','Fragrance tag',False)]},{'data':[{'properties':{'mode':lit('Dropdown')}}]})
for m,t,x in [('Distinct ingredients','Distinct ingredient names',32),('Ingredient entries','Ingredient entries',400),('Rated entries %','Entries with source rating',768),('Products','Products in selection',1136)]:card('ingredients',m,t,x)
bar('ingredients','Most common ingredients · top 12 ranks','Ingredients','Ingredient','Top ingredient reach',32,286,720,480)
bar('ingredients','Ingredient functions · top 10 ranks','Product functions','Function','Top function reach',768,286,720,480)
visual('ingredients','slicer','Brand',32,788,475,100,{'Values':[('Products','Brand',False)]},{'data':[{'properties':{'mode':lit('Dropdown')}}]})
visual('ingredients','slicer','Ingredient name',524,788,475,100,{'Values':[('Ingredients','Ingredient',False)]},{'data':[{'properties':{'mode':lit('Dropdown')}}]})
textbox('ingredients','Reach counts distinct products. Ingredient selection filters ingredient reach; function reach follows the brand selection.',1016,788,472,100,11,MUTED,WHITE)
for m,t,x in [('Products','Product IDs retained',32),('Name review records','Repeated-name records to review',400),('Image coverage %','Local image coverage',768),('Rated entries %','Source rating coverage',1136)]:card('quality',m,t,x)
visual('quality','tableEx','Quality findings',32,286,1456,300,{'Values':[('Quality checks',n,False) for n in ['Check','Result','Count','Detail']]},{'grid':[{'properties':{'gridVertical':lit(False),'gridHorizontal':lit(True),'rowPadding':lit(8)}}],'columnHeaders':[{'properties':{'fontColor':color(BROWN),'backColor':color('#E7D7C3'),'fontSize':lit(11)}}],'values':[{'properties':{'fontColorPrimary':color(INK),'fontSize':lit(10)}}]})
visual('quality','tableEx','Product review & catalog detail',32,606,1456,280,{'Values':[('Products',n,False) for n in ['Brand','Product','Ingredient count','Name review','Image available']]},{'grid':[{'properties':{'rowPadding':lit(5)}}],'values':[{'properties':{'fontSize':lit(10)}}]})
textbox('quality','Quality findings describe the full snapshot. Product cards and catalog detail respond to visual selections.',32,879,1456,25,10,MUTED)

write(OUT/'project_metrics.json',{'products':len(products),'brands':len(brand_lookup),'ingredients':len(ingredients),'ingredient_entries':len(occurrences),'alcohol_tagged_pct':sum(p['Alcohol tag']=='Tagged alcohol-free' for p in products)/len(products),'fragrance_tagged_pct':sum(p['Fragrance tag']=='Tagged fragrance / essential oil-free' for p in products)/len(products)})
assert len(products)==1000 and len(occurrences)==17442
assert all(o['Product ID'] in {p['Product ID'] for p in products} for o in occurrences)
assert sum(collections.Counter(p['Brand'] for p in products).values())==len(products)
print(json.dumps(audit,ensure_ascii=True,indent=2))
print('Built',counter,'visuals across',len(pages),'pages')
