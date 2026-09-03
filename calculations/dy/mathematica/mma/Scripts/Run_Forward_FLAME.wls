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


If[!ValueQ[$Parity],
Print["$Parity variable not set."];
$Parity=None
,
Print["Using $Parity: ",$Parity,"."];
]


(* ::Chapter::Closed:: *)
(*Setup*)


{$FLAMETime,$FToolTime,$MappingTime,$TransferTime,$IBPreadTime}={0,0,0,0,0};


time=AbsoluteTime[];


$Dir=Switch[True,
	$Notebooks,NotebookDirectory[],
	Length[$ScriptCommandLine]>0,
	FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];


(* loading utility packages and definitions *)
Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{
"LorentzVectorUtils.wl",
"GraphTools.wl",
"IntegralTools.wl",
"TwoBodyKinematics.wl",
"Scripts/paths.m",
"Scripts/fire_functions.m"}


(*clearing all temporary directories*)
ClearTempDirectories[]


(* setting graph data *)
diagData=Get[$StdGraphsPath];


(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


(*the default value of familySel is Range[$Shift] *)
rData=KeySelect[Get[$RemapDataPath],MemberQ[Range[$Shift],modID[#[[1]]]]&];
SetRemapData[rData];
autoRel={};


(* loading masters in the unique sectors*)
UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];

Print["check if masters are only in representative sectors: ",SameQ[allMasters,allMasters//MapIntegrals]]


HashTable=Association[];
UpdateHashTable[integral_Int]:=AssociateTo[HashTable,(Hash[integral]->integral)]
UpdateHashTable[integralList_List]:=AssociateTo[HashTable,(Hash[#]->#)&/@integralList];
UpdateHashTable[allMasters];

GetHash[x:Int[_,{1,hash_}]]:=Module[{toret=Lookup[HashTable,hash]},
	If[Head[toret]===Missing,Print["Found unexpected master integral ",x]];
	Return[toret];
]

UnmaskMasters[expr_]:=expr/.x:Int[_,{1,hash_}]:>GetHash[x];

(* only masks integrals of the form Int[id,{a1,...,an}] and not tail masked Int[id,{a,b}] *)
MaskInts[expr_,{id_,sec_}]:=expr/.x_Int:>(UpdateHashTable[x];Int[id,{sec,Hash[x]}])/;Length[x[[2]]]>2;


Print["loading integrals to reduce from: ",$ToReduce]
IntegralsToReduce=Get[$ToReduce];
Print["# of integrals to reduce: ",Length[IntegralsToReduce]]

(*inputSectors \[Equal] List of Sectors in which we have Seed integrals to begin with *)
inputSectors=ListIntSectors[IntegralsToReduce];
Print["input sectors of IntegralsToReduce: ",
MapThread[Rule,{inputSectors,LookupSectorID[inputSectors]}]
]


(* generates all the daughter sectors of all sectors of the problem *)
parentDaughterRelations=(Table[MapAt[Int[rs,#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,$Shift}]//Flatten);

(* adds all daughter sectors of the inputSectors *)
allSectors=VertexOutComponent[parentDaughterRelations,inputSectors];
Print["# of input sectors and their daughter sectors: ", Length[allSectors]]

ReductionSectors=Union[allSectors//MapIntegrals//ModIntegrals];

(* all 1-daughter sectors of reduction sectors *)
RequiredSectors=VertexOutComponent[parentDaughterRelations,ReductionSectors,1]//Union;

(*all sectors that are required but no reduction needed *)
NonReductionSectors=Complement[RequiredSectors,ReductionSectors];

familySel=ListIntFamilies[RequiredSectors];
Print["Perfoming reduction in families ",familySel,"."];


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
	"CreateSectorData"->False];

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


SectorAssociation=Association[Table[sec->Association["Integrals"->{},sec/.$RemapData];,{sec,$AllSectors}]];


(* need to find the linearized propagators *)
linString[intsList_]:=StringRiffle[ToString[#[[1]]]~~"-"~~ToString[#[[-1]]]&/@Split[intsList, #2 - #1 == 1 &],","];
Do[linPos[id]=linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],{id,familySel}];
Do[linP[id]=Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]],{id,familySel}]


IntegralsToReduce=Join[IntegralsToReduce,IntSectorSelector[RequiredSectors][Flatten[Values[UniqueSectorMaster]]]];
IntegralsToReduce=Union[ModIntegrals[IntegralsToReduce]];

(*
Print["addomg seed integrals up to tensor rank 3 in the RequiredSectors!"]
selectIntsByParity[intList_,parity_]:=Select[intList,If[$Parity\[Equal]"Odd",OddQ[Total[#[[2]][[linP[#[[1]]]]]]],EvenQ[Total[#[[2]][[linP[#[[1]]]]]]]]&]
newSeedInts=selectIntsByParity[GenerateSeedIntegrals[RequiredSectors,3],$Parity];
IntegralsToReduce=Join[IntegralsToReduce,newSeedInts]//Union;
Print["Length of integrals to reduce including minimal Rank 3 seed: ",Length[IntegralsToReduce]]
*)


(* distribute the input integrals into the given sectors, 
   we assume that the input was already mapped to unique sectors, 
   it should only populate RequiredSectors
 *)
 
Do[
	IntegralsInSector[sec]=IntSectorSelector[sec][IntegralsToReduce];
	If[MemberQ[ReductionSectors,sec],
		IntegralsInSector[sec]=Union[IntegralsInSector[sec],UniqueSectorMaster[sec]];
	];
,{sec,RequiredSectors}
];


UpdateIntegralList[intList_List]:=Do[IntegralsInSector[sec2]=Union[IntegralsInSector[sec2],IntSectorSelector[sec2][intList]],{sec2,RequiredSectors}]


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]


(*writes a ToReduce.m file for each family *)
(*ExportIntegralsFIRE[IntegralsToReduce];*)
(*ExportIntegralsFIRE[IntLevelSelector[levelMax][IntegralsToReduce],"NameFunction"->(StringJoin["ToReduce_"~~ToString[#]~~"_Level_"~~ToString[levelMax]~~".m"]&)];*)


(* ::Chapter::Closed:: *)
(*Prepare files*)


Print["Creating storage and other auxiliary folders"];

Quiet@Do[
	If[$Debug,CreateDirectory[debugPath[i]]];
	CreateDirectory[ftoolTempPath[i]];
	CreateDirectory[rulePath[i]];
	CreateDirectory[rulePathSave[i]];
	CreateDirectory[dataForwardPath[i]];
	CreateDirectory[dataForwardPath[i]<>"/daughter_requests"];
	CreateDirectory[logFilePath[i]];
	CreateDirectory[storagePath[i]];
	CreateDirectory[storagePathSave[i]];
	If[!DirectoryQ[storagePath[i]]||!DirectoryQ[storagePathSave[i]],Print["Failed to create storage."]; Quit[];];
,{i,familySel}]


(* ::Section:: *)
(*.config files for global-reduction*)


Print["Exporting FIRE configs for global reduction, global storage->storagePath[id] "];
Do[
	SetOptions[
	FIREConfigString,
	Switch[$Parity,
	None,{},
	"Even",
		{
		"even"->linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],
		(*"masters"->"|1-"~~ToString[nMasters[id]]~~"|mi-qe"~~ToString[id]~~"n.m",*)
		"preferred"->"qe"~~ToString[id]~~"n.pref"
		},
	"Odd",
		{
		"odd"->linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],
		(*"masters"->"|1-"~~ToString[nMasters[id]]~~"|mi-qo"~~ToString[id]~~"n.m",*)
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
	Export[configPath[id],FIREConfigString["integrals"->StringJoin["ToReduce.m"],"output"->StringJoin["ToReduce.tables"]],"String"];
	
,{id,familySel}];


(* ::Chapter::Closed:: *)
(*Setting FIRE & FTool Options for Hoffman2 run*)


(*
SetOptions[runFIREForwardByLevelHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREForwardBySectorHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardByLevelHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardBySectorHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardGlobalHoffman2,"extraFlags"->$FIREHoffmanFlags]
*)


(*
SetOptions[readTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
SetOptions[readTableBySectorFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
SetOptions[writeTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
*)


(* ::Chapter:: *)
(*Forward stage*)


Print["\n\n","Starting forward stage reduction!"];
Print["# of required sectors for the full reduction: ",Length[RequiredSectors],"\n"];
Print["sectors: ",SortBy[LookupSectorID/@RequiredSectors,{#[[1]],-#[[2]]}&],"\n"];


(* Large loop over the levels, starting from levelMax and going to levelMin *)
Do[
	Print["\n"<>"Forward step for level ",level,"\n"];

	(* Mapping integrals from NonReductionSectors *)
	Print["Mapping NonReductionSectors integrals (produced by higher level forward reduction)."];	  
	Print["Mapping in level ",level," for sectors: ",LookupSectorID[#]&/@IntLevelSelector[level][NonReductionSectors]];
	Do[mapIntegrals[sec],{sec,IntLevelSelector[level][NonReductionSectors]}];
		
	Print["Updating ReductionSectors integral lists in level ",level,"."];
	ToRed[level]=Union[Flatten[IntegralsInSector/@IntLevelSelector[level][ReductionSectors]]];
	
	If[!ContainsAll[ReductionSectors,ListIntSectors[ToRed[level]]],
	   Print["Found integrals in non-reduction sectors! Bad sectors are: ", Complement[ListIntSectors[ToRed[level]],ReductionSectors]];];

	(* writes a .tmp file (storageTempFile[id,secID]) into the central storage path *)
	(* with all integrals that are required for the reduction *)
	Do[writeTrivialRules[sec],{sec,IntLevelSelector[level][RequiredSectors]}];



	(* FLAME run *)
	Print["Integrals in families: ",ListIntFamilies[ToRed[level]]];
	Print["\n","run FLAME in level ",level," in ReductionSectors: ", LookupSectorID[#]&/@IntLevelSelector[level][ReductionSectors]];

	Do[
		{id,secID}=LookupSectorID[sec];
		Print["Running FLAME in sector ",sec," ",{id,secID}(*," jobID ",jobIDs[[-1]]*)];
		runFlameForward[id,secID];
	,{sec,IntLevelSelector[level][ReductionSectors]}];	

	(* some sanity checks ... *)
	Do[ {id,secID}=LookupSectorID[sec];
		If[!FileExistsQ[FLAMEForwardlogFile[id,secID]],
           Print["Missing ",FLAMEForwardlogFile[id,secID]]; Quit[];
		];
	,{sec,IntLevelSelector[level][ReductionSectors]}];



	Print["feed information about lower level integrals to the lower sectors:"];
	(*for a reduction sectors, look at all one-daughter integrals that appear on the RHS of the parent .tmp file after running FLAME in the parent sector *)
	jobIDs={};	
	Do[feedDaughterIntsToLowerSectors[sec],{sec,IntLevelSelector[level][ReductionSectors]}];		

,{level,Reverse[Range[levelMin,levelMax]]}];


Print["\n","Copying storage files to storagePathSave"]
Do[ 
Run["cp -r "<>storagePath[id]<>"/* "<>storagePathSave[id]] ;
Run["cp -r "<>rulePath[id]<>"/* "<>" "<>rulePathSave[id]];
,{id,familySel}]


Do[
	Put[Cases[ReductionSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"ReductionSectors.m"}]];
	Put[Cases[NonReductionSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"NonReductionSectors.m"}]];
	Put[Cases[RequiredSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"RequiredSectors.m"}]];
	Put[Cases[$RepresentativeSectors,Int[id,_]],FileNameJoin[{dataForwardPath[id],"RepresentativeSectors.m"}]];
,{id,familySel}]


Put[familySel,$IntegralToolsFIREDirectory<>"/families.m"];


Print["Done. 
Total time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[AbsoluteTime[]-time], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
FLAME time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$FLAMETime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
FTool time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$FToolTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
Mapping time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$MappingTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
Transfer time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$TransferTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]
]


(* ::Chapter::Closed:: *)
(*Play*)


(*reverseLookUp[id_,secID_]:=({id,secID}/.MapThread[Rule,{LookupSectorID/@RequiredSectors,RequiredSectors}])*)


(*ppp="/Users/eh10/Documents/amplitudes_offline_files/2022_4loop_classical_GR/mathematica/fire_mapping_git/examples/3PM_MapAndReduce/temp/FIRE/";
idSel=5;

secIDSel=13;

reverseLookUp[idSel,secIDSel]//DisplayIntPM
DeleteCases[ToExpression[StringReplace[Import[ppp<>"Diag"<>ToString[idSel]<>"/ftool/out_"<>ToString[secIDSel]<>".txt","String"],{"-> ,"\[Rule]"-> 0 ,"}]],{}][[;;,2]]//ListInts*)


(*ppp2="/Users/eh10/Documents/amplitudes_offline_files/2022_4loop_classical_GR/mathematica/fire_mapping_git/examples/3PM_MapAndReduce/"
DeleteCases[ToExpression[StringReplace[Import[ppp2<>"/testout_5_13.txt","String"],{"-> ,"\[Rule]"-> 0 ,"}]],{}][[;;,2]]/.G:>Int//ListInts
DisplayIntPM/@(%//UnmaskMasters)*)



