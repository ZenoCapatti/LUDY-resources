#!/usr/bin/env wolframscript
(* ::Package:: *)

(* ::Chapter::Closed:: *)
(*basic paths and argument setting*)


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


(* ::Chapter::Closed:: *)
(*Setup*)


{$FIRETime,$FToolTime,$MappingTime}={0,0,0};


time=AbsoluteTime[];


$Dir=Switch[True,
$Notebooks,NotebookDirectory[],
Length[$ScriptCommandLine]>0,
FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{"LorentzVectorUtils.wl","GraphTools.wl","IntegralTools.wl","TwoBodyKinematics.wl","Scripts/paths.m","Scripts/fire_functions.m"}


ClearTempDirectories[]


diagData=Get[$StdGraphsPath];


parentDaugherRelations=(Table[MapAt[Int[rs,#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,$Shift}]//Flatten);


(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


rData=KeySelect[Get[$RemapDataPath],MemberQ[familySel,Mod[#[[1]],$Shift,1]]&];
SetRemapData[rData];
autoRel={};


(* loading improved masters *)
UniqueSectorMaster=Get[$UniqueSectorMasterPath];


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
"Replacements"->consRescaled,
"TopSector"->diagData[[i]]["TopSector"],
"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
"CreateSectorData"->False];

Do[
InitializeTopology[softProps[i]/.(SoftMapFromID[nn]/.u->pbar),"ID"->i+nn*$Shift,
"LoopMom"-> {l},
"Graph"->LabelMap[MapFromID[nn]][diagData[[i]]["Graph"]],
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


(* starting from the seed integral list "IntegralsToReduce" and splitting integrrals by sectors *)
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


(* ::Chapter:: *)
(*Prepare files*)


Quiet@Do[
CreateDirectory[ftoolTempPath[i]];
CreateDirectory[storageMovedPath[i]];
CreateDirectory[rulePath[i]];
CreateDirectory[dataForwardPath[i]];
CreateDirectory[logFilePath[i]];
,
{i,familySel}]


linString[intsList_]:=StringRiffle[ToString[#[[1]]]~~"-"~~ToString[#[[-1]]]&/@Split[intsList, #2 - #1 == 1 &],","];
Do[linPos[id]=linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],{id,familySel}];


Print["Creating storage folder"];
Do[
	CreateDirectory[storagePath[i]];
	CreateDirectory[storagePathSave[i]];
	If[!DirectoryQ[storagePath[i]]||!DirectoryQ[storagePathSave[i]],Print["Failed to create storage."]; Quit[];];
,
{i,familySel}]//Quiet;


(* ::Section::Closed:: *)
(*.config files for by-sector-reduction*)


Print["Exporting FIRE configs for individual sector reduction storage->storagePath[{id,secID}] "];
Do[
	{id,secID}=LookupSectorID[sec];
	
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
		"database"->FileNameJoin[{basePath[id],"db/db_sector_"~~ToString[secID]}],
		(* adding exclemation mark to force FIRE to overwrite storage files in back-substitution *)
		"storage"->"!"<>storagePath[{id,secID}],
		"folder"->basePath[id],
		"threads"->$Parallel,
		"fthreads"->$Parallel,
		"variables"->"d,y",
		"problem"-> ToString[id]~~" |"~~ToString[Max[Flatten[Position[diagData[[id]]["TopSector"],_?Positive]]]]~~"|"~~TopoData[id]["Name"]~~".start"
		}
	];
	If[ValueQ[$FIREOptions],SetOptions[FIREConfigString,$FIREOptions]];
	
	(* config for individual sector reduction *)
	Export[configPath[{id,secID}],
		FIREConfigString[
			"integrals"->StringJoin["ToReduce_sector_"~~ToString[secID]~~".m"],
			"output"->StringJoin["ToReduce_sector_"~~ToString[secID]~~".tables"]]
	,"String"];

	
,{sec,ReductionSectors}];


(* ::Section::Closed:: *)
(*.config files for by-level-reduction*)


Print["Exporting FIRE configs for by-level-reduction storage->storagePath[id] "];
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
		"database"->FileNameJoin[{basePath[id],"db"}],
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
	Export[configPath[id],
		   FIREConfigString[
		       "integrals"->StringJoin["ToReduce.m"],
		       "output"->StringJoin["ToReduce.tables"]]
	,"String"];
	
	(* config for individual levels *)
	Do[
		Export[configPath[id,level],FIREConfigString["integrals"->StringJoin["ToReduce_"~~ToString[id]~~"_Level_"~~ToString[level]~~".m"],"output"->StringJoin["ToReduce_"~~ToString[id]~~"_Level_"~~ToString[level]~~".tables"]],"String"],
	{level,Range[levelMin,levelMax]}];
	
,{id,familySel}];


(* ::Chapter:: *)
(*Setting FIRE & FTool Options*)


SetOptions[runFIREForwardByLevelHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREForwardBySectorHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardByLevelHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardBySectorHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardGlobalHoffman2,"extraFlags"->$FIREHoffmanFlags]


SetOptions[readTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
SetOptions[readTableBySectorFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
SetOptions[writeTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]


(* ::Chapter:: *)
(*Forward stage*)


(* Large loop over the levels *)
Do[
Print["\n"<>"Forward step for level ",level,"\n"];

If[level===levelMax,
	Print["Skipping ftool step for maximal level "];
	,
	(*for a given parent reduction sectors, look at all one-daughter .tmp files and read the integrals *)
	jobIDs={};
	Print["reading all daughter integrals generated from parent sector reduction"];
	Do[ {idParent,secIDParent}=LookupSectorID[sec];
		daughterSectors=Select[parentDaugherRelations,#[[1]]==sec &][[;;,2]];
		Print["read daughter integrals with FTOOL from parent sector reduction: ",{idParent,secIDParent}];
		
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
			readTableBySectorFTool[{idParent,secIDParent},{idDaughter,secIDDaughter}];
			(*AppendTo[jobIDs,readTableBySectorFToolHoffman2[id,secID]];*)
		,{secDaughter,daughterSectors}];
		
	,{sec,IntLevelSelector[level+1][ReductionSectors]}];	
	
	(*waiting for all Hoffman jobs to finish *)
	(*waitForJobs[jobIDs];*)
	
	(* add the integrals from higher-level reduction *)
	Do[ {idParent,secIDParent}=LookupSectorID[sec];
		Print["\n","Loading from parent sector ",sec, " ",{idParent,secIDParent}];
		daughterSectors=Select[parentDaugherRelations,#[[1]]==sec &][[;;,2]];
		
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
			Print["reading integrals from daughter sector ",secDaughter," ",{idDaughter,secIDDaughter}];
			newInts[secDaughter]=DeleteCases[Get[ftoolTempFile[{idParent,secIDParent},{idDaughter,secIDDaughter}]],{}][[;;,1]]/.G->Int;
			IntegralsInSector[secDaughter]=Union[IntegralsInSector[secDaughter],newInts[secDaughter]];
		,{secDaughter,daughterSectors}];
		
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
			(* generating storage path for all daughter sectors that appear in the reduction of reduction sectors at higher level *)
			CreateDirectory[storagePath[{idDaughter,secIDDaughter}]];
			Run["cp "<>storageTempFile[{idParent,secIDParent},{idDaughter,secIDDaughter}]<>" "<>storageTempFile[{idDaughter,secIDDaughter}]];
			Run["cp "<>storageTempFile[{idParent,secIDParent},{idDaughter,1}]<>" "<>storagePath[{idDaughter,secIDDaughter}]];
		,{secDaughter,Complement[daughterSectors,ReductionSectors]}];
		
	,{sec,IntLevelSelector[level+1][ReductionSectors]}];	
];	



(* Mapping run *)
Print["\n"<>"Forward step for level ",level,"\n","Mapping integrals from NonReductionSectors and update the sector-by-sector integral lists "];
Do[
	{id,secID}=LookupSectorID[sec];
	Print["Mapping integrals in sector ",sec, " ", {id,secID}];
	{tt,rhs}=Timing[MapIntegrals[IntegralsInSector[sec]]];
	$MappingTime+=tt;
	
	If[Head[rhs]===IntegralsInSector,
		Continue[];
	];
	mapRule[sec]=Thread[IntegralsInSector[sec]->rhs];
	Put[mapRule[sec],FileNameJoin[{rulePath[id],"rules_mapping"~~ToString[secID]~~".txt"}]];
	
	UpdateIntegralList[ModIntegrals[ListInts[rhs]]];
	(*exporting also integrals in non-reduction sectors *)
	ExportIntegralsFIRE[IntegralsInSector[sec],"NameFunction"->(StringJoin["ToReduce_sector_"~~ToString[secID]~~".m"]&)];
	
,{sec,IntLevelSelector[level][Intersection[RequiredSectors,NonReductionSectors]]}
];




(* FIRE run *)
Print["\n"<>"Forward step for level ",level,"\n","Running FIRE in ReductionSectors"];
ToRed[level]=Flatten[IntegralsInSector/@IntLevelSelector[level][ReductionSectors]];

If[!ContainsAll[ReductionSectors,ListIntSectors[ToRed[level]]],
	Print["Found integrals in non-reduction sectors! Bad sectors are: ", Complement[ListIntSectors[ToRed[level]],ReductionSectors]];
];

Print["Integrals in families: ",familiesToConsider[level]=ListIntFamilies[ToRed[level]]];

jobIDs={};
Do[
	{id,secID}=LookupSectorID[sec];
	(*writing integral file *)
	ExportIntegralsFIRE[IntegralsInSector[sec],"NameFunction"->(StringJoin["ToReduce_sector_"~~ToString[secID]~~".m"]&)];
	
	Print["Running FIRE in sector ",sec," ",{id,secID}];	
	runFIREForwardBySector[id,secID,level];
	(*AppendTo[jobIDs,runFIREForwardBySector[id,secID,level]];*)
	
	FIRElogFile[{id,secID}]=FileNameJoin[{logFilePath[id],"FIREforward_sector_"~~ToString[secID]~~".txt"}];
,{sec,IntLevelSelector[level][ReductionSectors]}];

(*waiting for all Hoffman jobs to finish *)
(*waitForJobs[jobIDs];*)	

RequiredSectors=Join[RequiredSectors,Select[parentDaugherRelations,MemberQ[IntLevelSelector[level][ReductionSectors],#[[1]]]&][[;;,2]]];
(*Print["required sectors :",RequiredSectors];*)

Do[
	{id,secID}=LookupSectorID[sec];
	If[!FileExistsQ[FIRElogFile[{id,secID}]],
        Print["Missing ",FIRElogFile[{id,secID}]]; Quit[];
	];

	If[StringFreeQ[Import[FIRElogFile[{id,secID}],"String"],"STATISTICS"],
		Print["FIRE problem in ",FIRElogFile[{id,secID}]]; Quit[];
	];
,{sec,IntLevelSelector[level][ReductionSectors]}];

,{level,Reverse[Range[levelMin,levelMax]]}];


Print["Copying back storage files."];
Do[
	{id,secID}=LookupSectorID[sec];
	lv=IntLevel[sec];
	Run["cp "~~storageTempFile[{id,secID}]~~" "~~storagePath[id]];
	Run["cp "~~FileNameJoin[{storagePath[{id,secID}],StringPadLeft[ToString[1],4,"0"]~~".tmp"}]~~" "~~FileNameJoin[{storagePath[id],StringPadLeft[ToString[1],4,"0"]~~"_level_"~~ToString[lv]~~".tmp"}]];
	Run["cp "~~storageTempFile[{id,secID}]~~" "~~storagePathSave[id]];
	Run["cp "~~FileNameJoin[{storagePath[{id,secID}],StringPadLeft[ToString[1],4,"0"]~~".tmp"}]~~" "~~FileNameJoin[{storagePathSave[id],StringPadLeft[ToString[1],4,"0"]~~"_level_"~~ToString[lv]~~".tmp"}]];
,{sec,ReductionSectors}
]


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
