document.documentElement.classList.add("has-js");

const menu = document.querySelector(".mobile-menu");
menu.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    menu.open = false;
    const target = link.hash && document.querySelector(link.hash);
    if (target) {
      target.tabIndex = -1;
      target.focus({ preventScroll: true });
    }
  });
});
menu.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu.open) {
    menu.open = false;
    menu.querySelector("summary").focus();
  }
});

const langMenu = document.querySelector(".lang-menu");
if (langMenu) {
  document.addEventListener("click", (event) => {
    if (!langMenu.contains(event.target)) {
      langMenu.open = false;
    }
  });
  langMenu.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && langMenu.open) {
      langMenu.open = false;
      langMenu.querySelector("summary").focus();
    }
  });
}

const progress = document.querySelector(".reading-progress");
let progressFrame;
function updateProgress() {
  progressFrame = undefined;
  const travel = document.documentElement.scrollHeight - window.innerHeight;
  const fraction = travel > 0 ? Math.min(1, Math.max(0, window.scrollY / travel)) : 0;
  progress.style.transform = `scaleX(${fraction})`;
}
function queueProgress() {
  progressFrame ??= requestAnimationFrame(updateProgress);
}
window.addEventListener("scroll", queueProgress, { passive: true });
window.addEventListener("resize", queueProgress);
new ResizeObserver(queueProgress).observe(document.body);
queueProgress();

const navLinks = [...document.querySelectorAll(".header-inner nav a[href^='#']")];
const sections = [...new Set(navLinks.map((link) => document.querySelector(link.hash)))];
const sectionObserver = new IntersectionObserver(() => {
  const active = sections.findLast((section) => section.getBoundingClientRect().top <= innerHeight * .42);
  navLinks.forEach((link) => {
    if (active && link.hash === `#${active.id}`) {
      link.setAttribute("aria-current", "location");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}, { rootMargin: "-41% 0px -58% 0px" });
sections.forEach((section) => sectionObserver.observe(section));

function openLinkedDetail() {
  const id = window.location.hash.slice(1);
  const item = document.getElementById(id);
  if (item?.tagName === "DETAILS") item.open = true;
}
window.addEventListener("hashchange", openLinkedDetail);
openLinkedDetail();

const productViews = [...document.querySelectorAll(".product-picture .product-view")];
const viewButtons = [...document.querySelectorAll("[data-view]")];

productViews.forEach((img) => {
  if (img.complete) return;
  img.decode?.().catch(() => {});
});

viewButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (button.getAttribute("aria-pressed") === "true") return;
    const targetAngle = button.dataset.angle;
    viewButtons.forEach((view) => view.setAttribute("aria-pressed", String(view === button)));
    productViews.forEach((img) => {
      const match = img.dataset.angle === targetAngle;
      img.classList.toggle("is-active", match);
    });
  });
});

const filters = [...document.querySelectorAll("[data-filter]")];
const spaceGrid = document.getElementById("space-grid");
const scenarios = [...document.querySelectorAll("[data-space]")];
filters.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    spaceGrid.classList.toggle("is-filtered", filter !== "all");
    filters.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    scenarios.forEach((scenario) => {
      scenario.hidden = filter !== "all" && filter !== scenario.dataset.space;
    });
  });
});

const sceneDialog = document.getElementById("scene-dialog");
const filmDialog = document.getElementById("film-dialog");
if (typeof sceneDialog.showModal === "function") {
  const sceneTitle = sceneDialog.querySelector("h2");
  const sceneImage = sceneDialog.querySelector("img");
  const sceneDescription = sceneDialog.querySelector("p");
  let currentSceneRequest = 0;

  function resetSceneImage() {
    sceneImage.classList.add("is-loading");
    sceneImage.removeAttribute("src");
    sceneImage.removeAttribute("srcset");
  }

  sceneDialog.addEventListener("close", resetSceneImage);

  document.querySelectorAll("[data-scene]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();

      const requestId = ++currentSceneRequest;
      const targetSrc = link.href;
      const targetAlt = link.querySelector("img")?.alt || link.dataset.title;

      sceneTitle.textContent = link.dataset.title;
      sceneDescription.textContent = link.dataset.description;

      // Immediately clear the previous image and keep hidden to prevent flashing old content
      resetSceneImage();
      sceneDialog.showModal();

      // Decode/load new image before revealing
      const preload = new Image();
      preload.src = targetSrc;
      preload.decode?.()
        .catch(() => {})
        .finally(() => {
          if (requestId === currentSceneRequest && sceneDialog.open) {
            sceneImage.src = targetSrc;
            sceneImage.alt = targetAlt;
            sceneImage.classList.remove("is-loading");
          }
        });
    });
  });

  const film = document.querySelector("[data-film]");
  const video = filmDialog.querySelector("video");
  film.addEventListener("click", (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (!video.hasAttribute("src")) video.src = film.href;
    filmDialog.showModal();
    video.play().catch(() => { /* The native controls remain available. */ });
  });
  filmDialog.addEventListener("close", () => video.pause());

  [sceneDialog, filmDialog].forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  });
}
