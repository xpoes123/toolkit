// Tiny shared helpers for web/ui. Serve as /ui/ui.js next to ui.css. No dependencies.
//   ui.spark(values, {h, ref, dot, area, label}) -> SVG string (class ui-spark), scales to its box.
//   ui.cat(i) -> "var(--cat-N)" for the i-th category (by stable index); ui.catFor(name) hashes a name.
(function () {
  function spark(values, o) {
    o = o || {};
    const v = (values || []).map(Number).filter(x => isFinite(x));
    const W = 100, H = 30;
    const all = v.concat(o.ref != null ? [o.ref] : [], o.max != null ? [o.max] : [], o.min != null ? [o.min] : []);
    const lo = o.min != null ? o.min : Math.min.apply(null, all.length ? all : [0]);
    const hi = Math.max.apply(null, all.length ? all : [1]);
    const n = o.n || v.length;
    const x = i => n > 1 ? (i / (n - 1)) * W : 0;
    const y = val => hi === lo ? H / 2 : H - ((val - lo) / (hi - lo)) * H;
    const pts = v.map((val, i) => x(i).toFixed(2) + "," + y(val).toFixed(2)).join(" ");
    const last = v.length ? [x(v.length - 1), y(v[v.length - 1])] : null;
    const label = (o.label || "trend").replace(/[<>&"]/g, "");
    let s = `<svg class="ui-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="${label}">`;
    if (o.ref != null) s += `<line class="ui-spark__ref" x1="0" x2="${W}" y1="${y(o.ref)}" y2="${y(o.ref)}" vector-effect="non-scaling-stroke"/>`;
    if (o.refLine) s += `<line class="ui-spark__ref" x1="0" y1="${y(o.refLine[0])}" x2="${W}" y2="${y(o.refLine[1])}" vector-effect="non-scaling-stroke"/>`;
    if (o.area && v.length > 1) s += `<polygon class="ui-spark__area" points="0,${H} ${pts} ${x(v.length - 1)},${H}"/>`;
    if (v.length > 1) s += `<polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>`;
    s += "</svg>";
    if (o.dot !== false && last) {
      // dot drawn in HTML so it stays round when the SVG stretches
      s = `<span style="position:relative;display:block">${s}<span class="ui-spark__pt" style="position:absolute;width:5px;height:5px;border-radius:50%;background:var(--accent);left:calc(${last[0]}% - 2.5px);top:calc(${(last[1] / H) * 100}% - 2.5px)"></span></span>`;
    }
    return s;
  }
  const cat = i => `var(--cat-${((Math.abs(i | 0)) % 8) + 1})`;
  const catFor = name => { let h = 0; for (const c of String(name || "")) h = (h * 31 + c.charCodeAt(0)) | 0; return cat(h); };
  window.ui = Object.assign(window.ui || {}, {spark, cat, catFor});
})();
