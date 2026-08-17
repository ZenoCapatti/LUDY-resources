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


(*$ToolBoxPath="/Users/eh10/Documents/amplitudes_offline_files/2022_4loop_classical_GR/mathematica/fire_mapping_git";
$BasePath=FileNameJoin[{$ToolBoxPath,"examples/5PM_MapAndReduce_N8"}];
IntegralTools`$IntegralToolsBaseDirectory=$BasePath;

$ToReduce=$BasePath<>"/integrandIntsEvenMod_1SF.m";

$inputDataPath=FileNameJoin[{$ToolBoxPath,"/StandardData/PM/5PM_1SF"}];
$RemapDataPath=$inputDataPath<>"/RemapData_FixedExternal.m";
$StdGraphsPath=$inputDataPath<>"/StandardGraphs.m";
$UniqueSectorMasterPath=$inputDataPath<>"/UniqueSectorMasterEven.m";
$SectorIDPath=$inputDataPath<>"/sectorID.m";
$DiagDataPath=$inputDataPath<>"/DiagData";

$FLAMEHoffmanFlags="-l h_data=8G,h_rt=336:00:00,highp -pe shared 8";
$FToolHoffmanFlags="-l h_data=8G,h_rt=336:00:00,highp -pe shared 8";

$Shift=394;
$Parity="Even";
$parallel=2;
$Debug=True;
$TimerDetails=True;*)


(* Load remap data *)
If[!FileExistsQ[$RemapDataPath],
Print["Could not locate remap data file ",$RemapDataPath,"."];
Quit[];,
Print["Loading remap data from: ",$RemapDataPath,"."];
]


(* Load standard graph data *)
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


If[!ValueQ[$parallel],
	Print["$parallel variable not set. default $parallel=1."];
	$parallel=1;
	,
	Print["$parallel variable set to: ",$parallel]
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


If[ValueQ[$Restart],
	Print["$Restart set to: ",$Restart];
	If[ValueQ[$RestartLevel],
		Print["$RestartLevel set to: ",$RestartLevel];
	]
	,
	$Restart=False;
]


(* ::Chapter:: *)
(*Setup*)


{$FLAMETime,
$FToolTime,$FToolReadTime,$FToolWriteTime,
$MappingTime,
$TransferTime,
$IBPreadTime,$IBPlookupTime}={0,0,0,0,0,0,0,0};


time=AbsoluteTime[];


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


(* loading masters in the unique sectors*)
UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];

Print["check if masters are only in $RepresentativeSectors: ",SameQ[allMasters,allMasters//MapIntegrals]]


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


Print["loading integrals to reduce from: ",$ToReduce];
IntegralsToReduce=Get[$ToReduce];
Print["# of integrals to reduce: ",Length[IntegralsToReduce]];

(*inputSectors \[Equal] List of Sectors in which we have Seed integrals to begin with *)
inputSectors=ListIntSectors[IntegralsToReduce];
Print["input sectors of IntegralsToReduce: ",MapThread[Rule,{inputSectors,LookupSectorID[inputSectors]}]];


(* generates all the daughter sectors of all sectors of the problem *)
parentDaughterRelations=(Table[MapAt[Int[diagData[[rs]]["ID"],#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,Length[diagData]}]//Flatten);
(* adds all daughter sectors of the inputSectors *)
allSectors=VertexOutComponent[parentDaughterRelations,inputSectors];
Print["# of input sectors and their daughter sectors: ", Length[allSectors]];
ReductionSectors=Union[allSectors//MapIntegrals//ModIntegrals];
(* all 1-daughter sectors of reduction sectors *)
RequiredSectors=VertexOutComponent[parentDaughterRelations,ReductionSectors,1]//Union;

(*all sectors that are required but no reduction needed *)
NonReductionSectors=Complement[RequiredSectors,ReductionSectors];

familySel=ListIntFamilies[RequiredSectors];
Print["Perfoming reduction in families ",familySel,"."];


familySelInDiagData=First[Position[diagData[[#]]["ID"]&/@Range[Length[diagData]],#]]&/@familySel//Flatten;
familySelInDiagDataAssociation=Association[MapThread[Rule,{familySel,familySelInDiagData}]];


Print["Minimalistic topology setup."]
Do[
	softProps[diagData[[i]]["ID"]]=ExpandLeadingPropagators[ToSoftVariables[diagData[[i]]["StandardPropagators"]],SoftScalinqKin,qcnt]/.pbar:>u/.mq2:>1;
	(* initializing the basic topologies*)
	InitializeTopology[softProps[diagData[[i]]["ID"]],
	"LoopMom"->{l},
	"ID"->diagData[[i]]["ID"],
	"Name"->"Diag"<>ToString[diagData[[i]]["ID"]],
	"FIREProblemID"->diagData[[i]]["ID"],
	"Graph"->diagData[[i]]["Graph"],
	"Replacements"->consRescaled,
	"TopSector"->diagData[[i]]["TopSector"],
	"RESTRICTIONS"->diagData[[i]]["RESTRICTIONS"],
	"CreateSectorData"->False,
	If[$Restart===True,"CreateTempDirectories"->False,"CreateTempDirectories"->True]
	];

	(* generating crossed topologies as well *)
	Do[InitializeTopology[softProps[diagData[[i]]["ID"]]/.(SoftMapFromID[nn]/.u->pbar),
		"ID"->diagData[[i]]["ID"]+nn*$Shift,
		"LoopMom"-> {l},
		"Graph"->LabelMap[MapFromID[nn]][diagData[[i]]["Graph"]],
		"RESTRICTIONS"-> diagData[[i]]["RESTRICTIONS"],
		"Replacements"-> consRescaled,
		"TopSector"->diagData[[i]]["TopSector"],
		"CreateSectorData"->False,
		"CreateTempDirectories"->False];
	,{nn,1,7}]
,{i,familySelInDiagData}]


(* Move the start files *)
Print["Copying start files. "];
Do[
	CopyFile[
		FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/Diag"<>ToString[i]<>".start"}],
		$IntegralToolsFIREDirectory<>"/Diag"<>ToString[i]<>"/Diag"<>ToString[i]<>".start",
		OverwriteTarget->True
	];

Switch[$Parity,
	None,{}
	,
	"Even",
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/mi-qe"<>ToString[i]<>"n.m"}],$IntegralToolsFIREDirectory<>"/Diag"<>ToString[i]<>"/mi-qe"<>ToString[i]<>"n.m",OverwriteTarget->True];
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/qe"<>ToString[i]<>"n.pref"}],$IntegralToolsFIREDirectory<>"/Diag"<>ToString[i]<>"/qe"<>ToString[i]<>"n.pref",OverwriteTarget->True];
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/mi-qe"<>ToString[i]<>"n.m"}]];
	,
	"Odd",
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/mi-qo"<>ToString[i]<>"n.m"}],$IntegralToolsFIREDirectory<>"/Diag"<>ToString[i]<>"/mi-qo"<>ToString[i]<>"n.m",OverwriteTarget->True];
	CopyFile[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/qo"<>ToString[i]<>"n.pref"}],$IntegralToolsFIREDirectory<>"/Diag"<>ToString[i]<>"/qo"<>ToString[i]<>"n.pref",OverwriteTarget->True];
	nMasters[i]=Length@Get[FileNameJoin[{$DiagDataPath,"Diag"<>ToString[i]<>"/mi-qo"<>ToString[i]<>"n.m"}]];
];
,
{i,familySel}]


SectorAssociation=Association[Table[sec->Association["Integrals"->{},sec/.$RemapData];,{sec,$AllSectors}]];


(* need to find the linearized propagators *)
linString[intsList_]:=StringRiffle[ToString[#[[1]]]<>"-"<>ToString[#[[-1]]]&/@Split[intsList, #2 - #1 == 1 &],","];
Do[linPos[diagData[[id]]["ID"]]=linString[Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]]],{id,familySelInDiagData}];
Do[linP[diagData[[id]]["ID"]]=Union[Position[diagData[[id]]["SoftPropagators"],u[_]][[;;,1]]],{id,familySelInDiagData}]


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
Print["Distributing input integrals to RequiredSectors."] 
Do[
	IntegralsInSector[sec]=IntSectorSelector[sec][IntegralsToReduce];
	If[MemberQ[ReductionSectors,sec],
		IntegralsInSector[sec]=Union[IntegralsInSector[sec],UniqueSectorMaster[sec]];
	];
,{sec,RequiredSectors}
];


UpdateIntegralList[intList_List]:=Module[{secs=Intersection[ListIntSectors[intList],RequiredSectors]},
	Do[
		IntegralsInSector[sec2]=Union[IntegralsInSector[sec2],IntSectorSelector[sec2][intList]]
	,{sec2,secs}]
]
(*UpdateIntegralList[intList_List]:=Do[IntegralsInSector[sec2]=Union[IntegralsInSector[sec2],IntSectorSelector[sec2][intList]],{sec2,RequiredSectors}]*)


levelMin=Min[IntLevel/@ReductionSectors];
levelMax=Max[IntLevel/@ReductionSectors];
Print["Reduction in levels ",levelMin," to ",levelMax,"."]

If[$Restart==True,
	Print["Re-starting forward run with level ",$RestartLevel]; restartLevel=$RestartLevel;
	,
	restartLevel=levelMax;
];

Print["starting forward reduction with level: ",restartLevel]


(*writes a ToReduce.m file for each family *)
(*ExportIntegralsFIRE[IntegralsToReduce];*)
(*writes a ToReduce_Level_levelMax.m file for each family *)
(*ExportIntegralsFIRE[IntLevelSelector[levelMax][IntegralsToReduce],"NameFunction"->(StringJoin["ToReduce_"<>ToString[#]<>"_Level_"<>ToString[levelMax]<>".m"]&)];*)


SetOptions[runFlameForwardHoffman,"extraFlags"->$FLAMEHoffmanFlags];
SetOptions[runFlameBackwardHoffman,"extraFlags"->$FLAMEHoffmanFlags];


SetOptions[readTableFToolHoffman,"extraFlags"->$FToolHoffmanFlags];
SetOptions[writeTableToGlobalStorageFToolHoffman,"extraFlags"->$FToolHoffmanFlags];


(* ::Chapter:: *)
(*Prepare files*)


Print["Creating storage and other auxiliary folders"];

Quiet@Do[
	(*If[$Debug,CreateDirectory[debugPath[i]]];*)
	CreateDirectory[ftoolTempPath[i]];
	CreateDirectory[rulePath[i]];
	CreateDirectory[rulePathSave[i]];
	CreateDirectory[dataForwardPath[i]];
	CreateDirectory[dataForwardPath[i]<>"/daughter_requests"];
	CreateDirectory[logFilePath[i]];
	CreateDirectory[basePath[i]<>"/hoffman"];
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
		"even"->linString[Union[Position[diagData[[familySelInDiagDataAssociation[id]]]["SoftPropagators"],u[_]][[;;,1]]]],
		(*"masters"->"|1-"<>ToString[nMasters[id]]<>"|mi-qe"<>ToString[id]<>"n.m",*)
		"preferred"->"qe"<>ToString[id]<>"n.pref"
		},
	"Odd",
		{
		"odd"->linString[Union[Position[diagData[[familySelInDiagDataAssociation[id]]]["SoftPropagators"],u[_]][[;;,1]]]],
		(*"masters"->"|1-"<>ToString[nMasters[id]]<>"|mi-qo"<>ToString[id]<>"n.m",*)
		"preferred"->"qo"<>ToString[id]<>"n.pref"
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
		"threads"->$parallel,
		"fthreads"-> 4$parallel,
		"bucket"-> 30,
		"folder"->basePath[id],
		"variables"->"d,y",
		"problem"-> ToString[id]<>" |"<>ToString[Max[Flatten[Position[diagData[[familySelInDiagDataAssociation[id]]]["TopSector"],_?Positive]]]]<>"|"<>TopoData[id]["Name"]<>".start"
		}
	];
	If[ValueQ[$FIREOptions],SetOptions[FIREConfigString,$FIREOptions]];

	(* config for all levels *)
	Export[configPath[id],FIREConfigString["integrals"->StringJoin["ToReduce.m"],"output"->StringJoin["ToReduce.tables"]],"String"];
	
,{id,familySel}];


(* ::Chapter:: *)
(*Forward run*)


Print["\n\n","Starting forward stage reduction!"];
Print["RequiredSectors statistics:"]
Do[Print["# of RequiredSectors in lv "<>ToString[lv]<>": ",Length[IntLevelSelector[lv][RequiredSectors]]],{lv,levelMin,levelMax}]
Print["ReductionSectors statistics:"]
Do[Print["# of ReductionSectors in lv "<>ToString[lv]<>": ",Length[IntLevelSelector[lv][ReductionSectors]]],{lv,levelMin,levelMax}]
Print["NonReductionSectors statistics:"]
Do[Print["# of NonReductionSectors in lv "<>ToString[lv]<>": ",Length[IntLevelSelector[lv][NonReductionSectors]]],{lv,levelMin,levelMax}]
Print["\n","sectors: ",SortBy[LookupSectorID/@RequiredSectors,{#[[1]],-#[[2]]}&],"\n"];


(* Large loop over the levels, starting from levelMax and going to levelMin *)
Do[
	Print["\n"<>"Starting forward reduction in level "<>ToString[level]<>"!\n"];

	(* Mapping of NonReductionSector integrals to ReductionSectors to make sure we collect all integrals that are needed anywhere in the reduction *)
	Print["Mapping NonReductionSectors integrals (produced by higher level forward reduction)."];	  
	
	Print["Mapping in level ",level," for ", Length[IntLevelSelector[level][NonReductionSectors]]," sectors: ",LookupSectorID[#]&/@IntLevelSelector[level][NonReductionSectors]];
	If[level=!=levelMax,
		jobIDList={};
		tm1=AbsoluteTime[];
		jobAssociation=Association[];
		jobsOnQueue=jobsOnHoffman[];
		Print["# of jobs currently submitted to queue: ",jobsOnQueue];
		Do[ 
			(*waiting for some jobs to finish *)
			While[jobsOnQueue>495,Print["currently >495 jobs on Hoffman queue, wait 50sec."];Pause[50];jobsOnQueue=jobsOnHoffman[];];
			{id,secID}=LookupSectorID[sec];
			intsToMap=IntegralsInSector[sec];
			Put[intsToMap,intsToMapFile[id,secID]];
			Print["submit integral mapping job for sector ",sec," ",{id,secID}];
			AppendTo[jobIDList,jID=runMapIntegralsHoffman[id,secID]];
			AssociateTo[jobAssociation,jID->{id,secID}];
			jobsOnQueue++;
			(*mapIntegrals[sec]*)
		,{sec,IntLevelSelector[level][NonReductionSectors]}];
	
		(*waitForJobs[jobIDList];*)		
		Print["check ",jobIDList];
		successList={};  (* List of Hoffman jobIDs of successfully completed Mapping jobs *)
		deadList={};  (* List of Hoffman jobIDs of failed Mapping jobs *)
		jobsRunning=True;
		While[jobsRunning,
			runList=Select[Complement[jobIDList,deadList],jobRunningQ[#]&]; (* List of Hoffman jobIDs of running Mapping jobs *)
			jobsRunning=Or@@Table[jobRunningQ[jobID],{jobID,runList}];
			If[Length[runList]<=5,Print["jobs still running: ",runList];,Print[Length[runList]," jobs still running."];];
			checkList=Complement[jobIDList,Join[deadList,runList,successList]]; (* List of Hoffman jobIDs of completed Mapping jobs for which to check log-file*)
			Do[ 
				While[jobsOnQueue>495,Print["currently >495 jobs on Hoffman queue, wait 50sec."];Pause[50];jobsOnQueue=jobsOnHoffman[];];
				{id,secID}=jobAssociation[sec];
				If[{True,True}=!=mapIntegralslogFileCheck[id,secID],
					Print["mapIntegrals job did not complete properly! Check logfile "<>intsToMapLogFile[id,secID]];
					AppendTo[deadList,sec];
					Print["re-submit integral mapping job for sector ",{id,secID}];
					intsToMap=IntegralsInSector[sec];
					Put[intsToMap,intsToMapFile[id,secID]];
					Print["new job: ",newID=runMapIntegralsHoffmanHighMem[id,secID]];
					AppendTo[jobIDList,newID];
					AppendTo[runList,newID];
					AssociateTo[jobAssociation,newID->{id,secID}];
					jobsOnQueue++;
					,
					AppendTo[successList,sec];
				];
			,{sec,checkList}];
			
			ClearAll[runList];
			Pause[5];	
		];
		
		Print["dead mapIntegrals jobs that had to be restarted: ",deadList];
		Print["did all mapIntegrals jobs finish successfully? ",ContainsExactly[Complement[jobIDList,deadList],successList]];
		
		
		Print["loading mapped integrals from "<>ToString[Length[IntLevelSelector[level][NonReductionSectors]]]<>" NonReductionSectors and updating integral list in level "<>ToString[level]];
		rcc=0;
		Do[ If[Mod[rcc,10]==0,Print["progress report: ",rcc," of ",ToString[Length[IntLevelSelector[level][NonReductionSectors]]]," NonReductionSectors processed."]];
			{id,secID}=LookupSectorID[sec];
			intsToMap=Get[intsToMapFile[id,secID]];
			UpdateIntegralList[ModIntegrals[ListInts[intsToMap]]];
			rcc++;
			(*NOTE: at this point we could DeleteFile[intsToMapFile[id,secID]]; *)
		,{sec,IntLevelSelector[level][NonReductionSectors]}];
		tm2=AbsoluteTime[];  $MappingTime+=(tm2-tm1);
		If[$TimerDetails===True,Print["total mapping time in level "<>ToString[level]<>": ",niceTime[(tm2-tm1)]]];
	];
	
	ToRed[level]=Union[Flatten[IntegralsInSector/@IntLevelSelector[level][ReductionSectors]]];
	If[!ContainsAll[ReductionSectors,ListIntSectors[ToRed[level]]],
	   Print["Found integrals in non-reduction sectors! Bad sectors are: ", Complement[ListIntSectors[ToRed[level]],ReductionSectors]];];
	
	Print["exporting list of integrals in RequiredSectors between level ",levelMax," and level ",level];
	requiredInts[level]=Union[Flatten[Table[IntegralsInSector/@IntLevelSelector[lv][RequiredSectors],{lv,level,levelMax}]]];
	ExportIntegralsFIRE[requiredInts[level],"NameFunction"->(StringJoin["ints_required_"<>ToString[#]<>"_level_"<>ToString[level]<>".m"]&)];

	
	
	
	(* writes all integrals that are required for the reduction in a .tmp file (storageTempFile[id,secID]) to central storage *)
	Do[writeTrivialRules[sec],{sec,IntLevelSelector[level][RequiredSectors]}];



	
	(* FLAME run *)
	Print["\n\n","Integrals in families: ",ListIntFamilies[ToRed[level]]];
	Print["\n","run FLAME in level ",level," in ",Length[IntLevelSelector[level][ReductionSectors]]," ReductionSectors: ", LookupSectorID[#]&/@IntLevelSelector[level][ReductionSectors]];

	jobIDList={};
	jobAssociation=Association[];
	jobsOnQueue=jobsOnHoffman[];
	Print["# of jobs currently submitted to queue: ",jobsOnQueue];
	tf1=AbsoluteTime[];
		Do[
			While[jobsOnQueue>495,Print["currently >495 jobs on Hoffman queue, wait 50sec."];Pause[50];jobsOnQueue=jobsOnHoffman[];];
			{id,secID}=LookupSectorID[sec];
			Print["Running FLAME in sector ",sec," ",{id,secID}];
			AppendTo[jobIDList,jID=runFlameForwardHoffman[id,secID]];
			AssociateTo[jobAssociation,jID->{id,secID}];
			jobsOnQueue++;
		,{sec,IntLevelSelector[level][ReductionSectors]}];
	
		Print["waiting for ",Length[jobIDList]," Hoffman jobs to finish."];
		(*   waitForJobs[jobIDList];	*)
		Print["check ",jobIDList];
		
		successList={};  (* List of Hoffman jobIDs of successfully completed FLAME jobs *)
		deadList={};  (* List of Hoffman jobIDs of failed FLAME jobs *)
		jobsRunning=True;
		While[jobsRunning,
			runList=Select[Complement[jobIDList,deadList],jobRunningQ[#]&]; (* List of Hoffman jobIDs of running Mapping jobs *)
			jobsRunning=Or@@Table[jobRunningQ[jobID],{jobID,runList}];
			If[Length[runList]<=5,Print[runList];,Print[Length[runList]," jobs still running."];];
			checkList=Complement[jobIDList,Join[deadList,runList,successList]]; (* List of Hoffman jobIDs of completed Mapping jobs for which to check log-file*)
			Do[ 
				While[jobsOnQueue>495,Print["currently >495 jobs on Hoffman queue, wait 50sec."];Pause[50];jobsOnQueue=jobsOnHoffman[];];
				{id,secID}=jobAssociation[sec];
				If[{True,True}=!=FLAMEForwardlogFileCheck[id,secID],
				    Print["FLAME job did not complete properly! Check logfile "<>FLAMEForwardlogFile[id,secID]];
				    AppendTo[deadList,sec];
					$FLAMEHoffmanFlags="-l h_data=50G,h_rt=336:00:00,highp -pe shared 8";
					Print["increasing RAM and re-run FLAME: ",$FLAMEHoffmanFlags];
					Print["new job: ",newID=runFlameForwardHoffman[id,secID]];
					AppendTo[jobIDList,newID];
					AppendTo[runList,newID];
					AssociateTo[jobAssociation,newID->{id,secID}];
					jobsOnQueue++;
					,
					AppendTo[successList,sec];
				];
			,{sec,checkList}];
			
			ClearAll[runList];
			Pause[5];	
		];
		
		Print["dead FLAME jobs that had to be restarted: ",deadList];
		Print["did all FLAME jobs finish successfully? ",ContainsExactly[Complement[jobIDList,deadList],successList]];
		
		(*resetting $FLAMEHoffmanFlags to their default value *)
		$FLAMEHoffmanFlags=$FLAMEHoffmanFlagsDefault;
		
	tf2=AbsoluteTime[];   $FLAMETime+=(tf2-tf1);
	If[$TimerDetails===True,Print["flame time: ",niceTime[(tf2-tf1)]];];


    (*feed all one-daughter integrals that appear on the RHS of the ReductionSectors parent .tmp file after FLAME (forward) in the parent sector *)
	Print["feed information about lower level integrals to the lower sectors:"];
	Do[feedDaughterIntsToLowerSectors[sec],{sec,IntLevelSelector[level][ReductionSectors]}];	
				
,{level,Reverse[Range[levelMin,restartLevel]]}];


Print["\n","Copying storage files to storagePathSave[id], and rule files to rulePathSave[id]"]
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


Put[familySel,IntegralTools`$IntegralToolsFIREDirectory<>"/families.m"];


Print["
Done. \n
STATISTICS: \n
===================================\n"<>
"\n Total time: \t\t\t"<>niceTime[(AbsoluteTime[]-time)]<>
"\n\n FLAME time: \t\t\t"<>niceTime[$FLAMETime]<>
"\n\n total FTool time: \t\t"<>niceTime[$FToolTime]<>
"\n total FTool read time: \t"<>niceTime[$FToolReadTime]<>
"\n total FTool write time: \t"<>niceTime[$FToolWriteTime]<>
"\n\n Mapping time: \t\t\t"<>niceTime[$MappingTime]<>
"\n\n Transfer time: \t\t"<>niceTime[$TransferTime]<>
"\n\n IBP reading time: \t\t"<>niceTime[$IBPreadTime]
]
