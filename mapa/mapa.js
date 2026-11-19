'use strict';

const byId = id => document.getElementById(id);
const regions = new Intl.DisplayNames(['es'], { type: 'region' });
const numbers = new Intl.NumberFormat('es-ES');
const svgNamespace = 'http://www.w3.org/2000/svg';
let key = '';
let geography;
let activeRequest;
let view = location.hash === '#estados' ? 'states' : 'world';
let customRange;

function isoDay(date) {
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-');
}

function dateRange() {
  if (byId('period').value === 'custom') return customRange;
  const end = new Date();
  const start = new Date(end);
  start.setDate(start.getDate() - Number(byId('period').value) + 1);
  return [isoDay(start), isoDay(end)];
}

async function getRows(start, end, signal) {
  const url = new URL('https://roinaveiro.goatcounter.com/api/v0/stats/locations' + (view === 'states' ? '/US' : ''));
  // GoatCounter groups locations by calendar day in the account timezone.
  // Midday UTC selects the requested dates for the book's account.
  url.searchParams.set('start', start + 'T12:00:00Z');
  url.searchParams.set('end', end + 'T12:00:00Z');
  url.searchParams.set('limit', '100');
  const rows = [];
  while (true) {
    url.searchParams.set('offset', String(rows.length));
    const response = await fetch(url, {
      signal, headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
      credentials: 'omit', cache: 'no-store', redirect: 'error', referrerPolicy: 'no-referrer'
    });
    if (!response.ok) {
      const error = new Error('API');
      error.status = response.status;
      throw error;
    }
    const data = await response.json();
    // The API can return null for an empty Go slice.
    const page = data.stats ?? [];
    if (!Array.isArray(page) || (data.more && !page.length)) throw new Error('Respuesta incompleta');
    rows.push(...page);
    if (!data.more) return rows;
  }
}

function colorClass(n) {
  if (n >= 50) return 'c5';
  if (n >= 10) return 'c4';
  if (n >= 5) return 'c3';
  if (n >= 2) return 'c2';
  return n === 1 ? 'c1' : 'c0';
}

function placeName(shape) {
  if (view === 'world' && /^[A-Z]{2}$/.test(shape.id)) return regions.of(shape.id);
  return shape.name;
}

function draw(records) {
  const shapes = geography[view];
  const byCode = new Map(shapes.map(shape => [shape.id, shape]));
  const byName = new Map(shapes.map(shape => [shape.name, shape]));
  const counts = new Map();
  const body = byId('rows');
  body.replaceChildren();
  for (const row of records) {
    const shape = byCode.get(row.id) || byName.get(row.name);
    if (shape) counts.set(shape.id, row.count);
    const tr = body.insertRow();
    const cell = tr.insertCell();
    const label = shape ? placeName(shape) : row.name;
    if (view === 'world' && shape?.id === 'US') {
      const button = document.createElement('button');
      button.textContent = label;
      button.addEventListener('click', () => changeView('states'));
      cell.append(button);
    } else {
      cell.textContent = !label || label === '(unknown)' ? 'Sin identificar' : label;
    }
    tr.insertCell().textContent = numbers.format(row.count);
  }
  if (!records.length) {
    const cell = body.insertRow().insertCell();
    cell.colSpan = 2;
    cell.textContent = 'Sin visitantes en este período.';
  }
  const map = byId('map');
  const fragment = document.createDocumentFragment();
  for (const shape of shapes) {
    const count = counts.get(shape.id) || 0;
    const path = document.createElementNS(svgNamespace, 'path');
    path.setAttribute('d', shape.path);
    path.setAttribute('class', colorClass(count));
    path.dataset.id = shape.id;
    const title = document.createElementNS(svgNamespace, 'title');
    title.textContent = placeName(shape) + ' · ' + numbers.format(count);
    path.append(title);
    fragment.append(path);
  }
  map.replaceChildren(fragment);
}

function forget() {
  activeRequest?.abort();
  key = '';
  byId('key').value = '';
  byId('dashboard').hidden = true;
  byId('access').hidden = false;
  byId('map').replaceChildren();
  byId('rows').replaceChildren();
}

async function update() {
  if (!key) return;
  activeRequest?.abort();
  const controller = new AbortController();
  activeRequest = controller;
  const range = dateRange();
  byId('map').replaceChildren();
  byId('rows').replaceChildren();
  byId('status').textContent = 'Consultando GoatCounter…';
  try {
    if (!geography) {
      const response = await fetch('./geografia.json', { signal: controller.signal });
      if (!response.ok) throw new Error('Cartografía');
      geography = await response.json();
    }
    const records = await getRows(...range, controller.signal);
    if (controller.signal.aborted) return;
    draw(records);
    byId('access').hidden = true;
    byId('dashboard').hidden = false;
    const formatDay = day => new Intl.DateTimeFormat('es', {dateStyle:'medium'}).format(new Date(day + 'T12:00:00'));
    const label = range[0] === range[1] ? formatDay(range[0]) : range.map(formatDay).join(' – ');
    const time = new Date().toLocaleTimeString('es', {hour:'2-digit', minute:'2-digit'});
    byId('status').textContent = label + ' · Actualizado a las ' + time;
  } catch (error) {
    if (controller.signal.aborted) return;
    if (error.status === 401 || error.status === 403) {
      forget();
      byId('status').textContent = 'GoatCounter ha rechazado la clave. Comprueba que tiene permiso de lectura de estadísticas.';
      byId('key').focus();
    } else {
      byId('status').textContent = error.status === 429 ? 'GoatCounter ha recibido demasiadas consultas. Espera un momento y vuelve a intentarlo.' : 'No se pudieron cargar los datos. Comprueba la conexión y vuelve a intentarlo.';
      if (!byId('access').hidden) forget();
    }
  }
}

function changeView(next) {
  view = next;
  for (const id of ['world','states']) byId(id).setAttribute('aria-pressed', String(view === id));
  const states = view === 'states';
  byId('map-title').textContent = states ? 'Visitantes por estado' : 'Visitantes por país';
  byId('location').textContent = states ? 'Estado' : 'País';
  byId('map').setAttribute('viewBox', states ? '0 0 960 585' : '0 0 960 500');
  update();
}

byId('login').addEventListener('submit', event => {
  event.preventDefault();
  key = byId('key').value.trim();
  if (key) {
    byId('key').value = '';
    update();
  }
});
for (const id of ['world','states']) byId(id).addEventListener('click', () => changeView(id));
byId('map').addEventListener('click', event => {
  if (view === 'world' && event.target.closest('[data-id="US"]')) changeView('states');
});
byId('period').addEventListener('change', () => {
  const custom = byId('period').value === 'custom';
  byId('dates').hidden = !custom;
  if (custom && !customRange) {
    const today = isoDay(new Date());
    customRange = [today, today];
    byId('start').value = byId('end').value = today;
  }
  update();
});
byId('dates').addEventListener('submit', event => {
  event.preventDefault();
  if (byId('start').value > byId('end').value) {
    byId('status').textContent = 'La fecha final debe ser igual o posterior a la inicial.';
    return;
  }
  customRange = [byId('start').value, byId('end').value];
  update();
});
byId('refresh').addEventListener('click', update);
byId('disconnect').addEventListener('click', () => {
  forget();
  byId('status').textContent = 'Sesión cerrada.';
  byId('key').focus();
});
window.addEventListener('pagehide', () => {
  forget();
  byId('status').textContent = '';
});
setInterval(() => {
  if (key && !document.hidden && dateRange()[1] >= isoDay(new Date())) update();
}, 120000);
changeView(view);
