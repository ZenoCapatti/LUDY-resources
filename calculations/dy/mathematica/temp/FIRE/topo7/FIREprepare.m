Get["/Users/zeno/Documents/fire/FIRE6/FIRE6.m"];

Get["/Users/zeno/Documents/analytic_calculations_DY/temp/FIRE/topo7/FIREinput.m"];

PrepareIBP[];

Print[{Internal,External,Replacements,Propagators}];

If[ValueQ[TopSector],
positivePosition=Position[TopSector,1][[-1,1]];
Print[positivePosition];
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True,PositiveIndices->positivePosition];,
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True];
];

SaveStart["/Users/zeno/Documents/analytic_calculations_DY/temp/FIRE/topo7/topo7",7]