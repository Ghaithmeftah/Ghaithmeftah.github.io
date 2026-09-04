// ===== animated request packets along the diagram wires =====
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduced) return;

  const svg = document.getElementById("sysdiagram");
  if (!svg) return;

  const wires = {
    a1: document.getElementById("wire-app-api"),
    a2: document.getElementById("wire-app-api2"),
    db1: document.getElementById("wire-api-db"),
    db2: document.getElementById("wire-api2-db2"),
  };

  // each packet: sequence of [path, reverse] legs, then loops
  const packets = [
    { el: svg.querySelector(".pkt-a"), legs: [[wires.a1, false], [wires.db1, false], [wires.db1, true], [wires.a1, true]], dur: 1400, delay: 0 },
    { el: svg.querySelector(".pkt-b"), legs: [[wires.a2, false], [wires.db2, false], [wires.db2, true], [wires.a2, true]], dur: 1600, delay: 900 },
    { el: svg.querySelector(".pkt-c"), legs: [[wires.a1, false], [wires.a1, true]], dur: 1100, delay: 2100 },
  ];

  function animate(pkt) {
    let leg = 0;
    let start = null;

    function frame(ts) {
      if (start === null) start = ts;
      const [path, rev] = pkt.legs[leg];
      const len = path.getTotalLength();
      let t = Math.min((ts - start) / pkt.dur, 1);
      const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      const dist = rev ? len * (1 - eased) : len * eased;
      const p = path.getPointAtLength(dist);
      pkt.el.setAttribute("cx", p.x);
      pkt.el.setAttribute("cy", p.y);

      if (t >= 1) {
        leg = (leg + 1) % pkt.legs.length;
        start = null;
        // small pause at the end of a full loop
        if (leg === 0) { setTimeout(() => requestAnimationFrame(frame), 600); return; }
      }
      requestAnimationFrame(frame);
    }
    setTimeout(() => requestAnimationFrame(frame), pkt.delay);
  }

  packets.forEach(animate);
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
  });
})();

// ===== scroll reveal + load-bar trigger =====
(function () {
  const targets = document.querySelectorAll(".case, .lab-item, .timeline li, .loadbar-widget");
  targets.forEach((t) => t.classList.add("reveal"));

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in-view");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.18 }
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
