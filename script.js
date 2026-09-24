// ===== animated request packets along the diagram wires =====
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  const svg = document.getElementById("sysdiagram");
  if (!svg) return;

  const wires = {
    phSym: document.getElementById("wire-ph-sym"),
    phFa: document.getElementById("wire-ph-fa"),
    webSym: document.getElementById("wire-web-sym"),
    webFa: document.getElementById("wire-web-fa"),
    symDb: document.getElementById("wire-sym-db"),
    faDb: document.getElementById("wire-fa-db"),
  };

  // each packet: one clean round trip client → backend → db → back, at a steady pace
  const packets = [
    { el: svg.querySelector(".pkt-a"), legs: [[wires.phSym, false], [wires.symDb, false], [wires.symDb, true], [wires.phSym, true]], speed: 0.11, delay: 0 },
    { el: svg.querySelector(".pkt-b"), legs: [[wires.webFa, false], [wires.faDb, false], [wires.faDb, true], [wires.webFa, true]], speed: 0.11, delay: 1400 },
    { el: svg.querySelector(".pkt-c"), legs: [[wires.webSym, false], [wires.symDb, false], [wires.symDb, true], [wires.webSym, true]], speed: 0.1, delay: 2800 },
  ];

  function animate(pkt) {
    let leg = 0;
    let last = null;
    let dist = 0; // distance travelled along the current leg

    function frame(ts) {
      if (last === null) last = ts;
      const dt = ts - last;
      last = ts;

      const [path, rev] = pkt.legs[leg];
      const len = path.getTotalLength();
      dist += pkt.speed * dt; // constant speed → no jitter between legs

      const along = Math.min(dist, len);
      const p = path.getPointAtLength(rev ? len - along : along);
      pkt.el.setAttribute("cx", p.x);
      pkt.el.setAttribute("cy", p.y);

      if (dist >= len) {
        dist = 0;
        leg = (leg + 1) % pkt.legs.length;
        if (leg === 0) { // brief rest between round trips
          last = null;
          setTimeout(() => requestAnimationFrame(frame), 500);
          return;
        }
      }
      requestAnimationFrame(frame);
    }
    setTimeout(() => requestAnimationFrame(frame), pkt.delay);
  }

  packets.forEach(animate);
})();

// ===== client skeletons scroll to the matching projects =====
(function () {
  document.querySelectorAll("#sysdiagram .node[data-target]").forEach((node) => {
    const go = () => {
      const target = document.querySelector(node.dataset.target);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
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

// ===== scroll reveal + load-bar trigger =====
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

  const targets = document.querySelectorAll(
    ".case, .loadbar-widget, .mon-widget, .glance h2, .work > h2, .lab > h2, .path > h2, " +
    ".hire > h2, .says-head, " + groups.join(", ")
  );
  targets.forEach((t) => t.classList.add("reveal"));

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        // isIntersecting alone (threshold 0) so blocks taller than the
        // viewport still reveal; rootMargin holds the reveal until it's a bit in
        if (e.isIntersecting) {
          e.target.classList.add("in-view");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0, rootMargin: "0px 0px -12% 0px" }
  );
  targets.forEach((t) => io.observe(t));
})();

// ===== screenshot carousel =====
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
    const autoplay = parseInt(root.dataset.carouselAutoplay || "0", 10);

    const dots = slides.map((_, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", "Go to screen " + (i + 1));
      b.addEventListener("click", () => manual(i));
      dotsWrap.appendChild(b);
      return b;
    });

    function go(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = "translateX(-" + index * 100 + "%)";
      dots.forEach((d, di) => d.setAttribute("aria-current", di === index ? "true" : "false"));
      slides.forEach((s, si) => s.setAttribute("aria-hidden", si === index ? "false" : "true"));
    }

    // any deliberate move hands control to the visitor for good
    function manual(i) {
      taken = true;
      clearInterval(timer);
      go(i);
    }

    function restart() {
      if (!autoplay || reduced || taken) return;
      clearInterval(timer);
      timer = setInterval(() => go(index + 1), autoplay);
    }

    prev.addEventListener("click", () => manual(index - 1));
    next.addEventListener("click", () => manual(index + 1));
    root.addEventListener("mouseenter", () => clearInterval(timer));
    root.addEventListener("mouseleave", restart);
    root.addEventListener("focusin", () => clearInterval(timer));
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
      clearInterval(timer);
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

    go(0);
    restart();
  });
})();

// ===== sticky header: frosted once scrolled, reading progress, current section =====
(function () {
  const top = document.querySelector(".top");
  if (!top) return;
  const bar = top.querySelector(".top-progress");
  let ticking = false;

  function update() {
    ticking = false;
    const y = window.scrollY;
    top.classList.toggle("is-stuck", y > 24);
    if (bar) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    }
  }
  window.addEventListener("scroll", () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();

  // the nav link of the section under the header gets the underline
  const links = Array.from(document.querySelectorAll('.top nav a[href^="#"]'));
  const byId = new Map(links.map((a) => [a.getAttribute("href").slice(1), a]));
  const sections = links
    .map((a) => document.getElementById(a.getAttribute("href").slice(1)))
    .filter(Boolean);
  if (!sections.length) return;
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      links.forEach((a) => a.classList.remove("is-active"));
      const a = byId.get(e.target.id);
      if (a) a.classList.add("is-active");
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  sections.forEach((s) => spy.observe(s));
})();

// ===== proof numbers count up the first time they are seen =====
(function () {
  const nums = document.querySelectorAll("[data-count]");
  if (!nums.length) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const locale = document.documentElement.lang === "fr" ? "fr-FR" : "en-US";

  function fmt(v, decimals) {
    return v.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }
  // the final value is already in the HTML, so no-JS readers and crawlers see it
  if (reduced) return;

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

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { run(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.6 });
  nums.forEach((n) => io.observe(n));
})();

// ===== platform schematic: requests fan out from the gateway, services talk over gRPC =====
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const svg = document.getElementById("archdiagram");
  if (!svg || reduced) return;
  const w = (id) => document.getElementById(id);
  const pk = svg.querySelectorAll(".arch-pkt");
  const trips = [
    { el: pk[0], legs: [[w("arch-w0"), false], [w("arch-w2"), false], [w("arch-w2"), true], [w("arch-w0"), true]], delay: 0 },
    { el: pk[1], legs: [[w("arch-w0"), false], [w("arch-w4"), false], [w("arch-w4"), true], [w("arch-w0"), true]], delay: 1700 },
    { el: pk[2], legs: [[w("arch-g1"), false], [w("arch-g1"), true], [w("arch-g2"), false], [w("arch-g2"), true]], delay: 900 },
  ];
  const speed = 0.09; // svg units per ms

  function play(trip) {
    let leg = 0, dist = 0, last = null;
    trip.el.style.opacity = 1;
    function frame(ts) {
      if (last === null) last = ts;
      dist += speed * (ts - last);
      last = ts;
      const [path, rev] = trip.legs[leg];
      const len = path.getTotalLength();
      const p = path.getPointAtLength(rev ? len - Math.min(dist, len) : Math.min(dist, len));
      trip.el.setAttribute("cx", p.x);
      trip.el.setAttribute("cy", p.y);
      if (dist >= len) {
        dist = 0;
        leg = (leg + 1) % trip.legs.length;
        if (leg === 0) { last = null; setTimeout(() => requestAnimationFrame(frame), 700); return; }
      }
      requestAnimationFrame(frame);
    }
    setTimeout(() => requestAnimationFrame(frame), trip.delay);
  }

  // start only once the diagram is on screen
  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { trips.forEach(play); io.disconnect(); }
  }, { threshold: 0.3 });
  io.observe(svg);
})();

// ===== monitoring feed: the flagged row gets its highlight =====
(function () {
  document.querySelectorAll(".mon-feed li").forEach((li) => {
    if (li.querySelector(".mon-warn")) li.classList.add("is-flag");
  });
})();

// ===== language hint: offer the other language once, to readers whose browser prefers it =====
(function () {
  const lang = document.documentElement.lang === "fr" ? "fr" : "en";
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
