# Agent Corp

Интерактивная презентация: [опубликованная версия](https://brianis8090.github.io/presentation--agents-corp/).

Срез фактов — 8 октября 2026 года. [Источники и методика](docs/sources-2026-10-08.md).

## Проверка

```text
python -m unittest discover -s tests -p "test_*.py"
node --test tests/navigation.test.cjs
python -m http.server 8765 --bind 127.0.0.1
```

После запуска сервера открыть `http://127.0.0.1:8765/`. Навигация: стрелки, Page Up / Page Down, Home / End и кнопки внизу.

GitHub Pages публикует корень ветки `main`.
