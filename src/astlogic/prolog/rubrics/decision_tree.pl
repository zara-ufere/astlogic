% decision_tree.pl: an interactive decision tree built from nested ifs.
% An elif is an if nested in the else body, so an elif chain adds depth.

% Depth of the deepest if-inside-if nesting in a list of statements.
if_depth(Stmts, Depth) :-
    findall(D, ( member(S, Stmts), stmt_if_depth(S, D) ), Ds),
    max_list([0|Ds], Depth).
stmt_if_depth(if(_, body(T)), D) :-
    if_depth(T, D0), D is D0 + 1.
stmt_if_depth(if(_, body(T), body(E)), D) :-
    if_depth(T, A), if_depth(E, B), D is max(A, B) + 1.

% Every if must come after an input() assignment, in its own body or a parent.
is_input(assign(_, call(Name, _))) :- string_concat("input", _, Name).
ifs_walk([], _).
ifs_walk([S|Rest], Seen) :-
    stmt_walk(S, Seen),
    (   is_input(S) -> Seen2 = true ; Seen2 = Seen ),
    ifs_walk(Rest, Seen2).
stmt_walk(if(_, body(T)), Seen) :- !, Seen == true, ifs_walk(T, Seen).
stmt_walk(if(_, body(T), body(E)), Seen) :- !,
    Seen == true, ifs_walk(T, Seen), ifs_walk(E, Seen).
stmt_walk(_, _).

% Every leaf of the tree (a body with no if in it) must print something.
is_if(if(_, _)).
is_if(if(_, _, _)).
outcomes_print(Stmts) :-
    findall(I, ( member(I, Stmts), is_if(I) ), Ifs),
    (   Ifs == []
    ->  member(call("print", _), Stmts)
    ;   forall(member(I, Ifs), branches_print(I))
    ).
branches_print(if(_, body(T))) :- outcomes_print(T).
branches_print(if(_, body(T), body(E))) :- outcomes_print(T), outcomes_print(E).

check("At least four levels of nested if-statements",
      ( program(Stmts), if_depth(Stmts, Depth), Depth >= 4 )).

check("Every if-statement comes after a user input",
      ( program(Stmts), ifs_walk(Stmts, false) )).

check("Every outcome of the tree prints a result",
      ( program(Stmts), outcomes_print(Stmts) )).
