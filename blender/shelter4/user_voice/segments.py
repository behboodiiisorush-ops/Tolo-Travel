"""Where each line sits in the user's take (user_voice/take1.mp3, 88.5 s, all 29 lines in speaker order).
Cuts at the middle of the pauses (silencedetect) or between words (whisper word times) where there is no pause."""
SEG = [("n1", 0.00, 3.23), ("n2", 3.23, 7.35), ("me1", 7.35, 9.17), ("n3", 9.17, 14.07), ("me2", 14.07, 15.34),
       ("n4", 15.34, 19.18), ("me3", 19.18, 22.08), ("n5", 22.08, 26.22), ("me4", 26.22, 29.76),
       ("n6", 29.76, 33.40), ("me5", 33.40, 35.59), ("n7", 35.59, 40.28), ("lena1", 40.28, 42.20),
       ("lena2", 42.20, 44.62), ("mom1", 44.62, 48.16), ("mom2", 48.16, 50.10), ("resc1", 50.10, 52.02),
       ("resc2", 52.02, 55.54), ("resc3", 55.54, 58.84), ("old1", 58.84, 62.15), ("old2", 62.15, 67.53),
       ("old3", 67.53, 69.48), ("str1a", 69.48, 72.24), ("str1b", 72.24, 76.00), ("str1c", 76.00, 77.10),
       ("str1d", 77.10, 80.50), ("str1e", 80.50, 81.80), ("str2a", 81.80, 84.19), ("str2b", 84.19, 88.45)]
