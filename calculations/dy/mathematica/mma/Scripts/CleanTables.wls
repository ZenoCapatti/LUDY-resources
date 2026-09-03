#!/usr/bin/env wolframscript
(* ::Package:: *)

args=$ScriptCommandLine;
configpos=FirstPosition[args,"-config"|"-c"];
pathpos=FirstPosition[args,"-path"|"-p"];


If[configpos===Missing["NotFound"],
Print["Missing config path. Specify with -c | -config." ];
Quit[];
]


(* Load the config file *)
configFile=args[[configpos[[1]]+1]];
If[!FileExistsQ[configFile],
Print["Could not locate config file ",configFile,"."];
Quit[];,
Print["Loading config from: ",configFile,"."];
Get[configFile];
]


If[!FileExistsQ[$RemapDataPath],
Print["Could not locate remap data file ",$RemapDataPath,"."];
Quit[];,
Print["Loading remap data from: ",$RemapDataPath,"."];
]


If[!FileExistsQ[$StdGraphsPath],
Print["Could not locate standard graph file ",$StdGraphsPath,"."];
Quit[];,
Print["Loading standard graph data from: ",$StdGraphsPath,"."];
]


If[!FileExistsQ[$UniqueSectorMasterPath],
Print["Could not locate standard master file ",$UniqueSectorMasterPath,"."];
Quit[];,
Print["Loading standard master data from: ",$UniqueSectorMasterPath,"."];
]


If[!FileExistsQ[$SectorIDPath],
Print["Could not locate sector id file ",$SectorIDPath,"."];
Quit[];,
Print["Loading sector id from: ",$SectorIDPath,"."];
]


If[!FileExistsQ[$ToReduce],
Print["Could not locate integrals to reduce ",$ToReduce,"."];
Quit[];,
Print["Reducing integrals from: ",$ToReduce,"."];
]


If[!DirectoryQ[$DiagDataPath],
Print["Could not locate diagData folder ",$DiagDataPath,"."];
Quit[];,
Print["Loading diagram data from folder: ",$DiagDataPath,"."];
]


If[!ValueQ[$Shift],
Print["$Shift variable not set."];
Quit[];,
Print["Using $Shift: ",$Shift,"."];
]


If[!ValueQ[$Parallel],$Parallel=1];


If[!ValueQ[$Parity],
Print["$Parity variable not set."];
$Parity=None
,
Print["Using $Parity: ",$Parity,"."];
]


If[!ValueQ[$FIREBinPath],
$FIREBinPath="/u/project/bern/eherrman/fire_remapping/FIRE6/bin/FIRE6";
Print["$FIREBinPath variable not set; setting to ",$FIREBinPath];
,
Print["Using $FIREBinPath: ",$FIREBinPath,"."];
]


If[!ValueQ[$FToolBinPath],
$FToolBinPath="/u/project/bern/eherrman/fire_remapping/FIRE6/bin/FTool6";
Print["$FToolBinPath variable not set; setting to ",$FToolBinPath];
,
Print["Using $FToolBinPath: ",$FToolBinPath,"."];
]


If[!ValueQ[$FIREMathPath],
$FIREMathPath="/u/project/bern/eherrman/fire_remapping/FIRE6/FIRE6.m";
Print["$FIREMathPath variable not set; setting to ",$FIREMathPath];
,
Print["Using $FIREMathPath: ",$FIREMathPath,"."];
]


(* ::Title:: *)
(*Setup*)


$Dir=Switch[True,
$Notebooks,NotebookDirectory[],
Length[$ScriptCommandLine]>0,
FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{"LorentzVectorUtils.wl","GraphTools.wl","IntegralTools.wl","TwoBodyKinematics.wl","Scripts/paths.m"}


HashLookup=Get[FileNameJoin[{$IntegralToolsFIREDirectory,"HashTable.m"}]];


UnmaskMasters[expr_]:=expr/.Int[_,{1,hash_}]:>Lookup[HashLookup,hash];


$resultDir=FileNameJoin[{$BasePath,"results"}];
If[DirectoryQ[$resultDir],Print["clearing result directory"];DeleteDirectory[$resultDir,DeleteContents->True];]
CreateDirectory[$resultDir];


Print["Loading Tables."]
Do[
tabFile=FileNames[FileNameJoin[{$BasePath,"temp","FIRE","Diag"~~ToString[id],"ToReduce.1-*.tables"}]][[1]];
If[!FileExistsQ[tabFile],Print["Missing Table for family ",id]];
Put[UnmaskMasters[LoadFIRETable[tabFile]],FileNameJoin[{$resultDir,"table_"~~ToString[id]~~".m"}]];
,
{id,familySel}]


Quit[];
