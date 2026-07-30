/* ============================================================
   HelpCo AI - Website Lead Catcher chat widget.

   ONE LINE TO INSTALL, on any page:
     <script src="/chat.js" defer></script>

   Optional attributes on that tag:
     data-endpoint="https://.../chat"   override the Worker URL
     data-accent="#0d9488"              brand colour
     data-greeting="Hi! ..."            first message

   WHY THIS FILE EXISTS. The chatbot used to be a Base44 app in an iframe.
   Base44 wanted $40/mo to remove its badge, and it kept its OWN private copy
   of our pricing which drifted and quoted a real visitor a "$297/mo" plan
   that has never existed (2026-07-28). This widget holds no facts at all -
   it is a dumb pipe to the Worker, and the Worker holds the one prompt.

   SECURITY. There is no API key in this file and there must never be one.
   The browser talks only to our Worker; the Worker holds ANTHROPIC_API_KEY.
   Anything shipped here is public, permanently, to anyone who views source.
   ============================================================ */
(function () {
  if (window.__hcoChat) return;            // never double-mount
  window.__hcoChat = true;

  var me = document.currentScript || (function () {
    var s = document.getElementsByTagName('script');
    return s[s.length - 1];
  })();
  var attr = function (n, d) { return (me && me.getAttribute(n)) || d; };

  var ENDPOINT = attr('data-endpoint', 'https://helpco-dashboard.lhajnaj.workers.dev/chat');
  var ACCENT   = attr('data-accent', '#0d9488');
  var GREETING = attr('data-greeting',
    "Hi! I'm HelpCo AI's assistant. I can explain how our AI employees stop you losing customers, or get you booked in for a quick demo. What do you do?");

  var MAX_TURNS = 30;      // must not exceed the Worker's own cap
  var MAX_CHARS = 2000;
  var STORE_KEY = 'hco_chat_v1';

  /* ---------- state ---------- */
  var history = [];        // [{role, content, local?}]
  var busy = false;
  var open = false;

  try {
    var saved = sessionStorage.getItem(STORE_KEY);
    if (saved) history = JSON.parse(saved) || [];
  } catch (e) { history = []; }
  if (!history.length) history = [{ role: 'assistant', content: GREETING, local: true }];

  function persist() {
    try { sessionStorage.setItem(STORE_KEY, JSON.stringify(history.slice(-MAX_TURNS))); } catch (e) {}
  }
  function fire(ev, params) {
    try { if (typeof window.track === 'function') window.track(ev, params || {}); } catch (e) {}
  }

  /* ---------- styles ---------- */
  var css = ''
    + '.hco-fab{position:fixed;right:20px;bottom:20px;z-index:2147483000;width:60px;height:60px;border-radius:50%;'
    + 'border:0;cursor:pointer;background:' + ACCENT + ';color:#fff;box-shadow:0 6px 22px rgba(0,0,0,.28);'
    + 'display:flex;align-items:center;justify-content:center;transition:transform .18s ease}'
    + '.hco-fab:hover{transform:scale(1.06)}'
    + '.hco-fab svg{width:28px;height:28px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}'
    + '.hco-dot{position:absolute;top:2px;right:2px;width:13px;height:13px;border-radius:50%;background:#ef4444;border:2px solid #fff}'
    + '.hco-panel{position:fixed;right:20px;bottom:92px;z-index:2147483000;width:380px;max-width:calc(100vw - 32px);'
    + 'height:560px;max-height:calc(100vh - 120px);background:#fff;border-radius:16px;overflow:hidden;'
    + 'box-shadow:0 18px 60px rgba(0,0,0,.26);display:none;flex-direction:column;'
    + 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}'
    + '.hco-panel.hco-on{display:flex}'
    + '.hco-head{background:' + ACCENT + ';color:#fff;padding:14px 16px;display:flex;align-items:center;gap:10px;flex:0 0 auto}'
    + '.hco-head b{font-size:15px;font-weight:600;display:block;line-height:1.3}'
    + '.hco-head span{font-size:12px;opacity:.85}'
    + '.hco-x{margin-left:auto;background:transparent;border:0;color:#fff;font-size:26px;line-height:1;cursor:pointer;opacity:.85;padding:0 2px}'
    + '.hco-x:hover{opacity:1}'
    + '.hco-log{flex:1 1 auto;overflow-y:auto;padding:16px;background:#f7f8f8;display:flex;flex-direction:column;gap:10px}'
    + '.hco-msg{max-width:85%;padding:10px 13px;border-radius:14px;font-size:14px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;overflow-wrap:anywhere}'
    + '.hco-a{align-self:flex-start;background:#fff;color:#1f2937;border:1px solid #e5e7eb;border-bottom-left-radius:4px}'
    + '.hco-u{align-self:flex-end;background:' + ACCENT + ';color:#fff;border-bottom-right-radius:4px}'
    + '.hco-msg a{color:inherit;text-decoration:underline}'
    + '.hco-a a{color:' + ACCENT + '}'
    + '.hco-typing{align-self:flex-start;background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:12px 14px;display:flex;gap:4px}'
    + '.hco-typing i{width:7px;height:7px;border-radius:50%;background:#9ca3af;display:block;animation:hcob 1.3s infinite}'
    + '.hco-typing i:nth-child(2){animation-delay:.18s}.hco-typing i:nth-child(3){animation-delay:.36s}'
    + '@keyframes hcob{0%,60%,100%{opacity:.3;transform:translateY(0)}30%{opacity:1;transform:translateY(-4px)}}'
    + '.hco-foot{flex:0 0 auto;border-top:1px solid #e5e7eb;background:#fff;padding:10px;display:flex;gap:8px;align-items:flex-end}'
    + '.hco-in{flex:1;border:1px solid #d1d5db;border-radius:10px;padding:10px 12px;font-size:14px;font-family:inherit;'
    + 'resize:none;max-height:110px;line-height:1.4;outline:none}'
    + '.hco-in:focus{border-color:' + ACCENT + '}'
    + '.hco-send{background:' + ACCENT + ';color:#fff;border:0;border-radius:10px;width:40px;height:40px;cursor:pointer;'
    + 'display:flex;align-items:center;justify-content:center;flex:0 0 auto}'
    + '.hco-send:disabled{opacity:.45;cursor:default}'
    + '.hco-send svg{width:18px;height:18px;fill:#fff}'
    + '.hco-legal{flex:0 0 auto;background:#fff;padding:0 12px 9px;font-size:11px;color:#9ca3af;text-align:center}'
    + '@media(max-width:520px){.hco-panel{right:8px;left:8px;bottom:84px;width:auto;height:calc(100vh - 104px)}'
    + '.hco-fab{right:14px;bottom:14px;width:54px;height:54px}}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  /* ---------- markup ---------- */
  var fab = document.createElement('button');
  fab.className = 'hco-fab';
  fab.type = 'button';
  fab.setAttribute('aria-label', 'Open chat');
  fab.innerHTML = '<svg viewBox="0 0 24 24"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.9 8.9 0 0 1-3.8-.9L3 20.5l1.5-4.5A8.4 8.4 0 0 1 3.6 12a8.4 8.4 0 0 1 8.4-8.4h.5a8.4 8.4 0 0 1 8.5 7.9z"/></svg>'
    + '<span class="hco-dot"></span>';

  var panel = document.createElement('div');
  panel.className = 'hco-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Chat with HelpCo AI');
  panel.innerHTML =
      '<div class="hco-head"><div><b>HelpCo AI</b><span>Usually replies instantly</span></div>'
    + '<button class="hco-x" type="button" aria-label="Close chat">&times;</button></div>'
    + '<div class="hco-log" role="log" aria-live="polite"></div>'
    + '<div class="hco-foot">'
    + '<textarea class="hco-in" rows="1" placeholder="Type your message..." aria-label="Your message" maxlength="' + MAX_CHARS + '"></textarea>'
    + '<button class="hco-send" type="button" aria-label="Send"><svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg></button>'
    + '</div>'
    + '<div class="hco-legal">AI assistant. For anything urgent call 941-941-9930.</div>';

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var log  = panel.querySelector('.hco-log');
  var box  = panel.querySelector('.hco-in');
  var send = panel.querySelector('.hco-send');
  var xBtn = panel.querySelector('.hco-x');
  var dot  = fab.querySelector('.hco-dot');

  /* ---------- rendering ----------
     Model output goes into the DOM, so escape FIRST and only then turn plain
     URLs into links. Never assign raw model text to innerHTML. */
  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function linkify(safe) {
    return safe
      .replace(/\b(https?:\/\/[^\s<]+[^\s<.,:;"')\]])/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
      .replace(/\b([\w.+-]+@[\w-]+\.[\w.]{2,})\b/g, '<a href="mailto:$1">$1</a>')
      .replace(/\b(941-941-9930)\b/g, '<a href="tel:+19419419930">$1</a>');
  }
  function bubble(role, text) {
    var d = document.createElement('div');
    d.className = 'hco-msg ' + (role === 'user' ? 'hco-u' : 'hco-a');
    d.innerHTML = linkify(esc(text));
    log.appendChild(d);
    return d;
  }
  function scroll() { log.scrollTop = log.scrollHeight; }

  function paint() {
    log.innerHTML = '';
    history.forEach(function (m) { bubble(m.role, m.content); });
    scroll();
  }

  var typingEl = null;
  function typing(on) {
    if (on && !typingEl) {
      typingEl = document.createElement('div');
      typingEl.className = 'hco-typing';
      typingEl.innerHTML = '<i></i><i></i><i></i>';
      log.appendChild(typingEl);
      scroll();
    } else if (!on && typingEl) {
      typingEl.remove();
      typingEl = null;
    }
  }

  /* ---------- open / close ---------- */
  function setOpen(v) {
    open = v;
    panel.classList.toggle('hco-on', v);
    fab.setAttribute('aria-label', v ? 'Close chat' : 'Open chat');
    if (v) {
      dot.style.display = 'none';
      paint();
      setTimeout(function () { box.focus(); }, 60);
      if (!setOpen.fired) { fire('chat_open', { widget: 'website_chat' }); setOpen.fired = true; }
    }
  }
  fab.addEventListener('click', function () { setOpen(!open); });
  xBtn.addEventListener('click', function () { setOpen(false); fab.focus(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && open) { setOpen(false); fab.focus(); }
  });

  /* ---------- send ---------- */
  function autoGrow() {
    box.style.height = 'auto';
    box.style.height = Math.min(box.scrollHeight, 110) + 'px';
  }
  box.addEventListener('input', autoGrow);
  box.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
  });
  send.addEventListener('click', submit);

  function submit() {
    if (busy) return;
    var text = box.value.trim();
    if (!text) return;

    box.value = '';
    autoGrow();
    history.push({ role: 'user', content: text.slice(0, MAX_CHARS) });
    history = history.slice(-MAX_TURNS);
    bubble('user', text);
    persist();
    scroll();

    busy = true;
    send.disabled = true;
    typing(true);

    // Only real turns go to the model. The local greeting is cosmetic and the
    // Worker would drop a leading assistant turn anyway.
    var wire = history.filter(function (m) { return !m.local; })
                      .map(function (m) { return { role: m.role, content: m.content }; });

    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: wire }),
      mode: 'cors'
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        typing(false);
        var reply = (d && d.reply) || "Sorry, I did not catch that. Could you say it another way?";
        history.push({ role: 'assistant', content: reply });
        history = history.slice(-MAX_TURNS);
        bubble('assistant', reply);
        persist();
        scroll();
        if (d && d.lead) fire('generate_lead', { source: 'website_chat' });
      })
      .catch(function () {
        typing(false);
        var msg = "I could not reach our system just then. Please call 941-941-9930 or email Demo@HelpCoAI.com and we will help you right away.";
        history.push({ role: 'assistant', content: msg });
        bubble('assistant', msg);
        persist();
        scroll();
      })
      .then(function () {
        busy = false;
        send.disabled = false;
        if (open) box.focus();
      });
  }
})();
