/* ============================================================
   HelpCo AI - site-wide conversion tracking (single source).
   PASTE YOUR IDs BELOW and every page is tracked automatically.

   1. GA4_ID      - Google Analytics 4, looks like  G-XXXXXXXXXX
   2. ADS_ID      - Google Ads tag, looks like      AW-XXXXXXXXXX
   3. META_PIXEL  - Meta (Facebook) Pixel, looks like 1234567890
   Leave any of them blank ("") to skip that platform.

   Conversion events fired across the site:
     generate_lead  - any lead form submitted        (Meta: Lead)
     book_demo      - Cal.com booking completed      (Meta: Schedule)
     phone_call     - phone number tapped/clicked    (Meta: Contact)
     chat_open      - chat or voice widget opened
   Map these to conversions in Google Ads / Meta Events Manager.
   Tip: /thanks.html also works as a page-load conversion.
   ============================================================ */
var GA4_ID = "";
var ADS_ID = "";
var META_PIXEL = "";

(function(){
  window.dataLayer = window.dataLayer || [];
  function gtag(){ dataLayer.push(arguments); }

  if (GA4_ID || ADS_ID){
    var sc = document.createElement('script');
    sc.async = true;
    sc.src = 'https://www.googletagmanager.com/gtag/js?id=' + (GA4_ID || ADS_ID);
    document.head.appendChild(sc);
    gtag('js', new Date());
    if (GA4_ID) gtag('config', GA4_ID);
    if (ADS_ID) gtag('config', ADS_ID);
    window.gtag = gtag;
  }

  if (META_PIXEL){
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', META_PIXEL);
    fbq('track', 'PageView');
  }

  /* Canonical track() - overwrites any early inline fallback */
  window.track = function(ev, params){
    try{
      dataLayer.push(Object.assign({event: ev}, params || {}));
      if (typeof window.gtag === 'function') window.gtag('event', ev, params || {});
      if (typeof window.fbq === 'function'){
        var map = {generate_lead:'Lead', book_demo:'Schedule', phone_call:'Contact'};
        map[ev] ? fbq('track', map[ev]) : fbq('trackCustom', ev, params || {});
      }
    }catch(e){}
  };

  /* ----------------------------------------------------------
     WEBSITE LEAD CATCHER - mirror every lead form to the dashboard.

     Before this, all 9 lead forms on the site posted ONLY to formsubmit.co,
     which emails Demo@HelpCoAI.com. Nothing reached the dashboard, Airtable or
     the CRM, so the Lead Catcher employee had no pipe. This listens for ANY form
     submit anywhere on the site and sends a copy to the Worker.

     Deliberately additive: it does not preventDefault, does not touch the form,
     and never blocks. The existing formsubmit.co email path keeps working exactly
     as before, so if this fails the lead is still emailed. Because it is a
     document-level listener it also covers forms added to the site later, with no
     per-page edit. Pages that preventDefault and post by ajax still fire a real
     'submit' event first, so they are covered too.
     ---------------------------------------------------------- */
  var LEAD_ENDPOINT = 'https://helpco-dashboard.lhajnaj.workers.dev/ingest/web';
  var INTAKE_KEY = '';   // optional; must match INTAKE_KEY in the Worker if set

  function mirrorLead(form){
    try{
      var data = {};
      new FormData(form).forEach(function(v, k){
        if (typeof v !== 'string') return;                 // skip files
        if (k.charAt(0) === '_' && k !== '_honey' && k !== '_subject') return;  // formsubmit control fields
        data[k] = v;
      });
      data.page = document.title + ' (' + location.pathname + ')';
      data.source = 'Website form';
      // Idempotency key so a double-click does not create two leads. Same form +
      // same contact within the same minute is treated as one submission.
      var who = (data.phone || data.Phone || data.email || data.Email || data.name || data.Name || '');
      data.externalId = 'form-' + (form.id || 'x') + '-' + who.replace(/\W/g,'') + '-' + Math.floor(Date.now()/60000);

      var headers = {'Content-Type':'application/json'};
      if (INTAKE_KEY) headers['x-helpco-intake'] = INTAKE_KEY;
      var body = JSON.stringify(data);

      // keepalive matters: these forms navigate away on submit, and without it the
      // browser cancels the request mid-flight and the lead is silently lost.
      // Deliberately NOT navigator.sendBeacon: a beacon carrying application/json
      // is not a CORS-safelisted content type, so it would need a preflight that
      // sendBeacon cannot perform, and the lead would vanish with no error.
      fetch(LEAD_ENDPOINT, {method:'POST', headers:headers, body:body, keepalive:true, mode:'cors'})
        .catch(function(){});
    }catch(e){}
  }

  /* Auto-bind: phone clicks + tagged CTAs + lead forms (once per page) */
  function bind(){
    if (window.__hcoBound) return; window.__hcoBound = true;
    document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
      a.addEventListener('click', function(){ window.track('phone_call',{}); });
    });
    document.querySelectorAll('[data-track]').forEach(function(a){
      a.addEventListener('click', function(){ window.track('cta_click',{cta:a.getAttribute('data-track')}); });
    });
    // Capture phase, so it runs even if a page handler stops propagation.
    document.addEventListener('submit', function(e){
      var f = e.target;
      if (!f || f.tagName !== 'FORM') return;
      mirrorLead(f);
    }, true);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind);
  else bind();
})();
