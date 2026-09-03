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


(* ::Chapter:: *)
(*Setup*)


{$FIRETime,$FToolTime}={0,0};


DebugPrint[expr_]:=If[$Debug,Print[expr];];


time=AbsoluteTime[];


$Dir=Switch[True,
$Notebooks,NotebookDirectory[],
Length[$ScriptCommandLine]>0,
FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/"
];
SetDirectory[$Dir];


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{"LorentzVectorUtils.wl","GraphTools.wl","IntegralTools.wl","TwoBodyKinematics.wl","Scripts/paths.m","Scripts/fire_functions.m"}


diagData=Get[$StdGraphsPath];
parentDaugherRelations=(Table[MapAt[Int[rs,#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,$Shift}]//Flatten);


UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];
(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


Print["Perfoming reduction in families ",familySel," ."];


(* Minimalistic topology setup *)
Do[
softProps[i]=ExpandLeadingPropagators[ToSoftVariables[diagData[[i]]["StandardPropagators"]],SoftScalinqKin,qcnt]/.pbar:>u/.mq2:>1;
InitializeTopology[softProps[i],
"LoopMom"->{l},
"ID"->i,
"Name"->"Diag"<>ToString[i],
"FIREProblemID"->i,
"Replacements"-> consRescaled,
"TopSector"->diagData[[i]]["TopSector"],
"Graph"->diagData[[i]]["Graph"],
"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
"CreateSectorData"->False,
"CreateTempDirectories"->False];


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
,{nn,1,7}];
,
{i,familySel}]


SetRemapData[Get[$RemapDataPath]];


ReductionSectors=Union[ModIntegrals[$RepresentativeSectors]];
SectorsMod=Union[ModIntegrals[$AllSectors]];
NonReductionSectors=Complement[SectorsMod,ReductionSectors];
RequiredSectors=Flatten[Table[Get[FileNameJoin[{dataForwardPath[id],"RequiredSectors.m"}]],{id,familySel}]];


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]


(* ::Chapter:: *)
(*Prepare files*)


Do[
If[!FileExistsQ[FileNameJoin[{basePath[id],TopoData[id]["Name"]~~".start"}]],Print["Missing start file for family ",id, "!"]];
If[!DirectoryQ[ftoolTempPath[id]],Print["Missing ftoolTempPath ",id, "!"]];
If[!DirectoryQ[storagePath[id]],Print["Missing storagePath ",id, "!"];CreateDirectory[storagePath[id]];];
If[!DirectoryQ[rulePath[id]],Print["Missing rulePath ",id, "!"]];
If[!DirectoryQ[dataForwardPath[id]],Print["Missing dataForwardPath ",id, "!"]];

If[!DirectoryQ[dataForwardPath[id]],Print["Missing dataForwardPath ",id, "!"]];

Do[
If[!FileExistsQ[configPath[id,lv]],Print["Missing config ",id," level ", lv,"!"]];
,{lv,levelMin,levelMax}];

If[!FileExistsQ[configPath[id]],Print["Missing config ",id," !"]]

,{id,familySel}
]


Print["Copying back storage files."];
Do[
	Run["cp -r "~~storagePathSave[i]~~"/* "~~storagePath[i]];
,{i,familySel}];


Do[
	{id,secID}=LookupSectorID[sec];
	Quiet[CreateDirectory[storagePath[{id,secID}]],{CreateDirectory::eexist,CreateDirectory::filex}];
,{sec,Complement[RequiredSectors,ReductionSectors]}]


(* ::Section:: *)
(*.config files for backward*)


Do[
Switch[$Parity,
	None,{}
	,
	"Even",
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qe"~~ToString[i]~~"n.m"}]];
	,
	"Odd",
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"~~ToString[i]~~"/mi-qo"~~ToString[i]~~"n.m"}]];
];
,
{i,familySel}]


linString[intsList_]:=StringRiffle[ToString[#[[1]]]~~"-"~~ToString[#[[-1]]]&/@Split[intsList, #2 - #1 == 1 &],","];
Do[linPos[id]=linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],{id,familySel}];


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
		"database"->FileNameJoin[{basePath[id],"db/db_sector_backward_"~~ToString[secID]}],
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
	
	(* config for all levels *)
	Export[configPathBackward[{id,secID}],
	FIREConfigString["integrals"->StringJoin["ToReduce_sector_"~~ToString[secID]~~".m"],"output"->StringJoin["ToReduce_sector_"~~ToString[secID]~~".tables"]],"String"];

	
,{sec,RequiredSectors}];


(* ::Section:: *)
(*Masking rules*)


HashTable=Association[];
UpdateHashTable[integral_Int]:=AssociateTo[HashTable,(Hash[integral]->integral)]
UpdateHashTable[integralList_List]:=AssociateTo[HashTable,(Hash[#]->#)&/@integralList];


UpdateHashTable[allMasters];


GetHash[x:Int[_,{1,hash_}]]:=Module[{toret=Lookup[HashTable,hash]},
If[Head[toret]===Missing,Print["Found unexpected master integral ",x]];
Return[toret];
]


UnmaskMasters[expr_]:=expr/.x:Int[_,{1,hash_}]:>GetHash[x];


MaskInts[expr_,{id_,sec_}]:=expr/.x_Int:>(UpdateHashTable[x];Int[id,{sec,Hash[x]}]);


(* ::Chapter::Closed:: *)
(*Backward IBP-table functionality*)


Do[sectorsToMap[level]=IntLevelSelector[level][Complement[RequiredSectors,ReductionSectors]],{level,levelMin,levelMax}];


LookupIBPTable[sec:Int[id_,inds_]]/;id<=$Shift:=IBPTable[sec];
LookupIBPTable[sec:Int[id_,inds_]]/;id>$Shift:=Module[{modint,theShift=getShift[id],yFlip,table},
yFlip=(1===PadLeft[IntegerDigits[theShift,2],3][[3]]);
modint=ModIntegrals[sec];
table=IBPTable[modint];
table=UnmaskMasters[table];
If[yFlip,table=table/.y->-y];

table=table/.Int[i_,in_]:>Int[modID[i]+$Shift*SoftMapConcatination[getShift[i],theShift],in];

table=MapAt[MapIntegrals[#]/.MasterIdentificationList&,table,{All,2}];

Return[table];
];


MasterIdentification[sec:Int[id_,inds_],masters_]:=Module[{autos,shift,rel={},rr,shiftList={0},tab=Dispatch@LookupIBPTable[sec],toret},
autos=automorphismRule[GraphForInt[sec]];
(* only pick non-trivial automorphisms *)
autos=Select[autos,!ContainsOnly[(Normal[#]/.Rule->Subtract),{0}]&];
Do[
shift=SoftMapID[MapToSoftMap[map]];
AppendTo[shiftList,shift];
rr=MapIntegrals[masters/.Int[i_,ind_]:>Int[i+shift*$Shift,ind]];
AppendTo[rel,(rr/.tab)-rr];
,{map,autos}];
toret=First@Solve[rel==0,Complement[ListInts[rel],allMasters]];
toret=Flatten[Table[toret/.Int[i_,ind_]:>Int[i+ss*$Shift,ind],{ss,0,7}]];
toret=Select[toret,MemberQ[$RepresentativeSectors,IntSector[#[[1]]]]&];
Return[toret];
]


MasterIdentificationList={};


(* ::Chapter:: *)
(*Backward run*)


Do[ (* loop over level from levelMin to levelMax *)

Print["\n","Running FIRE backward for reduction sectors (runFIREBackwardBySector[id,secID,level]) in level ",level];
jobIDs={};
Do[
	{id,secID}=LookupSectorID[sec];
	Print["Running FIRE (backward) ",sec, " ",{id,secID}];
	(* copy the temp files from the daughters *)
	daughterSectors=Select[parentDaugherRelations,#[[1]]==sec &][[;;,2]];
	DebugPrint["Daughter sectors: ",daughterSectors];
	Do[
		{idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
		Run["cp "~~storageTempFile[{idDaughter,secIDDaughter}]~~" "~~storagePath[{id,secID}]];
	,{secDaughter,daughterSectors}];
	
	runFIREBackwardBySector[id,secID,level];
	(*AppendTo[jobIDs,runFIREBackwardBySectorHoffman2[id,secID,level]];*)
,{sec,IntLevelSelector[level][ReductionSectors]}];

	(*waiting for all Hoffman jobs to finish *)
	(*waitForJobs[jobIDs];*)



Print["\n","Loading IBP tables for reduction sectors (readTableFTool[{id,secID}]) in level ",level];
jobIDs={};
Do[
	{id,secID}=LookupSectorID[sec];
	Print["Reading IBP table ",sec, " ",{id,secID}];
	readTableFTool[{id,secID}];
	(*AppendTo[jobIDs,readTableFToolHoffman2[{id,secID}]];*)
,{sec,IntLevelSelector[level][ReductionSectors]}];

	(*waiting for all Hoffman jobs to finish *)
	(*waitForJobs[jobIDs];*)

(* processing the IBP-table textfile *)
Do[
	{id,secID}=LookupSectorID[sec];
	
	If[!FileExistsQ[ftoolTempFile[id,secID]],
		Print["ftool temp file not created."];
		Quit[];
	];
	
	test=DeleteCases[ToExpression[StringReplace[Import[ftoolTempFile[id,secID],"String"],"-> ,"->"->0 ,"]]/.G->Int,{}];
	IBPTable[sec]=UnmaskMasters[test];
	IBPTable[sec]=MapAt[#/.MasterIdentificationList&,IBPTable[sec],{All,2}];
	masters[sec]=IntSectorSelector[sec][ListInts[IBPTable[sec][[;;,2]]]];
	DebugPrint["masters in sector ",sec," :",{Length[masters[sec]],masters[sec]}]
	(*Print[IBPTable[sec]];*)
	
	(* check that the masters are as expected *)
	If[!ContainsExactly[masters[sec],UniqueSectorMaster[sec]],
		Print["Masters not aligned in sector ", sec," ",{id,secID},", e.g. ",Complement[masters[sec],UniqueSectorMaster[sec]][[1]] ];
	];
	
	IBPTable[sec]=Join[IBPTable[sec],Thread[masters[sec]->masters[sec]]];
	MasterMap[sec]=Quiet@MasterIdentification[sec,masters[sec]];
	
	(* generate identification rules for all equivalent sectors *)
	MasterIdentificationList=Join[MasterIdentificationList,MasterMap[sec]];
,{sec,IntLevelSelector[level][ReductionSectors]}];


Print["\n","Writing mapping rules with FTOOL for non-reduction sectors in level ",level];
Print["else, writing masked rules with FTOOL for reduction sectors in level ",level];
jobIDs={};
Do[
	{id,secID}=LookupSectorID[sec];
	DebugPrint["Assembling mapping rules ",sec, " ",{id,secID}];
	If[MemberQ[sectorsToMap[level],sec],

		r1=Get[FileNameJoin[{rulePath[id],"rules_mapping"~~ToString[secID]~~".txt"}]];
		(* for all sectors on the RHS get the corresponding IBP table *)
		r2=Flatten[LookupIBPTable/@ListIntSectors[r1[[;;,2]]]];

		r1Masked=MapAt[MaskInts[#,{id,secID}]&,r1,{All,2}];
		r2Masked=Map[MaskInts[#[[1]],{id,secID}]->MaskInts[#[[2]],{id,1}]&,r2];
		maskedRules=Join[r1Masked,r2Masked];
		,
		(* else do *)
		maskedRules=MapAt[MaskInts[#,{id,1}]&,IBPTable[sec],{All,2}];
	];

	maskedRules=MapAt[CollectInts,maskedRules,{All,2}];

	Put[RuleSum2List/@maskedRules/.Int->G,ruleFile[id,secID]];
	
	writeTableFTool[{id,secID}];
	(*AppendTo[jobIDs,writeTableFToolHoffman2[{id,secID}]];*)

,{sec,IntLevelSelector[level][RequiredSectors]}];
(*,{sec,IntLevelSelector[level][Intersection[RequiredSectors,NonReductionSectors]]}];*)	
	
	(*waiting for all Hoffman jobs to finish *)
	(*waitForJobs[jobIDs];*)

Print["\n","Running FIRE backsubstitution in non-reduction sectors in level ",level];
jobIDs={};
Do[
	{id,secID}=LookupSectorID[sec];
	Print["Running FIRE (backward) ",sec, " ",{id,secID}];
	runFIREBackwardBySector[id,secID,level];
	(*AppendTo[jobIDs,runFIREBackwardBySectorHoffman2[id,secID,level]];*)
,{sec,IntLevelSelector[level][Intersection[RequiredSectors,NonReductionSectors]]}];
	
	(*waiting for all Hoffman jobs to finish *)
	(*waitForJobs[jobIDs];*)
	
(*,{level,levelMin,levelMin}]	*)
,{level,levelMin,levelMax}]


Print["Merging storage folders."];
Do[
	{id,secID}=LookupSectorID[sec];
	Run["cp "~~storageTempFile[{id,secID}]~~" "~~storagePath[id]];
,{sec,RequiredSectors}]


Do[
	Put[Select[MasterIdentificationList,#[[1,1]]==id&],FileNameJoin[{basePath[id],"MasterIdentification.m"}]];
,{id,familySel}]


Put[HashTable,FileNameJoin[{$IntegralToolsFIREDirectory,"HashTable.m"}]];


Do[
	{id,secID}=LookupSectorID[sec];
	Print["Converting .tmp files in all required sectors after backward reduction with ftool. Working in sector: ",{id,secID}];
	Run[$FToolBinPath<>" -c "<>StringDelete[configPath[id],".config"]<>" -q -s "<>ToString[secID]<>" -d "<>storagePath[id]<>" > "<>ftoolTempPath[id]<>"/backward_"<>ToString[secID]<>".txt"];
,{sec,RequiredSectors}]


Print["Quitting before global table is produced."];


Quit[]


(* ::Section:: *)
(*Global backward*)


jobIDs={};
Do[
	Print["Running FIRE global backwards for family ",id];
	runFIREBackwardGlobal[id]
	(*AppendTo[jobIDs,runFIREBackwardGlobalHoffman2[id,secID,level]];*)
,{id,familySel}]

(*waiting for all Hoffman jobs to finish *)
(*waitForJobs[jobIDs];*)


Print["Done. 
Total time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[AbsoluteTime[]-time], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
FIRE time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$FIRETime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]
]
