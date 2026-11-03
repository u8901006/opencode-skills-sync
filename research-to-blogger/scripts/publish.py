"""Offline evidence-aware Blogger publisher. Python standard library only."""
import argparse, calendar, csv, datetime as dt, hashlib, html, json, re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parents[1]
COLORS={'green','purple','slate','pink'}
FIELDS=('id','title','authors','journal','first_published','issue_year','category','read_level','design','population','findings','limitations','implications','access_note')
def esc(s):return html.escape(str(s),quote=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def local(root,name):
    p=(root/name).resolve()
    require(not Path(name).is_absolute() and p.is_relative_to(root.resolve()),'Unsafe fulltext path: '+name)
    return p
def interval(value):
    require(bool(re.fullmatch(r'\d{4}(-\d{2})?(-\d{2})?',value)),'Invalid first_published date precision')
    parts=list(map(int,value.split('-')))
    y=parts[0];m=parts[1] if len(parts)>1 else 1;d=parts[2] if len(parts)>2 else 1
    start=dt.date(y,m,d)
    end=start if len(parts)==3 else dt.date(y,m,calendar.monthrange(y,m)[1]) if len(parts)==2 else dt.date(y,12,31)
    return start,end

class Document(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.tags=[];self.text=[];self.unsafe=[];self.cards=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags.append(tag)
        if a.get('id'):self.ids.append(a['id'])
        if a.get('href'):self.links.append(a['href'])
        if 'at-card' in a.get('class','').split():self.cards+=1
        if tag in {'script','iframe','style','html','head','body','form','input','object','embed','img','link','meta','base','svg','math'}:self.unsafe.append(tag)
        for k,v in attrs:
            if k.lower().startswith('on') or k in {'style','src','srcdoc'}:self.unsafe.append(k)
    def handle_data(self,data):self.text.append(data)
    def handle_endtag(self,tag):
        if tag in {'p','li','h2','h3','section'}:self.text.append('\n\n')

def valid_url(value):
    u=urlsplit(value)
    return u.scheme=='https' and bool(u.netloc) and not u.username and not u.password

def source_hashes(root):
    return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['project.json','papers.json','cards.json','article.html']}

def inspect_fulltext(root,paper,name):
    p=local(root,name);require(p.is_file(),'Missing fulltext: '+name)
    raw=p.read_bytes();suffix=p.suffix.lower()
    require(len(raw)>100,'Empty fulltext: '+name)
    if suffix=='.xml':
        try:t=ET.fromstring(raw)
        except ET.ParseError as e:raise ValueError('Invalid fulltext XML: '+name) from e
        for node in t.iter():
            if isinstance(node.tag,str):node.tag=node.tag.rsplit('}',1)[-1]
        body=t.find('body')
        require(t.tag=='article' and body is not None and len(''.join(body.itertext()).strip())>100,'Not fulltext article XML: '+name)
        dois=[''.join(e.itertext()).strip().lower() for e in t.findall('.//article-meta/article-id[@pub-id-type="doi"]')]
        require(not paper.get('doi') or paper['doi'].lower() in dois,'fulltext DOI mismatch: '+name)
    elif suffix=='.pdf':require(raw.startswith(b'%PDF-'),'Invalid fulltext PDF signature: '+name)
    elif suffix in {'.html','.htm','.txt'}:
        s=raw.decode('utf-8')
        if suffix!='.txt':
            d=Document();d.feed(s);plain=' '.join(d.text)
            require(('article' in d.tags or 'main' in d.tags) and len(plain)>2000,'Not fulltext HTML: '+name)
        else:plain=s;require(len(s)>2000,'Not fulltext TXT: '+name)
        require(not paper.get('doi') or paper['doi'].lower() in s.lower(),'fulltext DOI not present: '+name)
    else:raise ValueError('Unsupported fulltext format: '+name)
    return {'id':paper['id'],'file':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'source_url':paper['source_url'],'license':paper['license'],'retrieved_on':paper['retrieved_on'],'version':paper['fulltext_version']}

def validate(root):
    root=Path(root).resolve()
    project=json.loads((root/'project.json').read_text(encoding='utf-8'))
    papers=json.loads((root/'papers.json').read_text(encoding='utf-8'))
    cards=json.loads((root/'cards.json').read_text(encoding='utf-8'))
    article=(root/'article.html').read_text(encoding='utf-8')
    for key in ['title','subtitle','start_date','end_date','as_of','categories','method_note']:require(bool(project.get(key)),'Missing project field: '+key)
    start,end,asof=[dt.date.fromisoformat(project[k]) for k in ['start_date','end_date','as_of']]
    require(start<=end<=asof,'Date range must end on or before as_of')
    categories={}
    for c in project['categories']:
        require(bool(re.fullmatch('[a-z0-9]+(-[a-z0-9]+)*',c['id'])),'Invalid category ID')
        require(c['id'] not in categories and c['color'] in COLORS and c['label'],'Duplicate/invalid category')
        categories[c['id']]=c
    require(isinstance(papers,list) and papers,'No verified research supplied')
    seen=set();dois=set();manifest=[]
    for p in papers:
        for k in FIELDS:require(bool(p.get(k)),f'{p.get("id","paper")}: missing {k}')
        require(bool(re.fullmatch(r'R\d{2,}',p['id'])) and p['id'] not in seen,'Invalid/duplicate reference ID')
        seen.add(p['id'])
        doi=p.get('doi','')
        require(not doi or bool(re.fullmatch(r'10\.\d{4,9}/\S+',doi)),'Invalid DOI')
        require(not doi or doi.lower() not in dois,'Duplicate DOI')
        if doi:dois.add(doi.lower())
        require(bool(doi) or valid_url(p.get('source_url','')),'DOI or verified HTTPS source_url required')
        lo,hi=interval(p['first_published'])
        require(start<=lo and hi<=end,'first_published outside range or ambiguous boundary: '+p['id'])
        require(p['category'] in categories,'Unknown paper category')
        require(p['read_level'] in {'abstract','fulltext'},'Invalid read_level')
        files=p.get('fulltext',[])
        require(isinstance(files,list),'fulltext must be a list')
        require((p['read_level']=='fulltext')==bool(files),'read_level and fulltext files disagree: '+p['id'])
        if files:
            require(bool(p.get('license')) and valid_url(p.get('source_url','')),'Fulltext license and HTTPS source_url required')
            require(bool(p.get('retrieved_on')) and bool(p.get('fulltext_version')),'Fulltext retrieved_on and fulltext_version required')
            require(dt.date.fromisoformat(p['retrieved_on'])<=asof,'Fulltext acquisition is later than as_of')
            manifest.extend(inspect_fulltext(root,p,f) for f in files)
    require(isinstance(cards,list) and cards,'No evidence cards supplied')
    cited=set()
    for c in cards:
        for k in ['title','category','study','takeaway','description','refs']:require(bool(c.get(k)),'Missing card field: '+k)
        require(c['category'] in categories,'Unknown card category')
        require(isinstance(c['refs'],list),'Card refs must be a list')
        for rid in c['refs']:require(rid in seen,'Unknown card reference: '+rid);cited.add(rid)
    doc=Document();doc.feed(article)
    require(not doc.unsafe,'Unsafe article HTML: '+', '.join(doc.unsafe))
    require(len(doc.ids)==len(set(doc.ids)),'Duplicate article IDs')
    require(all(x.startswith('at-') and not x.startswith('at-ref-') for x in doc.ids),'Article IDs must use at- prefix, not reserved at-ref-')
    destinations=set(doc.ids)|{'at-ref-'+rid for rid in seen}
    for link in doc.links:
        require((link.startswith('#') and link[1:] in destinations) or valid_url(link),'Unresolved or unsafe article link: '+link)
        if link.startswith('#at-ref-'):cited.add(link[8:])
    require(cited==seen,'Uncited references: '+', '.join(sorted(seen-cited)))
    return project,papers,cards,article,categories,manifest

def build(root,overwrite=False):
    root=Path(root).resolve()
    config,papers,cards,article,categories,manifest=validate(root)
    result={'references':len(papers),'fulltext_articles':sum(bool(p.get('fulltext')) for p in papers),'cards':len(cards),'structural_validation':'passed','scientific_validation':'requires human source review','browser_validation':'not performed by this command'}
    result['summary_only_articles']=result['references']-result['fulltext_articles']
    result['source_sha256']=source_hashes(root)
    legend=''.join(f'<span><i class="at-swatch at-{c["color"]}" aria-hidden="true"></i>{esc(c["label"])}</span>' for c in categories.values())
    hero=f'<article class="at-blog" lang="zh-Hant"><header class="at-hero"><div><p class="at-kicker"><span class="at-save">保存版</span>英文研究 × 中文解讀</p><h2 class="at-title">{esc(config["title"])}</h2><p class="at-subtitle">{esc(config["subtitle"])}</p><p class="at-date">{esc(config["start_date"])} – {esc(config["end_date"])}｜整理日 {esc(config["as_of"])}</p></div><div class="at-legend">{legend}</div></header>'
    card_html=[]
    for n,c in enumerate(cards,1):
        cat=categories[c['category']];links=' '.join(f'<a href="#at-ref-{rid}">[{rid}]</a>' for rid in c['refs'])
        card_html.append(f'<section class="at-card"><div class="at-card-head at-{cat["color"]}"><span class="at-num">{n}</span><h3 class="at-card-title">{esc(c["title"])}<span class="at-category">{esc(cat["label"])}</span></h3></div><div class="at-card-body"><div class="at-study">{esc(c["study"])}</div><p class="at-takeaway">{esc(c["takeaway"])}</p><p class="at-desc">{esc(c["description"])}</p><div class="at-card-refs">來源 {links}</div></div></section>')
    bibliography=[];summary_files={};bib=[]
    for p in papers:
        rid=p['id'];url='https://doi.org/'+p['doi'] if p.get('doi') else p['source_url']
        status='已讀全文' if p['read_level']=='fulltext' else '僅摘要；未取得全文'
        bibliography.append(f'<li class="at-ref" id="at-ref-{rid}"><span class="at-ref-id">{rid} · {esc(p["issue_year"])}</span><p class="at-ref-title">{esc(p["title"])}</p><p class="at-ref-meta">{esc(p["authors"])}. <em>{esc(p["journal"])}</em>. 首次出版 {esc(p["first_published"])}.</p><p class="at-ref-meta"><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">原文來源</a>｜{status}｜{esc(p["design"])}</p><p class="at-ref-meta">{esc(p["access_note"])}</p></li>')
        s=f'# {rid}｜{p["title"]}\n\n作者：{p["authors"]}\n\n期刊：{p["journal"]}\n\n首次出版：{p["first_published"]}；卷期年：{p["issue_year"]}\n\n來源：{url}\n\n讀取層級：{status}\n\n全文狀態：{p["access_note"]}\n\n書目附註：{p.get("metadata_note", "無")}\n\n'
        for field,title in [('design','研究設計'),('population','對象與測量'),('findings','中文摘要與主要發現'),('limitations','限制與不能推論之處'),('implications','與本主題的關係')]:s+='## '+title+'\n\n'+p[field]+'\n\n'
        s+='## 本地全文與授權\n\n'+('\n'.join('- ['+Path(f).name+'](../'+f+')' for f in p.get('fulltext',[])) or '未取得全文；僅摘要與書目。')+'\n\n'+p.get('license','依原出版者授權。')+'\n'
        if p.get('abstract_en'):s+='\n## 英文來源摘要（非完整論文）\n\n'+p['abstract_en']+'\n'
        summary_files[f'summaries/{rid}_中文摘要.md']=s
        clean=lambda x:str(x).replace('\\',' ').replace('{','(').replace('}',')')
        fields={'title':p['title'],'author':p['authors'].replace('; ',' and '),'journal':p['journal'],'year':p['issue_year'],'doi':p.get('doi',''),'url':url}
        bib.append('@article{'+rid+',\n'+',\n'.join('  '+k+' = {'+clean(v)+'}' for k,v in fields.items() if v)+'\n}')
    note=f'<aside class="at-info"><strong>研究快覽，不是個人診斷或療效保證。</strong><br>{esc(config["method_note"])}<br>{len(papers)} 篇選定文獻；{result["fulltext_articles"]} 篇已保存且讀取全文；{result["summary_only_articles"]} 篇僅摘要。各篇依據與限制見下文。</aside>'
    css=(BASE/'templates/styles.css').read_text(encoding='utf-8')
    fragment='<style>\n'+css+'\n</style>\n'+hero+'<div class="at-grid">'+''.join(card_html)+'</div>'+note+'<section class="at-copy">'+article+'</section><section class="at-references"><h2>參考文獻與來源</h2><ol class="at-ref-list">'+''.join(bibliography)+'</ol></section><footer class="at-end">資料截止 '+esc(config['as_of'])+'｜僅為研究整理，不替代專業評估。全文不隨網頁公開轉載。</footer></article>'
    preview='<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(config['title'])+'</title></head><body style="margin:0;background:#e7eef4">'+fragment+'</body></html>'
    doc=Document();doc.feed(fragment)
    require(len(doc.ids)==len(set(doc.ids)),'Duplicate generated IDs')
    require(all(x[1:] in doc.ids for x in doc.links if x.startswith('#')),'Unresolved generated citation')
    contents={'Blogger_貼上版.html':fragment,'Blogger_完整預覽.html':preview,**summary_files,'fulltext/manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2),'verification.json':json.dumps(result,ensure_ascii=False,indent=2),'references.bib':'\n\n'.join(bib)+'\n'}
    contents['00_研究摘要總覽.md']='# '+config['title']+'｜中文研究摘要\n\n'+'\n\n---\n\n'.join(x.replace('../fulltext/','fulltext/') for x in summary_files.values())
    md=Document();md.feed(article)
    contents['02_研究文章.md']='# '+config['title']+'\n\n'+re.sub(r'\n{3,}','\n\n',''.join(md.text))+'\n\n參考文獻見 01_文獻清單.csv；此文字版由 HTML 擷取，引用跳轉請看網頁。\n'
    items=[]
    for p in papers:
        links=' · '.join('<a href="'+esc(f)+'">'+esc(Path(f).name)+'</a>' for f in p.get('fulltext',[])) or '未取得全文'
        items.append(f'<li><a href="summaries/{p["id"]}_中文摘要.md">{p["id"]}｜{esc(p["title"])}</a><br>{links}</li>')
    contents['index.html']='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>研究資料入口</title><body style="max-width:1000px;margin:30px auto;padding:18px;font:17px/1.8 system-ui;color:#18354e;background:#eff5f9;overflow-wrap:anywhere"><h1>'+esc(config['title'])+'</h1><p><a href="Blogger_完整預覽.html">網頁預覽</a> · <a href="README.md">使用說明</a> · <a href="00_研究摘要總覽.md">摘要總覽</a></p><p>全文個人研究存檔，勿將此入口或全文資料夾直接公開。</p><ol>'+''.join(items)+'</ol></body></html>'
    contents['README.md']=f'''# {config['title']}

## 開始閱讀
- `index.html`：本地資料入口。
- `Blogger_完整預覽.html`：獨立網頁；桌面三欄、手機單欄。
- `Blogger_貼上版.html`：用文字編輯器複製原始碼，貼入 Blogger 文章的 HTML 檢視，預覽後再自行發布。
- `00_研究摘要總覽.md`、`summaries/`：繁體中文摘要。
- `01_文獻清單.csv`、`references.bib`：書目。

範圍 {config['start_date']} 至 {config['end_date']}。文獻 {len(papers)} 篇，已讀及保存全文 {result['fulltext_articles']} 篇，僅摘要 {result['summary_only_articles']} 篇。全文格式請見各篇；XML／HTML／TXT 不等於出版 PDF。

{config['method_note']}

工具檢查不是研究真實性或品質保證，須核對原文；`verification.json` 只有資料與結構檢查。瀏覽器實測見另外產生的 `browser-verification.json`；未產生即未完成該項驗證。未在真實 Blogger 主題測試或發布。

若 Blogger 移除內嵌 style，將 skill 的 `templates/styles.css` 放入 Blogger 主題自訂 CSS，文章保留 article 部分。全文保留原授權，僅個人研究保存；勿隨 Blogger 整包上傳或公開散布格式轉換閱讀檔。檢索與全文缺口另見 `03_檢索與全文取得紀錄.md`（由研究者建立，不由生成工具捏造）。
'''
    from io import StringIO
    csvout=StringIO(newline='');writer=csv.writer(csvout)
    writer.writerow([*FIELDS,'doi','source_url','fulltext','license'])
    for p in papers:writer.writerow([p.get(k,'') for k in FIELDS]+[p.get('doi',''),p.get('source_url',''),' | '.join(p.get('fulltext',[])),p.get('license','')])
    contents['01_文獻清單.csv']='\ufeff'+csvout.getvalue()
    conflicts=[name for name in contents if (root/name).exists()]
    if conflicts and not overwrite:raise FileExistsError('Generated files already exist; back up and explicitly use --overwrite-generated: '+', '.join(conflicts))
    for name,text in contents.items():
        target=local(root,name);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
    return result

def check_outputs(root):
    root=Path(root).resolve();config,papers,cards,article,categories,manifest=validate(root)
    saved_result=json.loads((root/'verification.json').read_text(encoding='utf-8'))
    require(saved_result.get('source_sha256')==source_hashes(root),'Generated output is stale: source inputs changed')
    frag=(root/'Blogger_貼上版.html').read_text(encoding='utf-8')
    d=Document();d.feed(frag)
    require(not any(t in d.tags for t in ['html','head','body','script','iframe']),'Unsafe Blogger wrapper/script')
    require(len(set(d.ids))==len(d.ids),'Duplicate output IDs')
    require(d.cards==len(cards),'Generated card count mismatch')
    require(all(x[1:] in d.ids for x in d.links if x.startswith('#')),'Unresolved output anchor')
    require(all(x.startswith('#') or valid_url(x) for x in d.links),'Local or unsafe public output URL')
    require(set(d.ids)==set(re.findall(r'\bid="([^"]+)"',frag)),'HTML ID parser inconsistency')
    require(all('at-ref-'+p['id'] in d.ids for p in papers),'Missing reference section')
    saved=json.loads((root/'fulltext/manifest.json').read_text(encoding='utf-8'))
    require(saved==manifest,'Fulltext content or manifest changed')
    for p in papers:require((root/'summaries'/f'{p["id"]}_中文摘要.md').is_file(),'Missing Chinese summary')
    return {'status':'passed','references':len(papers),'fulltext_articles':sum(bool(p.get('fulltext')) for p in papers),'cards':len(cards)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--overwrite-generated',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    print(json.dumps(check_outputs(args.project) if args.check else build(args.project,args.overwrite_generated),ensure_ascii=False,indent=2))
