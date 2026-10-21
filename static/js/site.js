/* WEMASA website interactions — small, dependency-free, progressive. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, body = doc.body;
  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Header: solid background after scrolling, announcement offset */
  var header = $(".site-header"), announce = $(".announce"), toTop = $(".fab-top");
  function setAnnounce() { if (announce) root.style.setProperty("--announce-h", (announce.offsetHeight - window.scrollY > 0 ? announce.offsetHeight - window.scrollY : 0) + "px"); }
  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle("is-scrolled", y > 24);
    if (toTop) toTop.classList.toggle("is-visible", y > 900);
    setAnnounce();
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", setAnnounce);
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" }); });

  /* Generic open/close for drawer, search and modals */
  var lastFocus = null;
  function open(el) {
    if (!el) return;
    lastFocus = doc.activeElement;
    el.classList.add("is-open");
    el.setAttribute("aria-hidden", "false");
    body.style.overflow = "hidden";
    var f = $("[autofocus], input, button, a", el.querySelector(".drawer-panel, .search-box, .modal-panel") || el);
    if (f) setTimeout(function () { f.focus(); }, 60);
  }
  function close(el) {
    if (!el) return;
    el.classList.remove("is-open");
    el.setAttribute("aria-hidden", "true");
    body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  doc.addEventListener("click", function (e) {
    var opener = e.target.closest("[data-open]");
    if (opener) { e.preventDefault(); open(doc.getElementById(opener.getAttribute("data-open"))); return; }
    var closer = e.target.closest("[data-close]");
    if (closer) { e.preventDefault(); close(closer.closest(".drawer, .search-overlay, .modal")); return; }
    if (e.target.classList.contains("search-overlay") || e.target.classList.contains("modal")) close(e.target);
  });
  doc.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$(".drawer.is-open, .search-overlay.is-open, .modal.is-open").forEach(close);
    if (e.key === "/" && !/input|textarea|select/i.test(doc.activeElement.tagName)) {
      var s = doc.getElementById("search"); if (s) { e.preventDefault(); open(s); }
    }
  });

  /* Team biographies in a modal */
  var bioModal = doc.getElementById("bio-modal");
  if (bioModal) {
    $$("[data-bio]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var tpl = doc.getElementById(btn.getAttribute("data-bio"));
        if (!tpl) return;
        $(".modal-content", bioModal).innerHTML = tpl.innerHTML;
        open(bioModal);
      });
    });
  }

  /* Reveal on scroll. Anything already scrolled past is revealed too, so fast
     scrolling or jumping to an anchor never leaves hidden content behind. */
  var pending = $$(".reveal");
  function revealPassed() {
    if (!pending.length) return;
    var limit = window.innerHeight * 0.94;
    pending = pending.filter(function (el) {
      if (el.getBoundingClientRect().top < limit) { el.classList.add("is-in"); return false; }
      return true;
    });
  }
  if (reduceMotion) {
    pending.forEach(function (el) { el.classList.add("is-in"); });
    pending = [];
  } else {
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { revealPassed(); ticking = false; });
    }, { passive: true });
    window.addEventListener("resize", revealPassed);
    revealPassed();
  }

  /* Animated counters */
  var counters = $$("[data-count]");
  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    if (reduceMotion || target < 2) return;
    var start = null, dur = Math.min(2200, 900 + target / 4);
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min(1, (ts - start) / dur), eased = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(target * eased).toLocaleString("en-US");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { animateCount(en.target); co.unobserve(en.target); } });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* Lightbox for photo groups */
  var lb = doc.getElementById("lightbox");
  if (lb) {
    var lbImg = $("img", lb), lbCap = $(".lb-caption", lb), lbCount = $(".lb-count", lb), group = [], idx = 0;
    function show(i) {
      idx = (i + group.length) % group.length;
      var a = group[idx];
      lbImg.src = a.getAttribute("href");
      lbImg.alt = a.getAttribute("data-caption") || "";
      lbCap.textContent = a.getAttribute("data-caption") || "";
      lbCount.textContent = (idx + 1) + " / " + group.length;
    }
    doc.addEventListener("click", function (e) {
      var a = e.target.closest("[data-lightbox]");
      if (!a) return;
      e.preventDefault();
      group = $$('[data-lightbox="' + a.getAttribute("data-lightbox") + '"]');
      show(group.indexOf(a));
      open(lb);
    });
    $(".lb-prev", lb).addEventListener("click", function () { show(idx - 1); });
    $(".lb-next", lb).addEventListener("click", function () { show(idx + 1); });
    $(".lb-close", lb).addEventListener("click", function () { close(lb); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(lb); });
    doc.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
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

  /* Copy buttons (donation details) */
  doc.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    var text = btn.getAttribute("data-copy");
    var done = function () { btn.classList.add("is-done"); setTimeout(function () { btn.classList.remove("is-done"); }, 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done);
    else { var t = doc.createElement("textarea"); t.value = text; body.appendChild(t); t.select(); doc.execCommand("copy"); t.remove(); done(); }
  });

  /* Newsletter: submit without leaving the page */
  $$("form[data-subscribe]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var note = form.parentNode.querySelector(".subscribe-note"), btn = $("button", form);
      btn.disabled = true;
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "fetch" } })
        .then(function (r) { return r.text().then(function (t) { return { ok: r.ok, t: t }; }); })
        .then(function (res) {
          if (note) note.textContent = res.ok ? "Thank you! You are now subscribed to WEMASA updates." :
            (res.t === "limit" ? "Too many attempts — please try again later." : "Please enter a valid email address.");
          if (res.ok) form.reset();
        })
        .catch(function () { if (note) note.textContent = "Something went wrong. Please try again."; })
        .finally(function () { btn.disabled = false; });
    });
  });
})();

/* Home hero slider */
(function () {
  "use strict";
  var root = document.querySelector("[data-slider]");
  if (!root) return;
  var slides = Array.prototype.slice.call(root.querySelectorAll(".slide"));
  if (slides.length < 2) return;
  var dotsBox = root.querySelector("[data-dots]"), idx = 0, timer = null;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var dots = slides.map(function (_, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", "Show slide " + (i + 1));
    b.addEventListener("click", function () { go(i); restart(); });
    dotsBox.appendChild(b);
    return b;
  });
  function go(i) {
    idx = (i + slides.length) % slides.length;
    slides.forEach(function (s, n) {
      var on = n === idx;
      s.classList.toggle("is-active", on);
      s.setAttribute("aria-hidden", on ? "false" : "true");
      Array.prototype.forEach.call(s.querySelectorAll("a"), function (a) { a.tabIndex = on ? 0 : -1; });
      var img = s.querySelector("img[loading=lazy]");
      if (on && img) img.loading = "eager";
    });
    dots.forEach(function (d, n) { d.classList.toggle("on", n === idx); });
  }
  function restart() {
    if (reduce) return;
    clearInterval(timer);
    timer = setInterval(function () { go(idx + 1); }, 7000);
  }
  root.querySelector("[data-prev]").addEventListener("click", function () { go(idx - 1); restart(); });
  root.querySelector("[data-next]").addEventListener("click", function () { go(idx + 1); restart(); });
  root.addEventListener("mouseenter", function () { clearInterval(timer); });
  root.addEventListener("mouseleave", restart);
  go(0);
  restart();
})();

/* Home hero photos: each one fades into the next behind the headline. */
(function () {
  "use strict";
  var box = document.querySelector("[data-hero-photos]");
  if (!box) return;
  var imgs = Array.prototype.slice.call(box.querySelectorAll("img"));
  if (imgs.length < 2) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var idx = 0, busy = false;
  function load(img) {
    if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute("data-src"); }
  }
  function next() {
    if (busy || document.hidden) return;
    var n = (idx + 1) % imgs.length, img = imgs[n];
    load(img);
    function show() {
      busy = false;
      imgs[idx].classList.remove("is-on");
      img.classList.add("is-on");
      idx = n;
      load(imgs[(n + 1) % imgs.length]);
    }
    if (img.complete && img.naturalWidth) { show(); return; }
    busy = true;
    img.addEventListener("load", show, { once: true });
    img.addEventListener("error", function () { busy = false; imgs.splice(n, 1); }, { once: true });
  }
  window.addEventListener("load", function () { load(imgs[1]); });
  setInterval(next, 6000);
})();

/* Video player: a YouTube video loads only when played (thumbnails until then); uploaded files play in a <video>. */
(function () {
  var doc = document, modal, frame, video, lastFocus;
  function close() {
    if (!modal) return;
    modal.classList.remove("is-open");
    frame.src = "about:blank";
    video.pause();
    video.removeAttribute("src");
    video.load();
    doc.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  function open(url, title, kind) {
    if (!modal) {
      modal = doc.createElement("div");
      modal.className = "vid-modal";
      modal.setAttribute("role", "dialog");
      modal.setAttribute("aria-modal", "true");
      modal.innerHTML = '<div class="vid-modal-box"><button class="vid-modal-close" type="button" aria-label="Close video">&times;</button>' +
        '<div class="vid-modal-frame"><iframe allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>' +
        '<video controls playsinline></video></div></div>';
      doc.body.appendChild(modal);
      frame = modal.querySelector("iframe");
      video = modal.querySelector("video");
      modal.addEventListener("click", function (e) { if (e.target === modal || e.target.closest(".vid-modal-close")) close(); });
      doc.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    }
    lastFocus = doc.activeElement;
    modal.setAttribute("aria-label", title || "Video");
    var isFile = kind === "file";
    modal.classList.toggle("is-file", isFile);
    if (isFile) {
      video.src = url;
      video.play().catch(function () {});
    } else {
      frame.title = title || "Video";
      frame.src = url;
    }
    modal.classList.add("is-open");
    doc.body.style.overflow = "hidden";
    modal.querySelector(".vid-modal-close").focus();
  }
  doc.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-video]");
    if (!btn) return;
    e.preventDefault();
    open(btn.getAttribute("data-video"), btn.getAttribute("data-video-title"), btn.getAttribute("data-video-kind"));
  });
})();

/* Share buttons without a web link (Instagram): use the phone's share sheet, or copy the link. */
(function () {
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".share-native");
    if (!btn) return;
    var url = btn.getAttribute("data-share-url"), title = btn.getAttribute("data-share-title");
    var tip = btn.querySelector(".share-tip");
    function say(msg) {
      tip.textContent = msg;
      setTimeout(function () { tip.textContent = ""; }, 2600);
    }
    if (navigator.share && window.matchMedia("(pointer: coarse)").matches) {
      navigator.share({ title: title, url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () { say("Link copied: paste it on Instagram"); }, function () { window.prompt("Copy this link:", url); });
    } else {
      window.prompt("Copy this link:", url);
    }
  });
})();
