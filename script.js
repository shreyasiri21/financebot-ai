const messagesEl = document.getElementById('messages');
const form = document.getElementById('chatForm');
const input = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const suggestions = document.getElementById('suggestions');

const sessionId = 'sess-' + Math.random().toString(36).slice(2);
let entryCount = 1;

function pad(n) { return String(n).padStart(3, '0'); }

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Stamp initial welcome message timestamp
document.querySelectorAll('[data-time]').forEach(el => el.textContent = timeNow());

function formatContent(text) {
  // Escape HTML, then apply light markdown-ish formatting for readability.
  const escape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  let safe = escape(text);

  // Bold **text**
  safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Highlight rupee amounts
  safe = safe.replace(/(₹[\d,]+(\.\d+)?\s?(lakh|crore|L|Cr)?)/g, '<span class="amount">$1</span>');

  // Split into paragraphs / bullet lists
  const lines = safe.split('\n').filter(l => l.trim() !== '');
  let html = '';
  let inList = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (/^[-*•]\s+/.test(trimmed)) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += `<li>${trimmed.replace(/^[-*•]\s+/, '')}</li>`;
    } else {
      if (inList) { html += '</ul>'; inList = false; }
      html += `<p>${trimmed}</p>`;
    }
  }
  if (inList) html += '</ul>';
  return html;
}

function addEntry(role, content) {
  entryCount += 1;
  const wrapper = document.createElement('div');
  wrapper.className = `entry ${role === 'user' ? 'user-entry' : 'bot-entry'}`;
  wrapper.innerHTML = `
    <div class="entry-index">${pad(entryCount)}</div>
    <div class="entry-body">
      <div class="entry-meta">
        <span class="entry-tag">${role === 'user' ? 'You' : 'FinanceBot'}</span>
        <span class="entry-time">${timeNow()}</span>
      </div>
      ${role === 'user' ? `<p>${content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p>` : formatContent(content)}
    </div>
  `;
  messagesEl.appendChild(wrapper);
  scrollToBottom();
  return wrapper;
}

function addTyping() {
  const wrapper = document.createElement('div');
  wrapper.className = 'entry bot-entry typing';
  wrapper.id = 'typingEntry';
  wrapper.innerHTML = `
    <div class="entry-index">${pad(entryCount + 1)}</div>
    <div class="entry-body">
      <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
    </div>
  `;
  messagesEl.appendChild(wrapper);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typingEntry');
  if (el) el.remove();
}

function scrollToBottom() {
  const ledger = document.getElementById('ledger');
  ledger.scrollTop = ledger.scrollHeight;
}

async function sendMessage(text) {
  if (!text.trim()) return;
  suggestions.style.display = 'none';
  addEntry('user', text);
  input.value = '';
  sendBtn.disabled = true;
  addTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId })
    });
    const data = await res.json();
    removeTyping();
    if (data.error) {
      addEntry('bot', `Something went wrong on my end: ${data.error}`);
    } else {
      addEntry('bot', data.reply);
    }
  } catch (err) {
    removeTyping();
    addEntry('bot', 'I couldn\'t reach the server. Please check your connection and try again.');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  sendMessage(input.value);
});

suggestions.addEventListener('click', (e) => {
  const btn = e.target.closest('.chip');
  if (btn) sendMessage(btn.dataset.q);
});

resetBtn.addEventListener('click', async () => {
  await fetch('/api/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId })
  });
  messagesEl.innerHTML = '';
  entryCount = 0;
  suggestions.style.display = 'flex';
  addEntry('bot', 'Fresh page started. What would you like to know?');
});
