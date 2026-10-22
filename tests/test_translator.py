import pytest

from astlogic import UnsupportedNodeError, translate


def body(source):
    text, _ = translate(source)
    return text


def test_names_and_strings_become_prolog_strings():
    assert 'assign("N", "Hi")' in body("N = 'Hi'")


def test_keyword_constants_are_not_prolog_variables():
    text = body("x = None\ny = True\nz = False")
    assert 'assign("x", none)' in text
    assert 'assign("y", true)' in text and 'assign("z", false)' in text


def test_negative_number_is_collapsed():
    assert 'call("range", ["N", 0, -1])' in body("range(N, 0, -1)")


def test_quotes_and_backslashes_are_escaped():
    assert r'assign("s", "a\"b\\c")' in body("s = 'a\"b\\\\c'")


def test_augmented_assignment_is_expanded():
    assert 'assign("t", call("add", ["t", "i"]))' in body("t += i")


def test_elif_is_nested_in_else_body():
    text = body("if a:\n    pass\nelif b:\n    pass\n")
    assert text.count("if(") == 2 and "body([if(" in text


def test_method_chain_uses_dotted_name():
    assert 'call("input.strip.upper", [])' in body("input().strip().upper()")


def test_main_guard_is_skipped():
    text = body("x = 1\nif __name__ == '__main__':\n    print(x)\n")
    assert "print" not in text


def test_unsupported_syntax_warns_by_default():
    text, warnings = translate("y = [i for i in range(3)]")
    assert 'unknown("ListComp")' in text
    assert warnings and "ListComp" in warnings[0]


def test_unsupported_syntax_raises_in_strict_mode():
    with pytest.raises(UnsupportedNodeError):
        translate("y = [i for i in range(3)]", strict=True)


def test_bare_return_does_not_crash():
    assert "return(none)" in body("def f():\n    return\n")
