"""
Validate a notebook by executing every code cell in order in one shared namespace,
exactly as 'Runtime -> Run all' would. Catches NameErrors, typos, and runtime errors
before a notebook is ever shown to a participant.

    python3 build/validate_nb.py notebooks/04b_text_predict_extract.ipynb

Cells that need a heavy one-time install or network model (pip, Whisper, gTTS) are
SKIPPED by default so the self-contained logic can still be checked offline; pass
--all to attempt them too. matplotlib is forced to a non-interactive backend and
plt.show()/display() are turned into no-ops so nothing blocks.
"""
import json, sys, io, re, traceback
from contextlib import redirect_stdout

SKIP_PATTERNS = [
    r"!pip", r"pip install", r"import whisper", r"whisper\.load_model",
    r"from gtts", r"\bgTTS\(", r"import gtts",
]

def should_skip(src):
    return any(re.search(p, src) for p in SKIP_PATTERNS)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    run_all = "--all" in sys.argv
    path = args[0]
    nb = json.load(open(path))

    # Headless plotting; neutralise show/display so cells never block.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: None

    g = {"__name__": "__main__"}
    try:
        import IPython.display as _d
        _d.display = lambda *a, **k: None
        _d.Audio = lambda *a, **k: None
        g["display"] = lambda *a, **k: None
        g["Audio"] = lambda *a, **k: None
    except Exception:
        pass

    code_cells = [(i, "".join(c["source"])) for i, c in enumerate(nb["cells"])
                  if c["cell_type"] == "code"]
    print(f"== {path}: {len(code_cells)} code cells ==")
    skipped = 0
    for i, src in code_cells:
        if not run_all and should_skip(src):
            print(f"  cell {i:>3}: SKIPPED (heavy install/model)")
            skipped += 1
            continue
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                exec(compile(src, f"cell[{i}]", "exec"), g)
            plt.close("all")
            head = (buf.getvalue().strip().splitlines() or [""])[0][:70]
            print(f"  cell {i:>3}: OK   {head}")
        except Exception:
            print(f"  cell {i:>3}: ERROR")
            print("    " + buf.getvalue().replace("\n", "\n    "))
            traceback.print_exc()
            print(f"\nFAILED at cell {i}.")
            sys.exit(1)
    print(f"\nALL CELLS PASSED ({len(code_cells)-skipped} run, {skipped} skipped).")

if __name__ == "__main__":
    main()
