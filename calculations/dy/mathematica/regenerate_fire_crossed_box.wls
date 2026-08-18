(* Regenerate one curated FIRE oracle for DY family 20 through 31.

   Required environment:

     FIRE_ROOT=/absolute/path/to/FIRE6
     LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/an/empty/output/root
     LUDY_FIRE_TOPOLOGY_ID=20

   The output root is external so FIRE databases cannot be curated by
   accident. Run and review one topology at a time.
*)

dyDirectory = DirectoryName[ExpandFileName[$InputFileName]];
fireRoot = Environment["FIRE_ROOT"];
reproductionDirectory = Environment["LUDY_FIRE_GOLDEN_ROOT"];
topologyIDText = Environment["LUDY_FIRE_TOPOLOGY_ID"];

If[!StringQ[fireRoot] || fireRoot === "",
  Print["FIRE_ROOT must name the FIRE6 source/build directory."];
  Exit[2]
];
If[!StringQ[reproductionDirectory] || reproductionDirectory === "",
  Print["LUDY_FIRE_GOLDEN_ROOT must name an external output directory."];
  Exit[2]
];
If[!StringMatchQ[topologyIDText, DigitCharacter ..],
  Print["LUDY_FIRE_TOPOLOGY_ID must be an integer from 20 through 31."];
  Exit[2]
];
topologyID = FromDigits[topologyIDText];
If[!MemberQ[Range[20, 31], topologyID],
  Print["LUDY_FIRE_TOPOLOGY_ID must be an integer from 20 through 31."];
  Exit[2]
];
topologyName = "topo" <> ToString[topologyID];

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
IP[x_ + y_, z_] := IP[x, z] + IP[y, z];
IP[-x_, z_] := -IP[x, z];

crossedBoxPropagators = {
  Sq[k[1]],
  Sq[k[1] + p[1]],
  Sq[k[1] + p[1] + p[2]] - msq,
  Sq[k[1] + p[2]]
} /. Sq[x_] :> IP[x, x];

(* Reproduce the notebook's partialFractioner ordering, rather than assuming
   which one of the four crossed-box propagators is omitted. *)
loopProducts[props_] := Module[{allsps, extsps, loopsps},
  allsps = DeleteDuplicates[Flatten[Table[List @@ prps, {prps, props}]]];
  extsps = allsps /. {IP[x_, q[1]] :> 0, IP[x_, k[1]] :> 0};
  loopsps = Complement[allsps, extsps] /. y_*IP[x_, z_] :> IP[x, z]
];
partialFractioner[props_] := Module[{loopsps, mons, solpf},
  loopsps = loopProducts[props];
  mons = MonomialList[Sum[a[prop]*prop, {prop, props}], loopsps];
  solpf = Solve[
    Table[mons[[j]] == If[j == 4, 1, 0], {j, 1, 4}],
    Table[a[prop], {prop, props}]
  ];
  Sum[a[props[[j]]]*prop[j], {j, 1, Length[props]}] /. solpf[[1]]
];
partialFraction = partialFractioner[crossedBoxPropagators];
denominatorTerms = List @@ Expand[
  partialFraction/Product[prop[j], {j, 1, 4}]
];
familyPropagatorIndices =
  Cases[#, prop[index_] :> index, Infinity] & /@ denominatorTerms;
If[familyPropagatorIndices =!= {
    {1, 2, 3}, {1, 2, 4}, {1, 3, 4}, {2, 3, 4}
  },
  Print["Unexpected crossed-box partial-fraction ordering: ",
    InputForm[familyPropagatorIndices]];
  Exit[1]
];

familyIndex = Mod[topologyID - 20, 4] + 1;
propagators = crossedBoxPropagators[[familyPropagatorIndices[[familyIndex]]]];
kinematicsGroup = Quotient[topologyID - 20, 4];
onShell = Switch[kinematicsGroup,
  0, {Sq[p[1]] -> 0, Sq[p[2]] -> 0, p[1] . p[2] -> s/2},
  1, {Sq[p[1]] -> 0, p[1] . p[2] -> s/2},
  2, {Sq[p[2]] -> 0, p[1] . p[2] -> s/2}
];

InitializeTopology[
  propagators,
  "ID" -> topologyID,
  "Name" -> topologyName,
  "Replacements" -> onShell,
  "Internal" -> {k[1]},
  "PrepareFIRE" -> True
];

targetIndices = Tuples[{1, 0, -1}, 3];
targets = Int[topologyID, #] & /@ targetIndices;
ExportIntegralsFIRE[targets];

If[RunFIRE[topologyID, "PrintLog" -> 2] === $Failed,
  Print["FIRE reduction failed."];
  Exit[1]
];
rules = LoadFIRETable[topologyID];
If[rules === $Failed,
  Print["FIRE table loading failed."];
  Exit[1]
];

topologyDirectory = FileNameJoin[{
  reproductionDirectory, "temp", "FIRE", topologyName
}];
decodedRulesPath = FileNameJoin[{topologyDirectory, "decoded-rules.m"}];
convertedRulesPath = FileNameJoin[{
  topologyDirectory, topologyName <> ".rules.m"
}];
Export[decodedRulesPath, rules];
convertedRules = rules /. {
  Int[topologyID, {indices__Integer}] :> Symbol[topologyName][indices],
  IP[p[1], p[1]] -> ipp1p1,
  IP[p[1], p[2]] -> ipp1p2,
  IP[p[2], p[2]] -> ipp2p2
};
Put[convertedRules, convertedRulesPath];

implicitMasters = Complement[targets, First /@ rules];
rhsIntegrals = DeleteDuplicates[
  Cases[Last /@ rules, Int[topologyID, _], Infinity]
];
nonMasterRhs = Complement[rhsIntegrals, implicitMasters];

Print["Wolfram version: ", $Version];
Print["Topology: ", topologyID];
Print["Propagator indices: ", InputForm[familyPropagatorIndices[[familyIndex]]]];
Print["Requested targets: ", Length[targets]];
Print["Explicit FIRE rules: ", Length[rules]];
Print["Implicit masters: ", InputForm[implicitMasters]];
Print["Non-master family integrals on right-hand sides: ", InputForm[nonMasterRhs]];

If[Length[targets] =!= 27 || nonMasterRhs =!= {},
  Print["Crossed-box semantic validation failed."];
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
    topologyName <> ".tables",
    "decoded-rules.m",
    topologyName <> ".rules.m"
  }
];
