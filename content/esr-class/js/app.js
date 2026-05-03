const currentSlide = document.querySelector("[data-current-slide]")?.dataset.currentSlide;

if (currentSlide) {
  document.querySelectorAll("[data-slide]").forEach((link) => {
    if (link.dataset.slide === currentSlide) {
      link.classList.add("is-active");
      link.setAttribute("aria-current", "page");
    }
  });
}
