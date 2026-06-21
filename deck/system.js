/* ============================================================
   HAL Predictive-AI Workshop — DECK ENGINE + WIDGET LIBRARY
   deck/system.js
   Vanilla JS, no framework, no build step, fully offline.
   Pairs with deck/system.css.
   ------------------------------------------------------------
   Public surface:
     window.HALDeck.init(opts)            -> boot a deck
     window.HALWidgets.<name>(el, opts)   -> instantiate a widget
   Widgets also auto-init from data-widget="<name>" attributes.
   ------------------------------------------------------------
   NO NETWORK AT RUNTIME: this engine, every widget, and the
   shared CSS are fully self-contained — no CDN, no fetch(), no
   external fonts/links/scripts. The only assets referenced are
   local ../figs/*.svg via relative paths that must resolve from
   file:// on the presenter laptop. Keep it that way: anything new
   must ship in-repo so the deck runs offline in a HAL room.
   ============================================================ */
(function (global) {
  'use strict';

  /* ---------- tiny helpers ---------- */
  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  };
  const parseJSON = (s, fb) => { try { return s ? JSON.parse(s) : fb; } catch (e) { return fb; } };

  /* ============================================================
     SEASON MAP — four sessions, current one lit
     ============================================================ */
  const SESSIONS = [
    { id: 'text1',   label: 'Text I',   href: '01-text-i.html' },
    { id: 'text2',   label: 'Text II',  href: '02-text-ii.html' },
    { id: 'speech1', label: 'Speech I', href: '03-speech-i.html' },
    { id: 'speech2', label: 'Speech II',href: '04-speech-ii.html' }
  ];

  function buildSeasonMap(current) {
    const idx = SESSIONS.findIndex(s => s.id === current);
    const wrap = el('nav', 'seasonmap');
    wrap.setAttribute('aria-label', 'Season map');
    SESSIONS.forEach((s, k) => {
      if (k) wrap.appendChild(el('span', 'smline'));
      const a = el('a', 'smdot' + (k < idx ? ' done' : k === idx ? ' now' : ''));
      a.href = s.href;
      a.title = s.label;
      a.appendChild(el('i'));
      a.appendChild(el('span', null, s.label));
      if (k === idx) a.removeAttribute('href'); // current isn't a link
      wrap.appendChild(a);
    });
    return wrap;
  }

  /* ============================================================
     DECK ENGINE
     ============================================================ */
  const HALDeck = {
    init(opts) {
      opts = opts || {};
      const session = opts.session || document.body.getAttribute('data-session') || 'text1';
      document.body.setAttribute('data-session', session);

      const deck = $('#deck') || $('.deck');
      const slides = $$('.slide', deck);
      const prog = $('#prog') || (function(){ const p=el('div','progress'); p.id='prog'; document.body.appendChild(p); return p; })();

      // chrome the engine owns
      document.body.appendChild(buildSeasonMap(session));
      const counter = ensure('counter', 'counter', '<b>1</b> / ' + slides.length);
      ensure('brand', 'brand', opts.brand || 'HAL · Predictive AI');
      ensure('hint', 'hint', '&larr; &rarr; / Space move · F fullscreen · S notes · O overview');
      const notes = ensureFixed('notes', 'notes',
        '<div class="lbl">Speaker notes</div><div class="txt" id="notesTxt"></div>');
      const notesTxt = $('#notesTxt', notes);
      const overview = ensureFixed('overview', 'overview',
        '<h5>Overview — click a slide to jump (O / Esc to close)</h5><div class="ovgrid" id="ovgrid"></div>');
      const ovgrid = $('#ovgrid', overview);
      const nav = ensureFixed('nav', 'nav', '<div class="half" id="navPrev"></div><div class="half" id="navNext"></div>');

      let i = 0, frag = 0, notesOn = false, ovOn = false;

      const fragsOf = s => $$('.frag, ul.frags > li', s).filter(f => !f.closest('.notes,.overview'));

      function applyFrags() {
        fragsOf(slides[i]).forEach((f, k) => f.classList.toggle('on', k < frag));
      }
      function show(n, atEnd) {
        n = clamp(n, 0, slides.length - 1);
        slides[i].classList.remove('active');
        i = n;
        const f = fragsOf(slides[i]);
        frag = atEnd ? f.length : 0;
        slides[i].classList.add('active');
        applyFrags();
        prog.style.width = ((i + 1) / slides.length * 100) + '%';
        counter.innerHTML = '<b>' + (i + 1) + '</b> / ' + slides.length;
        notesTxt.textContent = slides[i].getAttribute('data-note') || '—';
        if (ovgrid) $$('.ovcell', ovgrid).forEach((c, k) => c.classList.toggle('now', k === i));
        location.hash = i + 1;
        slides[i].dispatchEvent(new CustomEvent('slideshown', { bubbles: false }));
      }
      function next() {
        const total = fragsOf(slides[i]).length;
        if (frag < total) { frag++; applyFrags();
          slides[i].dispatchEvent(new CustomEvent('fragment', { detail:{ index: frag } })); }
        else if (i < slides.length - 1) show(i + 1, false);
      }
      function prev() {
        if (frag > 0) { frag--; applyFrags(); }
        else if (i > 0) show(i - 1, true);
      }

      // overview grid
      slides.forEach((s, k) => {
        const cell = el('div', 'ovcell');
        const t = (s.getAttribute('data-title')
          || (s.querySelector('h1,h2,.assert,.eyebrow,.meta') || {}).textContent
          || 'Slide').trim().slice(0, 80);
        cell.innerHTML = '<div class="n">' + (k + 1) + '</div><div class="t">' + t + '</div>';
        cell.addEventListener('click', () => { toggleOverview(false); show(k, false); });
        ovgrid.appendChild(cell);
      });
      function toggleOverview(on) { ovOn = on; overview.classList.toggle('on', ovOn); }

      // keyboard
      document.addEventListener('keydown', (e) => {
        const k = e.key;
        if (k === 'ArrowRight' || k === 'PageDown' || k === ' ' || k === 'Spacebar') { e.preventDefault(); next(); }
        else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); prev(); }
        else if (k === 'Home') show(0, false);
        else if (k === 'End') show(slides.length - 1, false);
        else if (k === 'f' || k === 'F') { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
        else if (k === 's' || k === 'S') { notesOn = !notesOn; notes.classList.toggle('on', notesOn); }
        else if (k === 'o' || k === 'O') toggleOverview(!ovOn);
        else if (k === 'Escape') { if (ovOn) toggleOverview(false); if (notesOn) { notesOn = false; notes.classList.remove('on'); } }
      });

      // click / tap halves
      $('#navNext', nav).addEventListener('click', next);
      $('#navPrev', nav).addEventListener('click', prev);

      // boot widgets, then show
      HALWidgets.autoInit(document);

      // ---- EXPORT MODE (the takeaway-PDF contract) ----------
      // ?export in the URL (or opts.export) turns the deck into one
      // verified print artifact: every slide visible one-per-page,
      // all fragments revealed, every widget frozen in its teaching
      // state, money backgrounds promoted to real <img> so they
      // survive print. Recipe: open ?export -> Cmd-P -> landscape,
      // background graphics ON. Also runs on beforeprint so a plain
      // Cmd-P (no flag) still produces the same frozen artifact.
      const wantExport = /(?:\?|&)export\b/.test(location.search) ||
        /\bexport\b/.test((location.hash || '')) || opts.export === true;
      function enterExport() {
        document.body.classList.add('export');
        // reveal EVERY fragment across EVERY slide
        $$('.frag, ul.frags > li', deck).forEach(f => f.classList.add('on'));
        // un-mute any one-accent signalling so nothing vanishes on paper
        // (handled in CSS; here we just freeze the widgets)
        freezeAllWidgets();
        promoteMoneyImages();
      }
      function freezeAllWidgets() {
        $$('[data-widget]', deck).forEach(n => {
          try { if (typeof n.freeze === 'function') n.freeze(); } catch (e) {}
        });
      }
      // Convert any .moneyimg CSS background-image to a real inline <img>
      // (most browsers DROP CSS backgrounds from print) so figures survive.
      function promoteMoneyImages() {
        $$('.moneyimg', deck).forEach(mi => {
          if (mi.querySelector('img')) return;
          const bg = getComputedStyle(mi).backgroundImage || '';
          const m = bg.match(/url\((['"]?)(.*?)\1\)/);
          if (!m || !m[2]) return;
          const img = el('img');
          img.src = m[2];
          img.alt = '';
          img.style.cssText = 'width:100%;height:100%;object-fit:contain;display:block';
          mi.style.backgroundImage = 'none';
          mi.appendChild(img);
        });
      }
      if (wantExport) enterExport();
      // a bare Cmd-P (no flag) still freezes widgets + promotes images
      window.addEventListener('beforeprint', () => { freezeAllWidgets(); promoteMoneyImages(); });

      show((parseInt((location.hash || '').replace('#', ''), 10) || 1) - 1, false);
      window.addEventListener('hashchange', () => {
        const h = (parseInt((location.hash || '').replace('#', ''), 10) || 1) - 1;
        if (h !== i) show(h, false);
      });

      return { show, next, prev, slides };

      // local chrome helpers
      function ensure(id, cls, html) {
        let n = document.getElementById(id);
        if (!n) { n = el('div', cls, html); n.id = id; document.body.appendChild(n); }
        return n;
      }
      function ensureFixed(id, cls, html) {
        let n = document.getElementById(id);
        if (!n) { n = el('div', cls, html); n.id = id; document.body.appendChild(n); }
        return n;
      }
    }
  };

  /* ============================================================
     WIDGET LIBRARY
     Each widget is self-contained, offline, idempotent.
     Auto-init: <div data-widget="predictReveal" data-...>
     ============================================================ */
  const HALWidgets = {
    autoInit(root) {
      $$('[data-widget]', root).forEach(node => {
        if (node.__halInit) return;
        const name = node.getAttribute('data-widget');
        if (typeof this[name] === 'function') {
          this[name](node, dataset(node));
          node.__halInit = true;
        }
      });
    },

    /* ---- cmatrix : first-class confusion-matrix widget -----
       A 2x2 confusion matrix built in HTML/CSS grid (NOT an
       image) so it inherits the type system and animates a
       TWO-BEAT progressive build:
         beat 1  -> lights the diagonal (the WIN, teal/green)
         beat 2  -> dims the diagonal to grey + IGNITES the
                    costly-miss cell (coral + .spot ring + a
                    hairline callout)
       Presenter-driven: each slide "fragment" advances a beat;
       .freeze() (export) paints BOTH beats at once.

       data-rows    : JSON ["Urgent","Routine"]  (true,   top->bottom)
       data-cols    : JSON ["Urgent","Routine"]  (predicted, L->R)
       data-cells   : JSON [[c00,c01],[c10,c11]]  row-major counts
                      (row = true class, col = predicted class)
       data-win     : JSON [[r,c],...] diagonal "win" cells   (default both diagonal)
       data-miss    : JSON [r,c] the costly false-negative cell (default [0,1])
       data-callout : text for the hairline (default "a real crack, called routine")
       data-total   : optional override for the denominator (else summed)
       data-stats   : "0" to hide the accuracy/recall tallies
       data-head    : optional widget heading
       --------------------------------------------------------- */
    cmatrix(node, ds) {
      node.classList.add('widget', 'cmx');
      const rows = parseJSON(ds.rows, ['Urgent', 'Routine']);
      const cols = parseJSON(ds.cols, ['Urgent', 'Routine']);
      const cells = parseJSON(ds.cells, [[58, 2], [46, 294]]);
      const wins = parseJSON(ds.win, [[0, 0], [1, 1]]);
      const miss = parseJSON(ds.miss, [0, 1]);
      const callout = ds.callout || 'a real crack, called routine';
      const showStats = ds.stats !== '0';
      const isWin = (r, c) => wins.some(w => w[0] === r && w[1] === c);
      const isMiss = (r, c) => miss[0] === r && miss[1] === c;
      const sum = cells.flat().reduce((a, b) => a + b, 0);
      const total = parseInt(ds.total, 10) || sum;
      // tags name each cell honestly (caught / costly miss / false alarm / correct)
      const tagFor = (r, c) => {
        if (isMiss(r, c)) return 'costly miss';
        if (isWin(r, c)) return r === 0 ? 'caught' : 'correct';
        return 'false alarm';
      };
      const cellHTML = (r, c) => {
        const cls = 'cmx-cell c' + r + '' + c +
          (isWin(r, c) ? ' win' : '') + (isMiss(r, c) ? ' miss' : '');
        return '<div class="' + cls + '"><span class="num">' + cells[r][c] +
          '</span><span class="tag">' + tagFor(r, c) + '</span></div>';
      };
      // accuracy = trace/total ; urgent-recall = TP / (TP + FN) on row 0
      const correct = cells.reduce((a, row, r) => a + row[r], 0);
      const acc = total ? Math.round(correct / total * 100) : 0;
      const rowSum0 = cells[0][0] + cells[0][1];
      const recall = rowSum0 ? Math.round(cells[0][0] / rowSum0 * 100) : 0;

      node.innerHTML =
        (ds.head ? '<div class="whead">' + ds.head + '</div>' : '') +
        '<div class="cmx-grid">' +
          '<div class="cmx-corner"></div>' +
          '<div class="cmx-axtop">Predicted &rarr;</div>' +
          '<div class="cmx-axleft">&larr; True</div>' +
          '<div class="cmx-ch c0">' + cols[0] + '</div>' +
          '<div class="cmx-ch c1">' + cols[1] + '</div>' +
          '<div class="cmx-rh r0">' + rows[0] + '</div>' +
          '<div class="cmx-rh r1">' + rows[1] + '</div>' +
          cellHTML(0, 0) + cellHTML(0, 1) +
          cellHTML(1, 0) + cellHTML(1, 1) +
          '<div class="cmx-callout">' + callout + '</div>' +
          (showStats ?
            '<div class="cmx-stats">' +
              '<div>Accuracy<b>' + acc + '%</b></div>' +
              '<div class="rec">Urgent recall<b>' + recall + '%</b></div>' +
              '<div>Of <b style="color:var(--paper)">' + total + '</b> hidden notes</div>' +
            '</div>' : '') +
        '</div>';

      node.setAttribute('data-beat', '0');
      let beat = 0;
      function setBeat(b) {
        beat = clamp(b, 0, 2);
        node.setAttribute('data-beat', String(beat));
      }
      node.setBeat = setBeat;
      // freeze() (export): paint BOTH build beats — the full lesson on paper.
      node.freeze = () => { node.setAttribute('data-beat', 'frozen'); setBeat(2); };
      // presenter-driven: each slide fragment advances one beat.
      const slide = node.closest('.slide');
      if (slide) slide.addEventListener('fragment', () => setBeat(beat + 1));
    },

    /* ---- predictReveal -------------------------------------
       Participant clicks a guess (locks + highlights); on the
       next slide advance ("fragment" event or .reveal()) the
       REAL answer is shown with the guess-vs-truth gap.
       data-options : JSON array of {label,val} or strings
       data-answer  : index (0-based) of the truth option
       data-unit    : optional unit appended in the gap line
       data-cue     : "1" to render a CARDS/HANDS presenter cue
       --------------------------------------------------------- */
    predictReveal(node, ds) {
      node.classList.add('widget', 'pr');
      const opts = (parseJSON(ds.options, null) || []).map(o =>
        typeof o === 'string' ? { label: o, val: o } : o);
      const answer = parseInt(ds.answer, 10);
      const unit = ds.unit || '';
      const head = ds.head || 'Predict first — then we reveal';
      node.innerHTML = '<div class="whead">' + head + '</div>';
      if (ds.cue !== '0') {
        // Presenter-driven convention: the room votes on cards, the presenter
        // tallies on these buttons, THEN reveals. The buttons are the presenter's
        // tally surface — not a per-person control. The card letters reflect the
        // actual number of options (A/B/C for three, A/B/C/D for four) so the cue
        // never promises a D card the slide doesn't have.
        const letters = opts.map((_, k) => String.fromCharCode(65 + k)).join('/');
        const c = el('div', 'cuerow',
          '<span class="cue cards">Cards up ' + letters + ' — I tally, then reveal</span>');
        node.appendChild(c);
      }
      const grid = el('div', 'opts');
      const buttons = opts.map((o, k) => {
        const b = el('button', 'opt');
        b.type = 'button';
        b.innerHTML = '<span class="lbl">Option ' + String.fromCharCode(65 + k) + '</span>' +
                      '<span class="val">' + o.label + '</span>';
        b.addEventListener('click', () => pick(k));
        grid.appendChild(b);
        return b;
      });
      node.appendChild(grid);
      const gap = el('div', 'gap');
      node.appendChild(gap);
      // hidden fragment sentinel: the engine counts this as ONE build step,
      // so the FIRST advance on the slide flips it .on and we reveal.
      const sentinel = el('div', 'frag pr-sentinel');
      sentinel.style.cssText = 'height:0;margin:0;padding:0;pointer-events:none';
      node.appendChild(sentinel);

      let picked = -1, revealed = false;
      function pick(k) {
        if (revealed) return;
        picked = k;
        buttons.forEach((b, j) => b.classList.toggle('picked', j === k));
      }
      function reveal() {
        if (revealed) return;
        revealed = true;
        buttons.forEach((b, j) => {
          b.classList.add('locked');
          if (j === answer) b.classList.add('truth');
          if (j === picked && j !== answer) b.classList.add('wrongpick');
        });
        const truth = opts[answer] ? opts[answer].label : '?';
        if (picked < 0) {
          gap.innerHTML = 'No guess locked — the real answer is <b>' + truth + unit + '</b>.';
        } else if (picked === answer) {
          gap.innerHTML = 'You nailed it: <b>' + truth + unit + '</b>. Hold that intuition.';
        } else {
          gap.innerHTML = 'You guessed <span class="miss">' + opts[picked].label +
            '</span> · the model lands at <b>' + truth + unit +
            '</b>. <span style="color:var(--muted)">The gap is the lesson.</span>';
        }
        gap.classList.add('on');
      }
      node.reveal = reveal;
      // freeze() (export) = reveal() : the PDF shows the locked truth + gap line,
      // never a blank unanswered quiz.
      node.freeze = reveal;
      // The engine flips the hidden .frag sentinel .on as a build step.
      // On each slide fragment event, reveal once the sentinel is on.
      const slide = node.closest('.slide');
      if (slide) slide.addEventListener('fragment', () => {
        if (sentinel.classList.contains('on')) reveal();
      });
    },

    /* ---- thresholdConfusion --------------------------------
       Draggable threshold over a synthetic score distribution;
       live confusion matrix + precision/recall on canvas.
       data-n        : sample count per class (default 120)
       data-sep      : class separation 0..1 (default .32 — overlapping
                       on purpose: precision/recall land in the 80s and
                       visibly TRADE OFF as you drag, with a non-trivial
                       false-negative at threshold 0.5. Do NOT raise this
                       to show a near-perfect model right after the honest
                       88% peak.)
       data-threshold: initial threshold 0..1 (default .5)
       data-freeze   : threshold the freeze()/export state snaps to so the
                       PDF reproduces the peak's ~88% confusion (default .5)
       --------------------------------------------------------- */
    thresholdConfusion(node, ds) {
      node.classList.add('widget', 'tc');
      const N = parseInt(ds.n, 10) || 120;
      const sep = ds.sep != null ? parseFloat(ds.sep) : 0.32;
      // deterministic synthetic scores (seeded) so every screen matches
      let seed = 7;
      const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
      const gauss = (m, s) => { let u=0,v=0; while(!u)u=rnd(); while(!v)v=rnd();
        return m + s * Math.sqrt(-2*Math.log(u)) * Math.cos(2*Math.PI*v); };
      const pos = [], neg = [];
      for (let k=0;k<N;k++){ pos.push(clamp(gauss(0.5+sep/2,0.16),0,1)); neg.push(clamp(gauss(0.5-sep/2,0.16),0,1)); }

      node.innerHTML =
        '<div class="left">' +
          '<div class="whead">' + (ds.head || 'Drag the threshold — feel the trade-off') + '</div>' +
          '<canvas width="520" height="240"></canvas>' +
          '<div class="ctrl"><input type="range" min="0" max="1" step="0.01" value="' + (ds.threshold||0.5) + '">' +
          '<div class="thval"></div></div>' +
        '</div>' +
        '<div class="right">' +
          '<div class="cm">' +
            '<div class="cell hd"></div><div class="cell hd">Pred +</div><div class="cell hd">Pred −</div>' +
            '<div class="cell hd">Actual +</div><div class="cell tp">TP<b>0</b></div><div class="cell fn">FN<b>0</b></div>' +
            '<div class="cell hd">Actual −</div><div class="cell fp">FP<b>0</b></div><div class="cell tn">TN<b>0</b></div>' +
          '</div>' +
          '<div class="pr-rc"><div>Precision<b class="pcv">—</b></div><div>Recall<b class="rcv">—</b></div></div>' +
        '</div>';

      const cv = $('canvas', node), ctx = cv.getContext('2d');
      const range = $('input', node), thval = $('.thval', node);
      const cells = { tp:$('.tp b',node), fn:$('.fn b',node), fp:$('.fp b',node), tn:$('.tn b',node) };
      const pcv = $('.pcv', node), rcv = $('.rcv', node);

      function draw(th) {
        const W = cv.width, H = cv.height, pad = 18, bins = 26;
        ctx.clearRect(0,0,W,H);
        const hp = new Array(bins).fill(0), hn = new Array(bins).fill(0);
        pos.forEach(v => hp[clamp(Math.floor(v*bins),0,bins-1)]++);
        neg.forEach(v => hn[clamp(Math.floor(v*bins),0,bins-1)]++);
        const mx = Math.max(...hp, ...hn, 1);
        const bw = (W - pad*2) / bins;
        const bar = (arr, col) => { ctx.fillStyle = col; arr.forEach((c,k)=>{
          const h = (c/mx)*(H-pad*2); ctx.fillRect(pad+k*bw+1, H-pad-h, bw-2, h); }); };
        ctx.globalAlpha = .65; bar(hn, 'rgba(136,161,178,.8)');         // negatives = grey
        bar(hp, 'rgba(54,182,201,.85)'); ctx.globalAlpha = 1;           // positives = teal
        const x = pad + th*(W-pad*2);
        ctx.strokeStyle = '#e7a657'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(x, pad-6); ctx.lineTo(x, H-pad); ctx.stroke();
        ctx.fillStyle = '#e7a657'; ctx.font = '11px ui-monospace,monospace';
        ctx.fillText('threshold', x+6, pad+2);
      }
      function update() {
        const th = parseFloat(range.value);
        let tp=0,fn=0,fp=0,tn=0;
        pos.forEach(v => v>=th ? tp++ : fn++);
        neg.forEach(v => v>=th ? fp++ : tn++);
        cells.tp.textContent=tp; cells.fn.textContent=fn; cells.fp.textContent=fp; cells.tn.textContent=tn;
        const prec = tp+fp ? tp/(tp+fp) : 0, rec = tp+fn ? tp/(tp+fn) : 0;
        pcv.textContent = (prec*100).toFixed(0)+'%';
        rcv.textContent = (rec*100).toFixed(0)+'%';
        thval.textContent = 'threshold = ' + th.toFixed(2);
        draw(th);
      }
      range.addEventListener('input', update);
      update();
      // freeze() (export) = snap to the threshold that reproduces the peak's
      // ~88% confusion, then repaint, so the PDF shows the SAME model the room saw.
      node.freeze = () => {
        range.value = ds.freeze != null ? parseFloat(ds.freeze) : 0.5;
        update();
      };
    },

    /* ---- drawBoundary --------------------------------------
       Two-colour point cloud; click twice to drop a separating
       line; shows your accuracy vs the model's best line.
       data-n   : points per class (default 40)
       data-sep : separation 0..1 (default .5)
       --------------------------------------------------------- */
    drawBoundary(node, ds) {
      node.classList.add('widget', 'db');
      const N = parseInt(ds.n, 10) || 40;
      const sep = ds.sep != null ? parseFloat(ds.sep) : 0.5;
      node.innerHTML =
        '<div class="whead">' + (ds.head || 'Click two points to draw YOUR boundary') + '</div>' +
        '<canvas width="560" height="360"></canvas>' +
        '<div class="row">' +
          '<span class="you">Your accuracy <b>—</b></span>' +
          '<span class="mdl">Model <b>—</b></span>' +
          '<button class="btn reset" type="button">Reset</button>' +
          '<button class="btn showm" type="button">Show model line</button>' +
        '</div>';
      const cv = $('canvas', node), ctx = cv.getContext('2d');
      const youB = $('.you b', node), mdlB = $('.mdl b', node);
      const W = cv.width, H = cv.height;

      let seed = 11;
      const rnd = () => { seed = (seed*1103515245+12345)&0x7fffffff; return seed/0x7fffffff; };
      const pts = [];
      for (let k=0;k<N;k++){
        pts.push({ x:0.18+rnd()*0.3+sep*0.0, y:0.18+rnd()*0.64, c:0 });
        pts.push({ x:0.52+rnd()*0.3, y:0.18+rnd()*0.64, c:1 });
      }
      // model best vertical-ish line (true divider near x=0.5)
      const model = { ax:0.5, ay:0.05, bx:0.5, by:0.95 };
      let a=null, b=null, showModel=false;

      const px = p => p.x*W, py = p => p.y*H;
      function sideOf(line, p){ // sign of cross product
        return (line.bx-line.ax)*(p.y-line.ay) - (line.by-line.ay)*(p.x-line.ax);
      }
      function accOf(line){
        if(!line) return null;
        // assign each side to majority class, count correct
        let leftPos=0,leftNeg=0,rightPos=0,rightNeg=0;
        pts.forEach(p=>{ const s=sideOf(line,p);
          if(s<0){ p.c? leftPos++ : leftNeg++; } else { p.c? rightPos++ : rightNeg++; } });
        const leftIsPos = leftPos>=leftNeg;
        let correct=0;
        pts.forEach(p=>{ const s=sideOf(line,p); const pred = s<0 ? (leftIsPos?1:0) : (leftIsPos?0:1);
          if(pred===p.c) correct++; });
        return correct/pts.length;
      }
      function draw(){
        ctx.clearRect(0,0,W,H);
        if(showModel){ line(model, 'rgba(54,182,201,.9)', 2, [6,6]); }
        if(a&&b){ line({ax:a.x,ay:a.y,bx:b.x,by:b.y}, '#e7a657', 2.5); }
        else if(a){ dot(a.x,a.y,'#e7a657',5); }
        pts.forEach(p=>{ dot(p.x,p.y, p.c? '#36b6c9':'#d4756b', 5); });
      }
      function dot(x,y,col,r){ ctx.fillStyle=col; ctx.beginPath(); ctx.arc(x*W,y*H,r,0,7); ctx.fill(); }
      function line(l,col,w,dash){ ctx.save(); ctx.strokeStyle=col; ctx.lineWidth=w;
        if(dash) ctx.setLineDash(dash); ctx.beginPath();
        ctx.moveTo(l.ax*W,l.ay*H); ctx.lineTo(l.bx*W,l.by*H); ctx.stroke(); ctx.restore(); }
      function refresh(){
        const yl = a&&b ? accOf({ax:a.x,ay:a.y,bx:b.x,by:b.y}) : null;
        youB.textContent = yl==null ? '—' : (yl*100).toFixed(0)+'%';
        mdlB.textContent = showModel ? (accOf(model)*100).toFixed(0)+'%' : '—';
        draw();
      }
      cv.addEventListener('pointerdown', e=>{
        const r=cv.getBoundingClientRect();
        const p={ x:(e.clientX-r.left)/r.width, y:(e.clientY-r.top)/r.height };
        if(!a||(a&&b)){ a=p; b=null; } else { b=p; }
        refresh();
      });
      $('.reset',node).addEventListener('click',()=>{ a=null;b=null;showModel=false; refresh(); });
      $('.showm',node).addEventListener('click',()=>{ showModel=true; refresh(); });
      draw();
      // freeze() (export) = reveal the model's best line so the PDF shows the
      // teaching state, not an empty cloud.
      node.freeze = () => { showModel = true; refresh(); };
    },

    /* ---- liveTokenizer -------------------------------------
       Type a sentence -> live bag-of-words feature chips.
       data-stop : "1" to grey common stop-words (default on)
       data-seed : initial text
       --------------------------------------------------------- */
    liveTokenizer(node, ds) {
      node.classList.add('widget', 'lt');
      const stopOn = ds.stop !== '0';
      const STOP = new Set('the a an and or of to in is it on for with this that be are was'.split(' '));
      node.innerHTML =
        '<div class="whead">' + (ds.head || 'Type — watch words become numbers') + '</div>' +
        '<input type="text" value="' + (ds.seed || 'bearing failure on the pump again') + '" ' +
          'placeholder="Type a maintenance note…">' +
        '<div class="feats"></div>';
      const inp = $('input', node), feats = $('.feats', node);
      function render(){
        const words = inp.value.toLowerCase().replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(Boolean);
        const counts = {};
        words.forEach(w => counts[w] = (counts[w]||0)+1);
        feats.innerHTML = '';
        Object.keys(counts).forEach(w=>{
          const isStop = stopOn && STOP.has(w);
          const f = el('div', 'feat' + (isStop?' stop':''));
          f.innerHTML = '<span class="w">'+w+'</span><span class="n">'+counts[w]+'</span>';
          feats.appendChild(f);
        });
      }
      inp.addEventListener('input', render);
      render();
      // freeze() (export) = render the seed note's features so the PDF shows
      // words-as-counts, not an empty box.
      node.freeze = () => { if (ds.seed != null) inp.value = ds.seed; render(); };
    },

    /* ---- spectroPlay ---------------------------------------
       Play a short synthesized tone (WebAudio, offline) and
       reveal a static spectrogram image.
       data-img    : spectrogram image src (required to reveal)
       data-freq   : base frequency Hz (default 220)
       data-kind   : "tone" | "chirp" | "noise" (default chirp)
       data-dur    : seconds (default 1.4)
       --------------------------------------------------------- */
    spectroPlay(node, ds) {
      node.classList.add('widget', 'sp');
      const img = ds.img || '';
      const freq = parseFloat(ds.freq) || 220;
      const kind = ds.kind || 'chirp';
      const dur = parseFloat(ds.dur) || 1.4;
      node.innerHTML =
        '<div class="player">' +
          '<button class="play" type="button" aria-label="Play sound">' +
            '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>' +
          '</button>' +
          '<div class="meta">' + (ds.head || 'Press play — then see the sound') + '</div>' +
        '</div>' +
        (img ? '<div class="spectro"><img alt="spectrogram"></div>' : '');
      const btn = $('.play', node);
      const spectro = $('.spectro', node);
      const image = $('.spectro img', node);
      let ctx = null;
      btn.addEventListener('click', () => {
        try {
          ctx = ctx || new (global.AudioContext || global.webkitAudioContext)();
          if (ctx.state === 'suspended') ctx.resume();
          const t0 = ctx.currentTime;
          const gain = ctx.createGain();
          gain.gain.setValueAtTime(0.0001, t0);
          gain.gain.exponentialRampToValueAtTime(0.22, t0 + 0.04);
          gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
          gain.connect(ctx.destination);
          if (kind === 'noise') {
            const buf = ctx.createBuffer(1, ctx.sampleRate*dur, ctx.sampleRate);
            const d = buf.getChannelData(0);
            for (let k=0;k<d.length;k++) d[k] = (Math.random()*2-1)*0.6;
            const src = ctx.createBufferSource(); src.buffer = buf;
            const bp = ctx.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=freq*3; bp.Q.value=0.8;
            src.connect(bp); bp.connect(gain); src.start(t0); src.stop(t0+dur);
          } else {
            const osc = ctx.createOscillator();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(freq, t0);
            if (kind === 'chirp') osc.frequency.exponentialRampToValueAtTime(freq*4, t0+dur);
            osc.connect(gain); osc.start(t0); osc.stop(t0+dur);
          }
        } catch (e) { /* offline / no audio — still reveal image */ }
        if (image && img) { image.src = img; spectro.classList.add('on'); }
      });
      // freeze() (export) = reveal the spectrogram image so the PDF shows the
      // "see the sound" payoff without audio.
      node.freeze = () => { if (image && img) { image.src = img; spectro.classList.add('on'); } };
    }
  };

  /* read data-* into a plain object (camelCase keys) */
  function dataset(node) {
    const o = {};
    for (const k in node.dataset) o[k] = node.dataset[k];
    return o;
  }

  global.HALDeck = HALDeck;
  global.HALWidgets = HALWidgets;
})(window);
