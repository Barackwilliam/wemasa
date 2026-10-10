/* WEMASA website: menu, search, photo viewer, focus-area previews, copy buttons, newsletter. */
(function () {
  "use strict";
  var doc = document;
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };

  /* Menu and search panels */
  var lastFocus = null;
  function open(el) {
    if (!el) return;
    lastFocus = doc.activeElement;
    el.classList.add("is-open");
    doc.body.style.overflow = "hidden";
    var f = el.querySelector("input, a, button");
    if (f) setTimeout(function () { f.focus(); }, 30);
  }
  function close(el) {
    if (!el) return;
    el.classList.remove("is-open");
    doc.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  doc.addEventListener("click", function (e) {
    var o = e.target.closest("[data-open]");
    if (o) { e.preventDefault(); open(doc.getElementById(o.getAttribute("data-open"))); return; }
    var c = e.target.closest("[data-close]");
    if (c) { e.preventDefault(); close(c.closest(".menu, .search-panel")); return; }
    if (e.target.classList.contains("search-panel")) close(e.target);
  });
  doc.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$(".menu.is-open, .search-panel.is-open").forEach(close);
  });

  /* Focus-area list: a small photograph follows the pointer */
  var peek = doc.querySelector(".peek");
  if (peek && window.matchMedia("(hover: hover)").matches) {
    var img = peek.querySelector("img");
    $$("[data-peek]").forEach(function (a) {
      a.addEventListener("mouseenter", function () { img.src = a.getAttribute("data-peek"); peek.classList.add("is-on"); });
      a.addEventListener("mouseleave", function () { peek.classList.remove("is-on"); });
      a.addEventListener("mousemove", function (e) {
        peek.style.transform = "translate(" + (e.clientX + 24) + "px," + (e.clientY - 120) + "px)";
      });
    });
  }

  /* Photo viewer */
  var lb = doc.getElementById("lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img"), lbCap = lb.querySelector(".lb-caption"), lbCount = lb.querySelector(".lb-count");
    var group = [], idx = 0;
    var show = function (i) {
      idx = (i + group.length) % group.length;
      var a = group[idx];
      lbImg.src = a.getAttribute("href");
      lbImg.alt = a.getAttribute("data-caption") || "";
      lbCap.textContent = a.getAttribute("data-caption") || "";
      lbCount.textContent = (idx + 1) + " / " + group.length;
    };
    doc.addEventListener("click", function (e) {
      var a = e.target.closest("[data-lightbox]");
      if (!a) return;
      e.preventDefault();
      group = $$('[data-lightbox="' + a.getAttribute("data-lightbox") + '"]');
      show(group.indexOf(a));
      lb.classList.add("is-open");
      doc.body.style.overflow = "hidden";
    });
    var shut = function () { lb.classList.remove("is-open"); doc.body.style.overflow = ""; };
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(idx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(idx + 1); });
    lb.querySelector(".lb-close").addEventListener("click", shut);
    lb.addEventListener("click", function (e) { if (e.target === lb) shut(); });
    doc.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") shut();
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
    var tx = null;
    lb.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (tx === null) return;
      var dx = e.changedTouches[0].clientX - tx;
      if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
      tx = null;
    });
  }

  /* Copy account numbers */
  doc.addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b || !navigator.clipboard) return;
    navigator.clipboard.writeText(b.getAttribute("data-copy")).then(function () {
      var t = b.textContent; b.textContent = "Copied"; setTimeout(function () { b.textContent = t; }, 1500);
    });
  });

  /* Newsletter without leaving the page */
  $$("form[data-subscribe]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var note = doc.getElementById("letter-note");
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "fetch" } })
        .then(function (r) { return r.text().then(function (t) { return { ok: r.ok, t: t }; }); })
        .then(function (res) {
          note.textContent = res.ok ? "Thank you. You are on the list." :
            (res.t === "limit" ? "Too many tries. Please wait a few minutes." : "That email address does not look right.");
          if (res.ok) form.reset();
        })
        .catch(function () { note.textContent = "Something went wrong. Please try again."; });
    });
  });
})();
