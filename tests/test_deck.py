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
    for fact in ['Google', 'Яндекс', 'Microsoft', '75%', '5 000', '≈90%', '29.07.2026']:
      self.assertIn(fact, slide)
    for domain in ['blog.google/', 'yandex.ru/company/', 'microsoft.com/']:
      self.assertIn(domain, slide)
    self.assertNotIn('79%', HTML)
    self.assertNotIn('88%', HTML)

  def test_growth_index_has_no_invented_cost_series(self):
    values = re.findall(r'class="growth-month" data-value="([\d.]+)"', SLIDES[5])
    self.assertEqual([float(v) for v in values], [1, 2.5, 10, 20, 30, 100])
    self.assertIn('Шкала линейная', SLIDES[5])
    self.assertIn('Внутренняя статистика Agent Corp', SLIDES[5])
    self.assertNotIn('class="bar c"', SLIDES[5])
    self.assertIn('Что получает заказчик', SLIDES[6])

  def test_erp_metrics_match_audit(self):
    audit = json.loads((ROOT / 'docs/erp-audit-2026-10-08.json').read_text(encoding='utf-8'))
    self.assertEqual(len(audit['navigation']), 13)
    self.assertEqual(audit['source_files'], 1481)
    self.assertEqual(audit['nonblank_source_lines'], 274360)
    self.assertEqual(audit['test_files'], 1470)
    self.assertEqual(len(audit['agent_route_groups']), 10)
    for value in ['8.0.172', '1 481', '1 470', '274 тыс.']:
      self.assertIn(value, SLIDES[4])
    self.assertNotIn('8.0.77', SLIDES[4])

  def test_price_sources_and_boundaries(self):
    for value in ['6–20 млн ₽', '30–100 млн ₽', '150–550+ млн ₽', '≈10 сотрудников', '≈100 сотрудников', 'Более 1 000 сотрудников']:
      self.assertIn(value, SLIDES[10])
    for old in ['15–50 млн', '40–160 млн', '140–550 млн', '1,8 млрд']:
      self.assertNotIn(old, HTML)
    self.assertIn('Расчётная модель Agent Corp', SLIDES[10])
    self.assertNotIn('Бюджет рынка без НДС', HTML)

  def test_market_model_arithmetic_and_slide_values(self):
    model = json.loads((ROOT / 'docs/erp-market-model-2026-10-08.json').read_text(encoding='utf-8'))
    multiplier = 1 + (model['environment_percent'] + model['reserve_percent']) / 100
    totals = []
    for scenario in model['scenarios']:
      for key in ['display_budget', 'display_duration', 'display_team']:
        self.assertIn(scenario[key], SLIDES[10])
      low = scenario['team_min'] * model['hours_per_month'] * scenario['rate_min'] * scenario['months_min'] * multiplier
      high = scenario['team_max'] * model['hours_per_month'] * scenario['rate_max'] * scenario['months_max'] * multiplier
      self.assertLess(low, high)
      totals.append((round(low), round(high)))
    self.assertEqual(totals, [(5760000, 19660800), (31104000, 96768000), (145152000, 552960000)])
    example = model['example']
    self.assertEqual(sum(example['average_role_loads'].values()), example['team'])
    labor = example['team'] * model['hours_per_month'] * example['months'] * example['hourly_rate']
    self.assertEqual(labor, example['labor_budget'])
    self.assertEqual(labor * model['environment_percent'] / 100, example['environment_budget'])
    self.assertEqual(labor * model['reserve_percent'] / 100, example['reserve_budget'])
    self.assertEqual(labor * multiplier, example['total_budget'])

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
