"""Render English and Traditional Chinese pages with the Python standard library."""

from datetime import date
from html import escape
from os import environ
from pathlib import Path
from shutil import copyfile
from string import Template

from editorial import EN, ZH

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "docs"
SOURCE = ROOT / "src"
ORIGIN = environ.get("SITE_ORIGIN", "https://jedieason.github.io/include-life-demo").rstrip("/")

VIEWS = ("landscape", "portrait", "rear", "joint")
SCENES = (
    ("living", "living", 1280, 1600, 1067),
    ("wall", "living", 1350, 2000, 1333),
    ("beauty", "brands", 1280, 1400, 933),
    ("boutique", "brands", 1350, 1536, 1024),
)
# Diagonal inches, active width and height in mm, pixels, refresh seconds, net kg.
MODELS = (
    ("10.1", 203.2, 152.4, "1600 × 1200", "20–35", "0.4"),
    ("13.3", 270.4, 202.8, "1600 × 1200", "≤ 15", "≈ 1.5"),
    ("28.5", 592.2, 410.0, "2160 × 3060", "25–35", "6.1"),
    ("31.5", 696.3, 391.7, "2560 × 1440", "25–35", "6.2"),
)


def definition_list(labels, values):
    return "\n".join(f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"
                     for label, value in zip(labels, values, strict=True))


def picture_controls(words, base):
    buttons = []
    for index, (view, (label, alt)) in enumerate(zip(VIEWS, words["views"], strict=True)):
        selected = "true" if index == 0 else "false"
        asset = f"{base}/assets/{view}"
        buttons.append(f'<button type="button" aria-pressed="{selected}" aria-controls="product-view" '
                       f'data-view="{asset}" data-angle="{view}" data-alt="{escape(alt)}">{escape(label)}</button>')
    return "\n".join(buttons)


def model_cards(words):
    cards = []
    suffix = " 秒" if words["lang"] == "zh-Hant" else " s"
    for index, (size, width, height, pixels, refresh, weight) in enumerate(MODELS):
        specs = definition_list(words["model_labels"], (pixels, refresh + suffix,
                                words["batteries"][index], weight + " kg"))
        model_type = words["model_type"][index // 2]
        cards.append(f"""<article class="model">
          <div class="model-scale" aria-hidden="true">
            <span style="--model-width:{width / 696.3 * 100:.2f}%;--model-ratio:{width / height:.4f}"></span>
          </div>
          <h4>{size}<span>″</span></h4>
          <p>{escape(model_type)}</p>
          <dl>{specs}</dl>
        </article>""")
    return "\n".join(cards)


def scene_cards(words, base):
    cards = []
    for scene, localized in zip(SCENES, words["scenes"], strict=True):
        key, category, large, width, height = scene
        title, description, alt = map(escape, localized)
        asset = f"{base}/assets/{key}"
        category_label = words["filter_living" if category == "living" else "filter_brands"]
        cards.append(f"""<article class="space-card" data-space="{category}">
          <a class="space-image" href="{asset}-{large}.webp" data-scene data-title="{title}" data-description="{description}">
            <img src="{asset}-580.webp" width="{width}" height="{height}" loading="lazy" decoding="async" alt="{alt}">
            <span class="expand-icon" aria-hidden="true">+</span>
          </a>
          <div class="space-copy"><p class="space-category">{escape(category_label)}</p><h3>{title}</h3><p>{description}</p></div>
        </article>""")
    return "\n".join(cards)


def technology_details(words):
    rows = []
    for index, (anchor, title, body) in enumerate(words["tech_items"]):
        opened = " open" if index == 0 else ""
        rows.append(f'<details id="{anchor}"{opened}><summary>{escape(title)}</summary><p>{escape(body)}</p></details>')
    return "\n".join(rows)


def render_page(words, chinese):
    base = ".." if chinese else "."
    template = Template((SOURCE / "index.html").read_text(encoding="utf-8"))
    page = {
        key: escape(value) for key, value in words.items() if isinstance(value, str)
    }
    for key in ("hero_title", "collection_title", "product_title", "tech_title", "app_title", "film_title"):
        page[key] = words[key]
    page.update(
        base=base,
        origin=ORIGIN,
        current_year=date.today().year,
        canonical=f"{ORIGIN}/zh/" if chinese else f"{ORIGIN}/",
        en_path=f"{ORIGIN}/",
        zh_path=f"{ORIGIN}/zh/",
        home="./",
        alternate="../" if chinese else "./zh/",
        alternate_lang="en" if chinese else "zh-Hant",
        track_default=" default" if chinese else "",

        landscape_alt=escape(words["views"][0][1]),
        product_buttons=picture_controls(words, base),
        featured_specs=definition_list(*zip(*words["featured_specs"], strict=True)),
        models=model_cards(words),
        spaces=scene_cards(words, base),
        technology=technology_details(words),
        pigments_height="1450",
        app_list="\n".join(f"<li><strong>{escape(title)}</strong><span>{escape(body)}</span></li>"
                            for title, body in words["app_items"]),
    )
    path = DIST / "zh" / "index.html" if chinese else DIST / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.substitute(page), encoding="utf-8")


if __name__ == "__main__":
    render_page(EN, chinese=False)
    render_page(ZH, chinese=True)
    for file in ("style.css", "site.js"):
        copyfile(SOURCE / file, DIST / file)
