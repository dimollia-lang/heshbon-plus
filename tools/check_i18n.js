// Проверка словарей Хешбон+: синтаксис, паритет ключей RU/EN/HE, все data-i18n из index.html
// присутствуют, теги не попали в текстовые data-i18n. Запуск: node tools/check_i18n.js
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, '..');
const src = fs.readFileSync(path.join(dir, 'i18n.js'), 'utf8');
eval(src.replace(/^const I18N/m, 'global.I18N'));            // SyntaxError = словарь сломан
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const langs = ['ru', 'en', 'he'];

const used = new Set();
for (const m of html.matchAll(/data-i18n(?:-html|-ph)?="([^"]+)"/g)) used.add(m[1]);
for (const m of html.matchAll(/\bt\('([a-zA-Z0-9._-]+)'\)/g)) used.add(m[1]);
// tf('key', ...) — только литеральные ключи; tf('prefix.' + x ...) — динамические, пропускаем
for (const m of html.matchAll(/\btf\('([a-zA-Z0-9._-]+)'\s*,/g)) used.add(m[1]);

console.log('ключей:', langs.map(l => l + '=' + Object.keys(I18N[l]).length).join(' '));
let bad = 0;
for (const k of [...used].sort()) {
  const missing = langs.filter(l => !(k in I18N[l]));
  if (missing.length) { console.log('  ОТСУТСТВУЕТ', k, '->', missing.join(',')); bad++; }
}
console.log(bad ? 'НЕ ХВАТАЕТ КЛЮЧЕЙ: ' + bad : 'все используемые ключи на месте (' + used.size + ')');

const all = new Set(langs.flatMap(l => Object.keys(I18N[l])));
let par = 0;
for (const k of all) {
  const missing = langs.filter(l => !(k in I18N[l]));
  if (missing.length) { console.log('  ПАРИТЕТ', k, 'нет в', missing.join(',')); par++; }
}
console.log(par ? 'разъехались: ' + par : 'паритет ключей по языкам: ок');

let tagBug = 0;
for (const m of html.matchAll(/data-i18n="([^"]+)"/g)) {
  const k = m[1];
  const withTags = langs.filter(l => /<(b|br|a|p|i|u|span|table)\b/i.test(I18N[l][k] || ''));
  if (withTags.length) { console.log('  ТЕГИ В ТЕКСТОВОМ data-i18n:', k, '->', withTags.join(',')); tagBug++; }
}
console.log(tagBug ? 'нужен data-i18n-html: ' + tagBug : 'теги/атрибуты: ок');

// Зашитые пенсионные проценты в UI-текстах калькулятора — ЗАПРЕЩЕНЫ (инцидент 17.08.2026:
// «6% работник / 12,5%» показывались клинеру, у которого 7% / 15,83%). Ставки приходят через {emp}/{er}/{erT}/{pitz}.
const PENSION_UI_KEYS = ['emp.chk.pension', 'emp.chk.pension.hint', 'brk.pension', 'employer.pens', 'employer.pitz'];
let hard = 0;
for (const k of PENSION_UI_KEYS) for (const l of langs) {
  const v = I18N[l][k] || '';
  if (/\b(6|6[.,]5|12[.,]5|8[.,]33|7|7[.,]5|15[.,]83)\s?%/.test(v)) { console.log('  ЗАШИТЫЙ ПРОЦЕНТ в', l + '/' + k, '->', v.match(/[\d.,]+\s?%/g).join(' ')); hard++; }
}
console.log(hard ? 'зашитые пенсионные проценты: ' + hard : 'пенсионные подписи без зашитых процентов: ок');
process.exit(bad || par || tagBug || hard ? 1 : 0);
