"""Refine the existing report layout and repackage its native PBIX data model."""
from pathlib import Path
import ast, json, copy, zipfile, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'portfolio';P=OUT/'Beauty_Studio';R=P/'Beauty.Report';D=R/'definition';RES=R/'StaticResources/RegisteredResources'
BG='#F3EADF';PAPER='#FFFCF7';BROWN='#493126';DARK='#38251E';CARAMEL='#AA7953';BEIGE='#E8D6C1';SOFT='#D4B995';TEXT='#4D382D';MUTED='#8B7260';S=2
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def lit(v):return {'expr':{'Literal':{'Value':('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
def title(v,s):v['visual']['visualContainerObjects']['title'][0]['properties']['text']=lit(s)
def pos(v,x,y,w,h):v['position'].update(x=x,y=y,width=w,height=h)
def prop(t,c,m=False):return {('Measure' if m else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def projection(t,c,m=False):return {'field':prop(t,c,m),'queryRef':t+'.'+c,'nativeQueryRef':c}
def query(v,roles):v['visual']['query']={'queryState':{k:{'projections':[projection(*p) for p in ps]} for k,ps in roles.items()}}

backup=OUT/'before_home_layout.pbix'
if not backup.exists():shutil.copy2(P/'Beauty_Studio.pbix',backup)

# Reuse only the established drawing functions, with the requested beauty icon set.
source=(ROOT/'scripts/restyle_beauty.py').read_text(encoding='utf-8')
tree=ast.parse(source)
code='\n\n'.join(ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['font','make_background'])
code=code.replace(";txt(49,145,'CATALOG STUDIO',10,MUTED,'bold')",'')
code=code.replace("nav=[('overview','Catalog','grid'),('ingredients','Ingredients','leaf'),('quality','Data quality','check')]", "nav=[('overview','Home','jar'),('ingredients','Ingredients','dropper'),('quality','Data quality','mirror')]")
code=code.replace("elif kind=='grid':", """elif kind=='jar':
            r((5,15,35,36));r((4,10,36,16));l([(13,24),(27,24)]);l([(17,29),(23,29)])
        elif kind=='tube':
            l([(9,3),(31,3),(28,31),(12,31),(9,3)]);r((12,31,28,38));l([(11,8),(29,8)]);l([(16,19),(24,19)])
        elif kind=='mirror':
            r((8,2,32,27));l([(20,27),(20,38)]);l([(14,38),(26,38)]);l([(13,16),(18,21),(27,9)])
        elif kind=='grid':""")
code=code.replace("icon('leaf',79,623,37,CARAMEL)","icon('jar',79,623,37,CARAMEL)")
code=code.replace("icon('bottle',45,529,60,CARAMEL)","icon('tube',45,529,60,CARAMEL)")
code=code.replace("icon('tube',45,529,60,CARAMEL);icon('dropper',105,545,55,BROWN)\n    icon('jar',79,623,37,CARAMEL)","""# A cohesive cosmetic collection, drawn as editable product artwork.
    rect((46,529,169,680),'#E8D5BE',54)
    # Amber serum bottle and dropper.
    rect((55,561,103,647),'#BA8B5C',9, '#79533D',1.5)
    rect((61,541,97,568),'#4D382D',5)
    rect((71,524,87,546),'#4D382D',7)
    rect((63,584,95,624),'#FFF8ED',4)
    line([(72,600),(86,600)],'#AA7953',2)
    line([(79,593),(79,607)],'#AA7953',2)
    # Cream tube, with a gold seal and base.
    d.polygon([(111*S,562*S),(158*S,562*S),(152*S,638*S),(117*S,638*S)],fill='#FFFCF7',outline='#AA7953',width=2*S)
    line([(114,570),(156,570)],'#C5A27E',2)
    rect((118,636,151,650),'#8C6348',3)
    icon('leaf',124,587,23,CARAMEL)
    # Moisturizer jar in the foreground.
    rect((46,652,121,683),'#FFFCF7',8, '#B9916A',1.5)
    rect((43,644,124,656),'#B9916A',4)
    line([(67,667),(100,667)],'#D3B896',2)
    # Small botanical sprig ties the collection together.
    line([(159,547),(173,523)],'#AA7953',1.5)
    line([(165,537),(154,528),(166,530)],'#AA7953',1.5)
    line([(169,531),(179,529),(173,522)],'#AA7953',1.5)""")
code=code.replace("kinds=['bottle','sparkle','dropper','leaf']","kinds=['bottle','jar','dropper','tube']")
code=code.replace("if page=='overview':panels=[(248,266,1000,580),(1018,266,1568,580),(248,598,1000,835),(1018,598,1568,835)]", "if page=='overview':panels=[(248,266,900,552),(918,266,1568,552),(248,570,900,843),(918,570,1568,843)]")
code=code.replace("elif page=='ingredients':panels=[(248,266,900,735),(918,266,1568,735),(248,753,1568,843)]", "elif page=='ingredients':panels=[(248,266,900,610),(918,266,1568,610),(248,628,1568,843)]")
code=code.replace("line([(248,862),(1568,862)],'#DCC8B1',1)","""if page in ['overview','ingredients']:
        rect((982,18,1268,111),PAPER,13);rect((1282,18,1568,111),PAPER,13)
    line([(248,862),(1568,862)],'#DCC8B1',1)""")
exec(compile(code,'beauty_background_functions','exec'),globals())

all_visuals={}
for page in ['overview','ingredients','quality']:
    make_background(page)
    path=D/f'pages/{page}/page.json';pg=read(path)
    if page=='overview':pg['displayName']='01  Home'
    write(path,pg)
    visuals=[]
    for p in (D/f'pages/{page}/visuals').glob('*/visual.json'):
        v=read(p);kind=v['visual']['visualType']
        if kind=='textbox':
            runs=[r for q in v['visual']['objects']['general'][0]['properties']['paragraphs'] for r in q['textRuns']]
            text=''.join(r.get('value','') for r in runs)
            if text.startswith('BEAUTY  /') or text.startswith('PRODUCT &') or text.startswith('Catalog labels'):v['isHidden']=True
            elif text=='Catalog overview':
                for r in runs:r['value']='Home'
                pos(v,248,22,700,64)
            elif text in ['Ingredient explorer','Data quality']:pos(v,248,22,700,64)
            elif text.startswith('Supplied catalog'):
                pos(v,248,87,720,31)
                for run in runs:run['value']='Supplied catalog snapshot | Product-level exploration'
            elif text.startswith('Reach counts'):v['isHidden']=True
            elif text.startswith('Quality findings describe'):pos(v,248,833,1318,29)
        if kind=='slicer':
            i=sum(x['visual']['visualType']=='slicer' for x in visuals)
            pos(v,994 if i==0 else 1294,24,262,80)
            v['visual']['visualContainerObjects']['padding']=[{'properties':{k:lit(4) for k in ['top','bottom','left','right']}}]
            v['visual']['visualContainerObjects']['title'][0]['properties']['fontSize']=lit(12)
        if kind=='actionButton' and v['name']=='nav_overview':
            v['visual']['visualContainerObjects']['visualLink'][0]['properties']['tooltip']=lit('Open Home')
        visuals.append(v)
    all_visuals[page]=visuals

home=all_visuals['overview']
def uses_column(v,name):
    return any(p.get('nativeQueryRef')==name for role in v['visual'].get('query',{}).get('queryState',{}).values() for p in role.get('projections',[]))
brand=next(v for v in home if uses_column(v,'Top brand products'))
formula=next(v for v in home if uses_column(v,'Formula size'))
alcohol=next(v for v in home if uses_column(v,'Alcohol tag') and v['visual']['visualType']!='slicer')
home[:]=[v for v in home if v['name']!='formula_length_line']
pos(brand,264,278,620,260)
pos(formula,934,278,618,260)
formula['visual']['visualType']='columnChart';title(formula,'Formula size by fragrance tag')
query(formula,{'Category':[('Products','Formula size')],'Series':[('Products','Fragrance tag')],'Y':[('Products','Products',True)]})
formula['visual']['objects']['legend']=[{'properties':{'show':lit(True),'position':lit('Top'),'fontSize':lit(9),'labelColor':color(TEXT)}}]
formula['visual']['objects']['labels'][0]['properties']['show']=lit(False)
formula['visual']['objects'].pop('dataPoint',None)
formula['visual']['query']['sortDefinition']={'sort':[{'field':prop('Products','Formula size'),'direction':'Ascending'}],'isDefaultSort':True}

alcohol['visual']['visualType']='donutChart';pos(alcohol,934,582,618,245);title(alcohol,'Alcohol-free tag share')
query(alcohol,{'Category':[('Products','Alcohol tag')],'Y':[('Products','Products',True)]})
alcohol['visual']['objects']={'legend':[{'properties':{'show':lit(True),'position':lit('Right'),'fontSize':lit(10),'labelColor':color(TEXT)}}], 'labels':[{'properties':{'show':lit(True),'labelStyle':lit('Data value, percent of total'),'fontSize':lit(10),'color':color(TEXT),'labelDisplayUnits':lit(1)}}]}

line=copy.deepcopy(brand);line['name']='formula_length_line';line['position'].update(z=120,tabOrder=120);line['visual']['visualType']='lineChart';pos(line,264,582,620,245);title(line,'Products by ingredient count')
query(line,{'Category':[('Products','Ingredient count')],'Y':[('Products','Products',True)]})
line['visual']['query']['sortDefinition']={'sort':[{'field':prop('Products','Ingredient count'),'direction':'Ascending'}],'isDefaultSort':True}
line['visual']['objects']['labels'][0]['properties']['show']=lit(False)
line['visual']['objects']['categoryAxis'][0]['properties'].update(showAxisTitle=lit(True),axisTitle=lit('Ingredients per product'))
line['visual']['objects']['shapes']=[{'properties':{'showMarker':lit(True),'strokeWidth':lit(2),'markerSize':lit(4)}}]
home.append(line)

ing=all_visuals['ingredients'];ing[:]=[v for v in ing if v['name']!='source_rating_stack'];ibars=[v for v in ing if v['visual']['visualType']=='clusteredBarChart']
for i,v in enumerate(ibars):pos(v,264 if i==0 else 934,280,620 if i==0 else 618,315)
ratings=copy.deepcopy(brand);ratings['name']='source_rating_stack';ratings['position'].update(z=121,tabOrder=121);ratings['visual']['visualType']='clusteredBarChart';pos(ratings,264,641,1288,187);title(ratings,'Ingredient entries by source rating')
query(ratings,{'Category':[('Ingredient occurrences','Source rating')],'Y':[('Products','Ingredient entries',True)]})
ratings['visual']['query']['sortDefinition']={'sort':[{'field':prop('Products','Ingredient entries',True),'direction':'Descending'}],'isDefaultSort':True}
ratings['visual']['objects']['legend']=[{'properties':{'show':lit(False)}}]
ratings['visual']['objects']['labels'][0]['properties'].update(show=lit(True),labelPrecision=lit(0),labelDisplayUnits=lit(1),fontSize=lit(11))
ratings['visual']['objects']['dataPoint']=[{'properties':{'defaultColor':color(CARAMEL)}}]
ratings['visual']['objects']['categoryAxis'][0]['properties']['fontSize']=lit(11)
ing.append(ratings)
for page,visuals in all_visuals.items():
    for v in visuals:write(D/f'pages/{page}/visuals/{v["name"]}/visual.json',v)
meta=read(D/'pages/pages.json');meta['activePageName']='overview';write(D/'pages/pages.json',meta)
report=read(D/'report.json')
for package in report['resourcePackages']:
    for item in package['items']:
        if item['type']=='CustomTheme':item['path']='BeautyTheme.json'
write(D/'report.json',report)

# Integer percentage display only; preserve underlying numeric precision.
model_path=P/'Beauty.SemanticModel/model.bim';model=read(model_path)
percent_measures=set()
for table in model['model']['tables']:
    for measure in table.get('measures',[]):
        if '%' in measure.get('formatString',''):
            measure['formatString']='0%';percent_measures.add(measure['name'])
write(model_path,model)
for p in (D/'pages').rglob('visual.json'):
    v=read(p);config=v['visual']
    if config['visualType']=='card' and any(uses_column(v,n) for n in percent_measures):
        config['objects']['labels'][0]['properties']['labelPrecision']=lit(0)
    if config['visualType']=='donutChart':
        for labels in config['objects'].get('labels',[]):labels['properties'].update(labelPrecision=lit(0),percentageLabelPrecision=lit(0))
    # Explicit category colors survive a Desktop save/reopen even if theme resources change.
    if config['visualType'] in ['columnChart','donutChart']:
        field='Fragrance tag' if config['visualType']=='columnChart' else 'Alcohol tag'
        values=['Not tagged fragrance / essential oil-free','Tagged fragrance / essential oil-free'] if field=='Fragrance tag' else ['Not tagged alcohol-free','Tagged alcohol-free']
        config['objects']['dataPoint']=[]
        for value,hex_color in zip(values,['#C59C72','#6C4733']):
            scope={'Comparison':{'ComparisonKind':0,'Left':prop('Products',field),'Right':{'Literal':{'Value':"'"+value+"'"}}}}
            config['objects']['dataPoint'].append({'properties':{'fill':color(hex_color)},'selector':{'data':[{'scopeId':scope}]}})
    write(p,v)

print('Updated the PBIP: Home layout, top slicers, beauty icons, bar/line/donut/stacked charts. Save PBIX through Power BI Desktop.')
