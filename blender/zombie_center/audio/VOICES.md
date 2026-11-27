# THE ZOMBIE CENTER — fixed ElevenLabs voices (reuse in every episode)

Rule (user, CLAUDE.md 2026-11-27): only the Persian voices already in the user's ElevenLabs account; never design new
voices; the earlier Claude-designed "ZC Arin / ZC Nika / ZC Mark" voices are NOT used.

| Character | ElevenLabs voice | voice_id | why |
|---|---|---|---|
| Arin (001), 19 | Arash - Clear, Confident Narrator | `Mn0jJ3FC9Ijz7lQe8ELI` | young, clearest of the auditions (whisper lp −0.47, f0 ≈ 129 Hz) |
| Nika (002), 16 | Amitis - Young & Soft | `C2wYIMnQQbFDm3qaosBN` | young, soft, whispery — a frightened video message |
| Mark (the unknown caller), 52 | «خشن» | `iHeRnhwgi9L0gzVK2VUe` | low, rough, older (f0 ≈ 78 Hz); EP01: heard through a light voice changer |

Rules: Persian lines with `eleven_multilingual_v2` (emotion in wording/punctuation); loudnorm I=-16 per line;
effects ducked ≈ −13 dB under speech; final mix checked with faster-whisper (small/medium, fa).
Still to cast (from the same list, when their episodes start): Elena, Sara, Sam, Kaveh. Sara (the voice) is used for
Kian in «پرنده» — avoid it here.
