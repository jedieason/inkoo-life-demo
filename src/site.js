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

const productImage = document.getElementById("product-view");
const viewButtons = [...document.querySelectorAll("[data-view]")];
viewButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (button.getAttribute("aria-pressed") === "true") return;
    viewButtons.forEach((view) => view.setAttribute("aria-pressed", String(view === button)));
    const asset = button.dataset.view;
    productImage.dataset.angle = button.dataset.angle;
    productImage.srcset = `${asset}-900.webp 900w, ${asset}-1500.webp 1500w`;
    productImage.src = `${asset}-1500.webp`;
    productImage.alt = button.dataset.alt;
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
  document.querySelectorAll("[data-scene]").forEach((link) => {
    link.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      sceneTitle.textContent = link.dataset.title;
      sceneDescription.textContent = link.dataset.description;
      sceneImage.src = link.href;
      sceneImage.alt = link.querySelector("img").alt;
      sceneDialog.showModal();
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
