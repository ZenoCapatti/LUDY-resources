TopoID = 10;
Internal = {k1};
External = {p1, p2};
Propagators = {k1^2, k1^2 + 2*k1*p1 + p1^2, k1^2 - msq + 2*k1*p1 + p1^2 + 2*k1*p2 + 2*p1*p2 + p2^2};
Replacements = {p1^2 -> 0, p1*p2 -> ipp1p2, p2^2 -> 0};
