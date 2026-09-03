Get["~/gits/fire2/FIRE6/FIRE6.m"];

Get["/Users/michaelruf/gits/toolbox/mma/temp/FIRE/Box/FIREinput.m"];

PrepareIBP[];

Print[{Internal,External,Replacements,Propagators}];

If[ValueQ[TopSector],
positivePosition=Position[TopSector,1][[-1,1]];
Print[positivePosition];
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True,PositiveIndices->positivePosition];,
Prepare[AutoDetectRestrictions -> True,LI -> True,Parallel -> True];
];

SaveStart["/Users/michaelruf/gits/toolbox/mma/temp/FIRE/Box/Box",1]