from pathlib import Path
import json
import re
import unittest
from html.parser import HTMLParser


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
SLIDES = re.findall(r'<section\b[^>]*>.*?</section>', HTML, re.S)


class Links(HTMLParser):
  def __init__(self):
    super().__init__()
    self.links = []
    self.ids = []

  def handle_starttag(self, tag, attrs):
    values = dict(attrs)
    if 'id' in values:
      self.ids.append(values['id'])
    if tag == 'a':
      self.links.append(values)


class PresentationTests(unittest.TestCase):
  def test_requested_slide_changes(self):
    self.assertEqual(len(SLIDES), 14)
    self.assertIn('01 / 14', HTML)
    self.assertNotIn('Три этапа. Первый — маленький', HTML)
    self.assertIn('Назовите процесс', SLIDES[-1])
    self.assertIn('08.10.2026', SLIDES[4])
    self.assertIn('октябрь 2026', SLIDES[6])

  def test_public_facts_are_attributed(self):
    slide = SLIDES[1]
    for fact in ['800k+', '75%', '65,9%', '26,2%', 'n = 17 464', '06.10.2026']:
      self.assertIn(fact, slide)
    for domain in ['github.blog/', 'blog.google/', 'survey.stackoverflow.co/']:
      self.assertIn(domain, slide)
    self.assertNotIn('79%', HTML)
    self.assertNotIn('88%', HTML)

  def test_growth_index_has_no_invented_cost_series(self):
    values = re.findall(r'class="growth-month" data-value="([\d.]+)"', SLIDES[5])
    self.assertEqual([float(v) for v in values], [1, 2.5, 10, 20, 30, 100])
    self.assertIn('Шкала линейная', SLIDES[5])
    self.assertIn('владельца компании', SLIDES[5])
    self.assertNotIn('class="bar c"', SLIDES[5])
    self.assertIn('только к прежнему срезу до июня', SLIDES[6])

  def test_erp_metrics_match_audit(self):
    audit = json.loads((ROOT / 'docs/erp-audit-2026-10-08.json').read_text(encoding='utf-8'))
    self.assertEqual(len(audit['navigation']), 13)
    self.assertEqual(audit['source_files'], 1481)
    self.assertEqual(audit['nonblank_source_lines'], 274360)
    self.assertEqual(audit['test_files'], 1470)
    self.assertEqual(len(audit['agent_route_groups']), 10)
    for value in ['8.0.172', '1 481', '1 470', '274 тыс.', '44d8128']:
      self.assertIn(value, SLIDES[4])
    self.assertNotIn('8.0.77', SLIDES[4])

  def test_price_sources_and_boundaries(self):
    for value in ['от 1,5 млн ₽', 'от 4 млн ₽', 'от 8 млн ₽', 'индивидуально', '370 тыс.', 'от 7 млн ₽']:
      self.assertIn(value, SLIDES[10])
    for old in ['15–50 млн', '40–160 млн', '140–550 млн', '1,8 млрд']:
      self.assertNotIn(old, HTML)
    self.assertIn('НДС', SLIDES[10])
    self.assertNotIn('Бюджет рынка без НДС', HTML)

  def test_links_ids_and_local_sources(self):
    parser = Links()
    parser.feed(HTML)
    self.assertEqual(len(parser.ids), len(set(parser.ids)))
    for item in parser.links:
      href = item.get('href', '')
      if href.startswith('docs/'):
        self.assertTrue((ROOT / href).is_file(), href)
      if item.get('target') == '_blank':
        self.assertIn('noopener', item.get('rel', ''))


if __name__ == '__main__':
  unittest.main(verbosity=2)
