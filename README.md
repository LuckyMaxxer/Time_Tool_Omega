# Time Tool Ω

A small, efficient Windows time tool built to be fast, not pretty. Dark mode, no timezone databases, pure offset math, and one job on each tab.

## Features

- **AM/PM ⇄ 24h** — instantly convert one format to the other.
- **Time Difference** — enter a time for you and a time for a friend, get the offset (ahead/behind) and reuse it.
- **Live Clocks** — ticking local clock plus friend rows with their live time and actual weekday/date (e.g. `Sat 29`), persisted in `friends.txt`.
- **Time Calculator** — start time ± hours/minutes with a +/- toggle, showing the 24h result, the 12h equivalent, and `(+1 day)`-style rollover hints.
- Dark UI with dark title bar, non-selectable placeholder text, and window position/size remembered between runs.

## Run

Double-click **`Time Tool Ω .pyw`** (opens with no console window), or run:

```
python "Time Tool Ω .py"
```

Requires Python 3 with Tkinter (bundled with Windows Python installs). No third-party packages.

Keep both Python files in the same folder — the `.pyw` is just a launcher for the `.py`. `friends.txt` and `settings.json` are created automatically as you use the app.

## Files

| File | Purpose |
| --- | --- |
| `Time Tool Ω .py` | The entire app |
| `Time Tool Ω .pyw` | Console-less launcher (no command prompt) |
| `friends.txt` | Friend name + offset in minutes, one per line (created on first add) |
| `settings.json` | Remembered window position/size (written on close) |
| `examples.txt` | Usage examples |

## Made with OpenCode

This entire app was written **with [OpenCode](https://opencode.ai) **. Also: I have no clue what this script actually is. It compiles, it runs, the buttons do things — I'm not going to question it.

**Personal opinion on AI coding:** normally it's bad — there will be errors. That only matters if you're using it for something truly important, if you're writing more code on top of it, or if real code depends on the AI-generated code. This is a personal script. None of that applies here. Use accordingly.

## License

MIT — or whatever you want. It's a time tool.
