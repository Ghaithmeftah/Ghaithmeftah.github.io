// Ambient films for the section backgrounds, drawn on a canvas by
// tools/motion/scenes.html. Like the device scenes, nothing runs on its own:
// draw(name, t) paints time t, and every motion is periodic in the loop length
// T, so the films loop without a seam. Randomness is seeded, so a re-render
// gives the same film.
//
// Each film borrows from photography rather than from UI: depth of field
// (sharp small lights far away, large soft discs close up), long exposures,
// light leaks; the vignette is added by post().

const AMBIENT = (() => {
  const TAU = Math.PI * 2;
  const COBALT = [91, 123, 255], AMBER = [255, 181, 71], TEAL = [43, 196, 176], ICE = [210, 222, 255];
  const rgba = (c, a) => "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a.toFixed(3) + ")";

  function rng(seed) {
    return () => {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const mod = (a, n) => ((a % n) + n) % n;

  let W, H, T, ctx;

  function ground(top, bottom, glow) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, top); g.addColorStop(1, bottom);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    if (glow) {
      const r = ctx.createRadialGradient(glow.x * W, glow.y * H, 0, glow.x * W, glow.y * H, glow.r * W);
      r.addColorStop(0, glow.c); r.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
    }
  }

  // a lens bokeh disc: flat body, a slightly brighter rim, soft edge
  function bokeh(x, y, r, c, a) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(c, a * .55));
    g.addColorStop(.78, rgba(c, a * .7));
    g.addColorStop(.92, rgba(c, a));
    g.addColorStop(1, rgba(c, 0));
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  }

  function glowDot(x, y, r, c, a) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
    g.addColorStop(0, rgba(c, a)); g.addColorStop(.25, rgba(c, a * .45)); g.addColorStop(1, rgba(c, 0));
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x, y, r * 4, 0, TAU); ctx.fill();
  }

  // a warm leak drifting across a corner, as on a lens pointed near a light
  function leak(t, x, y, c, a) {
    const p = TAU * t / T;
    const lx = (x + .06 * Math.sin(p)) * W, ly = (y + .05 * Math.cos(p)) * H;
    const g = ctx.createRadialGradient(lx, ly, 0, lx, ly, .55 * W);
    g.addColorStop(0, rgba(c, a)); g.addColorStop(1, rgba(c, 0));
    ctx.globalCompositeOperation = "lighter";
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = "source-over";
  }

  // ---------------------------------------------------------------- flow
  // Request traffic: packets streaming along lanes. Amber requests go out,
  // teal answers come back, cobalt is the rest of the traffic.
  let FLOW;
  function flowSetup() {
    const r = rng(7);
    const lanes = Array.from({ length: 9 }, (_, i) => ({
      y: .14 + .76 * (i / 8) + (r() - .5) * .05, amp: 40 + r() * 80, wl: 900 + r() * 900, ph: r() * TAU,
    }));
    const span = W + 400;
    const parts = Array.from({ length: 420 }, () => {
      const d = Math.pow(r(), 1.6);              // depth: most far, a few near
      const kind = r();
      return {
        lane: lanes[Math.floor(r() * lanes.length)], x0: r() * span, d,
        cycles: 1 + Math.floor(r() * 3),         // whole crossings per loop
        c: kind < .12 ? AMBER : kind < .2 ? TEAL : COBALT,
        back: kind >= .12 && kind < .2,
        dy: (r() - .5) * 26,
      };
    });
    const discs = Array.from({ length: 12 }, () => ({
      x: r(), y: r(), rad: 60 + r() * 150, c: r() < .3 ? AMBER : COBALT, a: .05 + r() * .08, ph: r() * TAU,
    }));
    FLOW = { lanes, parts, discs, span };
  }
  const laneY = (l, x) => l.y * H + l.amp * Math.sin(TAU * x / l.wl + l.ph);
  function flow(t) {
    ground("#060B1C", "#0A1430", { x: .7, y: .55, r: .7, c: "rgba(40,62,160,.35)" });
    const p = TAU * t / T;
    ctx.lineWidth = 1;
    FLOW.lanes.forEach((l) => {
      ctx.strokeStyle = "rgba(120,145,255,.07)";
      ctx.beginPath();
      for (let x = -20; x <= W + 20; x += 20) { const y = laneY(l, x); x < 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
      ctx.stroke();
    });
    ctx.globalCompositeOperation = "lighter";
    FLOW.parts.forEach((q) => {
      const v = q.cycles * FLOW.span / T;
      let x = mod(q.x0 + (q.back ? -1 : 1) * v * t, FLOW.span) - 200;
      const y = laneY(q.lane, x) + q.dy * (1 - q.d);
      const len = 18 + 120 * q.d;
      const w = .6 + 3.2 * q.d;
      const a = .25 + .6 * q.d;
      const tail = q.back ? x + len : x - len;
      const g = ctx.createLinearGradient(tail, 0, x, 0);
      g.addColorStop(0, rgba(q.c, 0)); g.addColorStop(1, rgba(q.c, a));
      ctx.strokeStyle = g; ctx.lineWidth = w; ctx.lineCap = "round";
      ctx.beginPath(); ctx.moveTo(tail, laneY(q.lane, tail) + q.dy * (1 - q.d)); ctx.lineTo(x, y); ctx.stroke();
      if (q.d > .55) glowDot(x, y, w, q.c, a * .8);
    });
    FLOW.discs.forEach((b) => bokeh((b.x + .03 * Math.sin(p + b.ph)) * W, (b.y + .03 * Math.cos(p + b.ph)) * H, b.rad, b.c, b.a));
    ctx.globalCompositeOperation = "source-over";
    leak(t, .05, .1, AMBER, .08);
  }

  // ------------------------------------------------------- constellation
  // The stack as one system: a slowly turning cloud of linked nodes, with
  // pulses running along the links.
  let CON;
  function conSetup() {
    const r = rng(21);
    const pts = Array.from({ length: 300 }, () => {
      // a flattened shell, denser toward a band, like a galaxy seen at an angle
      const u = r() * TAU, v = Math.acos(2 * r() - 1);
      const rad = .78 + r() * .3;
      return { x: rad * Math.sin(v) * Math.cos(u), y: rad * Math.cos(v) * .55, z: rad * Math.sin(v) * Math.sin(u),
               hot: r() < .07, ph: r() * TAU };
    });
    const links = [];
    pts.forEach((a, i) => {
      const near = pts.map((b, j) => [j, (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2])
        .filter(([j]) => j !== i).sort((m, n) => m[1] - n[1]).slice(0, 2);
      near.forEach(([j, d2]) => { if (d2 < .09 && i < j) links.push([i, j, r() < .12, r()]); });
    });
    const discs = Array.from({ length: 9 }, () => ({ x: r(), y: r(), rad: 70 + r() * 160, c: r() < .4 ? TEAL : COBALT, a: .04 + r() * .06, ph: r() * TAU }));
    CON = { pts, links, discs };
  }
  function constellation(t) {
    ground("#050A1A", "#0B1430", { x: .5, y: .5, r: .6, c: "rgba(30,60,150,.3)" });
    const p = TAU * t / T;
    const rot = p, tilt = .42 + .05 * Math.sin(p);
    const cx = .5 * W, cy = .52 * H, R = .46 * H, f = 2.4;
    const proj = CON.pts.map((q) => {
      const x1 = q.x * Math.cos(rot) - q.z * Math.sin(rot), z1 = q.x * Math.sin(rot) + q.z * Math.cos(rot);
      const y2 = q.y * Math.cos(tilt) - z1 * Math.sin(tilt), z2 = q.y * Math.sin(tilt) + z1 * Math.cos(tilt);
      const s = f / (f + z2);
      return { x: cx + x1 * R * 1.9 * s, y: cy + y2 * R * s, s, d: (1 - z2) / 2, q };
    });
    ctx.globalCompositeOperation = "lighter";
    CON.links.forEach(([i, j, pulse, ph]) => {
      const a = proj[i], b = proj[j];
      const depth = (a.d + b.d) / 2;
      ctx.strokeStyle = rgba(COBALT, .05 + .22 * depth);
      ctx.lineWidth = .6 + depth;
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      if (pulse) {
        const k = mod(t / T * 2 + ph, 1);
        glowDot(a.x + (b.x - a.x) * k, a.y + (b.y - a.y) * k, 1.4 + depth * 1.6, AMBER, .5 + .4 * depth);
      }
    });
    proj.forEach((n) => {
      const beat = n.q.hot ? .5 + .5 * Math.sin(p * 3 + n.q.ph) : 0;
      const c = n.q.hot ? (beat > .5 ? AMBER : TEAL) : ICE;
      glowDot(n.x, n.y, (.8 + 2.2 * n.d) * (1 + beat * .8), c, .25 + .55 * n.d);
    });
    CON.discs.forEach((b) => bokeh((b.x + .025 * Math.sin(p + b.ph)) * W, (b.y + .025 * Math.cos(p + b.ph)) * H, b.rad, b.c, b.a));
    ctx.globalCompositeOperation = "source-over";
  }

  // --------------------------------------------------------------- bokeh
  // Warm city lights out of focus, drifting past: a quiet, human frame.
  let BOK;
  function bokSetup() {
    const r = rng(33);
    const discs = Array.from({ length: 70 }, () => {
      const d = Math.pow(r(), 1.3);
      const k = r();
      return { x: r(), y: .1 + r() * .85, rad: 14 + d * 170, a: .05 + (1 - d) * .1 + r() * .06,
               c: k < .5 ? AMBER : k < .82 ? COBALT : TEAL, ax: .02 + r() * .05, ay: .01 + r() * .03, ph: r() * TAU, d };
    }).sort((a, b) => a.d - b.d);
    BOK = { discs };
  }
  function bok(t) {
    ground("#07060F", "#0B1026", { x: .3, y: .8, r: .7, c: "rgba(120,70,20,.22)" });
    const p = TAU * t / T;
    const pan = .03 * Math.sin(p);
    ctx.globalCompositeOperation = "lighter";
    BOK.discs.forEach((b) => {
      const x = (b.x + pan * (1 + b.d) + b.ax * Math.cos(p + b.ph)) * W;
      const y = (b.y + b.ay * Math.sin(p + b.ph)) * H;
      const breathe = .75 + .25 * Math.sin(p * 2 + b.ph);
      bokeh(x, y, b.rad, b.c, b.a * breathe);
    });
    ctx.globalCompositeOperation = "source-over";
    leak(t, .95, .15, AMBER, .1);
  }

  // ----------------------------------------------------------- blueprint
  // A drafting table at night: a grid, wireframes being drawn, a scan light
  // sweeping across.
  let BLU;
  function bluSetup() {
    const r = rng(48);
    const shapes = Array.from({ length: 7 }, () => {
      const kind = Math.floor(r() * 3);
      return { kind, x: .08 + r() * .84, y: .15 + r() * .7, s: 60 + r() * 140, ph: r(), rot: (r() - .5) * .5 };
    });
    BLU = { shapes };
  }
  function shapePath(sh) {
    const s = sh.s;
    ctx.beginPath();
    if (sh.kind === 0) { ctx.rect(-s, -s * .62, s * 2, s * 1.24); ctx.moveTo(-s, -s * .36); ctx.lineTo(s, -s * .36); }
    else if (sh.kind === 1) { ctx.arc(0, 0, s * .8, 0, TAU); ctx.moveTo(-s * .8, 0); ctx.lineTo(s * .8, 0); ctx.moveTo(0, -s * .8); ctx.lineTo(0, s * .8); }
    else { ctx.rect(-s * .4, -s * .8, s * .8, s * 1.6); ctx.moveTo(-s * .4, s * .5); ctx.lineTo(s * .4, s * .5); }
  }
  function blueprint(t) {
    ground("#06102A", "#081634", null);
    const p = TAU * t / T;
    // grid, drifting by exactly one cell per loop
    const cell = 48, off = (t / T) * cell;
    ctx.lineWidth = 1;
    for (let x = -cell + off; x < W + cell; x += cell) {
      ctx.strokeStyle = Math.round((x - off) / cell) % 4 === 0 ? "rgba(120,160,255,.13)" : "rgba(120,160,255,.055)";
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = -cell + off * .5; y < H + cell; y += cell) {
      ctx.strokeStyle = Math.round((y - off * .5) / cell) % 4 === 0 ? "rgba(120,160,255,.13)" : "rgba(120,160,255,.055)";
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    // wireframes trace themselves in, hold, and fade, each on its own phase
    BLU.shapes.forEach((sh) => {
      const k = mod(t / T + sh.ph, 1);
      const draw = Math.min(1, k / .45), fade = k > .8 ? 1 - (k - .8) / .2 : 1;
      ctx.save();
      ctx.translate(sh.x * W, sh.y * H); ctx.rotate(sh.rot);
      shapePath(sh);
      ctx.setLineDash([2400 * draw, 2400]);
      ctx.strokeStyle = rgba(ICE, .35 * fade);
      ctx.lineWidth = 1.4;
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    });
    // the scan: a soft vertical band of light crossing once per loop
    const sx = mod(t / T, 1) * (W + 600) - 300;
    ctx.globalCompositeOperation = "lighter";
    const g = ctx.createLinearGradient(sx - 260, 0, sx + 260, 0);
    g.addColorStop(0, rgba(TEAL, 0)); g.addColorStop(.5, rgba(TEAL, .14)); g.addColorStop(1, rgba(TEAL, 0));
    ctx.fillStyle = g; ctx.fillRect(sx - 260, 0, 520, H);
    ctx.fillStyle = rgba(TEAL, .5); ctx.fillRect(sx - 1, 0, 2, H);
    ctx.globalCompositeOperation = "source-over";
    leak(t, .9, .9, COBALT, .12);
  }

  // --------------------------------------------------------------- trail
  // A road at night shot on a long exposure: headlights come toward us, tail
  // lights go away, the city is soft behind.
  let TRA;
  function traSetup() {
    const r = rng(64);
    const streaks = Array.from({ length: 120 }, () => ({
      lane: r() < .5 ? -1 : 1, off: (r() - .5) * .9, z0: r(), cycles: 1 + Math.floor(r() * 2), len: .08 + r() * .12,
    }));
    const city = Array.from({ length: 160 }, () => ({ x: r(), y: .3 + r() * .14, rad: 2 + r() * 7, c: r() < .6 ? AMBER : r() < .7 ? ICE : COBALT, a: .15 + r() * .45, ph: r() * TAU }));
    const discs = Array.from({ length: 10 }, () => ({ x: r(), y: .2 + r() * .3, rad: 50 + r() * 120, c: r() < .5 ? AMBER : COBALT, a: .04 + r() * .06, ph: r() * TAU }));
    TRA = { streaks, city, discs };
  }
  function trail(t) {
    ground("#03050F", "#0B0F22", { x: .62, y: .42, r: .55, c: "rgba(90,70,40,.25)" });
    const p = TAU * t / T;
    const vx = .62 * W, vy = .42 * H, f = .9 * H, camH = .55;
    ctx.globalCompositeOperation = "lighter";
    TRA.city.forEach((c) => glowDot(c.x * W, c.y * H, c.rad * .5, c.c, c.a * (.7 + .3 * Math.sin(p * 2 + c.ph))));
    TRA.discs.forEach((b) => bokeh((b.x + .02 * Math.sin(p + b.ph)) * W, b.y * H, b.rad, b.c, b.a));
    // depth z in (0,1]: 1 is at the camera
    const proj = (lane, off, z) => {
      const depth = .06 + 2.6 * (1 - z);           // distance
      const x = vx + ((lane * .5 + off * .4) / depth) * f * .55;
      const y = vy + (camH / depth) * f * .35;
      return [x, y, 1 / depth];
    };
    TRA.streaks.forEach((s) => {
      // headlights (lane -1) come toward the camera, tail lights (lane 1) go away
      const dir = s.lane < 0 ? 1 : -1;
      const z = mod(s.z0 + dir * s.cycles * t / T, 1);
      const z2 = Math.min(1, Math.max(0, z - dir * s.len));
      const [x1, y1, k1] = proj(s.lane, s.off, Math.min(z, z2));
      const [x2, y2, k2] = proj(s.lane, s.off, Math.max(z, z2));
      const c = s.lane < 0 ? ICE : AMBER;
      const g = ctx.createLinearGradient(x1, y1, x2, y2);
      g.addColorStop(0, rgba(c, 0)); g.addColorStop(1, rgba(c, .75));
      ctx.strokeStyle = g;
      ctx.lineCap = "round";
      ctx.lineWidth = Math.min(14, .6 + 2.2 * k2);
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    });
    ctx.globalCompositeOperation = "source-over";
    leak(t, .12, .85, AMBER, .1);
  }

  // -------------------------------------------------------------- aurora
  // A calm close: slow light curtains over a starfield.
  let AUR;
  function aurSetup() {
    const r = rng(81);
    const stars = Array.from({ length: 260 }, () => ({ x: r(), y: r() * .75, rad: .4 + r() * 1.3, a: .2 + r() * .6, ph: r() * TAU, k: 1 + Math.floor(r() * 3) }));
    const curtains = [
      { c: TEAL, y: .42, amp: 70, wl: 1300, h: 300, a: .16, m: 1, ph: 0 },
      { c: COBALT, y: .5, amp: 90, wl: 1700, h: 360, a: .18, m: 1, ph: 2 },
      { c: [150, 110, 255], y: .36, amp: 60, wl: 1100, h: 240, a: .1, m: 2, ph: 4 },
    ];
    AUR = { stars, curtains };
  }
  function aurora(t) {
    ground("#03060F", "#091128", null);
    const p = TAU * t / T;
    AUR.stars.forEach((s) => {
      ctx.fillStyle = rgba(ICE, s.a * (.6 + .4 * Math.sin(p * s.k + s.ph)));
      ctx.beginPath(); ctx.arc(s.x * W, s.y * H, s.rad, 0, TAU); ctx.fill();
    });
    ctx.globalCompositeOperation = "lighter";
    ctx.filter = "blur(10px)";   // light through air, not columns of pixels
    AUR.curtains.forEach((cu) => {
      for (let x = 0; x <= W; x += 4) {
        const y = cu.y * H + cu.amp * Math.sin(TAU * x / cu.wl + p * cu.m + cu.ph) + 25 * Math.sin(TAU * x / 400 - p * cu.m);
        const h = cu.h * (.6 + .4 * Math.sin(TAU * x / 700 + p * cu.m + cu.ph));
        const g = ctx.createLinearGradient(0, y - h, 0, y + 20);
        g.addColorStop(0, rgba(cu.c, 0)); g.addColorStop(.75, rgba(cu.c, cu.a * .6)); g.addColorStop(1, rgba(cu.c, 0));
        ctx.fillStyle = g;
        ctx.fillRect(x, y - h, 4, h + 20);
      }
    });
    ctx.filter = "none";
    ctx.globalCompositeOperation = "source-over";
    // a soft horizon so the copy above has ground to stand on
    const g = ctx.createLinearGradient(0, H * .6, 0, H);
    g.addColorStop(0, "rgba(3,6,15,0)"); g.addColorStop(1, "rgba(3,6,15,.9)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }

  const SCENES = {
    flow: [flowSetup, flow], constellation: [conSetup, constellation], bokeh: [bokSetup, bok],
    blueprint: [bluSetup, blueprint], trail: [traSetup, trail], aurora: [aurSetup, aurora],
  };

  // ------------------------------------------------------------------ post
  // A vignette over every film, device scenes included. Film grain is not
  // baked in: random noise is the one thing video compression cannot shrink,
  // so the page lays a live grain over the films instead (style.css).
  function postSetup(stage) {
    const vig = document.createElement("div");
    Object.assign(vig.style, { position: "absolute", inset: "0", pointerEvents: "none",
      background: "radial-gradient(120% 100% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.42) 100%)" });
    stage.appendChild(vig);
  }

  return {
    // make the canvas for an ambient film; returns nothing for device scenes
    setup(name, stage, w, h, T_, dpr) {
      W = w; H = h; T = T_;
      if (name) {
        const c = document.createElement("canvas");
        c.width = Math.round(w * dpr); c.height = Math.round(h * dpr);
        Object.assign(c.style, { position: "absolute", inset: "0", width: "100%", height: "100%" });
        stage.appendChild(c);
        ctx = c.getContext("2d");
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        SCENES[name][0]();
      }
      postSetup(stage);
    },
    draw(name, t) { if (name) SCENES[name][1](t); },
  };
})();
