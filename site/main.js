(function () {
  var cfg = window.PORTFOLIO || {};
  var space = (cfg.SPACE_URL || "").replace(/\/$/, "");

  // Point every demo link at the Hugging Face Space.
  document.querySelectorAll("[data-demo]").forEach(function (a) {
    a.href = space + "/" + a.getAttribute("data-demo") + "/";
  });
  document.querySelectorAll("[data-space]").forEach(function (a) { a.href = space + "/"; });

  // Show social buttons only when a link is configured.
  [["github", cfg.GITHUB], ["linkedin", cfg.LINKEDIN]].forEach(function (pair) {
    var el = document.querySelector('[data-social="' + pair[0] + '"]');
    if (!el) return;
    if (pair[1]) el.href = pair[1]; else el.hidden = true;
  });
  document.querySelectorAll("[data-name]").forEach(function (el) { el.textContent = cfg.NAME || ""; });

  // Reveal-on-scroll; everything stays visible if IntersectionObserver is missing.
  var items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) return;
  document.documentElement.classList.add("js-reveal");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  items.forEach(function (el) { io.observe(el); });
})();
