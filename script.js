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
  const targets = document.querySelectorAll(".case, .lab-item, .timeline li, .loadbar-widget");
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

// ===== live score ticks up once, a small wink =====
(function () {
  const el = document.getElementById("score-home");
  if (!el) return;
  const io = new IntersectionObserver((entries) => {
    if (!entries[0].isIntersecting) return;
    io.disconnect();
    let n = 17;
    const iv = setInterval(() => {
      n++;
      el.textContent = n;
      if (n >= 24) clearInterval(iv);
    }, 120);
  }, { threshold: 0.5 });
  io.observe(el);
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
