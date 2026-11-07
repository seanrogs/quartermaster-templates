# quartermaster-templates
Public repo for Quartermaster game systems and faction templates

## Website

templates.quartermaster.app is served from this repo by GitHub Pages. Each page (`index.html`, `HH.html`, `WHFB.html` and so on) is plain HTML: add templates inside the `<div id="content">` cards as before. The home page's "What's been updated?" list is the exception; see below. The header, footer and `style.css` match [quartermaster.app](https://github.com/seanrogs/quartermaster-site), so keep them in sync with that site's `_layouts/default.html` and `assets/css/site.css`.

## Posting a "What's been updated?" entry

The list on the home page is built from Markdown files in `_updates/`, newest first. The home page shows the latest 12 (`updates_shown` in `_config.yml`); older files can stay.

1. Add a file named `_updates/YYYY-MM-DD-short-name.md`. The date in the name is the date shown.
2. Write it like this:

   ```markdown
   ---
   title: "[Horus Heresy](HH.html#HH3): Prospero Burns & Errata"
   note: Game system updated with new Prime Advantages
   ---
   - [Daemons](HH.html#HH3-Daemons)
   - [Solar Auxilia](HH.html#HH3-Solar_Auxilia)
   - A change without a link
   - Escher: The House of Blades
     - [House Escher](GW.html#N26-House_Escher)
     - [Chymist Cult](GW.html#N26-Chymist_Cult)
   ```

   - `title` is required. Link the game system to its section, then add the release name after a colon.
   - `note` is optional, for game system changes. It shows in grey italics under the title.
   - Link each faction to its `id` on the game system's page. Indent items by two spaces to group them under a bold sub-heading.
3. Commit and push. GitHub Pages rebuilds the site within a minute or two.

To preview locally (uses the gems installed for quartermaster-site):

```bash
BUNDLE_GEMFILE=../quartermaster-site/Gemfile bundle exec jekyll serve --port 4001
```

Then open http://localhost:4001.
