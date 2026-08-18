(* Regenerate the curated FIRE oracle for DY family 11.

   Required environment:

     FIRE_ROOT=/absolute/path/to/FIRE6
     LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/an/empty/output/root

   FIRE_ROOT must contain FIRE6.m and bin/FIRE6. The output root is kept
   external to the repository so generated databases are never curated by
   accident. Copy only the reviewed files named in the fixture provenance.
*)

dyDirectory = DirectoryName[ExpandFileName[$InputFileName]];
fireRoot = Environment["FIRE_ROOT"];
reproductionDirectory = Environment["LUDY_FIRE_GOLDEN_ROOT"];

If[!StringQ[fireRoot] || fireRoot === "",
  Print["FIRE_ROOT must name the FIRE6 source/build directory."];
  Exit[2]
];
If[!StringQ[reproductionDirectory] || reproductionDirectory === "",
  Print["LUDY_FIRE_GOLDEN_ROOT must name an external output directory."];
  Exit[2]
];

$FIREMathPath = FileNameJoin[{fireRoot, "FIRE6.m"}];
$FIREBinPath = FileNameJoin[{fireRoot, "bin", "FIRE6"}];
If[!FileExistsQ[$FIREMathPath] || !FileExistsQ[$FIREBinPath],
  Print["FIRE_ROOT must contain FIRE6.m and bin/FIRE6."];
  Exit[2]
];

SetDirectory[dyDirectory];
Get[$FIREMathPath];
Get["mma/LorentzVectorUtils.wl"];
Get["mma/IntegralTools.wl"];

(* IntegralTools owns private copies of these paths after it is loaded. *)
IntegralTools`$IntegralToolsBaseDirectory = reproductionDirectory;
IntegralTools`$IntegralToolsTempDirectory =
  FileNameJoin[{reproductionDirectory, "temp"}];
IntegralTools`$IntegralToolsKiraDirectory =
  FileNameJoin[{IntegralTools`$IntegralToolsTempDirectory, "kira"}];
IntegralTools`$IntegralToolsFIREDirectory =
  FileNameJoin[{IntegralTools`$IntegralToolsTempDirectory, "FIRE"}];
IntegralTools`$IntegralToolsPySecDecDirectory =
  FileNameJoin[{IntegralTools`$IntegralToolsTempDirectory, "pySecDec"}];

If[!DirectoryQ[reproductionDirectory],
  CreateDirectory[reproductionDirectory, CreateIntermediateDirectories -> True]
];
CreateTempDirectories[];

SetAttributes[IP, Orderless];

propagators = {
  Sq[k[1]],
  Sq[k[1] + p[1]],
  Sq[k[1] + p[1] + p[2]] - msq
} /. Sq[x_] :> IP[x, x];

onShell = {
  Sq[p[2]] -> 0,
  p[1] . p[2] -> s/2
};

InitializeTopology[
  propagators,
  "ID" -> 11,
  "Name" -> "topo11",
  "Replacements" -> onShell,
  "Internal" -> {k[1]},
  "PrepareFIRE" -> True
];

targetIndices = Tuples[{2, 1, 0, -1, -2}, 3];
targets = Int[11, #] & /@ targetIndices;
ExportIntegralsFIRE[targets];

If[RunFIRE[11, "PrintLog" -> 2] === $Failed,
  Print["FIRE reduction failed."];
  Exit[1]
];

rules = LoadFIRETable[11];
If[rules === $Failed,
  Print["FIRE table loading failed."];
  Exit[1]
];

topologyDirectory = FileNameJoin[{
  reproductionDirectory, "temp", "FIRE", "topo11"
}];
decodedRulesPath = FileNameJoin[{topologyDirectory, "decoded-rules.m"}];
convertedRulesPath = FileNameJoin[{topologyDirectory, "topo11.rules.m"}];

Export[decodedRulesPath, rules];
convertedRules = rules /. {
  Int[11, {indices__Integer}] :> topo11[indices],
  IP[p[1], p[1]] -> ipp1p1,
  IP[p[1], p[2]] -> ipp1p2
};
Put[convertedRules, convertedRulesPath];

implicitMasters = Complement[targets, First /@ rules];
rhsIntegrals = DeleteDuplicates[Cases[Last /@ rules, Int[11, _], Infinity]];
nonMasterRhs = Complement[rhsIntegrals, implicitMasters];

Print["Wolfram version: ", $Version];
Print["Requested targets: ", Length[targets]];
Print["Explicit FIRE rules: ", Length[rules]];
Print["Implicit masters: ", InputForm[implicitMasters]];
Print["Non-master family integrals on right-hand sides: ", InputForm[nonMasterRhs]];

If[Length[targets] =!= 125 || Length[rules] =!= 121 ||
   implicitMasters =!= {
     Int[11, {0, 0, 1}],
     Int[11, {1, 0, 1}],
     Int[11, {1, 1, 0}],
     Int[11, {1, 1, 1}]
   } || nonMasterRhs =!= {},
  Print["Topology-11 semantic validation failed."];
  Exit[1]
];

Scan[
  Function[path,
    Print[
      FileNameTake[path], " SHA-256: ",
      FileHash[path, "SHA256", "HexString"]
    ]
  ],
  FileNameJoin[{topologyDirectory, #}] & /@ {
    "FIREinput.m",
    "ToReduce.m",
    "topo11.tables",
    "decoded-rules.m",
    "topo11.rules.m"
  }
];
