/**
 * Notion Early Career — Interview Guide
 * Skeleton behavior only: a scroll-reveal for elements tagged `.reveal`,
 * with a small stagger across timeline items. Replace/extend this once
 * specific components are ready to be animated for real.
 */
(() => {
  const revealTargets = document.querySelectorAll(".reveal");

  // Stagger the timeline entries so they don't all pop in at once.
  document.querySelectorAll(".timeline__item").forEach((item, i) => {
    item.style.transitionDelay = `${Math.min(i * 60, 240)}ms`;
  });

  if (!("IntersectionObserver" in window)) {
    revealTargets.forEach((el) => el.classList.add("is-visible"));
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
})();
