# Ambient beds

Three mood beds selected based on the dominant mood detected from scenes:

- `warm.mp3` — A3+E4 pad with light reverb
- `melancholy.mp3` — G3+A#3 pad with longer reverb
- `upbeat.mp3` — A4+E5 brighter pad

These are synth placeholders generated with ffmpeg `sine` + `aecho` so the
pipeline is functional out of the box. Before any public demo, replace each
file with a Pixabay-licensed track of the same name (Pixabay License =
commercial OK, no attribution required). See `docs/RESEARCH_NOTES.md §3.5`.
Filenames must remain `{warm,melancholy,upbeat}.mp3` to match the mood keys
in `caption.py` / `music.py`.
