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

(function initCalculator() {
  const calcSection = document.getElementById('calcSection');
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

  let x = 0, y = 0, calcType = 'kvartira';

  function buildRegions() {
    regionSel.innerHTML = '';
    REGION_NAMES.forEach(function(r) {
      const opt = document.createElement('option');
      opt.value = opt.textContent = r;
      regionSel.appendChild(opt);
    });
    buildCities('Вибрати');
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

  function getRate(city) {
    const found = REGIONS_DATA.find(function(d) { return d.city === city; });
    return found ? found.rate : 0;
  }
  function getRateByRegion(region) {
    const found = REGIONS_DATA.find(function(d) { return d.region === region; });
    return found ? found.rate : 0;
  }

  function calcBase(sq) {
    if (calcType === 'kvartira') {
      if (sq < 80)  return 2500;
      if (sq < 160) return Math.max(2500, sq * 25);
      return 4500;
    }
    if (calcType === 'budynky') {
      if (sq < 180) return 5500;
      if (sq < 250) return Math.max(5500, sq * 30);
      return 7500;
    }
    if (calcType === 'komerc') {
      if (sq < 100)  return 2500;
      if (sq < 300)  return Math.max(2500, sq * 25);
      if (sq < 626)  return 7500;
      return sq * 12;
    }
    return 0;
  }

  function getRegionalSurcharge() {
    return calcType === 'budynky' ? 0 : y;
  }

  function reset() {
    x = 0; y = 0;
    squareInp.value = '';
    if (resultBox)  resultBox.classList.remove('visible');
    if (orderBtn)   orderBtn.classList.add('hideFormBtn');
    if (calcForm)   calcForm.classList.remove('active');
    if (notation)   notation.innerHTML = '';
    buildRegions();
  }

  buildRegions();

  regionSel.addEventListener('change', function() {
    if (hiddenRegion) hiddenRegion.value = this.value;
    buildCities(this.value);
    y = getRateByRegion(this.value);
  });

  citySel && citySel.addEventListener('change', function() {
    if (hiddenCity) hiddenCity.value = this.value;
    y = getRate(this.value);
  });

  squareInp.addEventListener('input', function() {
    const sq = parseFloat(this.value) || 0;
    x = calcBase(sq);
    if (hiddenSquare) hiddenSquare.value = sq;
  });

  doCalcBtn && doCalcBtn.addEventListener('click', function(e) {
    e.preventDefault();
    if (x < 1) {
      if (notation) notation.innerHTML = '<p class="notion-p">Введіть площу об\'єкта</p>';
      squareInp.focus();
      return;
    }
    const total = x + getRegionalSurcharge();
    if (costOut) costOut.textContent = total.toLocaleString('uk-UA');
    if (hiddenPrice) hiddenPrice.value = total;
    if (resultBox)   resultBox.classList.add('visible');
    if (orderBtn)    orderBtn.classList.remove('hideFormBtn');
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
      calcType = this.dataset.cat;
      const typeMap = { kvartira:'Квартира', budynky:'Будинок', komerc:'Нежитлове приміщення' };
      if (hiddenType) hiddenType.value = typeMap[calcType] || '';
      reset();
    });
  });

})();
