// Portfolio interactions, shared by index.html, fr/index.html and the CV pages.
// Every block looks for its own elements and returns quietly when a page
// doesn't have them. Motion is opt-out: with prefers-reduced-motion the page
// shows every final state at once and nothing moves on its own.

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const FINE_POINTER = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
const FR = document.documentElement.lang === "fr";

// run cb the first time el scrolls into view
function onceInView(el, cb, options) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { io.unobserve(e.target); cb(e.target); }
    });
  }, options || { threshold: 0, rootMargin: "0px 0px -12% 0px" });
  io.observe(el);
}

// restart a one-shot CSS animation class on an element (works for SVG too)
function flash(el, cls, ms) {
  if (!el) return;
  clearTimeout(el._flashTimer);
  el.classList.remove(cls);
  el.getBoundingClientRect(); // reflow, so re-adding the class replays it
  el.classList.add(cls);
  el._flashTimer = setTimeout(() => el.classList.remove(cls), ms);
}

// Packets travelling along SVG paths. One rAF loop drives every packet of a
// diagram, and it only runs while the diagram is on screen.
//   trip = { el, tone, delay, legs: [[path, reversed, arrivalNode], ...] }
function runPackets(svg, trips, { speed, rest, startDelay = 0 }) {
  const state = trips.map((t) => ({ leg: -1, dist: 0, wakeAt: 0, t }));
  let visible = false;
  let raf = 0;
  let last = null;
  let clock = 0; // ms of on-screen time, so a paused diagram picks up where it was

  function heat(path, tone, on) {
    path._heat = Math.max(0, (path._heat || 0) + (on ? 1 : -1));
    if (path._heat) path.dataset.hot = tone;
    else delete path.dataset.hot;
  }

  function startLeg(s) {
    s.leg = (s.leg + 1) % s.t.legs.length;
    s.dist = 0;
    heat(s.t.legs[s.leg][0], s.t.tone, true);
  }

  function step(s, dt) {
    if (clock < s.wakeAt) return;
    if (s.leg === -1) { s.t.el.style.opacity = 1; startLeg(s); }
    const [path, rev, arrival] = s.t.legs[s.leg];
    const len = path.getTotalLength();
    s.dist += speed * dt;
    const along = Math.min(s.dist, len);
    const p = path.getPointAtLength(rev ? len - along : along);
    s.t.el.setAttribute("cx", p.x);
    s.t.el.setAttribute("cy", p.y);
    if (s.dist < len) return;

    heat(path, s.t.tone, false);
    flash(arrival, "is-hit", 280);
    if (s.leg === s.t.legs.length - 1) {
      // round trip done: rest, then go again from the client
      s.leg = -1;
      s.wakeAt = clock + rest;
      s.t.el.style.opacity = 0;
    } else {
      startLeg(s);
    }
  }

  function frame(ts) {
    const dt = last === null ? 16 : Math.min(ts - last, 64); // no jump after a stall
    last = ts;
    clock += dt;
    state.forEach((s) => step(s, dt));
    raf = visible ? requestAnimationFrame(frame) : 0;
  }

  state.forEach((s) => { s.wakeAt = startDelay + (s.t.delay || 0); });

  new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    if (visible && !raf) { last = null; raf = requestAnimationFrame(frame); }
  }, { threshold: 0.1 }).observe(svg);
}

// ===== hero diagram: request packets client → backend → db → back =====
(function () {
  const svg = document.getElementById("sysdiagram");
  if (!svg || REDUCED) return;
  const w = (id) => document.getElementById(id);
  const [phone, web, sym, fa, db] = svg.querySelectorAll(".node");

  runPackets(svg, [
    { el: svg.querySelector(".pkt-a"), tone: "a", delay: 0,
      legs: [[w("wire-ph-sym"), false, sym], [w("wire-sym-db"), false, db], [w("wire-sym-db"), true, sym], [w("wire-ph-sym"), true, phone]] },
    { el: svg.querySelector(".pkt-b"), tone: "b", delay: 1400,
      legs: [[w("wire-web-fa"), false, fa], [w("wire-fa-db"), false, db], [w("wire-fa-db"), true, fa], [w("wire-web-fa"), true, web]] },
    { el: svg.querySelector(".pkt-c"), tone: "c", delay: 2800,
      legs: [[w("wire-web-sym"), false, sym], [w("wire-sym-db"), false, db], [w("wire-sym-db"), true, sym], [w("wire-web-sym"), true, web]] },
  ], { speed: 0.11, rest: 900, startDelay: 1500 }); // let the nodes land first
})();

// ===== client skeletons scroll to the matching projects =====
(function () {
  document.querySelectorAll("#sysdiagram .node[data-target]").forEach((node) => {
    const go = () => {
      const target = document.querySelector(node.dataset.target);
      if (target) target.scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
    };
    node.addEventListener("click", go);
    node.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
    });
  });
})();

// ===== diagram node tips =====
(function () {
  const tip = document.getElementById("diagram-tip");
  if (!tip) return;
  const idle = tip.textContent;
  document.querySelectorAll("#sysdiagram .node").forEach((node) => {
    const show = () => { tip.textContent = node.dataset.tip; tip.classList.add("is-node"); };
    const hide = () => { tip.textContent = idle; tip.classList.remove("is-node"); };
    node.addEventListener("mouseenter", show);
    node.addEventListener("mouseleave", hide);
    node.addEventListener("focus", show);
    node.addEventListener("blur", hide);
    // touch has no hover: a tap on a plain node reveals its tip
    // (nodes with data-target navigate instead, so leave those alone)
    if (!node.dataset.target) node.addEventListener("click", show);
  });
  // tapping away puts the idle line back
  document.addEventListener("click", (e) => {
    if (!e.target.closest("#sysdiagram .node")) {
      tip.textContent = idle;
      tip.classList.remove("is-node");
    }
  });
})();

// ===== headlines rise word by word =====
// The words are wrapped at runtime, so the HTML (and the French generator that
// matches it string for string) stays plain.
(function () {
  if (REDUCED) return;

  function split(el) {
    let n = 0;
    let lastWord = null;
    const out = document.createDocumentFragment();
    const word = () => {
      const w = document.createElement("span");
      const inner = document.createElement("span");
      w.className = "w";
      inner.className = "w-i";
      inner.style.setProperty("--wi", n++);
      w.appendChild(inner);
      out.appendChild(w);
      return inner;
    };
    Array.from(el.childNodes).forEach((node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        node.textContent.split(/(\s+)/).forEach((tok) => {
          if (!tok) return;
          if (/^\s+$/.test(tok)) { out.appendChild(document.createTextNode(" ")); lastWord = null; return; }
          lastWord = word();
          lastWord.textContent = tok;
        });
      } else if (node.nodeName === "BR") {
        out.appendChild(node.cloneNode());
        lastWord = null;
      } else {
        // an inline element (the accent full stop) rides with the word it touches
        (lastWord || word()).appendChild(node.cloneNode(true));
      }
    });
    el.textContent = "";
    el.appendChild(out);
    el.classList.add("split");
  }

  const hero = document.querySelector(".hero h1");
  if (hero) {
    split(hero);
    requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add("is-in")));
  }
  const contact = document.querySelector(".contact h2");
  if (contact) {
    split(contact);
    onceInView(contact, () => contact.classList.add("is-in"), { threshold: 0.6 });
  }
})();

// ===== scroll reveal =====
(function () {
  // siblings that arrive together get a small stagger through --i
  const groups = [
    ".glance-grid > div", ".lab-item", ".timeline li", ".lane", ".howiwork li",
    ".says-grid .say", ".clients-row li",
  ];
  groups.forEach((sel) => {
    document.querySelectorAll(sel).forEach((el, i) => el.style.setProperty("--i", i % 6));
  });
  document.querySelectorAll(".case-stack").forEach((ul) => {
    ul.querySelectorAll("li").forEach((li, i) => li.style.setProperty("--i", i));
  });
  document.querySelectorAll(".mon-feed li").forEach((li, i) => li.style.setProperty("--i", i));
  document.querySelectorAll(".proof em").forEach((em, i) => em.style.setProperty("--i", i));

  const targets = document.querySelectorAll(
    ".case, .loadbar-widget, .mon-widget, .glance h2, .work > h2, .lab > h2, .path > h2, " +
    ".hire > h2, .says-head, " + groups.join(", ")
  );
  targets.forEach((t) => t.classList.add("reveal"));
  // isIntersecting alone (threshold 0) so blocks taller than the viewport still
  // reveal; the rootMargin holds the reveal until it's a bit in
  targets.forEach((t) => onceInView(t, (el) => el.classList.add("in-view")));

  // the proof line is never hidden, its numbers just get underlined in turn
  const proof = document.querySelector(".proof");
  if (proof) onceInView(proof, (el) => el.classList.add("in-view"), { threshold: 0.5 });
})();

// ===== load-time race: the old page crawls, the new one is done =====
(function () {
  const widget = document.querySelector(".loadbar-widget");
  if (!widget) return;
  const bars = Array.from(widget.querySelectorAll(".loadbar")).map((row) => {
    const val = row.querySelector(".loadbar-val");
    const nums = (val.textContent.match(/\d+(?:[.,]\d+)?/g) || ["0"]).map((x) => parseFloat(x.replace(",", ".")));
    return { fill: row.querySelector(".loadbar-fill"), val, final: val.textContent, to: nums[nums.length - 1] };
  });
  if (REDUCED || bars.length < 2) return; // CSS shows the end state

  widget.classList.add("is-race");
  // same time scale for both bars: the "after" bar really is ten times shorter
  const msPerSecond = 3200 / Math.max(...bars.map((b) => b.to));

  onceInView(widget, () => {
    const t0 = performance.now() + 250;
    bars.forEach((b) => {
      b.dur = b.to * msPerSecond;
      b.fill.style.transitionDuration = b.dur + "ms";
    });
    widget.classList.add("is-running");

    function frame(now) {
      let running = false;
      bars.forEach((b) => {
        if (b.done) return;
        const t = Math.max(0, Math.min(1, (now - t0) / b.dur));
        b.val.textContent = (b.to * t).toLocaleString(FR ? "fr-FR" : "en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + " s";
        if (t >= 1) {
          b.done = true;
          b.val.textContent = b.final;
          flash(b.val, "is-done", 700);
        } else {
          running = true;
        }
      });
      if (running) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }, { threshold: 0.6 });
})();

// ===== lightbox for screenshots and photos =====
(function () {
  const selector = ".phone-frame img, .shot-frame img, .case-proof-shots img, .tl-photos img, .wh-photo";
  const imgs = Array.from(document.querySelectorAll(selector));
  if (!imgs.length || typeof HTMLDialogElement === "undefined") return;

  const t = FR
    ? { open: "Agrandir l'image", close: "Fermer", prev: "Image précédente", next: "Image suivante" }
    : { open: "Enlarge image", close: "Close", prev: "Previous image", next: "Next image" };

  const dlg = document.createElement("dialog");
  dlg.className = "lb";
  dlg.innerHTML =
    '<figure class="lb-fig"><img alt=""><figcaption class="lb-cap"><span class="lb-count"></span><span class="lb-text"></span></figcaption></figure>' +
    '<button type="button" class="lb-btn lb-close">✕</button>' +
    '<button type="button" class="lb-btn lb-prev">‹</button>' +
    '<button type="button" class="lb-btn lb-next">›</button>';
  document.body.appendChild(dlg);
  const big = dlg.querySelector("img");
  const count = dlg.querySelector(".lb-count");
  const text = dlg.querySelector(".lb-text");
  const [btnClose, btnPrev, btnNext] = dlg.querySelectorAll(".lb-btn");
  btnClose.setAttribute("aria-label", t.close);
  btnPrev.setAttribute("aria-label", t.prev);
  btnNext.setAttribute("aria-label", t.next);

  // images that sit together browse together
  const groupOf = (img) => img.closest("[data-carousel], .case-proof-shots, .tl-photos") || img;
  let group = [];
  let index = 0;

  function caption(img) {
    const slide = img.closest(".carousel-slide");
    const cap = slide && slide.querySelector(".carousel-cap");
    return cap ? cap.textContent : img.alt;
  }

  function show(i) {
    index = (i + group.length) % group.length;
    const img = group[index];
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    text.textContent = caption(img);
    count.textContent = group.length > 1 ? (index + 1) + " / " + group.length : "";
    dlg.classList.toggle("is-single", group.length < 2);
    if (!REDUCED) flash(big, "is-swap", 400);
  }

  function open(img) {
    const root = groupOf(img);
    group = root === img ? [img] : Array.from(root.querySelectorAll(selector));
    dlg._carousel = root.matches && root.matches("[data-carousel]") ? root : null;
    show(group.indexOf(img));
    document.documentElement.classList.add("lb-open");
    dlg.showModal();
  }

  dlg.addEventListener("close", () => {
    document.documentElement.classList.remove("lb-open");
    // the carousel behind follows to the image the visitor ended on
    if (dlg._carousel && dlg._carousel._goTo) dlg._carousel._goTo(index);
  });

  btnClose.addEventListener("click", () => dlg.close());
  btnPrev.addEventListener("click", () => show(index - 1));
  btnNext.addEventListener("click", () => show(index + 1));
  dlg.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); }
    if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); }
  });
  // a click on the dark surround closes, a swipe browses
  let downX = 0, downY = 0;
  dlg.addEventListener("pointerdown", (e) => { downX = e.clientX; downY = e.clientY; });
  dlg.addEventListener("pointerup", (e) => {
    const dx = e.clientX - downX, dy = e.clientY - downY;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) && group.length > 1) {
      show(dx < 0 ? index + 1 : index - 1);
    } else if (Math.abs(dx) < 8 && Math.abs(dy) < 8 && (e.target === dlg || e.target.classList.contains("lb-fig"))) {
      dlg.close();
    }
  });

  imgs.forEach((img) => {
    img.classList.add("zoomable");
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.setAttribute("aria-label", t.open + (FR ? " : " : ": ") + img.alt);
    // a swipe on a carousel ends with a click on the image: that one isn't for us
    let x = 0;
    img.addEventListener("pointerdown", (e) => { x = e.clientX; });
    img.addEventListener("click", (e) => { if (Math.abs(e.clientX - x) < 10) open(img); });
    img.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(img); }
    });
  });
})();

// ===== screenshot carousel =====
(function () {
  document.querySelectorAll("[data-carousel]").forEach((root) => {
    const track = root.querySelector(".carousel-track");
    const slides = Array.from(root.querySelectorAll(".carousel-slide"));
    const dotsWrap = root.querySelector(".carousel-dots");
    const prev = root.querySelector(".carousel-prev");
    const next = root.querySelector(".carousel-next");
    if (!track || slides.length < 2) return;

    const viewport = root.querySelector(".carousel-viewport");
    let index = 0;
    let timer = null;
    let taken = false; // the visitor drove it — stop auto-advancing under them
    let onScreen = false;
    const autoplay = parseInt(root.dataset.carouselAutoplay || "0", 10);

    const dots = slides.map((_, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", (FR ? "Aller à l'écran " : "Go to screen ") + (i + 1));
      b.addEventListener("click", () => manual(i));
      dotsWrap.appendChild(b);
      return b;
    });

    function go(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = "translateX(-" + index * 100 + "%)";
      dots.forEach((d, di) => d.setAttribute("aria-current", di === index ? "true" : "false"));
      // off-screen slides are out of the tab order and out of the reading order
      slides.forEach((s, si) => { s.inert = si !== index; s.classList.toggle("is-current", si === index); });
    }

    // any deliberate move hands control to the visitor for good
    function manual(i) {
      taken = true;
      stop();
      root.classList.add("is-taken");
      go(i);
    }
    root._goTo = manual;

    function stop() {
      clearInterval(timer);
      timer = null;
      root.classList.remove("is-playing");
    }

    // autoplay only runs while the carousel is on screen and nobody is touching it
    function restart() {
      if (!autoplay || REDUCED || taken || !onScreen) return;
      stop();
      timer = setInterval(() => go(index + 1), autoplay);
      root.style.setProperty("--autoplay", autoplay + "ms");
      root.classList.add("is-playing");
    }

    prev.addEventListener("click", () => manual(index - 1));
    next.addEventListener("click", () => manual(index + 1));
    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", restart);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", restart);

    // keyboard: arrows move the carousel once it has focus
    root.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") { e.preventDefault(); manual(index - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); manual(index + 1); }
    });

    // touch / pointer swipe
    let startX = 0, startY = 0, dragging = false;
    viewport.addEventListener("pointerdown", (e) => {
      dragging = true; startX = e.clientX; startY = e.clientY;
      stop();
    });
    viewport.addEventListener("pointerup", (e) => {
      if (!dragging) return;
      dragging = false;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      // horizontal intent only, so a vertical scroll never flips a slide
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
        manual(dx < 0 ? index + 1 : index - 1);
      } else {
        restart();
      }
    });
    viewport.addEventListener("pointercancel", () => { dragging = false; restart(); });

    new IntersectionObserver((entries) => {
      onScreen = entries[0].isIntersecting;
      if (onScreen) restart(); else stop();
    }, { threshold: 0.35 }).observe(root);

    go(0);
  });
})();

// ===== sticky header: frosted once scrolled, reading progress, current section =====
(function () {
  const top = document.querySelector(".top");
  if (!top) return;
  const bar = top.querySelector(".top-progress");
  const nav = top.querySelector("nav");
  const links = Array.from(top.querySelectorAll('nav a[href^="#"]'));
  let ticking = false;
  let active = null;
  let ink = null;

  // one ink line slides under the nav: to the hovered link, then back to the
  // link of the section on screen
  function inkTo(a) {
    if (!ink) return;
    if (!a || !a.offsetWidth) { ink.style.opacity = 0; return; }
    ink.style.opacity = 1;
    ink.style.width = a.offsetWidth + "px";
    ink.style.transform = "translate(" + a.offsetLeft + "px," + (a.offsetTop + a.offsetHeight - 2) + "px)";
  }

  function setActive(a) {
    if (a === active) return;
    if (active) { active.classList.remove("is-active"); active.removeAttribute("aria-current"); }
    active = a || null;
    if (active) { active.classList.add("is-active"); active.setAttribute("aria-current", "true"); }
    if (!nav.matches(":hover")) inkTo(active);
  }

  function update() {
    ticking = false;
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    top.classList.toggle("is-stuck", y > 24);
    if (bar) bar.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    // the last section is too short to reach the middle of the screen: at the
    // very bottom, it's the current one anyway
    if (links.length && max > 0 && y >= max - 4) setActive(links[links.length - 1]);
  }
  window.addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();

  if (!nav || !links.length) return;
  ink = document.createElement("span");
  ink.className = "nav-ink";
  ink.setAttribute("aria-hidden", "true");
  nav.appendChild(ink);
  nav.classList.add("has-ink");
  links.forEach((a) => {
    a.addEventListener("mouseenter", () => inkTo(a));
    a.addEventListener("focus", () => inkTo(a));
  });
  nav.addEventListener("mouseleave", () => inkTo(active));
  window.addEventListener("resize", () => inkTo(active));

  const byId = new Map(links.map((a) => [a.getAttribute("href").slice(1), a]));
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) setActive(byId.get(e.target.id)); });
  }, { rootMargin: "-45% 0px -50% 0px" });
  byId.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });
  // back up in the hero, nothing is current
  const hero = document.querySelector(".hero");
  if (hero) {
    new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) setActive(null);
    }, { rootMargin: "0px 0px -60% 0px" }).observe(hero);
  }
})();

// ===== light / dark theme =====
// The <head> script already chose the theme before paint. This adds the toggle,
// remembers a deliberate choice, and otherwise keeps following the system.
(function () {
  const root = document.documentElement;
  const nav = document.querySelector(".top nav");
  if (!root.hasAttribute("data-theme") || !nav) return;
  const KEY = "gm-theme";
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const meta = document.querySelector('meta[name="theme-color"]');
  const t = FR ? { dark: "Passer en mode sombre", light: "Passer en mode clair" }
               : { dark: "Switch to dark mode", light: "Switch to light mode" };

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "theme-btn";
  btn.innerHTML =
    '<svg class="i-moon" viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>' +
    '<svg class="i-sun" viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg>';
  nav.insertBefore(btn, nav.querySelector(".nav-cv"));

  const stored = () => { try { return localStorage.getItem(KEY); } catch (e) { return null; } };

  function paint(theme) {
    root.setAttribute("data-theme", theme);
    const label = theme === "dark" ? t.light : t.dark;
    btn.setAttribute("aria-label", label);
    btn.title = label;
    if (meta) meta.setAttribute("content", theme === "dark" ? "#0F1420" : "#2B50E0");
  }

  function apply(theme, origin) {
    if (theme === root.getAttribute("data-theme")) return;
    if (REDUCED) { paint(theme); return; }
    if (document.startViewTransition && origin) {
      // the new theme grows out of the button as a circle
      const r = origin.getBoundingClientRect();
      const x = r.left + r.width / 2;
      const y = r.top + r.height / 2;
      const end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      document.startViewTransition(() => paint(theme)).ready.then(() => {
        root.animate(
          { clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + end + "px at " + x + "px " + y + "px)"] },
          { duration: 600, easing: "cubic-bezier(.2,.7,.2,1)", pseudoElement: "::view-transition-new(root)" }
        );
      });
    } else {
      root.classList.add("theme-fade");
      paint(theme);
      setTimeout(() => root.classList.remove("theme-fade"), 400);
    }
  }

  btn.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    // picking what the system already says means "follow the system" again
    try {
      if (next === (system.matches ? "dark" : "light")) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, next);
    } catch (e) { /* storage blocked: the choice lasts for this page only */ }
    apply(next, btn);
  });

  // no saved choice: follow the system live, e.g. when it switches at sunset
  system.addEventListener("change", () => {
    if (!stored()) apply(system.matches ? "dark" : "light");
  });

  paint(root.getAttribute("data-theme"));
})();

// ===== phone menu: the section links, one tap away =====
(function () {
  const top = document.querySelector(".top");
  const nav = top && top.querySelector("nav");
  const links = nav ? Array.from(nav.querySelectorAll('a[href^="#"]')) : [];
  if (links.length < 2) return;

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "menu-btn";
  btn.setAttribute("aria-expanded", "false");
  btn.setAttribute("aria-controls", "menu-sheet");
  btn.innerHTML = '<span class="menu-btn-bars" aria-hidden="true"></span><span class="menu-btn-label">Menu</span>';
  nav.appendChild(btn);

  const sheet = document.createElement("div");
  sheet.id = "menu-sheet";
  sheet.className = "menu-sheet";
  sheet.hidden = true;
  const list = document.createElement("ol");
  links.forEach((a, i) => {
    const li = document.createElement("li");
    li.style.setProperty("--i", i);
    const copy = a.cloneNode(true);
    copy.className = "";
    copy.removeAttribute("aria-current");
    copy.insertAdjacentHTML("afterbegin", '<span class="menu-num" aria-hidden="true">0' + (i + 1) + "</span>");
    li.appendChild(copy);
    list.appendChild(li);
  });
  sheet.appendChild(list);
  top.after(sheet);

  function set(open) {
    btn.setAttribute("aria-expanded", String(open));
    document.documentElement.classList.toggle("menu-open", open);
    if (open) {
      sheet.hidden = false;
      sheet.style.setProperty("--top-h", top.getBoundingClientRect().bottom + "px");
      requestAnimationFrame(() => sheet.classList.add("is-open"));
    } else {
      sheet.classList.remove("is-open");
      setTimeout(() => { if (!sheet.classList.contains("is-open")) sheet.hidden = true; }, REDUCED ? 0 : 260);
    }
  }
  btn.addEventListener("click", () => set(btn.getAttribute("aria-expanded") !== "true"));
  sheet.addEventListener("click", (e) => {
    const a = e.target.closest("a");
    if (!a && e.target !== sheet) return;
    set(false);
    if (!a) return;
    // scroll once the page is unlocked; the browser's own jump would start
    // while overflow is still hidden and stop short
    e.preventDefault();
    const target = document.querySelector(a.getAttribute("href"));
    requestAnimationFrame(() => {
      if (target) target.scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
      history.pushState(null, "", a.getAttribute("href"));
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") { set(false); btn.focus(); }
  });
  window.addEventListener("resize", () => { if (window.innerWidth > 620) set(false); });
})();

// ===== proof numbers count up the first time they are seen =====
(function () {
  const nums = document.querySelectorAll("[data-count]");
  // the final value is already in the HTML, so no-JS readers and crawlers see it
  if (!nums.length || REDUCED) return;
  const locale = FR ? "fr-FR" : "en-US";

  function fmt(v, decimals) {
    return v.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }

  function run(el) {
    const to = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || "0", 10);
    // a 99.8% counts up from 90, not from zero, so it reads as precision, not a race
    const from = to < 100 && decimals ? Math.floor(to * 0.9) : 0;
    const dur = 1400;
    let start = null;
    function frame(ts) {
      if (start === null) start = ts;
      const t = Math.min(1, (ts - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = fmt(from + (to - from) * eased, decimals);
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  nums.forEach((n) => onceInView(n, run, { threshold: 0.6 }));
})();

// ===== platform schematic: requests fan out from the gateway, services talk over gRPC =====
(function () {
  const svg = document.getElementById("archdiagram");
  if (!svg || REDUCED) return;
  const w = (id) => document.getElementById(id);
  const pk = svg.querySelectorAll(".arch-pkt");
  const [app, gw, absences, expenses, documents, tickets] = svg.querySelectorAll(".arch-node");

  onceInView(svg, () => runPackets(svg, [
    { el: pk[0], tone: "a", delay: 0,
      legs: [[w("arch-w0"), false, gw], [w("arch-w2"), false, expenses], [w("arch-w2"), true, gw], [w("arch-w0"), true, app]] },
    { el: pk[1], tone: "b", delay: 1700,
      legs: [[w("arch-w0"), false, gw], [w("arch-w4"), false, tickets], [w("arch-w4"), true, gw], [w("arch-w0"), true, app]] },
    { el: pk[2], tone: "c", delay: 900,
      legs: [[w("arch-g1"), false, expenses], [w("arch-g1"), true, absences], [w("arch-g2"), false, tickets], [w("arch-g2"), true, documents]] },
  ], { speed: 0.09, rest: 700 }), { threshold: 0.3 });
})();

// ===== monitoring feed: the flagged row gets its highlight =====
(function () {
  document.querySelectorAll(".mon-feed li").forEach((li) => {
    if (li.querySelector(".mon-warn")) li.classList.add("is-flag");
  });
})();

// ===== timeline: a line fills as you read down the path =====
(function () {
  const tl = document.querySelector(".timeline");
  if (!tl) return;
  const items = Array.from(tl.children);
  tl.classList.add("is-live");
  let ticking = false;

  function update() {
    ticking = false;
    const anchor = window.innerHeight * 0.62;
    const r = tl.getBoundingClientRect();
    const p = Math.max(0, Math.min(1, (anchor - r.top) / r.height));
    tl.style.setProperty("--tl", p.toFixed(4));
    items.forEach((li) => li.classList.toggle("is-on", li.getBoundingClientRect().top + 36 < anchor));
  }
  window.addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  window.addEventListener("resize", update);
  update();
})();

// ===== primary buttons lean toward the pointer =====
(function () {
  if (REDUCED || !FINE_POINTER) return;
  document.querySelectorAll(".hero-actions .btn-solid, .contact-links .btn-solid").forEach((btn) => {
    btn.classList.add("magnet");
    btn.addEventListener("pointermove", (e) => {
      const r = btn.getBoundingClientRect();
      const x = (e.clientX - r.left - r.width / 2) * 0.18;
      const y = (e.clientY - r.top - r.height / 2) * 0.28;
      btn.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px)";
    });
    btn.addEventListener("pointerleave", () => { btn.style.transform = ""; });
  });
})();

// ===== copy the email address in one click =====
// Not everyone reading on a desktop has a mail client wired to mailto: links.
(function () {
  if (!navigator.clipboard || !window.isSecureContext) return;
  const t = FR ? { done: "Copié", label: "Copier l'adresse e-mail" }
               : { done: "Copied", label: "Copy the email address" };
  const icon =
    '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6">' +
    '<rect x="5.5" y="5.5" width="8" height="8" rx="1.6"/><path d="M10.5 3.2V3a.9.9 0 0 0-.9-.9H3a.9.9 0 0 0-.9.9v6.6c0 .5.4.9.9.9h.3"/></svg>';
  const tick =
    '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8.5l3.2 3L13 4.5"/></svg>';

  document.querySelectorAll(".hero-mail, .contact-meta a[href^='mailto:']").forEach((link) => {
    const address = link.getAttribute("href").replace(/^mailto:/, "").split("?")[0];
    // address and button stay on one line, whatever the row around them does
    const pair = document.createElement("span");
    pair.className = "mail-pair";
    link.before(pair);
    pair.appendChild(link);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-mail";
    btn.innerHTML = icon + '<span class="copy-mail-note" aria-live="polite"></span>';
    btn.setAttribute("aria-label", t.label);
    btn.title = t.label;
    const note = btn.querySelector(".copy-mail-note");
    btn.addEventListener("click", () => {
      navigator.clipboard.writeText(address).then(() => {
        btn.firstChild.outerHTML = tick;
        note.textContent = t.done;
        btn.classList.add("is-done");
        clearTimeout(btn._t);
        btn._t = setTimeout(() => {
          btn.firstChild.outerHTML = icon;
          note.textContent = "";
          btn.classList.remove("is-done");
        }, 1800);
      });
    });
    pair.appendChild(btn);
  });
})();

// ===== language hint: offer the other language once, to readers whose browser prefers it =====
(function () {
  const lang = FR ? "fr" : "en";
  const KEY = "gm-lang";
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked: just ask */ }

  function remember(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* ignore */ } }

  // choosing a language from the nav counts as an answer too
  document.querySelectorAll(".nav-lang, [data-lang-switch]").forEach((a) => {
    a.addEventListener("click", () => remember(lang === "fr" ? "en" : "fr"));
  });

  if (saved) return;
  const prefs = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""])
    .map((l) => String(l).toLowerCase());
  const prefersFr = prefs[0] && prefs[0].startsWith("fr");
  const wantOther = lang === "en" ? prefersFr : !prefersFr && prefs[0];
  if (!wantOther) return;

  // same page in the other language: /x -> /fr/x on the English side, and back
  const file = location.pathname.split("/").pop();
  const target = lang === "en" ? "fr/" + file : "../" + file;
  const copy = lang === "en"
    ? { text: "Ce portfolio existe aussi en français, avec le CV en français.", go: "Version française", stay: "Rester en anglais", hl: "fr" }
    : { text: "This portfolio is also in English, with the English CV.", go: "English version", stay: "Stay in French", hl: "en" };

  const box = document.createElement("div");
  box.className = "lang-hint";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-label", copy.go);
  box.lang = copy.hl;
  box.innerHTML =
    '<p></p><a class="btn btn-solid" hreflang="' + copy.hl + '"></a><button type="button"></button>';
  box.querySelector("p").textContent = copy.text;
  const go = box.querySelector("a");
  go.href = target || "./";
  go.textContent = copy.go;
  go.addEventListener("click", () => remember(copy.hl));
  const stay = box.querySelector("button");
  stay.textContent = copy.stay;
  stay.addEventListener("click", () => { remember(lang); box.remove(); });
  document.body.appendChild(box);
})();
