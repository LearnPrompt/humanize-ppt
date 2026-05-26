# Presenter Render Report

status: pass

## Outputs

- `index.html`
- `notes.json`
- `presenter_manifest.json`
- `presenter-screenshot.png`

## Checks

- Deck control bridge added to `../ppt/index.html`.
- Presenter shell can control current slide through `postMessage`.
- Speaker notes cover all 8 slides.
- Current slide preview and next slide card are available.
- Timer controls are local-only and do not modify the deck.
- Playwright smoke check passed: clicking next moved the visible notes from slide 1 to slide 2 and the deck iframe reported `window.__currentSlideIndex === 1`.
