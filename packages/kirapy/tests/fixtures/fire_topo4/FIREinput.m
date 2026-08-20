TopoID = 4;
Internal = {q1};
External = {p1, p2};
Propagators = {p1^2 - 2*p1*q1 + q1^2, p2^2 - 2*p2*q1 + q1^2, p1^2 + 2*p1*p2 + p2^2 - 2*p1*q1 - 2*p2*q1 + q1^2};
Replacements = {p1^2 -> 0, p1*p2 -> ipp1p2, p2^2 -> 0};
