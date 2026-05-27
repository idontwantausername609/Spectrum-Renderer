Current want:
 - functionality for "Normalize" scale to auto-detect the number of peaks in atomic emission spectral data based on peak intensity. there can be anywhere from two to hundereds of peaks. these peaks need to be detected by the program, and only these peaks are to be shown in the "Normalize" scale option.


Tell me these exact values (I will implement using these):

1. Auto mode behavior for keepTopN=0: auto-detect. there should be NO option for the user to adjust this. i.e. there should be NO "N" selection on the UI.
2. Peak detector availability: scipy-ok.
3. Sensitivity: medium.
4. Min separation between peaks (nm): 0. 
5. Apply top‑N filtering when: normalize-only. this has been specified to you multiple times.
6. Max allowed N (cap): NO CAP
7. UI default for keepTopN input: 0 to enable auto (yes/no). IT SHOULD ONLY EVER BE AUTO. THERE SHOULD BE NO KEEPTOPN VISIBLE IN THE UI.
8. Output images: both.