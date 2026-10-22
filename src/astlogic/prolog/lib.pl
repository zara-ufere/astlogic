% lib.pl: helpers shared by every rubric.
% A translated student program is loaded as the fact program(Statements).

% contains_deep(+Term, ?Pattern): Pattern unifies with Term or with any term
% nested inside it, at any depth. =.. (univ) unpacks any functor into a list.
contains_deep(Term, Pattern) :-
    Term = Pattern.
contains_deep(Term, Pattern) :-
    Term =.. [_|Args],
    member(Arg, Args),
    (   is_list(Arg)
    ->  member(Item, Arg),
        contains_deep(Item, Pattern)
    ;   contains_deep(Arg, Pattern)
    ).

% function_def(?Name, ?Params, ?Body): a top-level function in the program.
function_def(Name, Params, Body) :-
    program(Stmts),
    member(function(Name, Params, Body), Stmts).

has_loop(Stmts) :- contains_deep(Stmts, for(_, _, _)), !.
has_loop(Stmts) :- contains_deep(Stmts, while(_, _)), !.

has_if(Stmts) :- contains_deep(Stmts, if(_, _)), !.
has_if(Stmts) :- contains_deep(Stmts, if(_, _, _)), !.

calls_self(Name, Stmts) :- contains_deep(Stmts, call(Name, _)), !.

% Each rubric defines check(Label, Goal) facts. run_rubric reports one line
% per check as STATUS<TAB>Label. A goal that raises an error counts as FAIL.
run_rubric :-
    forall(check(Label, Goal), report(Label, Goal)).

report(Label, Goal) :-
    (   catch(Goal, _, fail)
    ->  format("PASS\t~w~n", [Label])
    ;   format("FAIL\t~w~n", [Label])
    ).
