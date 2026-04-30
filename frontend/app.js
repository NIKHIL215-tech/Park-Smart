/* ── ParkSmart – Frontend Logic ─────────────────────────────────────────────
   All data now comes from the Java backend via fetch() → /api/...
   Session is kept in localStorage so it survives page refresh.
   ───────────────────────────────────────────────────────────────────────── */

const API = '/api';   // same-origin – Java server serves this file

// ── Session ──────────────────────────────────────────────────────────────
let currentUser  = JSON.parse(localStorage.getItem('parkUser') || 'null');
let selectedSlot = null;   // { id, floor, type }
let exitBookingId = null;
let allSlotsCache = [];    // cached for payment modal

function saveSession(user) {
  currentUser = user;
  localStorage.setItem('parkUser', JSON.stringify(user));
  document.getElementById('userBadge').textContent   = '👤 ' + user.name.split(' ')[0];
  document.getElementById('userBadge').style.display = 'block';
  document.getElementById('btnLogout').style.display = 'block';
  document.getElementById('navLogin').style.display  = 'none';
}
function clearSession() {
  currentUser = null;
  localStorage.removeItem('parkUser');
  document.getElementById('userBadge').style.display = 'none';
  document.getElementById('btnLogout').style.display = 'none';
  document.getElementById('navLogin').style.display  = '';
}
(function initSession() {
  if (currentUser) saveSession(currentUser);
})();

// ── Page navigation ──────────────────────────────────────────────────────
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const idx = { home:0, booking:1, history:2, admin:3, login:4 }[id];
  const btns = document.querySelectorAll('.nav-btn');
  if (idx !== undefined && btns[idx]) btns[idx].classList.add('active');
  if (id === 'home')    loadHome();
  if (id === 'booking') { loadBookingSlots(); initTimePickers(); }
  if (id === 'history') loadHistory();
  if (id === 'admin')   loadAdmin();
}

// ── API helpers ───────────────────────────────────────────────────────────
async function get(path) {
  const r = await fetch(API + path);
  return r.json();
}
async function post(path, body) {
  const r = await fetch(API + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return r.json();
}

// ── HOME PAGE ─────────────────────────────────────────────────────────────
async function loadHome() {
  const [stats, slots] = await Promise.all([get('/stats'), get('/slots')]);
  allSlotsCache = slots;

  document.getElementById('homeAvail').textContent    = stats.avail;
  document.getElementById('homeOccupied').textContent = stats.occupied;
  document.getElementById('homeActive').textContent   = stats.active;
  document.getElementById('homeRevenue').textContent  = '₹' + stats.revenue;
  document.getElementById('totalSlotPill').textContent = slots.length + ' slots';

  const grid = document.getElementById('homeSlotsGrid');
  grid.innerHTML = '';
  slots.forEach(slot => {
    const d = document.createElement('div');
    d.className = 'slot-card ' + (slot.status === 'Available' ? 'available' : 'occupied');
    d.innerHTML = `<div class="slot-num">S${slot.id}</div><div class="slot-floor">Floor ${slot.floor}</div><div class="slot-type-badge">${slot.type}</div>`;
    grid.appendChild(d);
  });
}

// ── BOOKING PAGE ──────────────────────────────────────────────────────────
async function loadBookingSlots(filterFloor) {
  const path = filterFloor ? `/slots?floor=${filterFloor}` : '/slots';
  const slots = await get(path);
  allSlotsCache = filterFloor ? allSlotsCache : slots; // update full cache on unfiltered load

  // Build floor filter pills (only on unfiltered load)
  if (!filterFloor) {
    const allSlots = slots;
    const floors   = [...new Set(allSlots.map(s => s.floor))].sort((a,b)=>a-b);
    const fc       = document.getElementById('floorFilter');
    fc.innerHTML   = '<button class="floor-pill active" onclick="filterFloor(\'all\',this)">All Floors</button>';
    floors.forEach(f => {
      fc.innerHTML += `<button class="floor-pill" onclick="filterFloor(${f},this)">Floor ${f}</button>`;
    });
  }

  const grid = document.getElementById('bookingSlotsGrid');
  grid.innerHTML = '';
  slots.forEach(slot => {
    const isSelected = selectedSlot && selectedSlot.id === slot.id;
    const d = document.createElement('div');
    d.className = 'slot-card ' + (isSelected ? 'selected' : slot.status === 'Available' ? 'available' : 'occupied');
    d.innerHTML = `<div class="slot-num">S${slot.id}</div><div class="slot-floor">Floor ${slot.floor}</div><div class="slot-type-badge">${slot.type}</div>`;
    if (slot.status === 'Available') d.onclick = () => selectSlot(slot);
    grid.appendChild(d);
  });
}

function filterFloor(floor, btn) {
  document.querySelectorAll('.floor-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadBookingSlots(floor === 'all' ? null : floor);
}

function selectSlot(slot) {
  selectedSlot = slot;
  const info = document.getElementById('selectedSlotInfo');
  info.className = 'selected-slot-info filled';
  info.innerHTML = `<strong>Slot S${slot.id} — Floor ${slot.floor}</strong>${slot.type} Parking · Available`;
  document.getElementById('bookType').value = slot.type;
  loadBookingSlots();
}

// ── TIME PICKERS ──────────────────────────────────────────────────────────
function localDateTimeString(date) {
  // Returns "YYYY-MM-DDTHH:MM" in local time for datetime-local inputs
  const pad = n => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function initTimePickers() {
  const minTime = new Date(Date.now() + 60 * 60 * 1000); // now + 1 hour
  const minStr  = localDateTimeString(minTime);

  const entryEl = document.getElementById('bookEntryTime');
  const exitEl  = document.getElementById('bookExitTime');

  entryEl.min   = minStr;
  entryEl.value = minStr;

  // Default exit = entry + 1 hour
  const defExit = new Date(minTime.getTime() + 60 * 60 * 1000);
  exitEl.min    = localDateTimeString(new Date(minTime.getTime() + 60 * 1000));
  exitEl.value  = localDateTimeString(defExit);

  updateEstFee();
}

function onEntryTimeChange() {
  const entryEl = document.getElementById('bookEntryTime');
  const exitEl  = document.getElementById('bookExitTime');
  const hint    = document.getElementById('entryHint');
  const entry   = new Date(entryEl.value);
  const minTime = new Date(Date.now() + 60 * 60 * 1000);

  if (!entryEl.value) { hint.textContent = ''; return; }

  if (entry < minTime) {
    hint.className   = 'field-hint error';
    hint.textContent = 'Must be at least 1 hour from now.';
  } else {
    hint.className   = 'field-hint ok';
    hint.textContent = 'Valid entry time.';
  }

  // Push exit min to at least 1 min after entry
  exitEl.min = localDateTimeString(new Date(entry.getTime() + 60 * 1000));
  if (exitEl.value && new Date(exitEl.value) <= entry) {
    exitEl.value = localDateTimeString(new Date(entry.getTime() + 60 * 60 * 1000));
  }
  updateEstFee();
}

function onExitTimeChange() { updateEstFee(); }

function updateEstFee() {
  const entryVal = document.getElementById('bookEntryTime').value;
  const exitVal  = document.getElementById('bookExitTime').value;
  const bar      = document.getElementById('estFeeBar');
  const feeEl    = document.getElementById('estFeeVal');

  if (!entryVal || !exitVal) { bar.style.display = 'none'; return; }

  const entry = new Date(entryVal);
  const exit  = new Date(exitVal);
  if (exit <= entry) { bar.style.display = 'none'; return; }

  const hours = Math.max(1, Math.ceil((exit - entry) / 3_600_000));
  feeEl.textContent  = `₹${hours * 50} (${hours} hr${hours > 1 ? 's' : ''} × ₹50)`;
  bar.style.display  = 'flex';
}

async function confirmBooking() {
  const vehicle    = document.getElementById('bookVehicle').value.trim().toUpperCase();
  const type       = document.getElementById('bookType').value;
  const name       = document.getElementById('bookName').value.trim();
  const entryVal   = document.getElementById('bookEntryTime').value;
  const msg        = document.getElementById('bookMsg');

  if (!vehicle || !name) return showMsg(msg, 'error', 'Please fill all fields.');
  if (!selectedSlot)     return showMsg(msg, 'error', 'Please select a parking slot first.');
  if (!entryVal)         return showMsg(msg, 'error', 'Please select an entry date and time.');

  const entry   = new Date(entryVal);
  const minTime = new Date(Date.now() + 60 * 60 * 1000);
  if (entry < minTime) return showMsg(msg, 'error', 'Entry time must be at least 1 hour from now.');

  const res = await post('/bookings', {
    vehicle,
    vehicle_type: type,
    slot_id:      selectedSlot.id,
    user_id:      currentUser ? currentUser.id : 0,
    name,
    entry_time:   entryVal   // "YYYY-MM-DDTHH:MM"
  });

  if (!res.success) return showMsg(msg, 'error', res.message);

  showMsg(msg, 'success', `✓ ${res.message}`);
  selectedSlot = null;
  document.getElementById('selectedSlotInfo').className   = 'selected-slot-info';
  document.getElementById('selectedSlotInfo').textContent = 'Click an available slot to select it';
  document.getElementById('bookVehicle').value = '';
  document.getElementById('bookName').value    = '';
  initTimePickers();
  loadBookingSlots();
}

// ── MY BOOKINGS PAGE ──────────────────────────────────────────────────────
async function loadHistory() {
  const path     = currentUser ? `/bookings?user_id=${currentUser.id}` : '/bookings';
  const bookings = await get(path);
  const list     = document.getElementById('historyList');

  if (!bookings.length) {
    list.innerHTML = '<p style="color:var(--text3);text-align:center;padding:3rem;">No bookings found.</p>';
    return;
  }

  list.innerHTML = bookings.map(b => {
    const entry   = fmt(b.entry_time);
    const exitStr = b.exit_time ? fmt(b.exit_time) : 'In Progress';
    const icon    = b.status === 'Active' ? '🚗' : '✅';
    const exitBtn = b.status === 'Active'
      ? `<button class="exit-btn" onclick="openPaymentModal(${b.id}, '${b.entry_time}', ${b.slot_id}, ${b.slot_floor}, '${b.vehicle}')">Exit →</button>`
      : '';
    return `<div class="history-card">
      <div class="history-icon ${b.status.toLowerCase()}">${icon}</div>
      <div class="history-info">
        <h4>${b.vehicle} · Slot S${b.slot_id} (Floor ${b.slot_floor})</h4>
        <p>${entry} → ${exitStr}</p>
      </div>
      <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:0.5rem;">
        <span class="status-badge ${b.status.toLowerCase()}">${b.status}</span>
        <span class="history-fee">${b.total_fee > 0 ? '₹' + b.total_fee : b.payment_status === 'Pending' ? 'Unpaid' : '—'}</span>
        ${exitBtn}
      </div>
    </div>`;
  }).join('');
}

// ── EXIT / PAYMENT MODAL ──────────────────────────────────────────────────
function openPaymentModal(bookingId, entryTimeStr, slotId, slotFloor, vehicle) {
  exitBookingId = bookingId;
  const now     = new Date();
  const entry   = new Date(entryTimeStr);
  const hours   = Math.max(1, Math.ceil((now - entry) / 3_600_000));
  const fee     = hours * 50;

  document.getElementById('paymentSummary').innerHTML = `
    <div class="payment-row"><span>Vehicle</span><span>${vehicle}</span></div>
    <div class="payment-row"><span>Slot</span><span>S${slotId} — Floor ${slotFloor}</span></div>
    <div class="payment-row"><span>Entry</span><span>${entry.toLocaleTimeString('en-IN', {timeStyle:'short'})}</span></div>
    <div class="payment-row"><span>Exit (estimated)</span><span>${now.toLocaleTimeString('en-IN', {timeStyle:'short'})}</span></div>
    <div class="payment-row"><span>Duration</span><span>${hours} hour${hours > 1 ? 's' : ''}</span></div>
    <div class="payment-row"><span>Rate</span><span>₹50 / hour</span></div>
    <div class="payment-row total"><span>Total Amount</span><span>₹${fee}</span></div>`;

  document.getElementById('paymentModal').classList.add('open');
}

async function processExit() {
  const res = await post('/bookings/exit', { booking_id: exitBookingId });
  closeModal();
  if (res.success) {
    alert(`Payment confirmed! Fee: ₹${res.fee}`);
    loadHistory();
  } else {
    alert('Error: ' + res.message);
  }
}

function closeModal()   { document.getElementById('paymentModal').classList.remove('open'); exitBookingId = null; }

// ── ADMIN PAGE ────────────────────────────────────────────────────────────
async function loadAdmin() {
  const [stats, bookings, users, slots] = await Promise.all([
    get('/stats'), get('/bookings'), get('/users'), get('/slots')
  ]);

  document.getElementById('adminUsers').textContent   = users.length;
  document.getElementById('adminAvail').textContent   = stats.avail;
  document.getElementById('adminActive').textContent  = stats.active;
  document.getElementById('adminRevenue').textContent = '₹' + stats.revenue;

  document.getElementById('adminBookingsTable').innerHTML = bookings.map(b => `<tr>
    <td><span style="font-family:'DM Mono',monospace;font-size:0.78rem;">#${b.id}</span></td>
    <td>${b.user_name}</td>
    <td><span class="tag ${b.vehicle_type === 'Car' ? 'car' : 'bike'}">${b.vehicle}</span></td>
    <td>S${b.slot_id} F${b.slot_floor}</td>
    <td style="font-size:0.8rem;">${fmtShort(b.entry_time)}</td>
    <td style="font-size:0.8rem;">${b.exit_time ? fmtShort(b.exit_time) : '—'}</td>
    <td><strong>${b.total_fee > 0 ? '₹' + b.total_fee : '—'}</strong></td>
    <td><span class="tag ${b.status.toLowerCase()}">${b.status}</span></td>
  </tr>`).join('');

  document.getElementById('adminUsersTable').innerHTML = users.map(u => `<tr>
    <td>${u.id}</td><td>${u.name}</td>
    <td style="font-size:0.8rem;">${u.email}</td><td>${u.phone}</td>
  </tr>`).join('');

  document.getElementById('adminSlotsTable').innerHTML = slots.map(s => `<tr>
    <td><strong>S${s.id}</strong></td>
    <td>Floor ${s.floor}</td>
    <td><span class="tag ${s.type.toLowerCase()}">${s.type}</span></td>
    <td><span class="tag ${s.status.toLowerCase()}">${s.status}</span></td>
  </tr>`).join('');
}

function openAddSlot()  { document.getElementById('addSlotModal').classList.add('open'); }
function closeAddSlot() { document.getElementById('addSlotModal').classList.remove('open'); }

async function addSlot() {
  const floor = parseInt(document.getElementById('newFloor').value);
  const type  = document.getElementById('newSlotType').value;
  const res   = await post('/slots', { floor, type });
  closeAddSlot();
  if (res.success) loadAdmin();
  else alert('Error: ' + res.message);
}

// ── AUTH ──────────────────────────────────────────────────────────────────
async function loginUser() {
  const email    = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const msg      = document.getElementById('loginMsg');
  if (!email || !password) return showMsg(msg, 'error', 'Please fill all fields.');

  const res = await post('/users/login', { email, password });
  if (res.success) {
    saveSession(res.user);
    showMsg(msg, 'success', 'Login successful! Redirecting...');
    setTimeout(() => showPage('home'), 800);
  } else {
    showMsg(msg, 'error', res.message);
  }
}

async function registerUser() {
  const name     = document.getElementById('regName').value.trim();
  const email    = document.getElementById('regEmail').value.trim();
  const phone    = document.getElementById('regPhone').value.trim();
  const password = document.getElementById('regPassword').value;
  const msg      = document.getElementById('registerMsg');
  if (!name || !email || !phone || !password) return showMsg(msg, 'error', 'All fields are required.');

  const res = await post('/users/register', { name, email, phone, password });
  if (res.success) {
    showMsg(msg, 'success', 'Account created! Please login.');
    setTimeout(() => { toggleAuth(); document.getElementById('loginEmail').value = email; }, 1200);
  } else {
    showMsg(msg, 'error', res.message);
  }
}

function logout() { clearSession(); showPage('home'); }

function toggleAuth() {
  const lb = document.getElementById('loginBox');
  const rb = document.getElementById('registerBox');
  lb.style.display = lb.style.display === 'none' ? 'block' : 'none';
  rb.style.display = rb.style.display === 'none' ? 'block' : 'none';
}

// ── Utilities ─────────────────────────────────────────────────────────────
function showMsg(el, type, text) {
  el.className = 'msg ' + type; el.textContent = text; el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function fmt(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
}

function fmtShort(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' });
}

// ── Boot ──────────────────────────────────────────────────────────────────
loadHome();
