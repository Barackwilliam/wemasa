(function () {
  "use strict";
  var doc = document;

  // Mobile sidebar
  doc.addEventListener("click", function (e) {
    if (e.target.closest("[data-toggle-sidebar]")) doc.body.classList.toggle("sidebar-open");
  });

  // Close the user menu when clicking elsewhere
  doc.addEventListener("click", function (e) {
    doc.querySelectorAll("details.user-menu[open]").forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute("open"); });
  });

  // Rich text: no file attachments (images are handled by the image fields)
  doc.addEventListener("trix-file-accept", function (e) { e.preventDefault(); });

  // File inputs: preview the chosen image and show the file name
  doc.querySelectorAll(".dropzone input[type=file]").forEach(function (input) {
    var zone = input.closest(".dropzone"), text = zone.querySelector(".dz-text"), preview = zone.querySelector(".dz-preview"), count = zone.querySelector(".dz-count");
    ["dragenter", "dragover"].forEach(function (ev) { zone.addEventListener(ev, function () { zone.classList.add("is-over"); }); });
    ["dragleave", "drop"].forEach(function (ev) { zone.addEventListener(ev, function () { zone.classList.remove("is-over"); }); });
    input.addEventListener("change", function () {
      var files = input.files;
      if (!files || !files.length) return;
      if (count) count.textContent = files.length + " file" + (files.length > 1 ? "s" : "") + " selected";
      if (files.length === 1) {
        text.innerHTML = "<strong></strong><small>Ready to upload — click Save</small>";
        text.querySelector("strong").textContent = files[0].name;
        if (preview && /^image\//.test(files[0].type)) {
          preview.src = URL.createObjectURL(files[0]);
          preview.hidden = false;
        }
      } else {
        text.innerHTML = "<strong>" + files.length + " photos selected</strong><small>Click Upload to add them</small>";
      }
    });
  });

  // Warn before leaving a form with unsaved changes
  var form = doc.querySelector("form.edit-form"), dirty = false;
  if (form) {
    form.addEventListener("input", function () { dirty = true; });
    form.addEventListener("change", function () { dirty = true; });
    doc.addEventListener("trix-change", function () { dirty = true; });
    form.addEventListener("submit", function () { dirty = false; });
    window.addEventListener("beforeunload", function (e) { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
  }

  // Sidebar: filter sections as you type
  var filter = doc.querySelector("[data-side-filter]");
  if (filter) {
    filter.addEventListener("input", function () {
      var q = filter.value.trim().toLowerCase();
      var group = null, groupHas = false;
      doc.querySelectorAll(".side-nav > *").forEach(function (el) {
        if (el.classList.contains("side-group")) {
          if (group) group.hidden = !groupHas;
          group = el; groupHas = false;
        } else {
          var hit = !q || el.textContent.toLowerCase().indexOf(q) > -1;
          el.hidden = !hit;
          if (hit) groupHas = true;
        }
      });
      if (group) group.hidden = !groupHas;
    });
    filter.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      var first = doc.querySelector(".side-nav > .side-link:not([hidden])");
      if (first) window.location.href = first.href;
    });
  }

  // Count up the overview figures
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    doc.querySelectorAll(".kpi [data-count]").forEach(function (el) {
      var end = parseInt(el.getAttribute("data-count"), 10) || 0, t0 = null;
      if (end < 2) return;
      el.textContent = "0";
      requestAnimationFrame(function step(t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / 900);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      });
    });
  }

  // Fade out success messages
  setTimeout(function () {
    doc.querySelectorAll(".toasts .toast-success").forEach(function (t) { t.style.transition = "opacity .5s"; t.style.opacity = "0"; setTimeout(function () { t.remove(); }, 500); });
  }, 5000);
})();
