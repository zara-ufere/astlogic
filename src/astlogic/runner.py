"""Run a Prolog rubric against a translated program using SWI-Prolog."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from .translator import translate

PROLOG_DIR = Path(__file__).parent / "prolog"
RUBRIC_DIR = PROLOG_DIR / "rubrics"


class PrologNotFoundError(RuntimeError):
    """SWI-Prolog (swipl) is not installed or not on PATH."""


def available_rubrics():
    return sorted(p.stem for p in RUBRIC_DIR.glob("*.pl"))


def check_source(source, rubric, strict=False):
    """Return (results, warnings); results is a list of (passed, label)."""
    if rubric not in available_rubrics():
        raise ValueError(f"unknown rubric '{rubric}'; choose from {available_rubrics()}")
    if shutil.which("swipl") is None:
        raise PrologNotFoundError("swipl not found; install SWI-Prolog (swi-prolog.org)")
    program, warnings = translate(source, strict=strict)
    with tempfile.TemporaryDirectory() as tmp:
        program_file = Path(tmp) / "program.pl"
        program_file.write_text(program, encoding="utf-8")
        proc = subprocess.run(
            ["swipl", "-q", "-g", "run_rubric", "-t", "halt",
             str(PROLOG_DIR / "lib.pl"), str(RUBRIC_DIR / f"{rubric}.pl"), str(program_file)],
            capture_output=True, text=True, timeout=30)
    results = []
    for line in proc.stdout.splitlines():
        status, _, label = line.partition("\t")
        if status in ("PASS", "FAIL"):
            results.append((status == "PASS", label))
    if not results:
        raise RuntimeError(f"Prolog produced no results:\n{proc.stderr.strip()}")
    return results, warnings
