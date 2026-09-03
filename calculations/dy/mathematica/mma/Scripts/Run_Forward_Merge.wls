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


(* ::Title:: *)
(*Setup*)


{$FIRETime,$FToolTime,$MappingTime}={0,0,0};


time=AbsoluteTime[];


$Dir=Switch[True,
$Notebooks,NotebookDirectory[],
Length[$ScriptCommandLine]>0,
FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{"LorentzVectorUtils.wl","GraphTools.wl","IntegralTools.wl","TwoBodyKinematics.wl","Scripts/paths.m"}


ClearTempDirectories[]


diagData=Get[$StdGraphsPath];


(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


rData=KeySelect[Get[$RemapDataPath],MemberQ[familySel,Mod[#[[1]],$Shift,1]]&];
SetRemapData[rData];
autoRel={};


(* loading improved masters *)
UniqueSectorMaster=UniqueSectorMaster=Get[$UniqueSectorMasterPath];


allMasters=Flatten[Values[UniqueSectorMaster]];


(* all sectors in the two families *)
IntegralsToReduce=Get[$ToReduce];
IntegralsToReduce=Join[IntegralsToReduce,Flatten[Values[UniqueSectorMaster]]];
IntegralsToReduce=Union[ModIntegrals[IntegralsToReduce]];
IntegralsToReduce=Select[IntegralsToReduce,MemberQ[familySel,First[#]]&];


Print["Input integrals in families ",ListIntFamilies[IntegralsToReduce],"."];
Print["Perfoming reduction in families ",familySel,"."];


(* Minimalistic topology setup *)
Do[
softProps[i]=ExpandLeadingPropagators[ToSoftVariables[diagData[[i]]["StandardPropagators"]],SoftScalinqKin,qcnt]/.pbar:>u/.mq2:>1;
InitializeTopology[softProps[i],
"LoopMom"->{l},
"ID"->i,
"Name"->"Diag"<>ToString[i],
"FIREProblemID"->i,
"Graph"->diagData[[i]]["Graph"],
"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
"CreateSectorData"->False];

Do[
InitializeTopology[softProps[i]/.(SoftMapFromID[nn]/.u->pbar),"ID"->i+nn*$Shift,
"LoopMom"-> {l},
"Graph"->LabelMap[MapFromID[nn]][ diagData[[i]]["Graph"]],
"RESTRICTIONS"-> diagData[[i]]["RESTRICTIONS"],
"Replacements"-> consRescaled,
"TopSector"->diagData[[i]]["TopSector"],
"CreateSectorData"->False,
"CreateTempDirectories"->False
];
,{nn,1,7}],
{i,familySel}]


ReductionSectors=Union[ModIntegrals[$RepresentativeSectors]];
SectorsMod=Union[ModIntegrals[$AllSectors]];
NonReductionSectors=Complement[SectorsMod,ReductionSectors];


(*DisplayIntPM/@Union@ModIntegrals[MapIntegrals[Flatten[Table[Thread[Int[id,diagData[[id]]["NonzeroSectors"]]],{id,$inputFamilies}]]]]*)


(* Move the start files *)
Print["Copying start files. "];
Do[
CopyFile[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/Diag"~~ToString[i]~~".start"}],$IntegralToolsFIREDirectory~~"/Diag"~~ToString[i]~~"/Diag"~~ToString[i]~~".start",OverwriteTarget->True];

Switch[$Parity,
	None,{}
	,
	"Even",
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qe"~~ToString[i]~~"n.m"}],$IntegralToolsFIREDirectory~~"/Diag"~~ToString[i]~~"/mi-qe"~~ToString[i]~~"n.m",OverwriteTarget->True];
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/qe"~~ToString[i]~~"n.pref"}],$IntegralToolsFIREDirectory~~"/Diag"~~ToString[i]~~"/qe"~~ToString[i]~~"n.pref",OverwriteTarget->True];
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qe"~~ToString[i]~~"n.m"}]];
	,
	"Odd",
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qo"~~ToString[i]~~"n.m"}],$IntegralToolsFIREDirectory~~"/Diag"~~ToString[i]~~"/mi-qo"~~ToString[i]~~"n.m",OverwriteTarget->True];
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/qo"~~ToString[i]~~"n.pref"}],$IntegralToolsFIREDirectory~~"/Diag"~~ToString[i]~~"/qo"~~ToString[i]~~"n.pref",OverwriteTarget->True];
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qo"~~ToString[i]~~"n.m"}]];
];
,
{i,familySel}]


SectorAssociation=Association[Table[
sec->Association["Integrals"->{},sec/.$RemapData];
,{sec,$AllSectors}]];


Do[
	IntegralsInSector[sec]=IntSectorSelector[sec][IntegralsToReduce];
	If[MemberQ[ReductionSectors,sec],
		IntegralsInSector[sec]=Union[IntegralsInSector[sec],UniqueSectorMaster[sec]];
	];
,{sec,SectorsMod}
];


UpdateIntegralList[intList_List]:=Do[IntegralsInSector[sec2]=Union[IntegralsInSector[sec2],IntSectorSelector[sec2][intList]],{sec2,SectorsMod}]


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]


RequiredSectors=IntLevelSelector[levelMax][ListIntSectors[IntegralsToReduce]];


ExportIntegralsFIRE[IntegralsToReduce];


(* ::Title:: *)
(*Prepare files*)


Quiet@Do[
CreateDirectory[ftoolTempPath[i]];
CreateDirectory[storageMovedPath[i]];
CreateDirectory[rulePath[i]];
CreateDirectory[dataForwardPath[i]];
CreateDirectory[logFilePath[i]];
,
{i,familySel}]


runFIREForward[id_,level_]:=Module[{tt},
tt=AbsoluteTime[];
Run@StringJoin[{
$FIREBinPath,
" -c ",
StringDelete[configPath[id,level],".config"],
" --forward ",
ToString[level],
" > ",
FileNameJoin[{logFilePath[id],"FIREforward"~~"_"~~ToString[level]~~".out"}]
}
];
$FIRETime+=tt-AbsoluteTime[];
]


linString[intsList_]:=StringRiffle[ToString[#[[1]]]~~"-"~~ToString[#[[-1]]]&/@Split[intsList, #2 - #1 == 1 &],","];
Do[linPos[id]=linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],{id,familySel}];


(* Export FIRE Configs *)
Print["Exporting FIRE configs "];


Do[
	SetOptions[
	FIREConfigString,
	Switch[$Parity,
	None,{},
	"Even",
		{
		"even"->linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],
		"masters"->"|1-"~~ToString[nMasters[id]]~~"|mi-qe"~~ToString[id]~~"n.m",
		"preferred"->"qe"~~ToString[id]~~"n.pref"
		},
	"Odd",
		{
		"odd"->linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],
		"masters"->"|1-"~~ToString[nMasters[id]]~~"|mi-qo"~~ToString[id]~~"n.m",
		"preferred"->"qo"~~ToString[id]~~"n.pref"
		}
	]
	];
	(* If requested set pos_pref *)
	If[ValueQ[$PosPref],SetOptions[FIREConfigString,"pos_pref"->ToString[$PosPref]]];

	(* common options *)
	SetOptions[FIREConfigString,
		{
		(* adding exclemation mark to force FIRE to overwrite storage files in back-substitution *)
		"storage"->"!"<>storagePath[id],
		"folder"->basePath[id],
		"threads"->$Parallel,
		"fthreads"->$Parallel,
		"folder"->basePath[id],
		"variables"->"d,y",
		"problem"-> ToString[id]~~" |"~~ToString[Max[Flatten[Position[diagData[[id]]["TopSector"],_?Positive]]]]~~"|"~~TopoData[id]["Name"]~~".start"
		}
	];
	If[ValueQ[$FIREOptions],SetOptions[FIREConfigString,$FIREOptions]];

	(* config for all levels *)
	Export[configPath[id],FIREConfigString["integrals"->StringJoin["ToReduce.m"],"output"->StringJoin["ToReduce.tables"]],"String"];
	
	(* config for individual levels *)
	Do[
		Export[configPath[id,level],FIREConfigString["integrals"->StringJoin["ToReduce_"~~ToString[id]~~"_Level_"~~ToString[level]~~".m"],"output"->StringJoin["ToReduce_"~~ToString[id]~~"_Level_"~~ToString[level]~~".tables"]],"String"],
	{level,Range[levelMin,levelMax]}];
	
,{id,familySel}];


Print["Creating temporary storage folder"];
Do[
	CreateDirectory[storageMovedPath[i]];
	If[!DirectoryQ[storageMovedPath[i]],Print["Failed to create temporary storage."]; Quit[];];
,
{i,familySel}]//Quiet;


(* ::Title:: *)
(*Forward stage*)


(* Large loop over the levels *)
Do[
Print["
Forward step for level ",level,"
"];

If[level===levelMax,
	Print["Skipping ftool step for maximal level "];
	,
	Do[(* START DO *)
		{id,secID}=LookupSectorID[sec];
		(* skip sectors that have not been touched, e.g. because there were no integrals *)
		If[
			!FileExistsQ[storageTempFile[id,secID]],
			Print["Skipping sector ",{id,secID}];
			Continue[];
		];
		(* if there is a temp file we have to provide it eventually to make the backward run work *)
		RequiredSectors=AppendTo[RequiredSectors,sec];
		
		Print["Loading from sector ",{id,secID}];
		Run@StringJoin[$FToolBinPath,
			" -c ", 
			StringDelete[configPath[id],".config"],
			" -q -s ",
			ToString[secID],
			" -d ",
			storagePath[id],
			" > ",
			ftoolTempFile[id,secID]
		];
		
		If[MemberQ[NonReductionSectors,sec]||True,
			(* No reduction in redundant sectors. So we move the temp files, keeping FIRE from running reduction. *)
			Run["mv "~~storageTempFile[id,secID]~~" "~~storageMovedTempFile[id,secID]]
		];
		
		(* add the integrals from higher-level reduction *)
		IntegralsInSector[sec]=Union[IntegralsInSector[sec],DeleteCases[Get[ftoolTempFile[id,secID]],{}][[;;,1]]/.G->Int];
		(* END DO *)
	,{sec,IntLevelSelector[level][SectorsMod]}]
];

(* Mapping run *)

Do[
	{id,secID}=LookupSectorID[sec];
	
	{tt,rhs}=Timing[MapIntegrals[IntegralsInSector[sec]]];
	$MappingTime+=tt;
	
	If[Head[rhs]===IntegralsInSector,
		Continue[];
	];
	mapRule[sec]=Thread[IntegralsInSector[sec]->rhs];
	Put[mapRule[sec],FileNameJoin[{rulePath[id],"rules_mapping"~~ToString[secID]~~".txt"}]];
	
	UpdateIntegralList[ModIntegrals[ListInts[rhs]]];
	
,{sec,IntLevelSelector[level][NonReductionSectors]}
];

(* FIRE run *)

ToRed[level]=Flatten[IntegralsInSector/@IntLevelSelector[level][ReductionSectors]];

If[!ContainsAll[ReductionSectors,ListIntSectors[ToRed[level]]],
	Print["Found integrals in non-reduction sectors! Bad sectors are: ", Complement[ListIntSectors[ToRed[level]],ReductionSectors]];
];

Print["Integrals in families: ",familiesToConsider[level]=ListIntFamilies[ToRed[level]]];
ExportIntegralsFIRE[ToRed[level],"NameFunction"->(StringJoin["ToReduce_"~~ToString[#]~~"_Level_"~~ToString[level]~~".m"]&)];

Do[
	(*Print[FileNameTake[#,-2]&/@FileNames[FileNameJoin[{storagePath[i],"*"}]]];*)
	If[MemberQ[familiesToConsider[level],i],
		Print["Running FIRE forward for level ",level, " of family ",i];
		runFIREForward[i,level];
		(* pipe through fire info *)
	(*	Print[StringSplit[Import[FileNameJoin[{logFilePath[i],"FIREforward_"~~ToString[level]~~".out"}],"String"],"STATISTICS"][[2]]];*)
		,
		Print["Skipping family ",i]
	]
,{i,familySel}];

,{level,Reverse[Range[levelMin,levelMax]]}];


(*Print["Copying back storage files."];
Do[
Run["cp "~~storageMovedPath[i]~~"/* "~~storagePath[i]];
(*DeleteDirectory[storageMovedPath[i],DeleteContents->True]*)
,
{i,familySel}];*)
Print["Copying back storage files."];
Do[
	{id,secID}=LookupSectorID[sec];
	Run["mv "~~storageMovedTempFile[id,secID]~~" "~~storageTempFile[id,secID]];
(*DeleteDirectory[storageMovedPath[i],DeleteContents->True]*)
,
{sec,Intersection[NonReductionSectors,RequiredSectors]}];


Do[
Put[Cases[ReductionSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"ReductionSectors.m"}]];
Put[Cases[NonReductionSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"NonReductionSectors.m"}]];
Put[Cases[RequiredSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"RequiredSectors.m"}]];
Put[Cases[$RepresentativeSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"RepresentativeSectors.m"}]];
,
{id,familySel}]


Print["Done. 
Total time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[AbsoluteTime[]-time], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
FIRE time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$FIRETime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
Mapping time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$MappingTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]
]
