"""Builds the course website in docs/ from the notebooks in notebooks/.

The site is generated entirely from the files in the repository, so adding
a language, lesson, or corpus never requires editing the site by hand.
See CONTRIBUTING.md for the conventions.

Run from the repository root:

    python scripts/build_site.py
"""

import html
import json
import os
import re
import urllib.parse

NOTEBOOKS_DIR = "notebooks"
OUTPUT_DIR = "docs"
COLAB_BASE = "https://colab.research.google.com/github/lecs-lab/belt/blob/main/"
REPO_URL = "https://github.com/lecs-lab/belt"

# Each language folder can have a site.json with the interface text for
# its page (subtitle, section names, badge text, and the language's display
# name). Copy notebooks/en/site.json and translate it. Languages without
# one fall back to the English text.
def load_ui_text(language):
    path = os.path.join(NOTEBOOKS_DIR, language, "site.json")
    with open(os.path.join(NOTEBOOKS_DIR, "en", "site.json")) as f:
        text = json.load(f)
    # Don't inherit English's display name; default to the folder code
    text["language_name"] = language.upper()
    if os.path.exists(path):
        with open(path) as f:
            text.update(json.load(f))
    return text

# Icons for known lessons, keyed by the lesson's slug (see slug()).
# Lessons without an entry get the default icon, so this is optional too.
ICONS = {
    "introduction": ("fa-solid fa-circle-play", "bg-purple"),
    "python": ("fa-brands fa-python", "bg-purple"),
    "data-types": ("fa-solid fa-database", "bg-indigo"),
    "logical-structures": ("fa-solid fa-diagram-next", "bg-blue"),
    "lists": ("fa-regular fa-rectangle-list", "bg-cyan"),
    "strings": ("fa-solid fa-font", "bg-teal"),
    "files": ("fa-regular fa-folder-open", "bg-blue"),
    "gradio": ("fa-solid fa-window-maximize", "bg-indigo"),
    "regex": ("fa-solid fa-magnifying-glass", "bg-purple"),
    "machine-learning": ("fa-solid fa-brain", "bg-teal"),
    "spellchecker": ("fa-solid fa-spell-check", "bg-purple"),
    "predictive-text": ("fa-solid fa-keyboard", "bg-indigo"),
    "word-games": ("fa-solid fa-puzzle-piece", "bg-blue"),
    "predictive-text-with-deep-learning": ("fa-solid fa-network-wired", "bg-cyan"),
    "automatic-inflection": ("fa-solid fa-arrows-split-up-and-left", "bg-teal"),
    "putting-your-app-on-a-phone": ("fa-solid fa-mobile-screen-button", "bg-indigo"),
}
DEFAULT_ICON = ("fa-solid fa-book", "bg-blue")


def slug(filename):
    """Identifies a lesson across languages: '3. Word Games.ipynb' -> 'word-games'.

    The number prefix is ignored so languages can number lessons differently.
    """
    name = os.path.splitext(filename)[0]
    name = re.sub(r"^\d+[\.\-]?\s*", "", name)
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def order(filename):
    """Sort key from the number prefix of a filename."""
    match = re.match(r"^(\d+)", filename)
    return int(match.group(1)) if match else 999


def notebook_title(path):
    """The lesson title is the first line of the first markdown cell."""
    with open(path) as f:
        nb = json.load(f)
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            for line in "".join(cell["source"]).splitlines():
                # Strip heading markers, bold markers, and any number prefix
                line = line.replace("#", "").replace("*", "").strip()
                line = re.sub(r"^\d+[\.\)]?\s*", "", line)
                if line:
                    return line
            break
    return os.path.splitext(os.path.basename(path))[0]


def find_lessons(language, subfolder=""):
    """Lists the lessons for a language, sorted by their number prefix."""
    folder = os.path.join(NOTEBOOKS_DIR, language, subfolder)
    if not os.path.isdir(folder):
        return []
    lessons = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".ipynb"):
            continue
        path = os.path.join(folder, filename)
        lessons.append({
            "slug": slug(filename),
            "order": order(filename),
            "title": notebook_title(path),
            "path": path,
        })
    return sorted(lessons, key=lambda lesson: lesson["order"])


def colab_url(path):
    return COLAB_BASE + urllib.parse.quote(path)


def tile(lesson, badge=None):
    icon, color = ICONS.get(lesson["slug"], DEFAULT_ICON)
    badge_html = f'<span class="badge">{html.escape(badge)}</span>' if badge else ""
    return f"""                <a class="tile" href="{colab_url(lesson['path'])}" target="_blank">
                    <span class="icon sm {color}"><i class="{icon}"></i></span>
                    <span class="label">{html.escape(lesson['title'])}{badge_html}</span>
                </a>
"""


def merge_with_english(lessons, english_lessons):
    """Pairs a language's lessons with English ones so missing translations
    still appear on the page (linked to the English notebook, with a badge)."""
    by_slug = {lesson["slug"]: lesson for lesson in lessons}
    merged = []
    for english_lesson in english_lessons:
        if english_lesson["slug"] in by_slug:
            merged.append((by_slug[english_lesson["slug"]], False))
        else:
            merged.append((english_lesson, True))
    # Keep any lessons the language has that English doesn't
    english_slugs = {lesson["slug"] for lesson in english_lessons}
    for lesson in lessons:
        if lesson["slug"] not in english_slugs:
            merged.append((lesson, False))
    return merged


def language_nav(languages, current):
    links = []
    for language in languages:
        href = "./" if language == current else (f"../{language}/" if current != "en" else f"{language}/")
        if language == "en":
            href = "../" if current != "en" else "./"
        active = ' class="active"' if language == current else ""
        links.append(f'<a href="{href}"{active}>{language.upper()}</a>')
    return "\n                    ".join(links)


def build_page(language, languages, english_skills, english_projects):
    text = load_ui_text(language)

    if language == "en":
        skills = [(lesson, False) for lesson in english_skills]
        projects = [(lesson, False) for lesson in english_projects]
    else:
        skills = merge_with_english(find_lessons(language, "skills"), english_skills)
        projects = merge_with_english(find_lessons(language), english_projects)

    # The first skills lesson is the introduction and gets the big card
    intro, intro_is_english = skills[0]
    skills = skills[1:]

    def tiles(lessons):
        return "".join(
            tile(lesson, text["english_only"] if is_english else None)
            for lesson, is_english in lessons
        )

    styles_href = "styles.css" if language == "en" else "../styles.css"
    intro_badge = f' <span class="badge">{html.escape(text["english_only"])}</span>' if intro_is_english else ""

    return f"""<!doctype html>
<html lang="{language}">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Building Endangered Language Technology</title>
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        />
        <link rel="stylesheet" href="{styles_href}" />
    </head>
    <body>
        <div class="wrap">
            <div class="topbar">
                <h1>Building Endangered Language Technology</h1>
                <nav class="langs">
                    {language_nav(languages, language)}
                </nav>
            </div>
            <p class="subtitle">{html.escape(text["subtitle"])}</p>

            <a class="card" href="{colab_url(intro['path'])}" target="_blank">
                <span class="icon md bg-purple"><i class="fa-solid fa-circle-play"></i></span>
                <span>
                    <div class="title">{html.escape(text["intro_title"])}{intro_badge}</div>
                    <div class="desc">{html.escape(text["intro_desc"])}</div>
                </span>
            </a>

            <section class="section">
                <h3>{html.escape(text["skills"])}</h3>
                <p class="desc">{html.escape(text["skills_desc"])}</p>
                <div class="grid">
{tiles(skills)}                </div>
            </section>

            <section class="section">
                <h3>{html.escape(text["projects"])}</h3>
                <p class="desc">{html.escape(text["projects_desc"])}</p>
                <div class="grid">
{tiles(projects)}                </div>
            </section>

            <footer class="footer">
                <p class="desc">
                    <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">{html.escape(text["contribute"])}</a>
                </p>
            </footer>
        </div>
    </body>
</html>
"""


def main():
    languages = sorted(
        entry for entry in os.listdir(NOTEBOOKS_DIR)
        if os.path.isdir(os.path.join(NOTEBOOKS_DIR, entry, "skills"))
    )
    # English first, since it's the reference language
    languages.remove("en")
    languages.insert(0, "en")

    english_skills = find_lessons("en", "skills")
    english_projects = find_lessons("en")

    for language in languages:
        page = build_page(language, languages, english_skills, english_projects)
        folder = OUTPUT_DIR if language == "en" else os.path.join(OUTPUT_DIR, language)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "index.html"), "w") as f:
            f.write(page)
        print(f"Built {folder}/index.html")


if __name__ == "__main__":
    main()
