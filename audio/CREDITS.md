# Audio credits

`fan_clips.zip` contains **120 real industrial-fan recordings** (60 normal, 60
faulty), excerpts from the **DCASE 2023 Challenge Task 2** development dataset
(machine condition monitoring), which is built on Hitachi's **MIMII / MIMII DG**
dataset. Each clip is a ~3-second window, downsampled to 8 kHz mono and
peak-normalized for classroom use; filenames are `normal_NN.wav` / `anomaly_NN.wav`.

Used by `notebooks/03_sound_fault_prediction.ipynb` to train and test a model on
**real** machine sound — no synthetic data.

**Source:** DCASE 2023 Task 2 dev set via the Hugging Face mirror
`renumics/dcase23-task2-enriched`. Original: MIMII / MIMII DG (Hitachi, Ltd.).
**License:** Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0). These
clips are derivatives (trimmed, downsampled, normalized) and are shared under the
same CC BY-SA 4.0 license, with attribution as above.

- MIMII: Purohit et al., DCASE 2019 / arXiv:1909.09347.
- DCASE 2023 Task 2: https://dcase.community/challenge2023/
