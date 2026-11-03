"""Measure local preview; does not sign in to or publish to Blogger."""
import argparse, json, os
from pathlib import Path

def run(root):
    from playwright.sync_api import sync_playwright
    root=Path(root).resolve()
    project=json.loads((root/'project.json').read_text(encoding='utf-8'))
    papers=json.loads((root/'papers.json').read_text(encoding='utf-8'))
    cards=json.loads((root/'cards.json').read_text(encoding='utf-8'))
    output=root/'screenshots';output.mkdir(exist_ok=True)
    errors=[];rows=[]
    with sync_playwright() as p:
        candidates=[Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Google/Chrome/Application/chrome.exe',Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')]
        exe=next((x for x in candidates if x.is_file()),None)
        browser=p.chromium.launch(executable_path=str(exe)) if exe else p.chromium.launch()
        try:
            for width in [1120,768,390,360]:
                page=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto((root/'Blogger_完整預覽.html').as_uri(),wait_until='load')
                row=page.evaluate('''() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,columns:getComputedStyle(document.querySelector('.at-grid')).gridTemplateColumns.split(' ').length,cards:document.querySelectorAll('.at-card').length,references:document.querySelectorAll('.at-ref').length,overflow:[...document.querySelectorAll('.at-blog *')].filter(e=>e.getBoundingClientRect().width>0 && (e.getBoundingClientRect().right>innerWidth+1 || e.getBoundingClientRect().left < -1)).map(e=>e.tagName+'.'+e.className)})''')
                page.screenshot(path=str(output/f'preview-{width}.png'))
                link=page.locator('a[href^="#at-ref-"]').first
                expected=link.get_attribute('href');link.click()
                row['citation_navigation']=page.evaluate('location.hash')==expected
                row['pass']=row['scrollWidth']<=width and not row['overflow'] and row['cards']==len(cards) and row['references']==len(papers) and row['columns']==(1 if width<=620 else 3) and row['citation_navigation']
                rows.append(row);page.close()
        finally:browser.close()
    report={'results':rows,'errors':errors,'all_pass':all(r['pass'] for r in rows) and not errors,'scope':'Local Chromium preview only; no live Blogger theme or publication tested.'}
    (root/'browser-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--project',required=True,type=Path)
    args=parser.parse_args();report=run(args.project)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(not report['all_pass'])
