const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

function setup() {
  const listeners = {};
  const slides = Array.from({ length: 14 }, (_, i) => ({ active: i === 0, setAttribute(name, value) { this[name] = value; } }));
  slides.forEach(s => s.classList = { toggle: (_, active) => { s.active = active; } });
  const elements = { cnt: { textContent: '01 / 14' }, prog: { style: {} }, prev: {}, next: {} };
  const context = { document: { querySelectorAll: () => slides, getElementById: id => elements[id] }, addEventListener: (name, cb) => { listeners[name] = cb; } };
  vm.runInNewContext(script.split('/* ───── Глобус')[0], context);
  return {
    slides, elements,
    key: (key, tag = 'body') => listeners.keydown({ key, preventDefault() {}, target: { closest: selector => selector.split(',').includes(tag) } }),
    swipe: (dx, dy, target = 'body') => {
      listeners.touchstart({ touches: [{ clientX: 300, clientY: 300 }], target: { closest: selector => selector.split(',').includes(target) } });
      listeners.touchend({ touches: [], changedTouches: [{ clientX: 300 - dx, clientY: 300 - dy }] });
    },
  };
}

test('Встроенный JavaScript синтаксически корректен', () => { new vm.Script(script); });
test('Навигация проходит все четырнадцать слайдов и не выходит за границы', () => {
  const app = setup();
  for (let i = 0; i < 20; i++) app.elements.next.onclick();
  assert.equal(app.elements.cnt.textContent, '14 / 14');
  assert.equal(app.slides.filter(s => s.active).length, 1);
  assert.equal(app.slides.filter(s => !s.inert).length, 1);
  assert.equal(app.slides[13]['aria-hidden'], 'false');
  for (let i = 0; i < 20; i++) app.elements.prev.onclick();
  assert.equal(app.elements.cnt.textContent, '01 / 14');
});
test('Клавиши работают и после нажатия кнопки навигации', () => {
  const app = setup();
  app.key('End', 'button');
  assert.equal(app.elements.cnt.textContent, '14 / 14');
  app.key('Home', 'button');
  app.key('ArrowRight', 'button');
  assert.equal(app.elements.cnt.textContent, '02 / 14');
});
test('Пробел на ссылке и ввод в поле не переключают слайды', () => {
  const app = setup();
  app.key(' ', 'a');
  app.key('ArrowRight', 'input');
  assert.equal(app.elements.cnt.textContent, '01 / 14');
});

test('Горизонтальный жест переключает слайд, вертикальная прокрутка — нет', () => {
  const app = setup();
  app.swipe(80, 220);
  assert.equal(app.elements.cnt.textContent, '01 / 14');
  app.swipe(150, 20);
  assert.equal(app.elements.cnt.textContent, '02 / 14');
  app.swipe(-150, 20);
  assert.equal(app.elements.cnt.textContent, '01 / 14');
});

test('Прокрутка таблицы и вращение глобуса не переключают слайды', () => {
  const app = setup();
  app.swipe(150, 0, '.table-scroll');
  app.swipe(150, 0, '#globe');
  assert.equal(app.elements.cnt.textContent, '01 / 14');
});
