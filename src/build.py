"""Render multilingual Inkoo Life pages with the Python standard library."""

from datetime import date
from html import escape
from os import environ
from pathlib import Path
from shutil import copyfile
from string import Template

from editorial import EN, ZH, FR, ES

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "docs"
SOURCE = ROOT / "src"
ORIGIN = environ.get("SITE_ORIGIN", "https://jedieason.github.io/inkoo-life-demo").rstrip("/")

LANGS = (
    ("en", EN),
    ("zh", ZH),
    ("fr", FR),
    ("es", ES),
)

VIEWS = ("landscape", "portrait", "rear", "joint")
SCENES = (
    ("living", "living", 1280, 1600, 1067),
    ("wall", "living", 1350, 2000, 1333),
    ("beauty", "brands", 1280, 1400, 933),
    ("boutique", "brands", 1350, 1350, 900),
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


def product_pictures(words, base):
    images = []
    for index, (view, (_, alt)) in enumerate(zip(VIEWS, words["views"], strict=True)):
        active_class = " is-active" if index == 0 else ""
        asset = f"{base}/assets/{view}"
        images.append(
            f'<img class="product-view{active_class}" data-angle="{view}" '
            f'src="{asset}-1500.webp" srcset="{asset}-900.webp 900w, {asset}-1500.webp 1500w" '
            f'sizes="(max-width: 880px) 93vw, 54vw" width="1500" height="1000" '
            f'decoding="async" alt="{escape(alt)}">'
        )
    return "\n".join(images)


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
    if words["lang"] == "zh-Hant":
        suffix = " 秒"
    elif words["lang"] == "fr":
        suffix = " s"
    elif words["lang"] == "es":
        suffix = " s"
    else:
        suffix = " s"
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


def make_lang_menu(current_code, is_root, words):
    prefix = "" if is_root else "../"
    options = []
    for code, dict_data in LANGS:
        href = f"{prefix}" if code == "en" else f"{prefix}{code}/"
        active = " is-active" if code == current_code else ""
        options.append(
            f'<a href="{href}" class="lang-item{active}" hreflang="{dict_data["lang"]}" lang="{dict_data["lang"]}">'
            f'{dict_data["lang_name"]} <span>{dict_data["lang_code"]}</span></a>'
        )
    options_html = "\n".join(options)
    chevron = '<svg class="lang-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m1 1 4 4 4-4"/></svg>'
    return f"""<details class="lang-menu">
        <summary class="lang-trigger" aria-haspopup="true" aria-label="{escape(words['lang_select_label'])}">
          <span>{words['lang_code']}</span>
          {chevron}
        </summary>
        <div class="lang-dropdown" role="menu">
          {options_html}
        </div>
      </details>"""


def make_mobile_lang_menu(current_code, is_root, words):
    prefix = "" if is_root else "../"
    buttons = []
    for code, dict_data in LANGS:
        href = f"{prefix}" if code == "en" else f"{prefix}{code}/"
        active = " is-active" if code == current_code else ""
        buttons.append(
            f'<a href="{href}" class="mobile-lang-btn{active}" hreflang="{dict_data["lang"]}" lang="{dict_data["lang"]}">'
            f'{dict_data["lang_code"]}</a>'
        )
    buttons_html = "\n".join(buttons)
    return f"""<div class="mobile-lang-wrap">
        <span class="mobile-lang-title">{escape(words['lang_select_label'])}</span>
        <div class="mobile-lang-grid">
          {buttons_html}
        </div>
      </div>"""


def make_video_tracks(current_code, base):
    tracks = [
        ("en", "English", "captions", f"{base}/assets/inkoo-film-en.vtt"),
        ("zh-Hant", "繁體中文", "subtitles", f"{base}/assets/inkoo-film-zh.vtt"),
        ("fr", "Français", "subtitles", f"{base}/assets/inkoo-film-fr.vtt"),
        ("es", "Español", "subtitles", f"{base}/assets/inkoo-film-es.vtt"),
    ]
    lines = []
    for srclang, label, kind, src in tracks:
        default_attr = " default" if (current_code == "zh" and srclang == "zh-Hant") or (current_code == srclang) else ""
        lines.append(f'<track kind="{kind}" label="{label}" srclang="{srclang}" src="{src}"{default_attr}>')
    return "\n".join(lines)


def render_page(code, words):
    is_root = (code == "en")
    base = "." if is_root else ".."
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
        canonical=f"{ORIGIN}/" if is_root else f"{ORIGIN}/{code}/",
        en_canonical=f"{ORIGIN}/",
        zh_canonical=f"{ORIGIN}/zh/",
        fr_canonical=f"{ORIGIN}/fr/",
        es_canonical=f"{ORIGIN}/es/",
        home="./" if is_root else "../",
        lang_menu=make_lang_menu(code, is_root, words),
        mobile_lang_menu=make_mobile_lang_menu(code, is_root, words),
        video_tracks=make_video_tracks(code, base),

        landscape_alt=escape(words["views"][0][1]),
        product_images=product_pictures(words, base),
        product_buttons=picture_controls(words, base),
        featured_specs=definition_list(*zip(*words["featured_specs"], strict=True)),
        models=model_cards(words),
        spaces=scene_cards(words, base),
        technology=technology_details(words),
        pigments_height="1450",
        app_list="\n".join(f"<li><strong>{escape(title)}</strong><span>{escape(body)}</span></li>"
                            for title, body in words["app_items"]),
    )
    path = DIST / "index.html" if is_root else DIST / code / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.substitute(page), encoding="utf-8")


if __name__ == "__main__":
    for code, words in LANGS:
        render_page(code, words)
    for file in ("style.css", "site.js"):
        copyfile(SOURCE / file, DIST / file)
