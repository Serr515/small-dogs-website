import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.hero_images = []
        self._card = None
        self._hero = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'section' and 'intro' in classes:
            self._hero = True
        if tag == 'article' and 'breed-card' in classes:
            self._card = {'images': [], 'traits': attrs.get('data-traits')}
            self.cards.append(self._card)
        if tag == 'img':
            if self._hero:
                self.hero_images.append(attrs)
            if self._card is not None:
                self._card['images'].append(attrs)

    def handle_endtag(self, tag):
        if tag == 'section' and self._hero:
            self._hero = False
        if tag == 'article':
            self._card = None


class BreedPhotographyTest(unittest.TestCase):
    def test_cards_have_descriptive_local_photos_and_hero_has_none(self):
        page = PageParser()
        page.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
        self.assertEqual(page.hero_images, [])
        self.assertEqual(len(page.cards), 4)
        for card in page.cards:
            self.assertTrue(card['traits'])
            self.assertEqual(len(card['images']), 1, 'Each breed card needs one photo')
            image = card['images'][0]
            self.assertTrue(image.get('alt', '').strip(), 'Photo needs descriptive alt text')
            src = image.get('src', '')
            self.assertFalse('://' in src or src.startswith('//'), src)
            self.assertTrue((ROOT / src).is_file(), f'Photo must exist locally: {src}')


if __name__ == '__main__':
    unittest.main()
