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
const fullscreenSessionKey = "esrClassFullscreen";

if (slideFigure && slideImage) {
  const previousPage = slideFigure.querySelector(".slide-arrow-left");
  const nextPage = slideFigure.querySelector(".slide-arrow-right");

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

  const createFullscreenArrow = (sourceLink, direction) => {
    if (!sourceLink) {
      return null;
    }

    const arrow = document.createElement("a");
    arrow.className = `fullscreen-arrow fullscreen-arrow-${direction}`;
    arrow.href = sourceLink.href;
    arrow.setAttribute(
      "aria-label",
      direction === "left" ? "Previous page" : "Next page"
    );

    return arrow;
  };

  const setFullscreenSession = (isActive) => {
    if (isActive) {
      sessionStorage.setItem(fullscreenSessionKey, "true");
    } else {
      sessionStorage.removeItem(fullscreenSessionKey);
    }
  };

  const navigateInFullscreen = (event) => {
    event.preventDefault();
    setFullscreenSession(true);
    window.location.href = event.currentTarget.href;
  };

  const previousArrow = createFullscreenArrow(previousPage, "left");
  const nextArrow = createFullscreenArrow(nextPage, "right");

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
  overlay.append(closeButton);
  if (previousArrow) {
    overlay.appendChild(previousArrow);
  }
  if (nextArrow) {
    overlay.appendChild(nextArrow);
  }
  overlay.appendChild(fullscreenContent);
  document.body.appendChild(overlay);

  const closeFullscreen = () => {
    setFullscreenSession(false);
    overlay.hidden = true;
    document.body.classList.remove("is-fullscreen-open");
    fullscreenButton.focus();
  };

  const openFullscreen = () => {
    setFullscreenSession(true);
    fullImage.src = slideImage.currentSrc || slideImage.src;
    overlay.hidden = false;
    document.body.classList.add("is-fullscreen-open");
    closeButton.focus();
  };

  fullscreenButton.addEventListener("click", openFullscreen);

  closeButton.addEventListener("click", closeFullscreen);

  if (previousArrow) {
    previousArrow.addEventListener("click", navigateInFullscreen);
  }

  if (nextArrow) {
    nextArrow.addEventListener("click", navigateInFullscreen);
  }

  document.addEventListener("keydown", (event) => {
    if (overlay.hidden) {
      return;
    }

    if (event.key === "ArrowLeft" && previousArrow) {
      previousArrow.click();
    } else if (event.key === "ArrowRight" && nextArrow) {
      nextArrow.click();
    }
  });

  if (sessionStorage.getItem(fullscreenSessionKey) === "true") {
    openFullscreen();
  }
}
