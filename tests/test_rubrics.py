import shutil
from pathlib import Path

import pytest

from astlogic import available_rubrics, check_source

FIXTURES = Path(__file__).parent / "fixtures"
pytestmark = pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog not installed")


def cases(prefix):
    return [pytest.param(r, f, id=f"{r}/{f.name}")
            for r in available_rubrics() for f in sorted((FIXTURES / r).glob(f"{prefix}_*.py"))]


@pytest.mark.parametrize("rubric,path", cases("pass"))
def test_correct_solutions_pass_every_check(rubric, path):
    results, _ = check_source(path.read_text(), rubric)
    assert all(ok for ok, _ in results), [l for ok, l in results if not ok]


@pytest.mark.parametrize("rubric,path", cases("fail"))
def test_flawed_solutions_fail_exactly_the_expected_checks(rubric, path):
    header = path.read_text().splitlines()[0].removeprefix("# fails: ")
    expected = [label.strip() for label in header.split(" | ")]
    results, _ = check_source(path.read_text(), rubric)
    failed = [label for ok, label in results if not ok]
    assert sorted(failed) == sorted(expected)


def test_every_rubric_has_passing_and_failing_fixtures():
    for rubric in available_rubrics():
        assert list((FIXTURES / rubric).glob("pass_*.py")), rubric
        assert list((FIXTURES / rubric).glob("fail_*.py")), rubric
