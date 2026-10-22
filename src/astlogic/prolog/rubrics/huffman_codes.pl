% huffman_codes.pl: encode and decode text with a Huffman code table.

check("Three globals are defined: one list and two dicts",
      ( program(Stmts),
        member(assign(_, list(_)), Stmts),
        aggregate_all(count, member(assign(_, dict(_)), Stmts), Dicts),
        Dicts >= 2 )).

check("encode and decode are both defined",
      ( function_def("encode", _, _), function_def("decode", _, _) )).

check("encode has a for loop over its parameter",
      ( function_def("encode", Params, Body),
        contains_deep(Body, for(_, Iter, _)),
        member(Iter, Params) )).

check("decode nests while > for > if",
      ( function_def("decode", _, Body),
        contains_deep(Body, while(_, body(WhileBody))),
        contains_deep(WhileBody, for(_, _, body(ForBody))),
        has_if(ForBody) )).

check("The result of encode is passed directly to decode",
      ( program(Stmts),
        member(assign(Var, call("encode", _)), Stmts),
        member(assign(_, call("decode", [Var])), Stmts) )).
