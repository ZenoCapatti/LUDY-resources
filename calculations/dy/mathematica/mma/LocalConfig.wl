(* Portable local configuration for DY_calculation.nb. *)

localConfigDirectory = DirectoryName[ExpandFileName[$InputFileName]];
dyCalculationDirectory = DirectoryName[localConfigDirectory];

fireRoot = Environment["FIRE_ROOT"];
If[!StringQ[fireRoot],
  fireRoot = FileNameJoin[{dyCalculationDirectory, "tools", "fire", "FIRE6"}]
];

If[!ValueQ[$FIREMathPath],
  $FIREMathPath = FileNameJoin[{fireRoot, "FIRE6.m"}]
];
If[!ValueQ[$FIREBinPath],
  $FIREBinPath = FileNameJoin[{fireRoot, "bin", "FIRE6"}]
];

If[!FileExistsQ[$FIREMathPath],
  Print[
    "FIRE6.m was not found. Set FIRE_ROOT or assign $FIREMathPath before " <>
    "evaluating the FIRE reduction cells."
  ]
];
If[!FileExistsQ[$FIREBinPath],
  Print[
    "The FIRE6 executable was not found. Set FIRE_ROOT or assign " <>
    "$FIREBinPath before evaluating the FIRE reduction cells."
  ]
];
