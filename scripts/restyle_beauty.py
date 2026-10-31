"""Apply the requested beauty editorial styling without changing analytical bindings."""
from pathlib import Path
import json, shutil, zipfile, urllib.parse, zlib, base64
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'portfolio'; P=OUT/'PowerBI'
R=P/'Beauty.Report'; D=R/'definition'; RES=R/'StaticResources/RegisteredResources'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def lit(v):return {'expr':{'Literal':{'Value':('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
BG='#F3EADF'; PAPER='#FFFCF7'; BROWN='#493126'; DARK='#38251E'; CARAMEL='#AA7953'; BEIGE='#E8D6C1'; SOFT='#D4B995'; TEXT='#4D382D'; MUTED='#8B7260'
backup=OUT/'before_beauty_restyle.zip'
if not backup.exists():
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for f in P.rglob('*'):
            if f.is_file():z.write(f,f.relative_to(OUT))

# Hand-drawn code-native icons and decorative panels; no metrics are baked into backgrounds.
S=2
def font(size,kind='regular'):
    name={'regular':'segoeui.ttf','bold':'seguisb.ttf','italic':'georgiai.ttf'}[kind]
    return ImageFont.truetype('C:/Windows/Fonts/'+name,int(size*S))
def make_background(page):
    im=Image.new('RGB',(1600*S,900*S),BG);d=ImageDraw.Draw(im)
    def rect(box,fill,r=0,outline=None,width=1):
        box=tuple(int(v*S) for v in box)
        if r:d.rounded_rectangle(box,int(r*S),fill,outline,width=int(width*S))
        else:d.rectangle(box,fill,outline,width=int(width*S))
    def line(points,fill=BROWN,width=2):d.line([(int(x*S),int(y*S)) for x,y in points],fill,width=int(width*S),joint='curve')
    def txt(x,y,s,size=14,fill=TEXT,kind='regular'):d.text((int(x*S),int(y*S)),s,font=font(size,kind),fill=fill)
    def icon(kind,x,y,size=30,ink=BROWN):
        scale=size/40
        def l(pts,w=2):line([(x+a*scale,y+b*scale) for a,b in pts],ink,w)
        def r(box):rect(tuple((x+v*scale if k%2==0 else y+v*scale) for k,v in enumerate(box)),None,4*scale,ink,2)
        if kind=='bottle':
            r((9,13,31,38));l([(15,13),(15,6),(25,6),(25,13)]);l([(20,6),(20,2),(32,2),(32,6)]);l([(14,24),(26,24)]);l([(20,19),(20,29)])
        elif kind=='dropper':
            r((10,18,30,38));l([(15,18),(15,10),(25,10),(25,18)]);r((15,1,25,10));l([(20,23),(16,29),(20,32),(24,29),(20,23)])
        elif kind=='leaf':
            l([(6,35),(28,10)]);l([(11,29),(7,17),(12,6),(32,3),(34,21),(24,30),(11,29)]);l([(18,22),(16,11)]);l([(22,17),(29,18)])
        elif kind=='grid':
            for a,b in [(4,4),(23,4),(4,23),(23,23)]:r((a,b,a+13,b+13))
        elif kind=='check':l([(7,5),(33,5),(33,35),(7,35),(7,5)]);l([(12,21),(18,27),(29,13)])
        elif kind=='sparkle':
            l([(20,2),(24,15),(37,20),(24,24),(20,38),(16,24),(3,20),(16,15),(20,2)]);l([(33,0),(33,8)]);l([(29,4),(37,4)])
    rect((0,0,216,900),PAPER)
    rect((216,0,217,900),'#E5D6C7')
    icon('dropper',79,37,48)
    txt(43,101,'beauty',35,BROWN,'italic');txt(49,145,'CATALOG STUDIO',10,MUTED,'bold')
    line([(29,189),(187,189)],BEIGE,1)
    nav=[('overview','Catalog','grid'),('ingredients','Ingredients','leaf'),('quality','Data quality','check')]
    for idx,(key,label,ic) in enumerate(nav):
        y=225+idx*66
        if key==page:rect((18,y,198,y+51),BEIGE,12);rect((18,y+12,22,y+39),CARAMEL,2)
        icon(ic,35,y+13,24,BROWN if key==page else MUTED)
        txt(73,y+15,label,15,BROWN if key==page else MUTED,'bold' if key==page else 'regular')
    txt(31,464,'THE BEAUTY EDIT',10,MUTED,'bold')
    # Beauty silhouettes and a botanical accent in the navigation rail.
    rect((28,498,188,704),'#F3E8DA',18)
    icon('bottle',45,529,60,CARAMEL);icon('dropper',105,545,55,BROWN)
    icon('leaf',79,623,37,CARAMEL)
    txt(40,733,'Ingredients.',16,BROWN,'italic');txt(40,759,'Brands. Discovery.',15,BROWN,'italic')
    txt(30,852,'SKINCARE / 01—03',10,MUTED)
    # KPI panels with separate icon lanes and accent caps.
    kinds=['bottle','sparkle','dropper','leaf']
    for i,x in enumerate([248,582,916,1250]):
        rect((x,133,x+318,250),'#E7D9C9',14)
        rect((x,130,x+318,246),PAPER,14)
        rect((x+12,130,x+306,134),CARAMEL if i%2==0 else BROWN,2)
        rect((x+17,153,x+65,201),'#F0E4D6',12);icon(kinds[i],x+26,161,30)
        line([(x+16,218),(x+302,218)],'#E8D9CA',1)
        txt(x+18,224,['CATALOG SNAPSHOT','PRODUCT EXPLORATION','FORMULATION PROFILE','SOURCE COVERAGE'][i],8,MUTED,'bold')
    if page=='overview':panels=[(248,266,1000,580),(1018,266,1568,580),(248,598,1000,835),(1018,598,1568,835)]
    elif page=='ingredients':panels=[(248,266,900,735),(918,266,1568,735),(248,753,1568,843)]
    else:panels=[(248,266,1568,521),(248,539,1568,843)]
    for box in panels:rect((box[0],box[1]+3,box[2],box[3]+3),'#E7DACB',16);rect(box,PAPER,16)
    line([(248,862),(1568,862)],'#DCC8B1',1)
    path=RES/f'Beauty_{page}.png';im.resize((1600,900),Image.Resampling.LANCZOS).save(path)
    # Standalone design asset for inspection and reuse.
    shutil.copy2(path,OUT/f'beauty_{page}_canvas.png')
    return path.name

def setpos(v,x,y,w,h):v['position'].update(x=x,y=y,width=w,height=h)
def add_visual(page,name,kind,x,y,w,h,objects=None,container=None,roles=None):
    v={'visualType':kind,'visualContainerObjects':{'background':[{'properties':{'show':lit(False)}}],'title':[{'properties':{'show':lit(False)}}],'visualHeader':[{'properties':{'show':lit(False)}}]}}
    if objects:v['objects']=objects
    if container:v['visualContainerObjects'].update(container)
    if roles:v['query']={'queryState':{k:{'projections':ps} for k,ps in roles.items()}}
    data={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.1.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':100,'tabOrder':100},'visual':v}
    write(D/f'pages/{page}/visuals/{name}/visual.json',data)
def proj(table,col):return {'field':{'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':col}},'queryRef':table+'.'+col,'nativeQueryRef':col}

report=read(D/'report.json')
pkg=next(p for p in report['resourcePackages'] if p['name']=='RegisteredResources')
pkg['items']=[i for i in pkg['items'] if not i['name'].startswith('Beauty_')]
for page in ['overview','ingredients','quality']:
    image=make_background(page);pkg['items'].append({'name':image,'path':image,'type':'Image'})
    p=D/f'pages/{page}/page.json';pg=read(p);pg.update(width=1600,height=900,displayOption='FitToPage')
    pg['objects']['background']=[{'properties':{'color':color(BG),'transparency':lit(0),'image':{'image':{'name':lit(image),'url':{'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':image}}},'scaling':lit('Fit')}}}}]
    write(p,pg)
    paths=list((D/f'pages/{page}/visuals').glob('*/visual.json'))
    card_index=0;bar_index=0;slicer_index=0;table_index=0
    for path in paths:
        data=read(path);v=data['visual'];kind=v['visualType'];c=v.setdefault('visualContainerObjects',{})
        c['background']=[{'properties':{'show':lit(False),'transparency':lit(100)}}]
        c['border']=[{'properties':{'show':lit(False)}}]
        c['padding']=[{'properties':{k:lit(10) for k in ['top','bottom','left','right']}}]
        title=c.get('title',[{'properties':{}}])[0]['properties']
        title.update(fontFamily=lit('Georgia'),italic=lit(True),fontSize=lit(15),fontColor=color(BROWN),bold=lit(False))
        if kind=='textbox':
            paras=v['objects']['general'][0]['properties']['paragraphs'];s=''.join(run.get('value','') for para in paras for run in para.get('textRuns',[]))
            if s in ['Catalog overview','Ingredient explorer','Data quality']:
                setpos(data,248,34,1120,72)
                for para in paras:
                    for run in para['textRuns']:run['textStyle'].update(fontFamily='Georgia',fontSize='30pt',fontStyle='italic',color=BROWN)
            elif s.startswith('BEAUTY  /'):setpos(data,248,11,900,26)
            elif s.startswith('PRODUCT &'):setpos(data,1250,48,318,34)
            elif s.startswith('Supplied catalog'):setpos(data,248,99,1280,30)
            elif s.startswith('Catalog labels'):setpos(data,248,866,1318,32)
            elif s.startswith('Reach counts'):setpos(data,1100,760,452,74)
            elif s.startswith('Quality findings describe'):setpos(data,900,867,650,30)
            for para in paras:
                for run in para['textRuns']:
                    run['textStyle']['color']=BROWN if s in ['Catalog overview','Ingredient explorer','Data quality'] else MUTED
            c['padding']=[{'properties':{k:lit(0) for k in ['top','bottom','left','right']}}]
        elif kind=='card':
            x=[248,582,916,1250][card_index];card_index+=1
            setpos(data,x+76,144,226,70)
            title.update(fontFamily=lit('Segoe UI'),italic=lit(False),fontSize=lit(11),fontColor=color(MUTED))
            c['padding']=[{'properties':{k:lit(0) for k in ['top','bottom','left','right']}}]
            v['objects']['labels'][0]['properties'].update(color=color(BROWN),fontSize=lit(28),fontFamily=lit('Segoe UI Semibold'))
        elif kind=='clusteredBarChart':
            positions={'overview':[(264,280,720,286),(1034,280,518,286),(264,610,720,208)],'ingredients':[(264,280,620,439),(934,280,618,439)]}
            setpos(data,*positions[page][bar_index]);bar_index+=1
            o=v['objects'];o['dataPoint'][0]['properties']['defaultColor']=color(CARAMEL if bar_index%2 else '#79533D')
            o['labels'][0]['properties'].update(color=color(TEXT),fontSize=lit(10))
            o['categoryAxis'][0]['properties'].update(labelColor=color(TEXT),fontSize=lit(10))
            o['valueAxis'][0]['properties'].update(labelColor=color(MUTED),gridlineColor=color('#E8DBCD'))
        elif kind=='slicer':
            positions={'overview':[(1034,615,246,194),(1294,615,258,194)],'ingredients':[(264,762,402,72),(686,762,394,72)]}
            setpos(data,*positions[page][slicer_index]);slicer_index+=1
            v.setdefault('objects',{})['header']=[{'properties':{'show':lit(False)}}]
            v['objects']['items']=[{'properties':{'fontColor':color(TEXT),'textSize':lit(11)}}]
        elif kind=='tableEx':
            setpos(data,264,280 if table_index==0 else 553,1288,228 if table_index==0 else 274)
            table_index+=1
            o=v.setdefault('objects',{});o['columnHeaders']=[{'properties':{'fontColor':color(BROWN),'backColor':color('#EFE2D2'),'fontSize':lit(11)}}]
            o['values']=[{'properties':{'fontColorPrimary':color(TEXT),'backColorPrimary':color(PAPER),'fontSize':lit(10)}}]
            o['grid']=[{'properties':{'gridVertical':lit(False),'gridHorizontal':lit(True),'rowPadding':lit(6),'imageHeight':lit(27)}}]
            if table_index==2:
                ps=v['query']['queryState']['Values']['projections']
                if not any(x['queryRef']=='Products.Product icon' for x in ps):ps.insert(0,proj('Products','Product icon'))
        write(path,data)
    for idx,key in enumerate(['overview','ingredients','quality']):
        add_visual(page,'nav_'+key,'actionButton',18,225+idx*66,180,51,
            objects={'icon':[{'properties':{'show':lit(False)}}],'text':[{'properties':{'show':lit(False)}}],'fill':[{'properties':{'show':lit(False)}}],'outline':[{'properties':{'show':lit(False)}}]},
            container={'visualLink':[{'properties':{'show':lit(True),'type':lit('PageNavigation'),'navigationSection':lit(key),'tooltip':lit('Open '+key)}}]})
write(D/'report.json',report)

theme=read(OUT/'Sand_Espresso_theme.json')
theme.update(background=BG,foreground=TEXT,tableAccent=CARAMEL,dataColors=[BROWN,CARAMEL,'#C5A27E','#886B54','#DCC5AA','#B5906C','#E8D6C1','#6E4C38'])
theme['textClasses']['title'].update(fontFace='Georgia',color=BROWN)
for path in [OUT/'Sand_Espresso_theme.json',RES/'BeautyTheme.json',RES/'BeautyTheme']:
    if path.exists():write(path,theme)

# A beauty bottle glyph in every product detail row, purely decorative.
svg='<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40"><rect x="1" y="1" width="38" height="38" rx="9" fill="#EFE2D2"/><g fill="none" stroke="#79533D" stroke-width="1.8" stroke-linejoin="round"><rect x="12" y="15" width="16" height="21" rx="3"/><path d="M16 15V9h8v6M20 9V4h11v4M16 24h8M20 20v8"/></g></svg>'
modelpath=P/'Beauty.SemanticModel/model.bim';model=read(modelpath)
pt=next(t for t in model['model']['tables'] if t['name']=='Products')
pt['columns']=[c for c in pt['columns'] if c['name']!='Product icon']
pt['columns'].append({'name':'Product icon','dataType':'string','sourceColumn':'Product icon','dataCategory':'ImageUrl','summarizeBy':'none','description':'Decorative skincare bottle glyph; does not classify or rate products.'})
source=pt['partitions'][0]['source']; payload=source['expression'][1].split('FromText("')[1].split('"')[0]
rows=json.loads(zlib.decompress(base64.b64decode(payload),-15))
for row in rows:row['Product icon']='data:image/svg+xml;utf8,'+urllib.parse.quote(svg,safe='')
comp=zlib.compressobj(wbits=-15); payload=base64.b64encode(comp.compress(json.dumps(rows,ensure_ascii=False).encode())+comp.flush()).decode()
source['expression'][1]=f'    Source = Json.Document(Binary.Decompress(Binary.FromText("{payload}", BinaryEncoding.Base64), Compression.Deflate)),'
if 'Product icon' not in source['expression'][3]:source['expression'][3]=source['expression'][3].replace('}, "en-US")',', {"Product icon", type text}}, "en-US")')
write(modelpath,model)
(OUT/'beauty_icon.svg').write_text(svg,encoding='utf-8')
print('Restyled three pages, added nine navigation buttons and product icons. Original project backed up.')
