const currentSlide = document.querySelector("[data-current-slide]")?.dataset.currentSlide;

/** Inclusive [start, end] by advancement index (`data-current-slide`). Keys match nav `data-slide`. */
const NAV_SECTION_RANGE = {
  1: [1, 1],
  12: [12, 14],
  15: [15, 17],
};

if (currentSlide) {
  const n = Number.parseInt(currentSlide, 10);
  if (!Number.isNaN(n)) {
    document.querySelectorAll(".nav-links [data-slide]").forEach((link) => {
      const key = Number.parseInt(link.dataset.slide, 10);
      const range = NAV_SECTION_RANGE[key];
      if (!range) {
        return;
      }
      const [lo, hi] = range;
      if (n >= lo && n <= hi) {
        link.classList.add("is-active");
        link.setAttribute("aria-current", "page");
      }
    });
  }
}

const slideFigure = document.querySelector(".slide-figure");
const slideImage = document.querySelector(".slide-image");
const slideCopy = document.querySelector(".slide-copy");
const fullscreenSessionKey = "esrClassFullscreen";
const slideShell = document.querySelector("main[data-current-slide]");
const slideAudioSrc =
  slideShell?.getAttribute("data-slide-audio")?.trim() || "";

if (slideFigure && slideImage) {
  let slideAudio = null;

  const resolveSlideAudioUrl = () => {
    if (!slideAudioSrc) {
      return "";
    }
    const fileName =
      slideAudioSrc.split("/").filter(Boolean).pop() || slideAudioSrc;
    if (slideImage?.src) {
      const imgUrl = new URL(slideImage.src, window.location.href);
      const audioPath = imgUrl.pathname.replace(
        /\/images\/esr-class\/[^/]+$/,
        `/audio/${fileName}`
      );
      if (audioPath !== imgUrl.pathname) {
        return `${imgUrl.origin}${audioPath}`;
      }
    }
    try {
      return new URL(slideAudioSrc, window.location.href).href;
    } catch {
      return slideAudioSrc;
    }
  };

  const ensureSlideAudio = () => {
    const url = resolveSlideAudioUrl();
    if (!url) {
      return null;
    }
    if (!slideAudio) {
      slideAudio = new Audio(url);
      slideAudio.preload = "auto";
    } else if (slideAudio.src !== url) {
      slideAudio.src = url;
    }
    return slideAudio;
  };

  const stopSlideAudio = () => {
    if (!slideAudio) {
      return;
    }
    slideAudio.pause();
    slideAudio.currentTime = 0;
  };

  const playSlideAudio = () => {
    const audio = ensureSlideAudio();
    if (!audio) {
      return;
    }
    audio.currentTime = 0;
    const playAttempt = audio.play();
    if (playAttempt !== undefined) {
      playAttempt.catch((error) => {
        console.warn("ESR slide audio could not play:", error);
      });
    }
  };
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
    stopSlideAudio();
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
    stopSlideAudio();
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
    requestAnimationFrame(() => closeButton.focus());
  };

  fullscreenButton.addEventListener("click", () => {
    playSlideAudio();
    openFullscreen();
  });

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
    playSlideAudio();
  }
}

const zoneModal = document.querySelector("[data-zone-modal]");
const zoneModalTitle = document.querySelector("#zone-modal-title");
const zoneModalBody = document.querySelector("#zone-modal-body");
let activeZoneTrigger = null;

if (zoneModal && zoneModalTitle && zoneModalBody) {
  const zoneCloseButton = zoneModal.querySelector(".zone-modal-close");

  const closeZoneModal = () => {
    if (zoneModal.hidden) {
      return;
    }

    zoneModal.hidden = true;
    document.body.classList.remove("is-zone-modal-open");

    if (activeZoneTrigger) {
      activeZoneTrigger.focus();
      activeZoneTrigger = null;
    }
  };

  const openZoneModal = (trigger) => {
    activeZoneTrigger = trigger;
    zoneModalTitle.textContent = trigger.dataset.zoneTitle || "";
    zoneModalBody.textContent = trigger.dataset.zoneBody || "";
    zoneModal.hidden = false;
    document.body.classList.add("is-zone-modal-open");

    if (zoneCloseButton) {
      zoneCloseButton.focus();
    }
  };

  document.querySelectorAll("[data-zone-title]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      openZoneModal(trigger);
    });
  });

  zoneModal.querySelectorAll("[data-zone-modal-close]").forEach((control) => {
    control.addEventListener("click", closeZoneModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeZoneModal();
    }
  });
}
