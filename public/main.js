(function () {
  var cfg = window.PORTFOLIO || {};

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
