import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Element:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.text = ''

    def descendants(self, tag):
        for child in self.children:
            if child.tag == tag:
                yield child
            yield from child.descendants(tag)

    def content(self):
        return ' '.join([self.text, *(child.content() for child in self.children)])


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.root = Element('document', [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs)
        self.stack[-1].children.append(element)
        if tag not in self.VOID:
            self.stack.append(element)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].text += data

    def section(self, section_id):
        return next((s for s in self.root.descendants('section') if s.attrs.get('id') == section_id), None)


class UsefulContentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Document()
        cls.page.feed((ROOT / 'index.html').read_text(encoding='utf-8'))

    def test_preparation_and_responsible_choice_have_practical_advice(self):
        preparation = self.page.section('preparation')
        choice = self.page.section('choice')
        self.assertIsNotNone(preparation, 'Добавьте подготовку к появлению собаки')
        self.assertIsNotNone(choice, 'Добавьте рекомендации по выбору и документам')
        text = preparation.content().lower()
        for word in ('безопас', 'ветеринар', 'время'):
            self.assertIn(word, text)
        text = choice.content().lower()
        for word in ('услови', 'документ', 'здоров', 'договор'):
            self.assertIn(word, text)

    def test_catalog_marks_preliminary_offers_and_illustrative_photos(self):
        catalog = self.page.section('listings')
        self.assertIsNotNone(catalog, 'Добавьте пустой каталог объявлений')
        self.assertIn('предваритель', catalog.content().lower())
        self.assertIn('иллюстрируют породы', catalog.content().lower())
        self.assertEqual(list(catalog.descendants('form')), [])
        self.assertEqual(len(list(catalog.descendants('article'))), 4)

    def test_faq_uses_native_accessible_details_with_answers(self):
        faq = self.page.section('faq')
        self.assertIsNotNone(faq, 'Добавьте FAQ')
        details = list(faq.descendants('details'))
        self.assertGreaterEqual(len(details), 4)
        for item in details:
            self.assertEqual(item.children[0].tag, 'summary')
            self.assertTrue(item.children[0].content().strip())
            self.assertTrue(any(child.tag != 'summary' and child.content().strip() for child in item.children))

    def test_about_explains_missing_seller_information_and_contacts(self):
        about = self.page.section('about')
        self.assertIsNotNone(about)
        text = about.content().lower()
        self.assertIn('продавц', text)
        self.assertIn('контакт', text)
        self.assertIn('не предоставлен', text)

    def test_new_sections_have_accessible_headings_and_real_anchor_targets(self):
        for name in ('preparation', 'choice', 'listings', 'faq'):
            section = self.page.section(name)
            self.assertIsNotNone(section, name)
            label = section.attrs.get('aria-labelledby')
            self.assertTrue(label, name)
            self.assertTrue(any(h.attrs.get('id') == label for h in section.descendants('h2')), name)
        ids = {element.attrs['id'] for tag in ('section', 'main', 'h2', 'nav') for element in self.page.root.descendants(tag) if 'id' in element.attrs}
        for anchor in self.page.root.descendants('a'):
            href = anchor.attrs.get('href', '')
            if href.startswith('#'):
                self.assertIn(href[1:], ids)


if __name__ == '__main__':
    unittest.main()
