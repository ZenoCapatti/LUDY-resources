(* ::Package:: *)

(* ::Chapter::Closed:: *)
(*basic paths and argument setting*)


Print[$CommandLine];
configFile=$CommandLine[[-3]];
id=ToExpression[$CommandLine[[-2]]];
secID=ToExpression[$CommandLine[[-1]]];


(* Load the config file *)
If[!FileExistsQ[configFile],
Print["Could not locate config file ",configFile,"."];
Quit[];,
Print["Loading config from: ",configFile,"."];
Get[configFile];
]


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


(* ::Chapter::Closed:: *)
(*Setup*)


{$FLAMETime,
$FToolTime,$FToolReadTime,$FToolWriteTime,
$MappingTime,
$TransferTime}={0,0,0,0,0,0};


Print["$ToolBoxPath: ",$ToolBoxPath]


(* loading utility packages and definitions *)
Get[FileNameJoin[{$ToolBoxPath,"mma",#}]]&/@{
"LorentzVectorUtils.wl",
"GraphTools.wl",
"IntegralTools.wl",
"TwoBodyKinematics.wl",
"Scripts/paths.m",
"Scripts/fire_functions.m"}


(* setting graph data *)
diagData=Get[$StdGraphsPath];


(* This has been obtained by studying FIRE's output. Not clear which logic the naming follows *)
sectorID=Get[$SectorIDPath];
LookupSectorID[sec_]:=Lookup[sectorID,sec];
secFromID[id_,secID_]:=Select[sectorID,#[[2]]=={id,secID}&][[1,1]];


(* loading masters in the unique sectors*)
UniqueSectorMaster=Get[$UniqueSectorMasterPath];
allMasters=Flatten[Values[UniqueSectorMaster]];


HashTable=Association[];
UpdateHashTable[integral_Int]:=AssociateTo[HashTable,(Hash[integral]->integral)]
UpdateHashTable[integralList_List]:=AssociateTo[HashTable,(Hash[#]->#)&/@integralList];

(* only masks integrals of the form Int[id,{a1,...,an}] and not tail masked Int[id,{a,b}] *)
MaskInts[expr_,{id_,sec_}]:=expr/.x_Int:>(UpdateHashTable[x];Int[id,{sec,Hash[x]}])/;Length[x[[2]]]>2;


(* generates all the daughter sectors of all sectors of the problem *)
parentDaughterRelations=(Table[MapAt[Int[diagData[[rs]]["ID"],#]&,GetPDRSectors[diagData[[rs]]["NonzeroSectors"]],{All,All}],{rs,1,Length[diagData]}]//Flatten);


(* ::Chapter:: *)
(*Running the 'transferDaughterInfo' command*)


sec=secFromID[id,secID];
Print[sec];


	Print["combining .tmp files to prepare FLAME backward run ",sec, " ",{id,secID}];
	tr1=AbsoluteTime[];
		tabParent=readDBFTool2[id,secID];
		daughterSectors=Select[parentDaughterRelations,#[[1]]==sec &][[;;,2]];
		Print["# of daughter sectors: ",Length[daughterSectors]];
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
		     requestInts=Get[dataForwardPath[id]<>"/daughter_requests/"<>ToString[secID]<>"_idDaughter_"<>ToString[idDaughter]<>"_sec_"<>ToString[secIDDaughter]<>".m"];
		     tabDaughter[secDaughter]=ReadFToolRequested[requestInts,ftoolTempFile[idDaughter,secIDDaughter]];
		,{secDaughter,daughterSectors}];
	tr2=AbsoluteTime[]; $FToolTime+=(tr2-tr1); $FToolReadTime+=(tr2-tr1);
	
	tt1=AbsoluteTime[]; (*adds to $TransferTime *)
		(* need to appropriately mask the tables for back-substitution *)
		r1=DeleteCases[ToExpression[tabParent],{}];
		ints1=DeleteCases[ListInts[r1[[;;,2]]],Int[i_Integer,{a_Integer,b_Integer}]];
		ints1=Complement[ints1,IntSectorSelector[sec][ints1]];
		r3=Association[Thread[Rule[ints1,MaskInts[ints1,{id,secID}]]]];
		r1Masked=r1/.r3 ;
		r1MaskedInts=MaskInts[ints1,{id,secID}];
		r2=Flatten[Table[ToExpression[tabDaughter[secDaughter]],{secDaughter,daughterSectors}],1];
	
		If[r2==={},r2Masked={},r2Masked=Map[MaskInts[#[[1]],{id,secID}]->MaskInts[#[[2]],{id,1}]&,r2]];
		If[r2==={},r2MaskedInts={},r2MaskedInts=r2Masked[[;;,1]]];
		
		If[{}===Complement[r1MaskedInts,r2MaskedInts],
			Print["all daughter integrals available!"]
			,
			Print["WARNING: NOT all daughter integrals available! ",Complement[r1MaskedInts,r2MaskedInts]]
		];
		
		tab=Join[r1Masked,r2Masked];
		tab=If[tab==={},{},MapAt[CollectInts,tab,{All,2}]];
		Put[RuleSum2List/@tab/.Int->G,ruleFile[id,secID]];
	tt2=AbsoluteTime[];   $TransferTime+=(tt2-tt1);
	
	tw1=AbsoluteTime[];
		writeTableToGlobalStorageFTool[id,secID];
		CopyFile[storageTempFile[id,secID],dbTempFile[id,secID],OverwriteTarget->True];
		(*Run["cp "<>storageTempFile[id,secID]<>" "<>dbTempFile[id,secID]];*)
	tw2=AbsoluteTime[];   $FToolTime+=(tw2-tw1);  $FToolWriteTime+=(tw2-tw1); 
	
	Put[HashTable,hashTabletransferDaughterFile[id,secID]];
	
	If[$TimerDetails===True,
		Print["ftool total time: ",niceTime[(tr2-tr1)+(tw2-tw1)]];
		Print["ftool read time: ",niceTime[(tr2-tr1)]];
		Print["ftool write time: ",niceTime[(tw2-tw1)]];
		Print["transfer time: ",niceTime[(tt2-tt1)]];
	];	
