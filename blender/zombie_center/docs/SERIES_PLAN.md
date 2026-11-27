# SERIES PLAN — THE ZOMBIE CENTER as a daily series (proposal, awaiting approval)
Same story and canon as `01_FULL_SCREENPLAY.md` v1.0, cut into **12 long-form (16:9) episodes of ~5 minutes**.
Episodes break only at scene boundaries, on a cliffhanger. Total = 60:00 of story (+ a short "previously" recap per episode).

| Ep | Scenes | Story time | Length | Ends on |
|---|---|---|---|---|
| 01 | CH01_SC001–SC005 | 00:00–05:05 | 5:05 | the stranger's call — "someone who owes you"; the pharmacy door is breaking |
| 02 | CH01_SC006–CH02_SC002 | 05:05–10:05 | 5:00 | Elena: "there is no Nika here" — Arin doesn't believe her |
| 03 | CH02_SC003–SC007 | 10:05–15:00 | 4:55 | Nika's voice in the vent — Sara heard it too |
| 04 | CH03_SC001–SC005 | 15:00–20:05 | 5:05 | Nika, close now: "don't come" |
| 05 | CH03_SC006–CH04_SC002 | 20:05–25:00 | 4:55 | file 001: the virus lives in Arin and doesn't kill him |
| 06 | CH04_SC003–SC008 | 25:00–30:00 | 5:00 | every cell opens, Kaveh walks free saying "001", Sam screams |
| 07 | CH05_SC001–SC005 | 30:00–34:40 | 4:40 | an infected refuses Arin a second time — Sara sees it |
| 08 | CH05_SC006–CH06_SC002 | 34:40–39:22 | 4:42 | Mark lost, Elena's betrayal, blood lock "SUBJECT 001", they reach Nika |
| 09 | CH06_SC003–SC008 | 39:22–45:00 | 5:38 | Nika breaks free: "you smell of blood" |
| 10 | CH07_SC001–SC005 | 45:00–50:30 | 5:30 | Elena bitten, the whole hall awake |
| 11 | CH07_SC006–CH08_SC003 | 50:30–55:05 | 4:35 | Elena's recording: Arin is Patient Zero |
| 12 | CH08_SC004–SC009 | 55:05–60:00 | 4:55 | the gate, Sara inside, the question to the viewer |

## Measured render speed on this server (4 CPU cores, no GPU) — one realistic character, corridor, fog
| setting | seconds per frame | one 5-min episode (7,200 frames) |
|---|---|---|
| Cycles 1080p, 32 samples | 122 | ~10 days |
| EEVEE 1080p, 32 samples | 96 | ~8 days |
| EEVEE 720p, 16 samples | 37 | ~3 days |
| EEVEE 720p, 8 samples | ~20 | ~40 h (≈20 h if animated on twos, 12 unique fps) |
Scenes with several characters and zombies will be slower. With an NVIDIA GPU, EEVEE 1080p is ~1–5 s/frame (2–10 h per episode).

## Before episode 01 can be made (one-time build, several days)
Characters (Arin, Nika, Elena, Sara, Mark, Sam) with Rigify rigs, zombie variants, Mixamo retargeting,
the city street and facility sets used by episodes 01–03.
