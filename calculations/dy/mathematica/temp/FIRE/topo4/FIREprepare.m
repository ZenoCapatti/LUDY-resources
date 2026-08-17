Get["tools/fire/FIRE6/FIRE6.m"];

Get["/Users/lcnbr/dev/work/bern/LUDY/DIS_DY_analytic/temp/FIRE/topo4/FIREinput.m"];

PrepareIBP[];

Print[{Internal,External,Replacements,Propagators}];

If[ValueQ[TopSector],
positivePosition=Position[TopSector,1][[-1,1]];
Print[positivePosition];
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True,PositiveIndices->positivePosition];,
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True];
];

SaveStart["/Users/lcnbr/dev/work/bern/LUDY/DIS_DY_analytic/temp/FIRE/topo4/topo4",4]