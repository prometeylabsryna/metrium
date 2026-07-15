'use strict';
/* =============================================
   CALCULATOR.JS — price calculator for BTI
   Extracted from parts/calculator.php
   ============================================= */

const REGIONS_DATA = [
  {region:"Вибрати",             city:"Вибрати",           rate:0},
  {region:"Київ",                city:"Голосіївський",     rate:0},
  {region:"Київ",                city:"Оболонський",       rate:0},
  {region:"Київ",                city:"Печерський",        rate:0},
  {region:"Київ",                city:"Подільський",       rate:0},
  {region:"Київ",                city:"Солом'янський",     rate:0},
  {region:"Київ",                city:"Шевченківський",    rate:0},
  {region:"Київ",                city:"Деснянський",       rate:0},
  {region:"Київ",                city:"Дніпровський",      rate:0},
  {region:"Київ",                city:"Дарницький",        rate:0},
  {region:"Броварський район",   city:"Баришівська",       rate:500},
  {region:"Броварський район",   city:"Березанська",       rate:500},
  {region:"Броварський район",   city:"Броварська",        rate:0},
  {region:"Броварський район",   city:"Великодимерська",   rate:500},
  {region:"Броварський район",   city:"Зазимська",         rate:0},
  {region:"Броварський район",   city:"Згурівська",        rate:1000},
  {region:"Броварський район",   city:"Калинівська",       rate:500},
  {region:"Броварський район",   city:"Калитянська",       rate:1000},
  {region:"Білоцерківський район",city:"Білоцерківська",   rate:1000},
  {region:"Білоцерківський район",city:"Рокитнянська",     rate:1000},
  {region:"Білоцерківський район",city:"Сквирська",        rate:1000},
  {region:"Білоцерківський район",city:"Таращанська",      rate:1000},
  {region:"Бориспільський район", city:"Бориспільська",    rate:0},
  {region:"Бориспільський район", city:"Переяславська",    rate:1000},
  {region:"Бориспільський район", city:"Яготинська",       rate:1000},
  {region:"Бучанський район",    city:"Білогородська",     rate:0},
  {region:"Бучанський район",    city:"Бородянська",       rate:0},
  {region:"Бучанський район",    city:"Бучанська",         rate:0},
  {region:"Бучанський район",    city:"Вишнева",           rate:0},
  {region:"Бучанський район",    city:"Гостомельська",     rate:0},
  {region:"Бучанський район",    city:"Ірпінська",         rate:0},
  {region:"Бучанський район",    city:"Коцюбинська",       rate:0},
  {region:"Бучанський район",    city:"Макарівська",       rate:500},
  {region:"Бучанський район",    city:"Пісківська",        rate:500},
  {region:"Вишгородський район", city:"Вишгородська",      rate:0},
  {region:"Вишгородський район", city:"Димерська",         rate:500},
  {region:"Вишгородський район", city:"Іванківська",       rate:1000},
  {region:"Вишгородський район", city:"Петрівська",        rate:0},
  {region:"Вишгородський район", city:"Пірнівська",        rate:500},
  {region:"Обухівський район",   city:"Богуславська",      rate:1000},
  {region:"Обухівський район",   city:"Васильківська",     rate:500},
  {region:"Обухівський район",   city:"Кагарлицька",       rate:0},
  {region:"Обухівський район",   city:"Козинська",         rate:500},
  {region:"Обухівський район",   city:"Обухівська",        rate:1000},
  {region:"Фастівський район",   city:"Боярська",          rate:0},
  {region:"Фастівський район",   city:"Гатненська",        rate:0},
  {region:"Фастівський район",   city:"Глевахівська",      rate:0},
  {region:"Фастівський район",   city:"Чабанівська",       rate:0},
  {region:"Фастівський район",   city:"Фастівська",        rate:1000},
];

const REGION_NAMES = [
  "Вибрати","Київ","Броварський район","Білоцерківський район",
  "Бориспільський район","Бучанський район","Вишгородський район",
  "Обухівський район","Фастівський район"
];

const TYPE_MAP = {
  kvartira: 'Квартира',
  budynky: 'Будинок',
  komerc: 'Нежитлове приміщення'
};

(function initCalculator() {
  const calcSection = document.getElementById('calcSection')
    || document.querySelector('.calcBlock');
  if (!calcSection) return;

  const regionSel  = calcSection.querySelector('#regionsselect');
  const citySel    = calcSection.querySelector('#cityselect');
  const squareInp  = calcSection.querySelector('#squareVal');
  const doCalcBtn  = calcSection.querySelector('.doCalc');
  const orderBtn   = calcSection.querySelector('.callFormCalc');
  const costOut    = calcSection.querySelector('#cost');
  const resultBox  = calcSection.querySelector('.form-result');
  const notation   = calcSection.querySelector('.notation');
  const calcTabs   = calcSection.querySelectorAll('.calcTabBtn');
  const calcForm   = calcSection.querySelector('#calc-form-data');
  const hiddenPrice  = calcSection.querySelector('input[name=price]');
  const hiddenType   = calcSection.querySelector('input[name=type]');
  const hiddenSquare = calcSection.querySelector('input[name=square]');
  const hiddenRegion = calcSection.querySelector('input[name=region]');
  const hiddenCity   = calcSection.querySelector('input[name=cityInput]');

  if (!regionSel || !squareInp) return;

  function resolveTypeLabel(btn) {
    if (!btn) return TYPE_MAP.kvartira;
    if (btn.dataset.typeLabel) return btn.dataset.typeLabel;
    return TYPE_MAP[btn.dataset.cat] || TYPE_MAP.kvartira;
  }

  function getActiveTab() {
    return calcSection.querySelector('.calcTabBtn.active') || calcTabs[0] || null;
  }

  const activeTab = getActiveTab();
  let calcType = (activeTab && activeTab.dataset.cat) || 'kvartira';

  if (hiddenType) hiddenType.value = resolveTypeLabel(activeTab);

  function buildRegions() {
    regionSel.innerHTML = '';
    REGION_NAMES.forEach(function(r) {
      const opt = document.createElement('option');
      opt.value = opt.textContent = r;
      regionSel.appendChild(opt);
    });
    buildCities('Вибрати');
    syncLocationFields();
  }

  function buildCities(region) {
    if (!citySel) return;
    citySel.innerHTML = '';
    const filtered = REGIONS_DATA.filter(function(d) { return d.region === region; });
    filtered.forEach(function(d) {
      const opt = document.createElement('option');
      opt.value = opt.textContent = d.city;
      citySel.appendChild(opt);
    });
  }

  function isKyivCity() {
    return regionSel.value === 'Київ';
  }

  function calcKomercLarge(sq) {
    if (sq <= 699) return sq * 20;
    if (sq <= 999) return sq * 18;
    if (sq <= 1999) return sq * 12;
    return sq * 10;
  }

  function calcPrice(sq) {
    if (calcType === 'kvartira') {
      // Київ: 40 грн/м², мін. 2500 | область: 50 грн/м², мін. 3000
      if (isKyivCity()) return Math.max(2500, sq * 40);
      return Math.max(3000, sq * 50);
    }

    if (calcType === 'budynky') {
      // до 250 м² — попередня логіка; від 251 — площа × 25
      if (sq < 180) return 5500;
      if (sq < 250) return Math.max(5500, sq * 30);
      if (sq <= 250) return 7500;
      return sq * 25;
    }

    if (calcType === 'komerc') {
      // до 300 м² включно — попередня логіка; від 301 — нова сітка
      if (sq < 100) return 2500;
      if (sq < 300) return Math.max(2500, sq * 25);
      if (sq < 301) return 7500;
      return calcKomercLarge(sq);
    }

    return 0;
  }

  function readSquare() {
    const raw = String(squareInp.value || '').trim();
    if (!raw) return null;
    const sq = parseFloat(raw.replace(',', '.'));
    if (!isFinite(sq) || sq < 1) return null;
    return sq;
  }

  function syncLocationFields() {
    const region = regionSel.value || '';
    const city = citySel ? (citySel.value || '') : '';
    const regionOk = region && region !== 'Вибрати';
    const cityOk = city && city !== 'Вибрати';

    if (hiddenRegion) hiddenRegion.value = regionOk ? region : '';
    if (hiddenCity) hiddenCity.value = cityOk ? city : '';
  }

  function syncLeadFields(sq, total) {
    syncLocationFields();
    if (hiddenSquare) hiddenSquare.value = sq;
    if (hiddenPrice) hiddenPrice.value = total;
    if (hiddenType) hiddenType.value = resolveTypeLabel(getActiveTab());
  }

  function reset() {
    squareInp.value = '';
    if (resultBox)  resultBox.classList.remove('visible');
    if (orderBtn)   orderBtn.classList.add('hideFormBtn');
    if (calcForm)   calcForm.classList.remove('active');
    if (notation)   notation.innerHTML = '';
    if (hiddenSquare) hiddenSquare.value = '';
    if (hiddenPrice)  hiddenPrice.value = '';
    buildRegions();
  }

  buildRegions();

  regionSel.addEventListener('change', function() {
    buildCities(this.value);
    syncLocationFields();
  });

  citySel && citySel.addEventListener('change', function() {
    syncLocationFields();
  });

  squareInp.addEventListener('input', function() {
    if (notation) notation.innerHTML = '';
  });

  doCalcBtn && doCalcBtn.addEventListener('click', function(e) {
    e.preventDefault();
    const sq = readSquare();
    if (sq === null) {
      if (notation) notation.innerHTML = '<p class="notion-p">Введіть площу об\'єкта</p>';
      squareInp.focus();
      return;
    }
    syncLocationFields();
    const total = Math.round(calcPrice(sq));
    syncLeadFields(sq, total);
    if (costOut) costOut.textContent = total.toLocaleString('uk-UA');
    if (resultBox) resultBox.classList.add('visible');
    if (orderBtn)  orderBtn.classList.remove('hideFormBtn');
  });

  orderBtn && orderBtn.addEventListener('click', function(e) {
    e.preventDefault();
    if (calcForm) calcForm.classList.toggle('active');
  });

  calcTabs.forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      calcTabs.forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');
      calcType = this.dataset.cat || 'kvartira';
      if (hiddenType) hiddenType.value = resolveTypeLabel(this);
      reset();
    });
  });

})();
