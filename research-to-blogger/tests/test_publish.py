"""Offline regression tests. No user project or network is touched."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]

class InstallationTests(unittest.TestCase):
    def test_reusable_publisher_exists(self):
        self.assertTrue((BASE/'scripts/publish.py').is_file(), 'Reusable publisher has not been implemented yet')

class PublishTests(unittest.TestCase):
    def setUp(self):
        if not (BASE/'scripts/publish.py').exists():self.skipTest('Publisher absent; installation contract fails separately')
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        spec=importlib.util.spec_from_file_location('research_publish',BASE/'scripts/publish.py')
        self.m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.project={'title':'照顧者與創作','subtitle':'關聯不等於因果','start_date':'2022-01-01','end_date':'2026-10-21','as_of':'2026-10-21','categories':[{'id':'direct','label':'直接研究','color':'green'}],'method_note':'敘述性整理；不是系統性回顧。'}
        self.paper={'id':'R01','title':'A caregiver study','authors':'Researcher, A.','journal':'Example Journal','doi':'10.1234/example','first_published':'2026-01-01','issue_year':'2026','category':'direct','read_level':'abstract','design':'質性研究','population':'8 名照顧者','findings':'受訪者描述創作經驗。','limitations':'不能推論療效。','implications':'保留自主。','fulltext':[],'access_note':'未取得全文；僅摘要。'}
        self.paper.update(license='CC BY 4.0',source_url='https://example.org/article',retrieved_on='2026-10-21',fulltext_version='publisher XML')
        self.cards=[{'title':'相關不是因果','category':'direct','study':'2026｜質性研究','takeaway':'不推論療效','description':'樣本小。','refs':['R01']}]

    def prepare(self,papers=None):
        for name,data in [('project.json',self.project),('papers.json',papers or [self.paper]),('cards.json',self.cards)]:
            (self.root/name).write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        (self.root/'article.html').write_text('<h2>先說結論</h2><p>相關不是因果。<a href="#at-ref-R01">[R01]</a></p>',encoding='utf-8')

    def test_dynamic_counts_and_scoped_fragment(self):
        self.prepare()
        result=self.m.build(self.root)
        page=(self.root/'Blogger_貼上版.html').read_text(encoding='utf-8')
        self.assertEqual(result['references'],1)
        self.assertEqual(result['fulltext_articles'],0)
        self.assertEqual(result['cards'],1)
        self.assertNotIn('18 篇',page)
        self.assertNotIn('<body',page)
        self.assertNotIn('<script',page)
        self.assertIn('at-ref-R01',page)
        self.assertTrue((self.root/'summaries/R01_中文摘要.md').exists())

    def test_first_publication_excludes_older_online_date(self):
        self.paper['first_published']='2021-11-01'
        self.paper['issue_year']='2022'
        self.prepare()
        with self.assertRaisesRegex(ValueError,'first_published'):self.m.build(self.root)

    def test_abstract_does_not_count_as_fulltext(self):
        self.paper['fulltext']=['fulltext/paper.xml']
        self.prepare()
        with self.assertRaisesRegex(ValueError,'read_level'):self.m.build(self.root)

    def test_login_page_rejected_even_with_xml_extension(self):
        self.paper['read_level']='fulltext';self.paper['fulltext']=['fulltext/paper.xml']
        (self.root/'fulltext').mkdir()
        (self.root/'fulltext/paper.xml').write_text('<html><body>Sign in</body></html>',encoding='utf-8')
        self.prepare()
        with self.assertRaisesRegex(ValueError,'fulltext'):self.m.build(self.root)

    def test_genuine_xml_is_counted_and_hashed(self):
        self.paper['read_level']='fulltext';self.paper['fulltext']=['fulltext/paper.xml']
        self.paper['license']='CC BY 4.0';self.paper['source_url']='https://example.org/article'
        (self.root/'fulltext').mkdir()
        (self.root/'fulltext/paper.xml').write_text('<article><front><article-meta><article-id pub-id-type="doi">10.1234/example</article-id></article-meta></front><body><sec><title>Results</title><p>'+('Research findings. '*150)+'</p></sec></body></article>',encoding='utf-8')
        self.prepare();result=self.m.build(self.root)
        self.assertEqual(result['fulltext_articles'],1)
        manifest=json.loads((self.root/'fulltext/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest),1)
        self.assertEqual(len(manifest[0]['sha256']),64)
        self.assertEqual(manifest[0]['retrieved_on'],'2026-10-21')
        self.assertEqual(manifest[0]['version'],'publisher XML')

    def test_missing_reference_prevents_generation(self):
        self.cards[0]['refs']=['R99'];self.prepare()
        with self.assertRaisesRegex(ValueError,'R99'):self.m.build(self.root)
        self.assertFalse((self.root/'Blogger_貼上版.html').exists())

    def test_duplicate_doi_is_rejected(self):
        second=dict(self.paper,id='R02');self.prepare([self.paper,second])
        with self.assertRaisesRegex(ValueError,'DOI'):self.m.build(self.root)

    def test_source_html_script_is_rejected(self):
        self.prepare()
        (self.root/'article.html').write_text('<script>alert(1)</script><p>Hello</p>',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'script'):self.m.build(self.root)

    def test_path_traversal_is_rejected(self):
        self.paper['read_level']='fulltext';self.paper['fulltext']=['../outside.xml'];self.prepare()
        with self.assertRaisesRegex(ValueError,'path'):self.m.build(self.root)

    def test_existing_generated_file_needs_explicit_flag(self):
        self.prepare();self.m.build(self.root)
        with self.assertRaises(FileExistsError):self.m.build(self.root)
        self.m.build(self.root,overwrite=True)

    def test_partial_date_preserves_precision(self):
        self.paper['first_published']='2025-02';self.prepare()
        self.assertEqual(self.m.build(self.root)['references'],1)

    def test_no_doi_uses_verified_source_url(self):
        self.paper['doi']='';self.prepare();self.m.build(self.root)
        page=(self.root/'Blogger_貼上版.html').read_text(encoding='utf-8')
        self.assertIn('https://example.org/article',page)

    def test_output_check_detects_stale_data(self):
        self.prepare();self.m.build(self.root)
        self.assertEqual(self.m.check_outputs(self.root)['status'],'passed')
        p=self.root/'Blogger_貼上版.html'
        p.write_text(p.read_text(encoding='utf-8').replace('id="at-ref-R01"','id="wrong"'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'anchor|reference'):self.m.check_outputs(self.root)

    def test_output_check_detects_new_findings_after_build(self):
        self.prepare();self.m.build(self.root)
        data=json.loads((self.root/'papers.json').read_text(encoding='utf-8'))
        data[0]['findings']='An updated interpretation not present in generated summaries.'
        (self.root/'papers.json').write_text(json.dumps(data),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'stale|changed'):self.m.check_outputs(self.root)

    def test_namespaced_article_xml_is_accepted(self):
        self.paper['read_level']='fulltext';self.paper['fulltext']=['fulltext/paper.xml']
        (self.root/'fulltext').mkdir()
        (self.root/'fulltext/paper.xml').write_text('<article xmlns="urn:test:jats"><front><article-meta><article-id pub-id-type="doi">10.1234/example</article-id></article-meta></front><body><p>'+('Findings. '*30)+'</p></body></article>',encoding='utf-8')
        self.prepare();self.assertEqual(self.m.build(self.root)['fulltext_articles'],1)

if __name__=='__main__':unittest.main()
