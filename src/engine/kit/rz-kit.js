/* ==========================================================================
   rz-kit.js — «оживлення» сторінки «Свій дизайн» (демо «Розвідки»).
   Сторінку верстає Claude: лише HTML і CSS, без жодного скрипту. Усе, що має працювати, — тут,
   за data-атрибутами розмітки (довідка — food-landing/demo-page-prompt.md, розділ «Розмітка набору»):

     <article data-item="gunbao" data-name="Курка Гунбао" data-price="330" data-weight="270 г"
              data-tags="hot" data-pair="rice ohirky" data-role="main" data-desc="…">
       <img src="photo:3" alt="…"> … <button data-add>Додати</button> <button data-open>Детальніше</button>
     </article>
     data-min="3" на позиції — «замовлення від 3 шт» з меню (хінкалі): «Додати» кладе одразу 3, «−» з 3 прибирає зовсім
     <button data-add="gunbao">…</button>        — кнопка тієї ж страви деінде (герой, «з чого почати»)
     <button data-open-cart>Кошик <span data-cart-count></span></button>   <span data-cart-sum></span>
     <button data-filter="hot">Лише гостре <span data-filter-count="hot"></span></button>  (+ data-filter="" — усі)
     <section data-group>…позиції…</section>     — розділ меню ховається, якщо фільтр лишив його порожнім
     <body data-hours="11:00-22:00,…×7 (пн→нд), «-» = вихідний" data-modes="pickup delivery" data-address="…">
     <span data-now></span> <i data-now-dot></i> <ul data-hours-list></ul>
     id="menu" (або data-menu) — «долистали до меню»

   Набір сам малює: рядок «це демо» згори, лічильник замість «Додати», плашку кошика знизу, тост
   «Додано · Поруч добре», шторку страви, кошик (рядки, «Прибрати» з поверненням, «Додайте до замовлення»),
   оформлення (+380), «Готово — у демо нічого не надіслано».
   Параметри — атрибути тегу <script>, який ставить рушій: data-name, data-src (звідки меню),
   data-sb/data-anon/data-slug (сайт демо: події «відкрили»), data-own="1" (свій перегляд).
   3.9: мова й країна — <body data-lang="uk|ru" data-cc="380|7|375|…" data-cur="₴|₽|₸|…" data-tz="…"> (ставить рушій із config):
   словник підписів TX, валюта, маска й перевірка телефону, часовий пояс «відчинено зараз». Без атрибутів — uk, ₴, +380.
   У пісочниці прев’ю (opaque origin) localStorage кидає — тому все в try/catch.
   ========================================================================== */
(() => {
  'use strict';
  const me = document.currentScript, P = (me && me.dataset) || {};
  // прев'ю в «Розвідці» (пісочниця, без сервера): помилки набору — у рушій, а він покаже їх у вікні «Демо»
  if (!P.sb && window.parent !== window) addEventListener('error', e => { try { window.parent.postMessage({ type: 'rzk:error', msg: String(e.message || e).slice(0, 200), line: e.lineno || 0 }, '*'); } catch (x) {} });
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const body = document.body;

  /* ---------- мова, валюта, код телефону: <body data-lang data-cc data-cur>; криве або немає — uk, ₴, 380 ---------- */
  const LANG = String(body.dataset.lang || '').toLowerCase().trim() === 'ru' ? 'ru' : 'uk';
  const CC = (c => /^[1-9]\d{0,2}$/.test(c) ? c : '380')(String(body.dataset.cc || '').trim().replace(/^\+/, ''));
  const CUR = (c => c && [...c].length <= 4 && !/[<>"'&`\\\u0000-\u001f]/.test(c) ? c : '₴')(String(body.dataset.cur || '').trim());
  // код країни → [цифр після коду, місцевий префікс («0…», «8…»), групи цифр маски, часовий пояс «відчинено зараз»]
  const TEL = {
    380: [9, '0', [2, 3, 2, 2], 'Europe/Kyiv'], 7: [10, '8', [3, 3, 2, 2], CUR === '₸' ? 'Asia/Almaty' : ''],   // 3.15: Россия — 11 поясів: без data-tz час гостя, а не Москва
    375: [9, '80', [2, 3, 2, 2], 'Europe/Minsk'], 998: [9, '', [2, 3, 2, 2], 'Asia/Tashkent'], 996: [9, '0', [3, 3, 3], 'Asia/Bishkek'],
    992: [9, '', [2, 3, 2, 2], 'Asia/Dushanbe'], 993: [8, '8', [2, 2, 2, 2], 'Asia/Ashgabat'], 994: [9, '0', [2, 3, 2, 2], 'Asia/Baku'],
    374: [8, '0', [2, 2, 2, 2], 'Asia/Yerevan'], 995: [9, '', [3, 2, 2, 2], 'Asia/Tbilisi'], 373: [8, '0', [2, 3, 3], 'Europe/Chisinau']
  };
  // 3.15: <body data-tz> — пояс закладу з config (IANA «Asia/Novosibirsk» або хвилини від UTC, як utcOffsetMinutes Google) — головніший
  const TZ_RAW = String(body.dataset.tz || '').trim(), TZ_MIN = /^[+-]?\d{1,3}$/.test(TZ_RAW) && Math.abs(+TZ_RAW) <= 840 ? +TZ_RAW : null;
  const tzOk = z => { try { new Intl.DateTimeFormat('en-GB', { timeZone: z }); return true; } catch (e) { return false; } };
  const TELC = TEL[CC] || null, TZ = TZ_RAW && TZ_MIN == null && tzOk(TZ_RAW) ? TZ_RAW : TELC ? TELC[3] : '';   // невідомий код — час гостя
  const MASK = '+' + CC + (TELC ? TELC[2] : [3, 3, 4]).map(n => ' ' + 'X'.repeat(n)).join('');
  // номер: міжнародний із цим кодом або місцевий із префіксом (для 380 — рівно як було: 380XXXXXXXXX або 0XXXXXXXXX)
  const telOk = d => TELC ? (d.startsWith(CC) && d.length === CC.length + TELC[0]) || (!!TELC[1] && d.startsWith(TELC[1]) && d.length === TELC[1].length + TELC[0])
    : d.startsWith(CC) && d.length >= 10 && d.length <= 15;

  /* ---------- словник підписів: uk — як було до 3.9, літера в літеру; ru — для Росії, Казахстану, Білорусі й ін. ---------- */
  const TX = {
    uk: {
      num: 'uk-UA', grn: ' гривень', place: 'закладу',
      demo: (n, mid) => `<b>Демо-концепт сайту для ${n}.</b> ${mid}Замовлення з цієї сторінки не надсилаються.`,
      sample: 'Меню й ціни на сторінці — приклад, не справжні. ', from: s => 'Меню й ціни — з ' + s + '. ',
      pos: ['позиція', 'позиції', 'позицій'], dish: ['страва', 'страви', 'страв'],
      ask: 'Ціну уточнюйте в закладі', askDot: 'Ціну уточнюйте в закладі.', inCart: n => `${n} у кошику`, less: 'Менше', more: 'Більше',
      lessOf: n => `Менше: ${n}`, moreOf: n => `Більше: ${n}`, cart: 'Кошик', dishDlg: 'Страва', go: 'Оформити',
      addAria: (n, p) => `Додати: ${n}, ${p}`, addOf: n => `Додати: ${n}`, added: n => `Додано: ${n}`, pair: (n, p) => `Поруч добре: ${n} +${p}`, pairs: 'Поруч добре',
      hot: 'гостро', veg: 'без м’яса', close: 'Закрити', closeCart: 'Закрити кошик', qty: 'Кількість', addN: (q, s) => `Додати ${q} — ${s}`,
      modes: { pickup: 'Самовивіз', delivery: 'Доставка', dinein: 'У залі' },
      removed: n => `Прибрано: ${n}`, undo: 'Повернути', empty: 'Кошик порожній',
      emptyHint: 'Додайте страву з меню — кошик порахує суму й підкаже, що взяти до неї.', addFirst: (n, s) => `Додати: ${n} — ${s}`, openMenu: p => `Відкрити меню — ${p}`,
      rm: 'Прибрати', upsell: 'Додайте до замовлення', upsellHint: 'Порада сайту до того, що вже в кошику.', total: 'Разом', goOn: s => `Оформити на ${s}`,
      form: 'Оформлення', name: 'Ваше імʼя', namePh: 'Наприклад, Олена…', nameErr: 'Напишіть імʼя — так заклад звернеться до вас.', tel: 'Телефон',
      telErr: m => `Потрібен номер у форматі ${m} — на нього передзвонять для підтвердження.`, way: 'Як отримати',
      addr: 'Адреса доставки', addrPh: 'Вулиця, будинок, під’їзд…', addrErr: 'Напишіть адресу — куди везти замовлення.',
      wayDelivery: 'Вартість і час доставки підтвердить заклад.', wayDinein: 'Столик і час підтвердить заклад.', wayPickup: a => 'Самовивіз — ' + a + '.', wayAny: 'Час, коли забрати, підтвердить заклад.',
      note: 'Коментар', notePh: 'Наприклад, без цибулі або на котру годину…', back: '← Назад до кошика', toPay: 'До сплати', send: s => `Надіслати замовлення на ${s}`,
      sending: ' Надсилаємо…', done: 'Готово', doneH: s => `Замовлення на ${s} прийняте — у демо`,
      doneP: (d, who) => `${d}, ${who}. Це демо-сторінка, тож нічого не надіслано. На робочому сайті замовлення одразу прийде закладу, а вам передзвонять для підтвердження.`,
      toMenu: 'Повернутися до меню',
      days: ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя'], off: 'вихідний',
      soon: (l, h) => `Відчинено ще ${l} хв — до ${h}`, openNow: h => `Зараз відчинено — до ${h}`, closed: 'Зараз зачинено',
      when: (k, i, days) => k === 0 ? 'сьогодні' : k === 1 ? 'завтра' : 'у ' + days[i].toLowerCase().replace('пʼятниця', 'пʼятницю').replace('середа', 'середу').replace('субота', 'суботу').replace('неділя', 'неділю'),
      opens: (w, h) => `Зараз зачинено — відчинимо ${w} о ${h}`
    },
    ru: {
      num: 'ru-RU', grn: ' гривен', place: 'заведения',
      demo: (n, mid) => `<b>Демо-концепт сайта для ${n}.</b> ${mid}Заказы с этой страницы не отправляются.`,
      sample: 'Меню и цены на странице — пример, не настоящие. ', from: s => 'Меню и цены — ' + (/^с[^аеёиоуыэюя]/i.test(s) ? 'со ' : 'с ') + s + '. ',
      pos: ['позиция', 'позиции', 'позиций'], dish: ['блюдо', 'блюда', 'блюд'],
      ask: 'Цену уточняйте в заведении', askDot: 'Цену уточняйте в заведении.', inCart: n => `${n} в корзине`, less: 'Меньше', more: 'Больше',
      lessOf: n => `Меньше: ${n}`, moreOf: n => `Больше: ${n}`, cart: 'Корзина', dishDlg: 'Блюдо', go: 'Оформить',
      addAria: (n, p) => `Добавить: ${n}, ${p}`, addOf: n => `Добавить: ${n}`, added: n => `Добавлено: ${n}`, pair: (n, p) => `К этому берут: ${n} +${p}`, pairs: 'К этому берут',
      hot: 'остро', veg: 'без мяса', close: 'Закрыть', closeCart: 'Закрыть корзину', qty: 'Количество', addN: (q, s) => `Добавить ${q} — ${s}`,
      modes: { pickup: 'Самовывоз', delivery: 'Доставка', dinein: 'В зале' },
      removed: n => `Убрано: ${n}`, undo: 'Вернуть', empty: 'Корзина пуста',
      emptyHint: 'Добавьте блюдо из меню — корзина посчитает сумму и подскажет, что взять к нему.', addFirst: (n, s) => `Добавить: ${n} — ${s}`, openMenu: p => `Открыть меню — ${p}`,
      rm: 'Убрать', upsell: 'Добавьте к заказу', upsellHint: 'Совет сайта к тому, что уже в корзине.', total: 'Итого', goOn: s => `Оформить на ${s}`,
      form: 'Оформление', name: 'Ваше имя', namePh: 'Например, Анна…', nameErr: 'Напишите имя — так заведение обратится к вам.', tel: 'Телефон',
      telErr: m => `Нужен номер в формате ${m} — на него перезвонят для подтверждения.`, way: 'Как получить',
      addr: 'Адрес доставки', addrPh: 'Улица, дом, подъезд…', addrErr: 'Напишите адрес — куда везти заказ.',
      wayDelivery: 'Стоимость и время доставки подтвердит заведение.', wayDinein: 'Столик и время подтвердит заведение.', wayPickup: a => 'Самовывоз — ' + a + '.', wayAny: 'Время, когда забрать, подтвердит заведение.',
      note: 'Комментарий', notePh: 'Например, без лука или к какому времени…', back: '← Назад в корзину', toPay: 'К оплате', send: s => `Отправить заказ на ${s}`,
      sending: ' Отправляем…', done: 'Готово', doneH: s => `Заказ на ${s} принят — в демо`,
      doneP: (d, who) => `${d}, ${who}. Это демо-страница, поэтому ничего не отправлено. На рабочем сайте заказ сразу придёт в заведение, а вам перезвонят для подтверждения.`,
      toMenu: 'Вернуться в меню',
      days: ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'], off: 'выходной',
      soon: (l, h) => `Открыто ещё ${l} мин — до ${h}`, openNow: h => `Сейчас открыто — до ${h}`, closed: 'Сейчас закрыто',
      when: (k, i) => k === 0 ? 'сегодня' : k === 1 ? 'завтра' : ['в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу', 'в воскресенье'][i],
      opens: (w, h) => `Сейчас закрыто — откроемся ${w} в ${h}`
    }
  };
  const T = TX[LANG];

  const UAH = n => Math.round(n).toLocaleString(T.num) + ' ' + CUR;
  const SAY = n => CUR === '₴' ? n + T.grn : UAH(n);   // сума для екранного читача: «70 гривень» як було; інша валюта — «70 ₽»
  const plural = (n, a, b, c) => { const m = n % 10, h = n % 100; return m === 1 && h !== 11 ? a : m >= 2 && m <= 4 && (h < 12 || h > 14) ? b : c; };
  const pos = n => `${n} ${plural(n, ...T.pos)}`;
  const dishes = n => `${n} ${plural(n, ...T.dish)}`;
  const svg = d => `<svg class="rzk-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">${d}</svg>`;
  const I_PLUS = svg('<path d="M12 5v14M5 12h14"/>'), I_MINUS = svg('<path d="M5 12h14"/>'), I_X = svg('<path d="M6 6l12 12M18 6L6 18"/>'), I_GO = svg('<path d="M5 12h14M13 5l7 7-7 7"/>');
  const NAME = String(P.name || document.title || T.place).trim().slice(0, 80);

  /* ---------- рядок «це демо»: завжди перший і завжди видно ---------- */
  const line = document.createElement('p');
  line.className = 'rzk-demo';
  // звідки меню: від «Розвідки» (data-src скрипту) або зі сторінки (<body data-menu-source>); меню-приклад — <body data-sample="menu">
  const SRC = String(P.src || body.dataset.menuSource || '').trim().slice(0, 120), SAMPLE = /\bmenu\b/.test(body.dataset.sample || '');
  line.innerHTML = T.demo(esc(NAME), SAMPLE ? T.sample : SRC ? T.from(esc(SRC)) : '');
  body.prepend(line);
  line.style.setProperty('display', 'block', 'important');
  line.style.setProperty('visibility', 'visible', 'important');

  /* ---------- каталог з розмітки ---------- */
  const BY = new Map();   // id → {id, name, price|null, weight, tags[], pair[], role, img, desc}
  $$('[data-item][data-name]').forEach(el => {
    const id = String(el.dataset.item || '').trim();
    if (!id || BY.has(id)) return;
    const raw = String(el.dataset.price == null ? '' : el.dataset.price).replace(/\s/g, '').replace(',', '.');
    const price = raw !== '' && isFinite(+raw) && +raw > 0 ? +raw : null;
    const im = $('img', el);
    const dEl = $('[data-desc]', el);
    BY.set(id, {
      id, name: String(el.dataset.name).trim().slice(0, 120), price,
      weight: String(el.dataset.weight || '').trim().slice(0, 40),
      min: Math.max(1, Math.min(30, parseInt(el.dataset.min, 10) || 1)),   // data-min: «замовлення від N шт» з меню (хінкалі, суші-сети): додали — одразу N
      tags: String(el.dataset.tags || '').toLowerCase().split(/[\s,]+/).filter(Boolean),
      pair: String(el.dataset.pair || '').split(/[\s,]+/).filter(Boolean),
      role: String(el.dataset.role || '').toLowerCase().trim(),
      img: el.dataset.img || (im && (im.currentSrc || im.getAttribute('src'))) || '',
      desc: String(el.dataset.desc || (dEl && dEl.textContent) || '').replace(/\s+/g, ' ').trim().slice(0, 600)
    });
  });
  const itemOf = el => {
    const v = el.getAttribute('data-add') || el.getAttribute('data-open') || '';
    if (v && BY.has(v)) return BY.get(v);
    const host = el.closest('[data-item]');
    return host ? BY.get(host.dataset.item) || null : null;
  };

  /* ---------- кошик: зручність цього гостя, у браузері ---------- */
  const KEY = 'rzk:' + (P.slug || location.pathname);
  let cart = {};
  try { cart = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { cart = {}; }
  Object.keys(cart).forEach(k => { const it = BY.get(k); if (!it || it.price == null || !(cart[k] > 0)) delete cart[k]; });
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) {} };
  const qOf = id => cart[id] || 0;
  const count = () => Object.values(cart).reduce((s, q) => s + q, 0);
  const total = () => Object.entries(cart).reduce((s, [id, q]) => s + BY.get(id).price * q, 0);

  /* ---------- події для «Розвідки»: лише назва дії й дрібниці, ні імені, ні телефону ---------- */
  // сервер демо (https; http://localhost:порт — стенд перевірки) + публічний ключ + адреса демо
  const RS = /^(https:\/\/|http:\/\/localhost:\d+$)/.test(P.sb || '') && P.anon && /^[a-z0-9-]{3,64}$/.test(P.slug || '') ? P : null;
  const OWN = (() => {
    if (!RS) return true;
    if (P.own === '1') return true;
    try { return localStorage.getItem('rz_own') === '1'; } catch (e) { return false; }
  })();
  const SID = (() => {
    let s = '';
    try { s = sessionStorage.getItem('rz_sid') || ''; } catch (e) {}
    if (!/^[A-Za-z0-9_-]{8,40}$/.test(s)) {
      const a = new Uint8Array(12);
      try { crypto.getRandomValues(a); } catch (e) { for (let i = 0; i < a.length; i++) a[i] = Math.random() * 256 | 0; }
      s = Array.from(a, b => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join('');
      try { sessionStorage.setItem('rz_sid', s); } catch (e) {}
    }
    return s;
  })();
  const once = new Set(); let hits = 0;
  function hit(ev, data, key){
    if (!RS || OWN || navigator.webdriver) return;
    if (key) { if (once.has(key)) return; once.add(key); }
    if (++hits > 40) return;
    fetch(RS.sb + '/rest/v1/rpc/rz_demo_hit', {
      method: 'POST', keepalive: true, headers: { apikey: RS.anon, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_slug: RS.slug, p_sid: SID, p_ev: ev, p_data: data || {} })
    }).catch(() => {});
  }
  // «Відкрили» — після 2 с на видимій сторінці; далі «долистали до меню» і вехи 30 с, 1, 2, 5 хв
  // 4.0 «Відкритка з QR» («Розвідка», postcard.js): QR веде на демо з ?f=qr — «відкрили» йде з позначкою src: 'qr'
  const fromQr = () => { try { return new URLSearchParams(location.search).get('f') === 'qr'; } catch (e) { return false; } };
  (function track(){
    if (!RS) return;
    let vis = 0, last = document.visibilityState === 'visible' ? Date.now() : 0, menuSeen = false;
    const add = () => { const now = Date.now(); if (last) vis += now - last; last = document.visibilityState === 'visible' ? now : 0; };
    const tick = () => {
      add();
      if (vis >= 2000) hit('open', fromQr() ? { w: innerWidth, src: 'qr' } : { w: innerWidth }, 'open');
      if (once.has('open')) { if (menuSeen) hit('menu', {}, 'menu'); for (const s of [30, 60, 120, 300]) if (vis >= s * 1000) hit('ping', { ms: s * 1000 }, 'ping' + s); }
      if (vis < 300000) setTimeout(tick, vis < 2000 ? 500 : 5000);
    };
    document.addEventListener('visibilitychange', add);
    setTimeout(tick, 500);
    const m = document.getElementById('menu') || $('[data-menu]');
    if (m && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { menuSeen = true; if (once.has('open')) hit('menu', {}, 'menu'); } }, { threshold: 0.15 });
      io.observe(m);
    }
  })();

  /* ---------- зміна кількості ---------- */
  function setQ(id, q, opt){
    const it = BY.get(id); if (!it || it.price == null) return;
    q = Math.max(0, Math.min(30, q | 0));
    if (q > 0 && q < it.min) q = q > qOf(id) ? it.min : 0;   // нижче мінімуму: додали — одразу до N, прибрали — до нуля
    const was = qOf(id);
    if (q > was) hit('cart_add', { item: it.name.slice(0, 80), qty: q - was });
    if (q) cart[id] = q; else delete cart[id];
    save(); sync();
    if (q > was && !(opt && opt.quiet)) toast(it);
  }

  /* ---------- кнопки «Додати»: у кошику — лічильник на їх місці ---------- */
  function syncButtons(){
    $$('[data-add]').forEach(b => {
      const it = itemOf(b); if (!it) return;
      if (it.price == null) { b.disabled = true; b.setAttribute('aria-disabled', 'true'); b.title = T.ask; return; }
      const q = qOf(it.id);
      let st = b.nextElementSibling && b.nextElementSibling.classList.contains('rzk-step') ? b.nextElementSibling : null;
      if (!q) { b.style.removeProperty('display'); if (st) st.remove(); return; }
      if (!st) {
        st = document.createElement('span'); st.className = 'rzk-step'; st.setAttribute('role', 'group');
        // лічильник стає в ту саму клітинку сітки / flex-позицію, що й кнопка (сторінка могла розставити кнопку явно)
        const cs = getComputedStyle(b);
        ['gridColumnStart', 'gridColumnEnd', 'gridRowStart', 'gridRowEnd', 'alignSelf', 'justifySelf', 'order', 'marginLeft', 'marginTop'].forEach(k => { st.style[k] = cs[k]; });
        b.after(st);
      }
      st.setAttribute('aria-label', T.inCart(it.name));
      st.innerHTML = `<button type="button" data-rzk-dec="${esc(it.id)}" aria-label="${T.lessOf(esc(it.name))}">${I_MINUS}</button><output aria-live="polite">${q}</output><button type="button" data-rzk-inc="${esc(it.id)}" aria-label="${T.moreOf(esc(it.name))}">${I_PLUS}</button>`;
      b.style.setProperty('display', 'none', 'important');   // не hidden: display кнопки зі стилів сторінки його перебив би
    });
  }

  /* ---------- плашка кошика, лічильники ---------- */
  const bag = document.createElement('div');
  bag.className = 'rzk-bag'; bag.setAttribute('role', 'region'); bag.setAttribute('aria-label', T.cart);
  body.append(bag);
  function sync(){
    syncButtons();
    const n = count(), s = total();
    $$('[data-cart-count]').forEach(el => { el.textContent = n; el.toggleAttribute('data-zero', !n); });
    $$('[data-cart-sum]').forEach(el => { el.textContent = UAH(s); });
    bag.innerHTML = `<div class="s"><b>${UAH(s)}</b><span>${T.inCart(dishes(n))}</span></div><button class="rzk-btn" type="button" data-open-cart>${T.go} ${I_GO}</button>`;
    bag.classList.toggle('on', n > 0 && !cartD.open && !dishD.open);
    if (cartD.open) renderCart();
    if (dishD.open && dItem) renderDishPairs();
  }

  /* ---------- «Поруч добре»: що запропонувати до страви / до кошика ---------- */
  // за роллю — лише дрібне до вже взятого; іншу основну страву пропонує тільки data-pair
  const ROLE_NEXT = { main: ['side', 'drink', 'sauce'], side: ['drink', 'sauce'], drink: ['dessert'], dessert: ['drink'], sauce: [] };
  function pairsFor(it, n){
    const out = [];
    const ok = x => x && x.price != null && x.id !== it.id && !qOf(x.id) && !out.includes(x);
    it.pair.forEach(id => { const x = BY.get(id); if (ok(x)) out.push(x); });
    if (out.length < n) (ROLE_NEXT[it.role] || []).forEach(r => { for (const x of BY.values()) { if (out.length >= n) break; if (x.role === r && ok(x)) { out.push(x); break; } } });
    return out.slice(0, n);
  }
  function cartPairs(n){
    const out = [];
    Object.keys(cart).forEach(id => pairsFor(BY.get(id), n).forEach(x => { if (!out.includes(x) && !qOf(x.id)) out.push(x); }));
    return out.slice(0, n);
  }
  // мініатюри — лише якщо на сторінці в страв є фото; інакше рядок без порожньої колонки
  const anyImg = () => [...BY.values()].some(x => x.img);
  const thumb = it => it.img ? `<img class="th" src="${esc(it.img)}" alt="" loading="lazy">` : anyImg() ? '<span class="th none"></span>' : '';
  const miniRow = it => `<div class="rzk-line${thumb(it) ? '' : ' noimg'}">${thumb(it)}<div class="t"><b>${esc(it.name)}</b><span>${[it.weight, UAH(it.price)].filter(Boolean).join(' · ')}</span></div>
    <button class="rzk-plus" type="button" data-rzk-inc="${esc(it.id)}" aria-label="${T.addAria(esc(it.name), SAY(it.price))}">${I_PLUS}</button></div>`;

  /* ---------- тост «Додано» ---------- */
  const tst = document.createElement('div');
  tst.className = 'rzk-toast'; tst.setAttribute('role', 'status'); tst.setAttribute('aria-live', 'polite');
  body.append(tst);
  let tstT = 0;
  function toast(it){
    if (cartD.open || dishD.open) return;
    const p = pairsFor(it, 1)[0];
    tst.innerHTML = `<p>${T.added(esc(it.name))}</p>${p ? `<div class="pair"><span>${T.pair(esc(p.name), UAH(p.price))}</span><button class="rzk-plus" type="button" data-rzk-inc="${esc(p.id)}" data-rzk-quiet aria-label="${T.addOf(esc(p.name))}">${I_PLUS}</button></div>` : ''}`;
    tst.classList.add('on');
    clearTimeout(tstT); tstT = setTimeout(() => tst.classList.remove('on'), p ? 4500 : 2200);
  }

  /* ---------- діалоги ---------- */
  const mkDialog = (label) => { const d = document.createElement('dialog'); d.className = 'rzk-sheet'; d.setAttribute('aria-label', label); body.append(d); return d; };
  const dishD = mkDialog(T.dishDlg), cartD = mkDialog(T.cart);
  function openDlg(d){ if (!d.open) d.showModal(); document.documentElement.classList.add('rzk-lock'); bag.classList.remove('on'); tst.classList.remove('on'); }
  function closeDlg(d){ if (d.open) d.close(); }
  [dishD, cartD].forEach(d => {
    d.addEventListener('close', () => { if (!dishD.open && !cartD.open) document.documentElement.classList.remove('rzk-lock'); if (d === cartD && stage === 'done') stage = 'list'; lastRm = null; sync(); });
    d.addEventListener('click', e => { if (e.target === d) closeDlg(d); });   // клік по тлу
  });

  /* страва */
  let dItem = null, dQ = 1;
  function openDish(it){
    dItem = it; dQ = it.min;
    const meta = [it.weight, it.tags.includes('hot') ? T.hot : '', it.tags.includes('veg') ? T.veg : ''].filter(Boolean).join(' · ');
    dishD.innerHTML = `${it.img ? `<figure class="rzk-img"><img src="${esc(it.img)}" alt="${esc(it.name)}"></figure>` : ''}
      <div class="rzk-head"><div><h2>${esc(it.name)}</h2>${meta ? `<p>${esc(meta)}</p>` : ''}</div><button class="rzk-x" type="button" data-rzk-close aria-label="${T.close}">${I_X}</button></div>
      <div class="rzk-body">${it.desc ? `<p class="rzk-desc">${esc(it.desc)}</p>` : ''}<div data-rzk-pairs></div></div>
      <div class="rzk-foot">${it.price == null ? `<p class="rzk-hint">${T.askDot}</p>`
        : `<div class="rzk-buy"><span class="rzk-qty" role="group" aria-label="${T.qty}"><button type="button" data-rzk-dq="-1" aria-label="${T.less}">${I_MINUS}</button><output aria-live="polite" data-rzk-dqv>${it.min}</output><button type="button" data-rzk-dq="1" aria-label="${T.more}">${I_PLUS}</button></span>
          <button class="rzk-btn" type="button" data-rzk-dadd></button></div>`}</div>`;
    renderDishPairs(); dSync(); openDlg(dishD);
  }
  function renderDishPairs(){
    const box = $('[data-rzk-pairs]', dishD); if (!box || !dItem) return;
    const p = pairsFor(dItem, 2);
    box.innerHTML = p.length ? `<div class="rzk-ups"><p class="rzk-h">${T.pairs}</p>${p.map(miniRow).join('')}</div>` : '';
  }
  function dSync(){
    const v = $('[data-rzk-dqv]', dishD), b = $('[data-rzk-dadd]', dishD); if (!v || !b) return;
    v.textContent = dQ; b.textContent = T.addN(dQ, UAH(dItem.price * dQ));
  }

  /* кошик: list → form → done */
  let stage = 'list', lastRm = null, undoT = 0;
  const modes = (body.dataset.modes || 'pickup').split(/[\s,]+/).filter(m => ['pickup', 'delivery', 'dinein'].includes(m));
  const MODE_T = T.modes;
  const firstItem = () => { for (const x of BY.values()) if (x.price != null) return x; return null; };
  function renderCart(){
    const n = count(), s = total();
    if (stage === 'done') return;
    if (!n && stage === 'form') stage = 'list';
    const head = (t, sub) => `<div class="rzk-head"><div><h2>${t}</h2>${sub ? `<p>${sub}</p>` : ''}</div><button class="rzk-x" type="button" data-rzk-close aria-label="${T.closeCart}">${I_X}</button></div>`;
    const undo = lastRm ? `<div class="rzk-undo" role="status"><span>${T.removed(esc(BY.get(lastRm.id).name))}</span><button class="rzk-link" type="button" data-rzk-undo>${T.undo}</button></div>` : '';
    if (stage === 'list') {
      if (!n) {
        const f = firstItem();
        cartD.innerHTML = head(T.cart) + `<div class="rzk-body">${undo}<div class="rzk-empty"><h3>${T.empty}</h3><p>${T.emptyHint}</p>
          ${f ? `<button class="rzk-btn" type="button" data-rzk-inc="${esc(f.id)}">${T.addFirst(esc(f.name), UAH(f.price))}</button>` : ''}
          <button class="rzk-link" type="button" data-rzk-tomenu>${T.openMenu(pos(BY.size))}</button></div></div>`;
        return;
      }
      const ups = cartPairs(2);
      cartD.innerHTML = head(T.cart, `${dishes(n)} · ${UAH(s)}`)
        + `<div class="rzk-body"><div class="rzk-lines">${Object.entries(cart).map(([id, q]) => { const it = BY.get(id);
            return `<div class="rzk-line${thumb(it) ? '' : ' noimg'}">${thumb(it)}<div class="t"><b>${esc(it.name)}</b><span>${UAH(it.price)} × ${q} = ${UAH(it.price * q)}</span></div>
              <div class="c"><span class="rzk-step" role="group" aria-label="${T.inCart(esc(it.name))}"><button type="button" data-rzk-dec="${esc(id)}" data-rzk-cart aria-label="${T.lessOf(esc(it.name))}">${I_MINUS}</button><output>${q}</output><button type="button" data-rzk-inc="${esc(id)}" aria-label="${T.moreOf(esc(it.name))}">${I_PLUS}</button></span>
              <button class="rm" type="button" data-rzk-rm="${esc(id)}">${T.rm}</button></div></div>`; }).join('')}</div>
          ${undo}${ups.length ? `<div class="rzk-ups"><div><p class="rzk-h">${T.upsell}</p><p class="rzk-hint">${T.upsellHint}</p></div>${ups.map(miniRow).join('')}</div>` : ''}</div>
          <div class="rzk-foot"><div class="rzk-sum"><span>${T.total}</span><span>${UAH(s)}</span></div><button class="rzk-btn wide" type="button" data-rzk-form>${T.goOn(UAH(s))} ${I_GO}</button></div>`;
      return;
    }
    // stage === 'form'
    const addr = String(body.dataset.address || '').trim().slice(0, 120);
    cartD.innerHTML = head(T.form, `${dishes(n)} · ${UAH(s)}`)
      + `<div class="rzk-body"><form class="rzk-form" novalidate data-rzk-order>
        <div class="rzk-f"><label for="rzk-name">${T.name}</label><input id="rzk-name" name="name" autocomplete="given-name" placeholder="${T.namePh}" required><p class="err">${T.nameErr}</p></div>
        <div class="rzk-f"><label for="rzk-tel">${T.tel}</label><input id="rzk-tel" name="tel" type="tel" inputmode="tel" autocomplete="tel" placeholder="${MASK}…" required><p class="err">${T.telErr(MASK)}</p></div>
        ${modes.length > 1 ? `<div class="rzk-f"><span class="l">${T.way}</span><div class="rzk-seg">${modes.map((m, i) => `<label><input type="radio" name="way" value="${m}" ${i ? '' : 'checked'}>${MODE_T[m]}</label>`).join('')}</div></div>` : `<input type="hidden" name="way" value="${modes[0] || 'pickup'}">`}
        ${modes.includes('delivery') ? `<div class="rzk-f" data-rzk-addr hidden><label for="rzk-addr">${T.addr}</label><input id="rzk-addr" name="addr" autocomplete="street-address" placeholder="${T.addrPh}"><p class="err">${T.addrErr}</p></div>` : ''}
        <p class="rzk-hint" data-rzk-wayhint>${modes[0] === 'delivery' ? T.wayDelivery : addr ? T.wayPickup(esc(addr)) : T.wayAny}</p>
        <div class="rzk-f"><label for="rzk-note">${T.note}</label><textarea id="rzk-note" name="note" placeholder="${T.notePh}"></textarea></div>
        <button class="rzk-link" type="button" data-rzk-back>${T.back}</button></form></div>
        <div class="rzk-foot"><div class="rzk-sum"><span>${T.toPay}</span><span>${UAH(s)}</span></div><button class="rzk-btn wide" type="button" data-rzk-submit>${T.send(UAH(s))}</button></div>`;
    const f = $('[data-rzk-order]', cartD);
    const way = () => (f.elements.way && (f.elements.way.value || ($('input[name="way"]:checked', f) || {}).value)) || 'pickup';
    f.addEventListener('change', () => {
      const w = way(), a = $('[data-rzk-addr]', f);
      if (a) a.hidden = w !== 'delivery';
      $('[data-rzk-wayhint]', f).textContent = w === 'delivery' ? T.wayDelivery : w === 'dinein' ? T.wayDinein : addr ? T.wayPickup(addr) : T.wayAny;
    });
    f.addEventListener('input', e => { const x = e.target.closest('.rzk-f.bad'); if (x) x.classList.remove('bad'); });
    f.addEventListener('submit', e => e.preventDefault());
  }
  function submit(btn){
    const f = $('[data-rzk-order]', cartD); if (!f || btn.getAttribute('aria-busy') === 'true') return;
    const name = f.elements.name, tel = f.elements.tel, ad = f.elements.addr;
    const w = ($('input[name="way"]:checked', f) || f.elements.way || {}).value || 'pickup';
    const digits = tel.value.replace(/\D/g, '');
    const okTel = telOk(digits);   // для 380 — як було: /^(380\d{9}|0\d{9})$/
    name.closest('.rzk-f').classList.toggle('bad', !name.value.trim());
    tel.closest('.rzk-f').classList.toggle('bad', !okTel);
    if (ad) ad.closest('.rzk-f').classList.toggle('bad', w === 'delivery' && !ad.value.trim());
    const bad = $('.rzk-f.bad input', f); if (bad) { bad.focus(); return; }
    btn.setAttribute('aria-busy', 'true'); btn.innerHTML = '<span class="rzk-spin" aria-hidden="true"></span>' + T.sending;
    setTimeout(() => {   // демо: замовлення нікуди не йде
      const s = total(), n = count(), who = name.value.trim().slice(0, 40);
      hit('checkout', { n, sum: s, mode: w });
      stage = 'done'; cart = {}; save(); syncButtons();
      $$('[data-cart-count]').forEach(el => { el.textContent = 0; el.setAttribute('data-zero', ''); });
      $$('[data-cart-sum]').forEach(el => { el.textContent = UAH(0); });
      cartD.innerHTML = `<div class="rzk-head"><div><h2>${T.done}</h2></div><button class="rzk-x" type="button" data-rzk-close aria-label="${T.close}">${I_X}</button></div>
        <div class="rzk-body"><div class="rzk-done" role="status"><h3>${T.doneH(UAH(s))}</h3>
        <p>${T.doneP(dishes(n), esc(who))}</p>
        <button class="rzk-btn" type="button" data-rzk-tomenu>${T.toMenu}</button></div></div>`;
    }, 900);
  }
  function openCart(){ if (stage === 'done') stage = 'list'; hit('cart_open', { n: count() }, 'cart_open'); renderCart(); if (dishD.open) closeDlg(dishD); openDlg(cartD); }

  /* ---------- фільтр за міткою ---------- */
  let filt = '';
  function applyFilter(tag){
    filt = tag && filt !== tag ? tag : '';
    const scope = document.getElementById('menu') || $('[data-menu]') || body;
    $$('[data-item]', scope).forEach(el => { const it = BY.get(el.dataset.item); el.hidden = !!filt && !(it && it.tags.includes(filt)); });
    $$('[data-group]', scope).forEach(g => { const items = $$('[data-item]', g); g.hidden = !!filt && items.length > 0 && items.every(x => x.hidden); });
    $$('[data-filter]').forEach(b => {
      const on = (b.dataset.filter || '') === filt;
      if (b.type === 'checkbox') b.checked = !!filt && on; else b.setAttribute('aria-pressed', String(on));
    });
  }
  $$('[data-filter-count]').forEach(el => { const t = el.dataset.filterCount.toLowerCase(); el.textContent = [...BY.values()].filter(x => x.tags.includes(t)).length; });
  $$('[data-filter]').forEach(b => { if (b.type !== 'checkbox') b.setAttribute('aria-pressed', String(!(b.dataset.filter || ''))); });

  /* ---------- години: «зараз відчинено» за часом країни закладу (380 — київський, як було) ---------- */
  const DAYS = T.days;
  const H = String(body.dataset.hours || '').split(',').map(s => {
    const m = String(s).trim().match(/^(\d{1,2}):(\d{2})\s*[-–—]\s*(\d{1,2}):(\d{2})$/);
    return m ? { o: +m[1] * 60 + +m[2], c: +m[3] * 60 + +m[4], t: `${m[1].padStart(2, '0')}:${m[2]}–${m[3].padStart(2, '0')}:${m[4]}` } : null;
  });
  const hm = m => `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
  function kyiv(){
    if (TZ_MIN != null) { const n = new Date(Date.now() + TZ_MIN * 60000); return { d: (n.getUTCDay() + 6) % 7, m: n.getUTCHours() * 60 + n.getUTCMinutes() }; }
    try {
      const p = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: TZ || undefined, weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date()).map(x => [x.type, x.value]));
      return { d: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(p.weekday), m: +p.hour * 60 + +p.minute };
    } catch (e) { const n = new Date(); return { d: (n.getDay() + 6) % 7, m: n.getHours() * 60 + n.getMinutes() }; }
  }
  function hours(){
    if (H.length !== 7) return;
    const { d, m } = kyiv();
    const list = $('[data-hours-list]');
    if (list) list.innerHTML = DAYS.map((n, i) => `<li${i === d ? ' aria-current="date"' : ''}><span>${n}</span><span class="rzk-num">${H[i] ? H[i].t : T.off}</span></li>`).join('');
    // відкрито зараз: сьогоднішній інтервал (можливо, через північ) або вчорашній, що переходить через північ
    const today = H[d], yest = H[(d + 6) % 7];
    let open = false, closeAt = 0;
    if (today) { const c = today.c > today.o ? today.c : today.c + 1440; if (m >= today.o && m < c) { open = true; closeAt = c; } }
    if (!open && yest && yest.c <= yest.o && m < yest.c) { open = true; closeAt = yest.c; }
    let txt;
    if (open) { const left = closeAt - m; txt = left <= 60 ? T.soon(left, hm(closeAt)) : T.openNow(hm(closeAt)); }
    else {
      let k = 0, nd = null;
      if (today && m < today.o) nd = today;
      else for (k = 1; k <= 7; k++) { if (H[(d + k) % 7]) { nd = H[(d + k) % 7]; break; } }
      txt = !nd ? T.closed : T.opens(T.when(k, (d + k) % 7, DAYS), hm(nd.o));
    }
    $$('[data-now]').forEach(el => { el.textContent = txt; });
    $$('[data-now-dot]').forEach(el => { el.setAttribute('data-open', open ? '1' : '0'); });
  }
  hours(); setInterval(hours, 60000);

  /* ---------- одна делегація кліків ---------- */
  document.addEventListener('click', e => {
    const t = e.target.closest('button, a, [data-open], [data-filter]'); if (!t) return;
    const ds = t.dataset;
    // посилання на розділ: прокрутка вручну (у прев’ю сторінка в srcdoc — «#menu» інакше відкрив би інший документ)
    if (t.tagName === 'A' && !t.hasAttribute('data-open-cart') && !t.hasAttribute('data-add') && !t.hasAttribute('data-open')) {
      const h = t.getAttribute('href') || '';
      if (h === '#' || h.startsWith('#')) {
        e.preventDefault();
        const id = decodeURIComponent(h.slice(1)), el = id ? document.getElementById(id) : null;
        if (el) el.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); else if (!id) scrollTo({ top: 0, behavior: 'smooth' });
        if (cartD.open) closeDlg(cartD);
        return;
      }
      return;   // tel:, карти, Instagram — як звичайне посилання
    }
    if (ds.rzkInc !== undefined) { setQ(ds.rzkInc, qOf(ds.rzkInc) + 1, { quiet: cartD.open || dishD.open || ds.rzkQuiet !== undefined }); if (ds.rzkQuiet !== undefined) tst.classList.remove('on'); return; }
    if (ds.rzkDec !== undefined) { const id = ds.rzkDec; if (qOf(id) <= ((BY.get(id) || {}).min || 1) && cartD.open) armUndo(id, qOf(id)); setQ(id, qOf(id) - 1); return; }
    if (ds.rzkRm !== undefined) { armUndo(ds.rzkRm, qOf(ds.rzkRm)); setQ(ds.rzkRm, 0, { quiet: true }); return; }
    if (t.hasAttribute('data-rzk-undo') && lastRm) { const r = lastRm; lastRm = null; setQ(r.id, qOf(r.id) + r.q, { quiet: true }); return; }
    if (t.hasAttribute('data-rzk-close')) { closeDlg(t.closest('dialog')); return; }
    if (t.hasAttribute('data-rzk-form')) { stage = 'form'; renderCart(); const n = $('#rzk-name', cartD); if (n) n.focus({ preventScroll: true }); return; }
    if (t.hasAttribute('data-rzk-back')) { stage = 'list'; renderCart(); return; }
    if (t.hasAttribute('data-rzk-submit')) { submit(t); return; }
    if (t.hasAttribute('data-rzk-tomenu')) { closeDlg(cartD); stage = 'list'; const m = document.getElementById('menu') || $('[data-menu]'); if (m) m.scrollIntoView({ behavior: 'smooth' }); return; }
    if (ds.rzkDq !== undefined) { dQ = Math.max(dItem ? dItem.min : 1, Math.min(30, dQ + (+ds.rzkDq))); dSync(); return; }
    if (t.hasAttribute('data-rzk-dadd') && dItem) { setQ(dItem.id, qOf(dItem.id) + dQ, { quiet: true }); closeDlg(dishD); return; }
    if (t.hasAttribute('data-open-cart')) { e.preventDefault(); openCart(); return; }
    if (t.hasAttribute('data-add')) { e.preventDefault(); const it = itemOf(t); if (it) setQ(it.id, qOf(it.id) + 1); return; }
    if (t.hasAttribute('data-open')) { e.preventDefault(); const it = itemOf(t); if (it) openDish(it); return; }
    if (t.hasAttribute('data-filter') && t.type !== 'checkbox') { applyFilter((ds.filter || '').toLowerCase()); return; }
  });
  document.addEventListener('change', e => { const t = e.target; if (t.matches && t.matches('input[type="checkbox"][data-filter]')) applyFilter(t.checked ? (t.dataset.filter || '').toLowerCase() : ''); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.target.matches && e.target.matches('[data-rzk-order] input')) { e.preventDefault(); const b = $('[data-rzk-submit]', cartD); if (b) submit(b); }
    // data-open на не-кнопці (картка, рядок) — відкривається й з клавіатури
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[data-open]:not(button):not(a)')) { e.preventDefault(); const it = itemOf(e.target); if (it) openDish(it); }
  });
  $$('[data-open]:not(button):not(a)').forEach(el => { if (!el.hasAttribute('tabindex')) el.tabIndex = 0; el.setAttribute('role', el.getAttribute('role') || 'button'); el.style.cursor = 'pointer'; });
  function armUndo(id, q){ lastRm = { id, q }; clearTimeout(undoT); undoT = setTimeout(() => { lastRm = null; if (cartD.open && stage === 'list') renderCart(); }, 6000); }

  sync();
  window.RZK = { items: () => [...BY.values()], cart: () => Object.assign({}, cart), version: 1 };
})();
