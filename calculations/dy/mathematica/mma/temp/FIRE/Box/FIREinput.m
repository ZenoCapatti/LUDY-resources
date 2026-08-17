TopoID = 1;
Internal = {};
External = {q, k1, u1, u2};
Propagators = {2*k1*u1, s - 2*k1*u2, k1^2, k1^2 - 2*k1*q + q^2};
Replacements = {q^2 -> (ipqq /. rep), k1*q -> (ipqk1 /. rep), q*u1 -> (ipqu1 /. rep), q*u2 -> (ipqu2 /. rep), k1^2 -> (ipk1k1 /. rep), k1*u1 -> (ipk1u1 /. rep), k1*u2 -> (ipk1u2 /. rep), u1^2 -> (ipu1u1 /. rep), u1*u2 -> (ipu1u2 /. rep), u2^2 -> (ipu2u2 /. rep)};
