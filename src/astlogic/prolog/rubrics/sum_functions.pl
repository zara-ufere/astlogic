% sum_functions.pl: sum the integers from N down to 1, once with a loop
% and once with recursion. Function names are free; the structure is not.

iterative_fn(Name, Params, Body) :-
    function_def(Name, Params, Body), has_loop(Body), \+ calls_self(Name, Body).

recursive_fn(Name, Params, Body) :-
    function_def(Name, Params, Body), calls_self(Name, Body), \+ has_loop(Body).

% Loop forms that visit N, N-1, ..., 1 using the parameter P as the bound.
spans_n_to_1(P, call("range", [P, 0, -1])).
spans_n_to_1(P, call("range", [1, call("add", [P, 1])])).
spans_n_to_1(P, call("range", [1, call("add", [P, 1]), 1])).

check("Two functions are defined",
      ( findall(N, function_def(N, _, _), Ns), length(Ns, Count), Count >= 2 )).

check("One function loops from N to 1 using its parameter as the bound",
      ( iterative_fn(_, Params, Body),
        contains_deep(Body, for(_, Iter, _)),
        member(P, Params),
        spans_n_to_1(P, Iter) )).

check("The other function has an if-statement for the base and recursive cases",
      ( recursive_fn(_, _, Body), has_if(Body) )).

check("The recursive function calls itself and uses no loop",
      recursive_fn(_, _, _)).
