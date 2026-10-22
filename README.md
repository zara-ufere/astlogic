# astlogic

![CI](https://github.com/zara-ufere/astlogic/actions/workflows/ci.yml/badge.svg)

Checks the structure of Python programs against rubrics written in Prolog, without ever running the code.

Output-based autograders only ask whether a program prints the right answer. Two students can pass with completely different implementations, so a loop assignment can be satisfied by hard-coded output. astlogic asks a different question: does the program use the structures the assignment is about, such as a loop bounded by the parameter, a base case and a recursive case, or while > for > if nesting?

## How it works

1. **Parse.** Python's `ast` module turns the source into a syntax tree. Nothing is executed.
2. **Translate.** A dispatch table maps each node type to a converter that emits a nested Prolog term. Names and strings become Prolog strings so capitals are not read as variables.
3. **Check.** A rubric is a set of Prolog rules that pattern-match over the term. A recursive helper, `contains_deep`, finds a pattern at any depth.
4. **Report.** Each rule prints PASS or FAIL, and the exit code reflects the result.

```python
def total(n):                 function("total", ["n"], [
    s = 0                         assign("s", 0),
    for i in range(n, 0, -1):     for("i", call("range", ["n", 0, -1]), body([
        s += i                        assign("s", call("add", ["s", "i"]))])),
    return s                      return("s")])
```

## Install and use

Requires Python 3.9+ and [SWI-Prolog](https://www.swi-prolog.org/Download.html) (`swipl` on your PATH).

```
pip install -e .
astlogic rubrics
astlogic translate student.py
astlogic check student.py --rubric sum_functions
astlogic check student.py --rubric sum_functions --json
```

Exit code is 0 when every check passes, 1 when any check fails, and 2 on errors such as a syntax error in the student file.

## Rubrics

| Rubric | Assignment idea |
| --- | --- |
| `sum_functions` | Sum N down to 1 with a loop in one function and recursion in another. Accepts `range(N, 0, -1)` and `range(1, N + 1)`. |
| `huffman_codes` | Encode and decode with a code table: globals, a loop over the parameter, while > for > if nesting, and encode feeding decode. |
| `decision_tree` | A nested-if decision tree: at least four levels, input before every if, and a print on every outcome. |

Adding a rubric means adding one file to `src/astlogic/prolog/rubrics/` with `check(Label, Goal)` facts. The helpers in `lib.pl` do the rest.

## Tests

```
pip install -e ".[dev]"
pytest
```

Every rubric has fixtures that should pass, including alternative correct solutions, and fixtures that are deliberately wrong. Each wrong fixture declares which checks it must fail, and the test confirms those checks fail and nothing else does. This shows the rubrics can reject bad submissions, not only accept good ones.

## Limits

- Unsupported syntax such as comprehensions becomes `unknown("ListComp")` with a warning. Use `--strict` to fail instead.
- Structural checks say how code is built, not whether it is correct. They complement output testing and do not replace it.
- The `if __name__ == "__main__":` block is skipped as test scaffolding.
- Rubrics currently match one assignment shape each. Generating rules from an assignment description is future work.

## Credit

Developed from a capstone project in the Department of Computer Science at The College of New Jersey, under the mentorship of Dr. Mark F. Russo, and presented at the Celebration of Student Affairs, Spring 2026.
