/**
 * Notion Early Career — Interview Guide
 *
 * Scroll-reveal for elements tagged `.reveal`, with a small stagger across
 * timeline items, plus a per-doodle reveal for the hand-drawn ink.
 *
 * The doodles are observed individually rather than inheriting `.is-visible`
 * from an ancestor: the whole timeline lives inside one `.section.reveal`, so
 * an ancestor-keyed rule fired every marker's ink animation at once the moment
 * the section's top edge appeared — with stages further down still well below
 * the fold, their animations played to nobody. Observing each drawing means
 * each one is actually drawn on as it arrives.
 */
(() => {
  const revealTargets = document.querySelectorAll(".reveal");
  const inkTargets = document.querySelectorAll(".doodle-ink, .doodle-bulb");

  // Stagger the timeline entries so they don't all pop in at once.
  document.querySelectorAll(".timeline__item").forEach((item, i) => {
    item.style.transitionDelay = `${Math.min(i * 60, 240)}ms`;
  });

  const revealAll = () => {
    revealTargets.forEach((el) => el.classList.add("is-visible"));
    inkTargets.forEach((el) => el.classList.add("is-visible"));
  };

  if (!("IntersectionObserver" in window)) {
    revealAll();
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
  );

  revealTargets.forEach((el) => observer.observe(el));

  // Watch each doodle's CONTAINER, not the doodle itself. The un-revealed
  // state clips the image to zero width via clip-path, and IntersectionObserver
  // measures the clipped area — so an unrevealed doodle reports
  // intersectionRatio 0 even when it is sitting in the middle of the screen.
  // Observing it directly with any non-zero threshold deadlocks: it can never
  // become visible enough to be told to become visible. The container has no
  // such clip, so its ratio is honest.
  const inkObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target
          .querySelectorAll(".doodle-ink, .doodle-bulb")
          .forEach((d) => d.classList.add("is-visible"));
        inkObserver.unobserve(entry.target);
      });
    },
    { threshold: 0, rootMargin: "0px 0px -70px 0px" }
  );

  inkTargets.forEach((el) => {
    const anchor = el.parentElement || el;
    inkObserver.observe(anchor);
  });
})();
