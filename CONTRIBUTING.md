# Contributing to BELT

The website is built automatically from the notebooks in this repository.
You never need to edit HTML: add or translate notebooks, push, and the site
updates itself. Here is how to contribute each kind of addition.

## Translate the course into a new language

1. Copy the whole `notebooks/en/` folder to a new folder named with your
   language code, for example `notebooks/nah/` for Nahuatl.
2. In each notebook, translate the **text (markdown) cells only**. Leave the
   code cells exactly as they are, so that fixes to the code can be applied
   to every language automatically.
3. Open a pull request.

That's it. The site gets a new page for your language, with a link in the
top navigation, built from your translated notebooks.

**You don't have to translate everything at once.** Any lesson you haven't
translated yet will appear on your language's page with an "English only"
badge, linking to the English version. Translate lessons one at a time and
the badges disappear as you go.

A few details:

- The lesson title shown on the website is the first heading of the
  notebook, so translating that heading translates the site too.
- Keep the number at the start of each filename. It controls the order of
  lessons on the page. The rest of the filename is used to match your
  translation to the English lesson, so don't change it.
- To translate the website's own text (the subtitle and section headers),
  add an entry for your language to `UI_TEXT` in `scripts/build_site.py`,
  or just ask for help in your pull request and we'll add it.

## Add a new lesson

1. Add a notebook to `notebooks/en/skills/` (for a skill lesson) or
   `notebooks/en/` (for a project), named with the next number, for example
   `11. My New Lesson.ipynb`.
2. Start the notebook with a heading. That heading becomes the title on the
   website.
3. Open a pull request.

The lesson appears on the English page right away, and on every other
language's page with an "English only" badge until someone translates it.

## Add a corpus

1. Zip your plain text (.txt) files: `zip mylanguage.zip *.txt`
2. Add the zip to the `corpora/` folder and open a pull request.

Once merged, anyone can load it in a lesson with
`util.download_corpus("mylanguage")`.

## Testing the site locally

```
python scripts/build_site.py
```

Then open `docs/index.html` in a browser. The same script runs
automatically on GitHub after every merge to main.
