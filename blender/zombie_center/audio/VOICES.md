# THE ZOMBIE CENTER — fixed ElevenLabs voices (designed 2026-11-27, reuse in every episode)

| Character | ElevenLabs name | voice_id | Notes |
|---|---|---|---|
| Arin (001) | ZC Arin | `esUiLHlOC7xxPj76NPct` | young, tense, clear; f0 ≈ 113 Hz |
| Nika (002) | ZC Nika | `7f6ZfcsK6yFC46DmasB8` | soft, breathy, clearest of 3 (whisper logprob −0.24); f0 ≈ 222 Hz |
| Mark (unknown caller) | ZC Mark | `J1hbNXzUMAwyHYkHyltM` | low, rough, calm; in EP01 heard through a light voice changer (band-pass + slight pitch-down) |

Rules: Persian lines with `eleven_multilingual_v2` (emotion in wording/punctuation, v2 ignores [tags]);
loudnorm I=-16 per line; effects ducked ≈ −13 dB under speech; final mix checked with faster-whisper (small, fa).
Not designed yet: Elena, Sara, Sam, Kaveh (design when their episodes start, same method; save the id here).
Design previews (audition files) are in `voice_design/`.
