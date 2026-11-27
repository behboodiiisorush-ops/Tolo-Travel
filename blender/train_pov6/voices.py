"""ElevenLabs voices of «واگن آخر» (fixed per character, reuse them in later episodes).
Generated with the ElevenLabs MCP tools (eleven_v3).  Child voices could not be designed (ElevenLabs blocks
child-voice design), so the two kids are library voices pitched up in el_mix.py."""
VOICES = {
    "Me":    {"voice_id": "4COD2AbGomb4Znu8FPyr", "name": "amir (library)", "fx": "pitch x1.19 (+3 st), formants kept"},
    "Lena":  {"voice_id": "RBEKbcQ62sKk2tsmPsAU", "name": "Sara - Neutral Persian Female (library)", "fx": "pitch x1.33 (+5 st)"},
    "Rahim": {"voice_id": "41Jt86rYN2Yqnjt1W6hi", "name": "Wagon - Rahim (train driver), designed + saved", "fx": "none"},
    "Mom":   {"voice_id": "CW1H0ECNiIvEZCNLa1az", "name": "Wagon - Mom, designed + saved", "fx": "walkie-talkie band-pass + crackle"},
}
PITCH = {"Me": 1.19, "Lena": 1.335, "Rahim": 1.0, "Mom": 1.0}
