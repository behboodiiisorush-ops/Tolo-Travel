# Fixed ElevenLabs voices of the cast (reuse in every film — never pick another voice for these people)

Model for lines: `eleven_v4` (audio tags in English square brackets). Teenagers are pitched up a little in post
(`rubberband`, formants kept): Kian +2.5, Arian +1.5, Me +1.5, Mahsa +1.0 semitones.

| character | voice_id | ElevenLabs name |
|---|---|---|
| مامان (mom) | `9HVxKdwDzPJv4huwQfAt` | Hengameh — warm, expressive |
| آقای کاظمی (kazemi) | `UTG6yGbLJfJMpcozj8a5` | Aidin — husky middle-aged male |
| آقای رضایی (rezaei) | `iHeRnhwgi9L0gzVK2VUe` | «خشن» — rough old male (designed in this workspace) |
| آرین (arian) | `yPRQMUW8csecd8blHFfA` | Danesh — young male |
| مهسا (mahsa) | `g36FEKq8A536osj4GuaD` | Rashnow — young female |
| کیان (kian) | `fvCP6Z9Dzulf2E6NsM8a` | Amin.GS — young male |
| من (me) | `Mn0jJ3FC9Ijz7lQe8ELI` | Arash — clear young male |
| گوینده اخبار (anchor) | `qIzr1Kq6CyeYNQkLnWy4` | MohammadHossein — calm, formal |

First used in «دیوار ۲» (`blender/wall2/`). Sound effects: `eleven_text_to_sound_v3` (see `blender/wall2/audio.py`).

## ANIMATION_STUDIO family (`blender/ANIMATION_STUDIO`, first used in «سایه‌ی دانیال» EP_002_SAYEH)
| character | voice_id | ElevenLabs name | post pitch |
|---|---|---|---|
| مامان (CHAR_005_MOTHER) | `9HVxKdwDzPJv4huwQfAt` | Hengameh (same as the cast's mom) | 0 |
| بابا (CHAR_004_FATHER) | `TXoBVQ9S1J8PyUCOfL3s` | Javid — natural, expressive | 0 |
| آرین (CHAR_001_ARIAN) | `yPRQMUW8csecd8blHFfA` | Danesh (same as the cast's Arian) | +1.5 |
| لینا (CHAR_003_LINA) | `RBEKbcQ62sKk2tsmPsAU` | Sara — neutral young female | +3 |
| دانیال (CHAR_002_DANIEL) | `4Uw730VKF274NsJJmpdv` | Farshad — young male | +2 |
