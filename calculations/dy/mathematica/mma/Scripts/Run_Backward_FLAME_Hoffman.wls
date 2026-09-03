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


If[!ValueQ[$Parallel],
	Print["$Parallel variable not set. default $Parallel=1."];
	$Parallel=1;
	,
	Print["$Parallel variable set to: ",$Parallel]
]


If[!ValueQ[$Debug],
	Print["$Debug not set, default $Debug = False"]; 
	$Debug=False
	, 
	Print["$Debug variable set to: ",$Debug]
]


If[!ValueQ[$TimerDetails],
	Print["$TimerDetails variable not set. default $TimerDetails=False."];
	$TimerDetails=False;
	,
	Print["$TimerDetails variable set to: ",$TimerDetails]
]


If[!ValueQ[$Parity],
Print["$Parity variable not set."];
$Parity=None
,
Print["Using $Parity: ",$Parity,"."];
]


If[ValueQ[$FLAMEHoffmanFlags],
	Print["$FLAME resources set to: ",$FLAMEHoffmanFlags];
]


If[ValueQ[$FToolHoffmanFlags],
	Print["$FTool resources set to: ",$FToolHoffmanFlags];
]


(* ::Chapter::Closed:: *)
(*Setup*)


{$FLAMETime,
$FToolTime,$FToolReadTime,$FToolWriteTime,
$MappingTime,
$TransferTime,
$IBPreadTime,$IBPlookupTime}={0,0,0,0,0,0,0,0};


DebugPrint[expr_]:=If[$Debug,Print[expr];];


time=AbsoluteTime[];


$Dir=Switch[True,
$Notebooks,NotebookDirectory[],
Length[$ScriptCommandLine]>0,
FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];
SetDirectory[$Dir];


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{
"LorentzVectorUtils.wl",
"GraphTools.wl",
"IntegralTools.wl",
"TwoBodyKinematics.wl",
"Scripts/paths.m",
"Scripts/fire_functions.m"}


familySel=Get[$IntegralToolsFIREDirectory<>"/families.m"];


diagData=Get[$StdGraphsPath];
parentDaughterRelations=(Table[MapAt[Int[rs,#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,$Shift}]//Flatten);


UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];
(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


Print["Perfoming reduction in families ",familySel," ."];


(* Minimalistic topology setup *)
Do[
	softProps[i]=ExpandLeadingPropagators[ToSoftVariables[diagData[[i]]["StandardPropagators"]],SoftScalinqKin,qcnt]/.pbar:>u/.mq2:>1;
	(* initializing the basic topologies*)
	InitializeTopology[softProps[i],
	"LoopMom"->{l},
	"ID"->i,
	"Name"->"Diag"<>ToString[i],
	"FIREProblemID"->i,
	"Graph"->diagData[[i]]["Graph"],
	"Replacements"->consRescaled,
	"TopSector"->diagData[[i]]["TopSector"],
	"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
	"CreateSectorData"->False,
	"CreateTempDirectories"->False];

	(* generating crossed topologies as well *)
	Do[InitializeTopology[softProps[i]/.(SoftMapFromID[nn]/.u->pbar),"ID"->i+nn*$Shift,
		"LoopMom"-> {l},
		"Graph"->LabelMap[MapFromID[nn]][diagData[[i]]["Graph"]],
		"RESTRICTIONS"-> diagData[[i]]["RESTRICTIONS"],
		"Replacements"-> consRescaled,
		"TopSector"->diagData[[i]]["TopSector"],
		"CreateSectorData"->False,
		"CreateTempDirectories"->False];
	,{nn,1,7}]
,{i,familySel}]


SetRemapData[Get[$RemapDataPath]];


ReductionSectors={};
NonReductionSectors={};
RequiredSectors={};

Do[ ReductionSectors=Join[ReductionSectors,Get[FileNameJoin[{dataForwardPath[id],"ReductionSectors.m"}]]];
	NonReductionSectors=Join[NonReductionSectors,Get[FileNameJoin[{dataForwardPath[id],"NonReductionSectors.m"}]]];
	RequiredSectors=Join[RequiredSectors,Get[FileNameJoin[{dataForwardPath[id],"RequiredSectors.m"}]]];
,{id,familySel}]


Print[ContainsExactly[Join[ReductionSectors,NonReductionSectors],RequiredSectors]]
Print[Intersection[ReductionSectors,NonReductionSectors]]


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]


Do[
	If[!FileExistsQ[FileNameJoin[{basePath[id],TopoData[id]["Name"]~~".start"}]],Print["Missing start file for family ",id, "!"]];
	If[!DirectoryQ[ftoolTempPath[id]],Print["Missing ftoolTempPath ",id, "!"]];
	If[!DirectoryQ[storagePath[id]],Print["Missing storagePath ",id, "!"];CreateDirectory[storagePath[id]];];
	If[!DirectoryQ[rulePath[id]],Print["Missing rulePath ",id, "!"]];
	If[!DirectoryQ[dataForwardPath[id]],Print["Missing dataForwardPath ",id, "!"]];
	If[!FileExistsQ[configPath[id]],Print["Missing config ",id," !"]]
,{id,familySel}]


Print["Copying back storage files from storagePathSave[id] to storagePath[id] and dbPath[id]"]
Do[
	Run["cp -r "<>storagePathSave[id]<>"/* "<>storagePath[id]];
	Run["cp -r "<>storagePathSave[id]<>"/* "<>dbPath[id]];
	Run["cp -r "<>rulePathSave[id]<>"/* "<>" "<>rulePath[id]];
,{id,familySel}]


HashTable=Association[];
UpdateHashTable[integral_Int]:=AssociateTo[HashTable,(Hash[integral]->integral)]
UpdateHashTable[integralList_List]:=AssociateTo[HashTable,(Hash[#]->#)&/@integralList];


UpdateHashTable[allMasters];


GetHash[x:Int[_,{1,hash_}]]:=Module[{toret=Lookup[HashTable,hash]},
If[Head[toret]===Missing,Print["Found unexpected master integral ",x]];
Return[toret];
]


UnmaskMasters[expr_]:=expr/.x:Int[_,{1,hash_}]:>GetHash[x];


MaskInts[expr_,{id_,sec_}]:=expr/.x_Int:>(UpdateHashTable[x];Int[id,{sec,Hash[x]}])/;Length[x[[2]]]>2;


MasterIdentificationList={};


SetOptions[runFlameForwardHoffman,"extraFlags"->$FLAMEHoffmanFlags];
SetOptions[runFlameBackwardHoffman,"extraFlags"->$FLAMEHoffmanFlags];


SetOptions[readTableFToolHoffman,"extraFlags"->$FToolHoffmanFlags];
SetOptions[writeTableToGlobalStorageFToolHoffman,"extraFlags"->$FToolHoffmanFlags];


(* ::Chapter:: *)
(*Backward run*)


Print["\n\n","Starting backward stage reduction!"];
Print["# of required sectors for the full reduction: ",Length[RequiredSectors],"\n"];
Print["sectors: ",SortBy[LookupSectorID/@RequiredSectors,{#[[1]],-#[[2]]}&],"\n"];


Do[ (* loop over level from levelMin to levelMax *)
	Print["\n","Running FLAME backward for ReductionSectors (runFLAMEBackward[id,secID]) in level ",level,"\n"];
	
	Print["transferring Daughter IBP-tables for the ReductionSectors in level ",level];
	(*this should be parallelized somehow *)
	Do[transferDaughterInfo[sec];,{sec,IntLevelSelector[level][ReductionSectors]}];
	
	(* for ReductionSectors: runs flame back-substitution *)
	jobIDs={};
	tt1=AbsoluteTime[];
		Do[
			{id,secID}=LookupSectorID[sec];
			Print["Running FLAME (backward) ",sec, " ",{id,secID}];
			AppendTo[jobIDs,runFlameBackwardHoffman[id,secID]];
		,{sec,IntLevelSelector[level][ReductionSectors]}];

		Print["waiting for ",Length[jobIDs]," Hoffman jobs to finish."];
		waitForJobs[jobIDs];
	tt2=AbsoluteTime[];   $FLAMETime+=(tt2-tt1);
	If[$TimerDetails===True,Print["FLAME time: ",niceTime[(tt2-tt1)]]];
	
	(* for ReductionSectors: reads back-substituted tables and writes them into ftoolTempFile[id,secID] *)
	(* ftoolTempFile[id,secID] is necessary for the transferDaughterInfo[sec_] function *)	
	tf1=AbsoluteTime[];
	Do[ 
		{id,secID}=LookupSectorID[sec];
		tr1=AbsoluteTime[];
			tab=readDBFTool2[id,secID];
		tr2=AbsoluteTime[];    $FToolReadTime+=(tr2-tr1);
		tt1=AbsoluteTime[];	
			Export[ftoolTempFile[id,secID],tab,"String"];
		tt2=AbsoluteTime[];	$TransferTime+=(tt2-tt1);
		If[$TimerDetails===True,
			Print["ftool read time: ",niceTime[(tr2-tr1)]];
			Print["transfer time: ",niceTime[(tt2-tt1)]];
		];
	,{sec,IntLevelSelector[level][ReductionSectors]}];
	tf2=AbsoluteTime[];    $FToolTime+=(tf2-tf1);
	If[$TimerDetails===True,
		Print["ftool total time: ",niceTime[(tf2-tf1)]];
	];
	
	Print["\n","Loading IBP tables for reduction sectors from db folder in level ",level];
	Do[readIBPTable[sec]; ,{sec,IntLevelSelector[level][ReductionSectors]}];
	
	Print["\n","Writing mapping rules with FTOOL for NonReductionSectors sectors in level ",level];
	Do[mappingRules[sec];,{sec,IntLevelSelector[level][NonReductionSectors]}];


	Print["\n","Running FLAME backsubstitution in NonReductionSectors that are RequiredSectors for level > ", level," substitutions"];
	jobIDs={};
	tt1=AbsoluteTime[];
		Do[{id,secID}=LookupSectorID[sec];
			Print["Running FLAME (backward) ",sec, " ",{id,secID}];
			AppendTo[jobIDs,runFlameBackwardHoffman[id,secID]];
		,{sec,IntLevelSelector[level][NonReductionSectors]}];
	
		Print["waiting for ",Length[jobIDs]," Hoffman jobs to finish."];
		waitForJobs[jobIDs];
	tt2=AbsoluteTime[];   $FLAMETime+=(tt2-tt1);
	If[$TimerDetails===True,
		Print["flame time: ",niceTime[(tt2-tt1)]]
	];
	
	
	
	Print["for NonReductionSectors: reads back-substituted tables and writes them into ftoolTempFile[id,secID]"];
	tf1=AbsoluteTime[];
	Do[ 
		{id,secID}=LookupSectorID[sec];
		tr1=AbsoluteTime[];
			tab=readDBFTool2[id,secID];
		tr2=AbsoluteTime[];    $FToolReadTime+=(tr2-tr1);
		tt1=AbsoluteTime[];	
			Export[ftoolTempFile[id,secID],tab,"String"];
		tt2=AbsoluteTime[];	$TransferTime+=(tt2-tt1);
		If[$TimerDetails===True,
			Print["ftool read time: ",niceTime[(tr2-tr1)]];
			Print["transfer time: ",niceTime[(tt2-tt1)]];
		];
	,{sec,IntLevelSelector[level][NonReductionSectors]}];
	tf2=AbsoluteTime[];  $FToolTime+=(tf2-tf1);
	If[$TimerDetails===True,
		Print["ftool total time: ",niceTime[(tf2-tf1)]];
	];
	
	
	(* some sanity checks ... *)
	Do[ {id,secID}=LookupSectorID[sec];
		If[!FileExistsQ[FLAMEBackwardlogFile[id,secID]],
           Print["Missing ",FLAMEBackwardlogFile[id,secID]]; Quit[];
		];
	,{sec,IntLevelSelector[level][ReductionSectors]}];
	
	
,{level,levelMin,levelMax}]


Do[
	Put[Select[MasterIdentificationList,#[[1,1]]==id&],FileNameJoin[{basePath[id],"MasterIdentification.m"}]];
,{id,familySel}]


Put[HashTable,FileNameJoin[{$IntegralToolsFIREDirectory,"HashTable.m"}]];


Print["Copying all back-substituted data-base files into a /tables-folder."]
Do[
	{id,secID}=LookupSectorID[sec];
	If[!DirectoryQ[$BasePath<>"/tables"],CreateDirectory[$BasePath<>"/tables"]];
	Run["cp "<>ftoolTempFile[id,secID]<>" "<>$BasePath<>"/tables/int_"<>ToString[id]<>"_sec_"<>ToString[secID]<>".tables"];
,{sec,RequiredSectors}]


Print["Done. 
STATISTICS: 
===================================
Total time: ",
niceTime[(AbsoluteTime[]-time)],
"
FLAME time: ",
niceTime[$FLAMETime],
"
total FTool time: ",
niceTime[$FToolTime],
"
total FTool read time: ",
niceTime[$FToolReadTime],
"
total FTool write time: ",
niceTime[$FToolWriteTime],
"
Mapping time: ",
niceTime[$MappingTime],
"
Transfer time: ",
niceTime[$TransferTime],
"
IBP reading time: ",
niceTime[$IBPreadTime]
]
