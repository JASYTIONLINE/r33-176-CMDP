const currentSlide = document.querySelector("[data-current-slide]")?.dataset.currentSlide;

if (currentSlide) {
  document.querySelectorAll("[data-slide]").forEach((link) => {
    if (link.dataset.slide === currentSlide) {
      link.classList.add("is-active");
      link.setAttribute("aria-current", "page");
    }
  });
}

const slideFigure = document.querySelector(".slide-figure");
const slideImage = document.querySelector(".slide-image");
const slideCopy = document.querySelector(".slide-copy");

if (slideFigure && slideImage) {
  const fullscreenButton = document.createElement("button");
  fullscreenButton.className = "fullscreen-toggle";
  fullscreenButton.type = "button";
  fullscreenButton.setAttribute("aria-label", "View image full screen");
  slideFigure.appendChild(fullscreenButton);

  const overlay = document.createElement("div");
  overlay.className = "fullscreen-overlay";
  overlay.hidden = true;
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "Full screen slide image");

  const closeButton = document.createElement("button");
  closeButton.className = "fullscreen-close";
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "Close full screen image");

  const fullImage = document.createElement("img");
  fullImage.className = "fullscreen-image";
  fullImage.src = slideImage.currentSrc || slideImage.src;
  fullImage.alt = slideImage.alt;

  const fullscreenContent = document.createElement("div");
  fullscreenContent.className = "fullscreen-content";

  const imagePane = document.createElement("div");
  imagePane.className = "fullscreen-image-pane";
  imagePane.appendChild(fullImage);

  const copyPane = document.createElement("div");
  copyPane.className = "fullscreen-copy";
  if (slideCopy) {
    copyPane.innerHTML = slideCopy.innerHTML;
  }

  fullscreenContent.append(imagePane, copyPane);
  overlay.append(closeButton, fullscreenContent);
  document.body.appendChild(overlay);

  const closeFullscreen = () => {
    overlay.hidden = true;
    document.body.classList.remove("is-fullscreen-open");
    fullscreenButton.focus();
  };

  fullscreenButton.addEventListener("click", () => {
    fullImage.src = slideImage.currentSrc || slideImage.src;
    overlay.hidden = false;
    document.body.classList.add("is-fullscreen-open");
    closeButton.focus();
  });

  closeButton.addEventListener("click", closeFullscreen);

  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) {
      closeFullscreen();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !overlay.hidden) {
      closeFullscreen();
    }
  });
}
