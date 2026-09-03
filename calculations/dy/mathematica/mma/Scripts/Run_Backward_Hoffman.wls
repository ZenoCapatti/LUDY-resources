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


Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{"LorentzVectorUtils.wl","GraphTools.wl","IntegralTools.wl","TwoBodyKinematics.wl","Scripts/paths.m"}


diagData=Get[$StdGraphsPath];


UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];
(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];


(*
(* all sectors in the two families *)
IntegralsToReduce=Get["input/IntegralsToReduce.m"];
IntegralsToReduce=Join[IntegralsToReduce,Flatten[Values[UniqueSectorMaster]]];
IntegralsToReduce=Union[ModIntegrals[IntegralsToReduce]];
*)


Print["Perfoming reduction in families ",familySel," ."];


(* Minimalistic topology setup *)
Do[
softProps[i]=ExpandLeadingPropagators[ToSoftVariables[diagData[[i]]["StandardPropagators"]],SoftScalinqKin,qcnt]/.pbar:>u/.mq2:>1;
InitializeTopology[softProps[i],
"LoopMom"->{l},
"ID"->i,
"Name"->"Diag"<>ToString[i],
"FIREProblemID"->i,
"Graph"->diagData[[i]]["Graph"],
"Replacements"-> consRescaled,
"TopSector"->diagData[[i]]["TopSector"],
"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
"CreateSectorData"->False,
"CreateTempDirectories"->False];


Do[
InitializeTopology[softProps[i]/.(SoftMapFromID[nn]/.u->pbar),
"ID"->i+nn*$Shift,
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


(*dropping *)
SetRemapData[Get[$RemapDataPath]];
autoRel={};


ReductionSectors=Union[ModIntegrals[$RepresentativeSectors]];
SectorsMod=Union[ModIntegrals[$AllSectors]];
NonReductionSectors=Complement[SectorsMod,ReductionSectors];


RequiredSectors=Flatten[Table[Get[FileNameJoin[{dataForwardPath[id],"RequiredSectors.m"}]],{id,familySel}]];


(*Do[
IntegralsInSector[sec]=IntSectorSelector[sec][IntegralsToReduce],{sec,SectorsMod}
]*)


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]


Do[
If[!FileExistsQ[FileNameJoin[{basePath[id],TopoData[id]["Name"]~~".start"}]],Print["Missing start file for family ",id, "!"]];
If[!DirectoryQ[ftoolTempPath[id]],Print["Missing ftoolTempPath ",id, "!"]];
If[!DirectoryQ[storagePath[id]],Print["Missing storagePath ",id, "!"]];
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
Run["cp -r "~~storagePathSave[i]~~" "~~storagePath[i]];
(*DeleteDirectory[storageMovedPath[i],DeleteContents->True]*)
,
{i,familySel}];


(* ::Chapter:: *)
(*Fire & FTool Run Scripts*)


(* ::Section::Closed:: *)
(*FIRE Backward By Level*)


runFIREBackward[id_,level_]:=Module[{tt},
tt=AbsoluteTime[];
Run@StringJoin[{
$FIREBinPath,
" -c ",
StringDelete[configPath[id,level],".config"],
" --backward ",
ToString[level],
" > ",
FileNameJoin[{logFilePath[id],"FIREbackward"~~"_"~~ToString[level]~~".out"}]
}
];
$FIRETime+=tt-AbsoluteTime[];
]


writeFIREbackwardSH[id_,level_]:=
WriteString[ 
FileNameJoin[{basePath[id],"fireRunBackward_"<>ToString[id]<>"_"<>ToString[level]<>".sh"}],
$FIREBinPath<>" -c "<>StringDelete[configPath[id,level],".config"]<>" --backward "<>ToString[level]
]


Options[runFIREBackwardHoffman2]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}
runFIREBackwardHoffman2[id_,level_,OptionsPattern[]]:=Module[{jobID},
writeFIREbackwardSH[id,level];
Run@StringJoin[
"#!/bin/bash \n",
"qsub ",
OptionValue["extraFlags"],
" -N "<>"bwd"<>ToString[id]<>"_"<>ToString[level]<>" ",
"-o "<>FileNameJoin[{logFilePath[id],"FIREbackward"~~"_"~~ToString[level]~~".out "}],
FileNameJoin[{basePath[id],"fireRunBackward_"<>ToString[id]<>"_"<>ToString[level]<>".sh"}],
" > ",
FileNameJoin[{basePath[id],"hoffmanID_FIREbackward_"<>ToString[id]<>"_"<>ToString[level]<>".txt"}]
];
jobID=StringSplit[Import[FileNameJoin[{basePath[id],"hoffmanID_FIREbackward_"<>ToString[id]<>"_"<>ToString[level]<>".txt"}],"String"]," "][[3]]
]


(* ::Section::Closed:: *)
(*FIRE Global*)


runFIREBackward[id_]:=Module[{tt},
tt=AbsoluteTime[];
Run@StringJoin[{
$FIREBinPath,
" -c ",
StringDelete[configPath[id],".config"],
" --backward",
" > ",
FileNameJoin[{logFilePath[id],"FIREbackward_global.out"}]
}
];
$FIRETime+=tt-AbsoluteTime[];
]


writeFIREbackwardGlobalSH[id_]:=
WriteString[ 
FileNameJoin[{basePath[id],"fireRunBackward_"<>ToString[id]<>".sh"}],
$FIREBinPath<>" -c "<>StringDelete[configPath[id],".config"]<>" --backward"
]


Options[runFIREBackwardGlobalHoffman2]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}
runFIREBackwardGlobalHoffman2[id_,OptionsPattern[]]:=Module[{jobID},
writeFIREbackwardGlobalSH[id];

Run@StringJoin[
"#!/bin/bash \n",
"qsub ",
OptionValue["extraFlags"],
" -N "<>"bwd"<>ToString[id]<>"_global"<>" ",
"-o "<>FileNameJoin[{logFilePath[id],"FIREbackward_global.out "}],
FileNameJoin[{basePath[id],"fireRunBackward_"<>ToString[id]<>".sh"}],
" > ",
FileNameJoin[{basePath[id],"hoffmanID_FIREbackward_"<>ToString[id]<>".txt"}]
];
jobID=StringSplit[Import[FileNameJoin[{basePath[id],"hoffmanID_FIREbackward_"<>ToString[id]<>".txt"}],"String"]," "][[3]]
]


(* ::Section::Closed:: *)
(*Ftool Read*)


readTableFTool[id_,secID_]:=Module[{},		
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
];		


writeFtoolReadSH[id_,secID_]:=WriteString[
FileNameJoin[{basePath[id],"ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".sh"}],
StringJoin[$FToolBinPath,
    " -c ", 
    StringDelete[configPath[id],".config"],
    " -q -s ",
    ToString[secID],
    " -d ",
    storagePath[id],
    " > ",
    ftoolTempFile[id,secID]
]
];      


Options[readTableFToolHoffman2]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}
readTableFToolHoffman2[id_,secID_,OptionsPattern[]]:=
Module[{},
writeFtoolReadSH[id,secID];

Run@StringJoin[
"#!/bin/bash \n",
"qsub ",
OptionValue["extraFlags"],
" -N "<>"ftool"<>ToString[id]<>"_"<>ToString[secID]<>" ",
"-o "<>FileNameJoin[{logFilePath[id],"ftool"~~"_"~~ToString[secID]~~".out "}],
FileNameJoin[{basePath[id],"ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".sh"}],
" > ",
FileNameJoin[{basePath[id],"hoffmanID_Ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".txt"}]
];
jobID=StringSplit[Import[FileNameJoin[{basePath[id],"hoffmanID_Ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".txt"}],"String"]," "][[3]]
]


(* ::Section::Closed:: *)
(*FTool Write*)


writeTableFTool[id_,secID_]:=Module[{},
Run@StringJoin[$FToolBinPath,
	" -c ", 
	StringDelete[configPath[id,level],".config"],
	" -q -s ",
	ToString[secID],
	" -d ",
	storagePath[id],
	" --backward ",
	" <",
	ruleFile[id,secID]
];
];


writeFtoolWriteSH[id_,secID_]:=WriteString[
FileNameJoin[{basePath[id],"ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".sh"}],
StringJoin[$FToolBinPath,
	" -c ", 
	StringDelete[configPath[id,level],".config"],
	" -q -s ",
	ToString[secID],
	" -d ",
	storagePath[id],
	" --backward ",
	" <",
	ruleFile[id,secID]
]
];      


Options[writeTableFToolHoffman2]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}

writeTableFToolHoffman2[id_,secID_,OptionsPattern[]]:=Module[{jobID},
writeFtoolWriteSH[id,secID];

Run@StringJoin[
"#!/bin/bash \n",
"qsub ",
OptionValue["extraFlags"],
" -N "<>"ftool"<>ToString[id]<>"_"<>ToString[secID]<>" ",
"-o "<>FileNameJoin[{logFilePath[id],"ftool"~~"_"~~ToString[secID]~~".out "}],
FileNameJoin[{basePath[id],"ftool_"<>ToString[id]<>"_"<>ToString[secID]<>".sh"}],
" > ",
FileNameJoin[{basePath[id],"hoffmanID_Ftoolbackward_"<>ToString[id]<>"_"<>ToString[secID]<>".txt"}]
];
jobID=StringSplit[Import[FileNameJoin[{basePath[id],"hoffmanID_Ftoolbackward_"<>ToString[id]<>"_"<>ToString[secID]<>".txt"}],"String"]," "][[3]]
]


(* ::Section::Closed:: *)
(*check status of Hoffman jobs*)


jobRunningQ[jobID_]:=!StringFreeQ[RunProcess[{"qstat","-j",jobID},"StandardOutput"],"=============================================================="]


waitForJobs[jobIDList_]:=Module[{jobsRunning=True},
While[jobsRunning,
		Pause[2];
		Print["check ",jobIDList];
		jobsRunning=Or@@Table[jobRunningQ[jobID],{jobID,jobIDList}];	
];
]	


(* ::Chapter:: *)
(*Setting FIRE & FTool Options*)


SetOptions[runFIREBackwardHoffman2,"extraFlags"->$FIREHoffmanFlags]
SetOptions[runFIREBackwardGlobalHoffman2,"extraFlags"->$FIREHoffmanFlags]

SetOptions[readTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]
SetOptions[writeTableFToolHoffman2,"extraFlags"->$FToolHoffmanFlags]


(* ::Chapter::Closed:: *)
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
(*Backward*)


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


Do[
    jobIDs={};
	Do[Print["Running FIRE backwards for level ",level, " of family ",i];
		(*runFIREBackward[i,level];*)
		AppendTo[jobIDs,runFIREBackwardHoffman2[i,level]];
	,{i,familySel}
	];
	waitForJobs[jobIDs];
	
	Do[
		{id,secID}=LookupSectorID[sec];
		(* skip sektors that have not been touched, e.g because there were no integrals *)
		If[
			!FileExistsQ[storageTempFile[id,secID]],
			Print["Missing temp file!"];
			Continue[];
		];

		readTableFTool[id,secID];
	
		If[!FileExistsQ[ftoolTempFile[id,secID]],
		Print["ftool temp file not created."];
		Quit[];
		];
	
		IBPTable[sec]=UnmaskMasters[DeleteCases[ToExpression[StringReplace[Import[ftoolTempFile[id,secID],"String"],"-> ,"->"->0 ,"]]/.G->Int,{}]];
		masters[sec]=IntSectorSelector[sec][ListInts[IBPTable[sec][[;;,2]]]];
	
		(* check that the masters are as expected *)
		If[!ContainsExactly[masters[sec],UniqueSectorMaster[sec]],
			Print["Masters not aligned!"];
		];
	
		IBPTable[sec]=Join[IBPTable[sec],Thread[masters[sec]->masters[sec]]];
		MasterMap[sec]=Quiet@MasterIdentification[sec,masters[sec]];
	
		(* generate identification rules for all equivalent sectors *)
		MasterIdentificationList=Join[MasterIdentificationList,MasterMap[sec]];
	,{sec,IntLevelSelector[level][Intersection[RequiredSectors,ReductionSectors]]}
	];

	jobIDs={};
	Do[
		{id,secID}=LookupSectorID[sec];
		DebugPrint[{id,secID}];
		If[MemberQ[sectorsToMap[level],sec],
			r1=Get[FileNameJoin[{rulePath[id],"rules_mapping"~~ToString[secID]~~".txt"}]];
			(* for all sectors on the RHS get the corresponding IBP table *)
			r2=Flatten[LookupIBPTable/@ListIntSectors[r1[[;;,2]]]];

			r1Masked=MapAt[MaskInts[#,{id,secID}]&,r1,{All,2}];
			r2Masked=Map[MaskInts[#[[1]],{id,secID}]->MaskInts[#[[2]],{id,1}]&,r2];
			maskedRules=Join[r1Masked,r2Masked];
			,(* else do *)
			maskedRules=MapAt[MaskInts[#,{id,1}]&,IBPTable[sec],{All,2}];
		];

		maskedRules=MapAt[CollectInts,maskedRules,{All,2}];
		Put[RuleSum2List/@maskedRules/.Int->G,ruleFile[id,secID]];
		
		(*writeTableFTool[id,secID];*)
		AppendTo[jobIDs,writeTableFToolHoffman2[id,secID]];

	,{sec,IntLevelSelector[level][RequiredSectors]}
	];
	(*waiting for all Hoffman jobs to finish *)
	waitForJobs[jobIDs];
	
	jobIDs={};
	Do[Print["Re-running FIRE backwards for level ",level, " of family ",i];
		(*runFIREBackward[i,level];*)
		AppendTo[jobIDs,runFIREBackwardHoffman2[i,level]];
	,{i,familySel}];
	(*waiting for all Hoffman jobs to finish *)
	waitForJobs[jobIDs];

,{level,levelMin,levelMax}]


Do[
	Put[Select[MasterIdentificationList,#[[1,1]]==id&],FileNameJoin[{basePath[id],"MasterIdentification.m"}]];
,{id,familySel}]


Put[HashTable,FileNameJoin[{$IntegralToolsFIREDirectory,"HashTable.m"}]];


(* ::Chapter:: *)
(*Global backward*)


jobIDs={};
Do[
	Print["Running FIRE global backwards for family ",id];
	(*runFIREBackward[id]*)
	AppendTo[jobIDs,runFIREBackwardGlobalHoffman2[id]];
,{id,familySel}];

waitForJobs[jobIDs]


Print["Done. 
Total time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[AbsoluteTime[]-time], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]],
"
FIRE time: ",
StringRiffle[Riffle[PadLeft[IntegerDigits[Round[$FIRETime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]
]
