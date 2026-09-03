(* ::Package:: *)

(* ::Chapter:: *)
(*local run*)


(* ::Section::Closed:: *)
(*FLAME functions*)


(* ::Subsection::Closed:: *)
(*FLAME forward-by-sector*)


runFlameForward[id_,secID_]:=Module[{tt},
Run@StringJoin[{
$FLAMEBinPath,
" -c ",
StringDelete[configPath[id],".config"],
" -s ",
ToString[secID],
" > ",
FLAMEForwardlogFile[id,secID]
}
];
]


(* ::Subsection::Closed:: *)
(*FLAME backward-by-sector*)


runFLAMEBackward[id_,secID_]:=Module[{tt},
Run@StringJoin[{
$FLAMEBinPath,
" -c ",
StringDelete[configPath[id],".config"],
" -s ",
"-"<>ToString[secID],
" > ",
FLAMEBackwardlogFile[id,secID]
}
];
]


(* ::Section:: *)
(*FTOOL functions*)


(* ::Subsection::Closed:: *)
(*Read table from db*)


readDBFTool[id_,secID_]:=Module[{tt},		
Run@StringJoin[$FToolBinPath,
			" -c ", 
			StringDelete[configPath[id],".config"],
			" -q -s ",
			ToString[secID],
			" -d ",
			(* central storage folder "Diag/storage/" *)
			dbPath[id],
			" > ",
			ftoolTempFile[id,secID]
		];
];		


readDBFTool2[id_,secID_]:=Module[{toRed},		
toRed=RunProcess[{AbsoluteFileName[$FToolBinPath],
			"-c",StringDelete[AbsoluteFileName[configPath[id]],".config"],
			"-q", 
			"-s",ToString[secID],
			"-d",AbsoluteFileName[dbPath[id]]
			}
		,"StandardOutput"];
StringReplace[toRed,{"-> ,"->"->0 ,","G"->"Int"}]
];


(* read only requested integrals out of a table *)
(* integrals in the intRequestsFile must be of the form {{id,{indices1}},{id,{indices2}}}*)
readDBFTool2[id_,secID_,intRequestsFile_]:=Module[{toRed},		
toRed=RunProcess[{AbsoluteFileName[$FToolBinPath],
			"-c",StringDelete[AbsoluteFileName[configPath[id]],".config"],
			"-q", 
			"-s",ToString[secID],
			"-d",AbsoluteFileName[storagePath[id]],
			"-I",AbsoluteFileName[intRequestsFile]
			}
		,"StandardOutput"];
StringReplace[toRed,{"-> ,"->"->0 ,","G"->"Int"}]
];


(* ::Subsection::Closed:: *)
(*Write table in global storage*)


writeTableToGlobalStorageFTool[id_,secID_]:=Module[{tt},
Run@StringJoin[$FToolBinPath,
		" -c ", 
		StringDelete[configPath[id],".config"],
		" -q -s ",
		ToString[secID],
		" -d ",
		(* central storage folder "Diag/storage/" *)
		storagePath[id],
		" --backward ",
		" < ",
		ruleFile[id,secID]
		];
]


(* ::Chapter:: *)
(*Hoffman run*)


(* ::Section:: *)
(*FLAME functions Hoffman*)


(* ::Subsection:: *)
(*FLAME forward-by-sector Hoffman*)


runFlameForwardSH[id_,secID_]:=WriteString[
	FLAMEForwardSHfile[id,secID],
	StringJoin[
	(*  "echo $TMPDIR >>/u/project/bern/eherrman/fire_mapping_git/examples/3PM_MapAndReduce_Hoffman/tmpdir.txt; ",
		"echo $JOB_ID >>/u/project/bern/eherrman/fire_mapping_git/examples/3PM_MapAndReduce_Hoffman/jobid.txt; ",   *)
		$FLAMEBinPath,
		" -c ",
		StringDelete[configPath[id],".config"],
		" -s ",
		ToString[secID]
	]
];


Options[runFlameForwardHoffman]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}

runFlameForwardHoffman[id_,secID_,OptionsPattern[]]:=Module[{jobID},
runFlameForwardSH[id,secID];
(*running command file*)
Run@StringJoin[
"qsub -V -cwd ",
OptionValue["extraFlags"],
" -N "<>"flame_"<>ToString[id]<>"_"<>ToString[secID],
" -o "<>FLAMEForwardlogFile[id,secID],
" ",
FLAMEForwardSHfile[id,secID],
" > ",
FLAMEForwardHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[FLAMEForwardHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Subsection::Closed:: *)
(*FLAME backward-by-sector Hoffman*)


runFlameBackwardSH[id_,secID_]:=WriteString[
FLAMEBackwardSHfile[id,secID],
	StringJoin[$FLAMEBinPath,
		" -c ",
		StringDelete[configPath[id],".config"],
		" -s ",
		"-"<>ToString[secID]
	]
];      


Options[runFlameBackwardHoffman]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}

runFlameBackwardHoffman[id_,secID_,OptionsPattern[]]:=Module[{jobID},
runFlameBackwardSH[id,secID];
(*running command file*)
Run@StringJoin[
"qsub -V ",
OptionValue["extraFlags"],
" -N "<>"flame"<>ToString[id]<>"_"<>ToString[secID],
" -o "<>FLAMEBackwardlogFile[id,secID],
" ",
FLAMEBackwardSHfile[id,secID],
" > ",
FLAMEBackwardHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[FLAMEBackwardHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Section::Closed:: *)
(*FTOOL functions Hoffman -- not utilized*)


(* ::Subsection::Closed:: *)
(*Read table from central storage Hoffman*)


readDBFToolSH[id_,secID_]:=WriteString[
FtoolReadSHfile[id,secID],
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


Options[readTableFToolHoffman]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}

readTableFToolHoffman[id_,secID_,OptionsPattern[]]:=Module[{jobID},
writeFtoolReadSH[id,secID];
Run@StringJoin[
"qsub -V ",
OptionValue["extraFlags"],
" -N "<>"ftool"<>ToString[id]<>"_"<>ToString[secID]<>" ",
"-o "<>FileNameJoin[{logFilePath[id],"ftool"~~"_"~~ToString[secID]~~".txt "}],
FtoolReadSHfile[id,secID],
" > ",
FtoolReadHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[FtoolReadHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Subsection::Closed:: *)
(*Write table in global storage Hoffman*)


writeTableToGlobalStorageFToolSH[id_,secID_]:=WriteString[
FtoolWriteSHfile[id,secID],
StringJoin[$FToolBinPath,
	" -c ", 
	StringDelete[configPath[id],".config"],
	" -q -s ",
	ToString[secID],
	" -d ",
	storagePath[id],
	" --backward ",
	" < ",
	ruleFile[id,secID]
]
];  


Options[writeTableToGlobalStorageFToolHoffman]={"extraFlags"->"-l h_data=1G,h_rt=1:00:00,highp -pe shared 1"}

writeTableToGlobalStorageFToolHoffman[id_,secID_,OptionsPattern[]]:=Module[{jobID},
writeTableToGlobalStorageFToolSH[id,secID];
Run@StringJoin[
	"qsub -V ",
	OptionValue["extraFlags"],
	" -N "<>"ftool"<>ToString[id]<>"_"<>ToString[secID]<>" ",
	"-o "<>FileNameJoin[{logFilePath[id],"ftool"~~"_"~~ToString[secID]~~".txt "}],
	FtoolWriteSHfile[id,secID],
	" > ",
	FtoolWriteHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[FtoolWriteHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Section:: *)
(*parallelization on Hoffman via qsub command files*)


(* ::Subsection::Closed:: *)
(*mapIntegrals in forward step with Mathematica code*)


runMapIntegralsHoffman[id_,secID_]:=Module[{jobID},

Run@StringJoin[
"qsub "<>$ToolBoxPath<>"/mma/Scripts/mapIntegrals.cmd",
" ",
intsToMapFile[id,secID],
" ",
ToString[$Shift],
" ",
$ToolBoxPath,
" ",
$RemapDataPath,
" ",
ruleMappingFile[id,secID],
" ",
intsToMapLogFile[id,secID],
" > ",
mapIntegralsHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[mapIntegralsHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(*for jobs that crashed, run with higher RAM in the .cmd file *)
runMapIntegralsHoffmanHighMem[id_,secID_]:=Module[{jobID},

Run@StringJoin[
"qsub "<>$ToolBoxPath<>"/mma/Scripts/mapIntegrals_highmem.cmd",
" ",
intsToMapFile[id,secID],
" ",
ToString[$Shift],
" ",
$ToolBoxPath,
" ",
$RemapDataPath,
" ",
ruleMappingFile[id,secID],
" ",
intsToMapLogFile[id,secID],
" > ",
mapIntegralsHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[mapIntegralsHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Subsection::Closed:: *)
(*transferDaughterInfo in backward step*)


transferDaughterInfoHoffman[id_,secID_,setupFilePath_]:=Module[{jobID},

Run@StringJoin[
"qsub "<>$ToolBoxPath<>"/mma/Scripts/transferDaughterInfo.cmd",
" ",
transferDaughterInfoLogFile[id,secID],
" ",
setupFilePath,
" ",
ToString[id],
" ",
ToString[secID],
" > ",
transferDaughterInfoHoffmanIDfile[id,secID]
];
jobID=StringSplit[StringSplit[Import[transferDaughterInfoHoffmanIDfile[id,secID],"String"],"\n"][[-1]]," "][[3]]
]


(* ::Section:: *)
(*Hoffman job status check*)


jobsOnHoffman[]:=((StringSplit[StringSplit[RunProcess[{"bash", "-c","qstat -u eherrman | grep eherrman | wc"},"StandardOutput"],"\n"]," "]//Union//ToExpression)/.Null:>Nothing)[[1,1]];
jobsRunningOnHoffman[]:=((StringSplit[StringSplit[RunProcess[{"bash", "-c","qstat -u eherrman | grep eherrman | grep r | wc"},"StandardOutput"],"\n"]," "]//Union//ToExpression)/.Null:>Nothing)[[1,1]];
jobsQueuedOnHoffman[]:=((StringSplit[StringSplit[RunProcess[{"bash", "-c","qstat -u eherrman | grep eherrman | grep qw | wc"},"StandardOutput"],"\n"]," "]//Union//ToExpression)/.Null:>Nothing)[[1,1]];


jobRunningQ[jobID_]:=!StringFreeQ[RunProcess[{"qstat","-j",jobID},"StandardOutput"],"=============================================================="]


(* tells you the Hoffman node where the job is running*)
jobHost[jobID_]:=StringDelete[RunProcess[{"bash", "-c","qstat -j "<>ToString[jobID]<>" | grep exec_host_list"},"StandardOutput"],"\t"|" "]
jobResources[jobID_]:=StringDelete[RunProcess[{"bash", "-c","qstat -j "<>ToString[jobID]<>" | grep usage"},"StandardOutput"],"\t"|" "]


waitForJobs[jobIDList_]:=Module[{jobsRunning=True,runList},
	Print["check ",jobIDList];
	(*
	Print["job hosts: "];
	Print[#->jobHost[#]]&/@jobIDList;
	*)
	While[jobsRunning,
		runList=Select[jobIDList,jobRunningQ[#]&];
		(*
		Print["resources used: "];
		Print[#\[Rule]jobResources[#]]&/@runList;
		*)
		Print["jobs still running: ",runList];
		jobsRunning=Or@@Table[jobRunningQ[jobID],{jobID,runList}];
		ClearAll[runList];
		Pause[5];	
	];
]	


(* ::Chapter::Closed:: *)
(*Safety LogFile checks*)


FLAMEForwardlogFileCheck[id_,secID_]:=Block[{tmpString,out1,out2},
	out1=FileExistsQ[AbsoluteFileName[FLAMEForwardlogFile[id,secID]]];
	tmpString=RunProcess[{"bash","-c","tail -n 1 "<>AbsoluteFileName[FLAMEForwardlogFile[id,secID]]},"StandardOutput"];
	(*Print[tmpString];*)
	out2=StringContainsQ[tmpString,"FLAME time"];
	Return[{out1,out2}]
]


mapIntegralslogFileCheck[id_,secID_]:=Block[{tmpString,out1,out2},
	out1=FileExistsQ[AbsoluteFileName[intsToMapLogFile[id,secID]]];
	tmpString=RunProcess[{"bash","-c","tail -n 7 "<>AbsoluteFileName[intsToMapLogFile[id,secID]]},"StandardOutput"];
	(*Print[tmpString];*)
	out2=StringContainsQ[tmpString,"done mapping all integrals"];
	Return[{out1,out2}]
]


(* ::Chapter::Closed:: *)
(*Functionality for FORWARD/BACKWARD reduction runs with FLAME*)


niceTime[mmaTime_]:=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[mmaTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]


(*currently this function still reads integrals on the LHS and RHS of the table *)
IntsFromFToolString[string_,probSize_]:=Module[{toret},
	toret=StringCases[string,StringExpression@@Join[{"Int[",NumberString,",{"},Riffle[Table[NumberString,probSize],","],{"}]"}]];
	Return[ToExpression[toret]];
]


(* expresses integrals in a mapping sector in terms of integrals in Unique Sectors *)
mapIntegrals[sec_]:=Block[{intsToMap,tm1,tm2,rhs},
	{id,secID}=LookupSectorID[sec];
	tm1=AbsoluteTime[];
		intsToMap=IntegralsInSector[sec];
		Print["Mapping "<>ToString[Length[intsToMap]]<>" integrals in sector ",sec, " ", {id,secID}];
		rhs=CollectInts[MapIntegrals[intsToMap]];
		If[Head[rhs]===IntegralsInSector,Continue[];];
		mapRule[sec]=Thread[intsToMap->rhs];
		Put[mapRule[sec],ruleMappingFile[id,secID]];
	
		(*update integral list from non-reduction sectors *)
		UpdateIntegralList[ModIntegrals[ListInts[rhs]]];
	tm2=AbsoluteTime[];  $MappingTime+=(tm2-tm1);
	
	If[$TimerDetails===True,
		Print["mapping time: ",niceTime[(tm2-tm1)]]
	];
]


writeTrivialRules[sec_]:=Block[{tt1,tt2,tw1,tw2},	
	{id,secID}=LookupSectorID[sec];
	tt1=AbsoluteTime[];
		If[!DirectoryQ[dbPath[id]],CreateDirectory[dbPath[id]]];
		Print["writing trivial rules in ",{id,secID}];
		map=MapThread[Rule,{IntegralsInSector[sec],IntegralsInSector[sec]}];
		(*in order for FLAME to understand the #master option, we need to mask the desired masters *)
		map=map/.Rule[a_,b_]:>Rule[a,MaskInts[b,{id,1}]]/;MemberQ[allMasters,b];
		Put[RuleSum2List/@map/.Int->G,ruleFile[id,secID]];
	tt2=AbsoluteTime[];   $TransferTime+=(tt2-tt1);
	
	(* writes a storageTempFile[id,secID] .tmp file into the central storage path  *)
	tw1=AbsoluteTime[];
		writeTableToGlobalStorageFTool[id,secID];
		CopyFile[storageTempFile[id,secID],dbTempFile[id,secID],OverwriteTarget->True];
		(*Run["cp "<>storageTempFile[id,secID]<>" "<>dbTempFile[id,secID]];*)
	tw2=AbsoluteTime[];	$FToolTime+=(tw2-tw1);   $FToolWriteTime+=(tw2-tw1);
	
	If[$TimerDetails===True,
		Print["ftool write time: ",niceTime[(tw2-tw1)]];
		Print["transfer time: ",niceTime[(tt2-tt1)]];
	];
]	


(* relevant in the forward reduction, after FLAME has run in a ReductionSector, it looks on the r.h.s. of the table to see which lower level integrals appear *)
feedDaughterIntsToLowerSectors[sec_]:=Block[{idParent,secIDParent,tab,intsInTab,daughterSectors,idDaughter,secIDDaughter,probSize,newInts,comp,tr1,tr2,tt1,tt2},
	{idParent,secIDParent}=LookupSectorID[sec];
	probSize=Length[sec[[2]]];
	Print["\n","Loading parent sector ",sec, " ",{idParent,secIDParent}];
	daughterSectors=Select[parentDaughterRelations,#[[1]]==sec &][[;;,2]];
	(*Print["daugther sectors of sec ",sec, " : ",daughterSectors];*)
	comp=Complement[daughterSectors,RequiredSectors];
	If[comp==={},Print["all daughter sectors are in RequiredSectors"],Print["some daughter sectors are NOT in RequiredSectors! ",comp]];
	
	tr1=AbsoluteTime[];
		(* reading parent .tmp file from global db folder *)
		tab=readDBFTool2[idParent,secIDParent];
		intsInTab=IntsFromFToolString[tab,probSize];
		intsInTab=DeleteCases[ListInts[intsInTab],Int[i_Integer,{a_,b_}]]; (*only keep non-dummy integrals in the list*)
		Print["number of integrals in parent sector ",{idParent,secIDParent}," table: ",Length[intsInTab]];
	tr2=AbsoluteTime[];  $FToolTime+=(tr2-tr1); $FToolReadTime+=(tr2-tr1);
	
	tt1=AbsoluteTime[];
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
			newInts=IntSectorSelector[secDaughter][intsInTab];
			(*Print["new integrals in daugther sector: ",{idDaughter,secIDDaughter},": ",newInts];*)
			Print["passing "<>ToString[Length[newInts]]<>" integrals to daughter sector ",secDaughter," ",{idDaughter,secIDDaughter}];
			Put[newInts/.Int:>List,dataForwardPath[idParent]<>"/daughter_requests/"<>ToString[secIDParent]<>"_idDaughter_"<>ToString[idDaughter]<>"_sec_"<>ToString[secIDDaughter]<>".m"];
			UpdateIntegralList[newInts];
		,{secDaughter,daughterSectors}];
	tt2=AbsoluteTime[];    $TransferTime+=(tt2-tt1);
	
	If[$TimerDetails===True,
		Print["ftool read time: ",niceTime[(tr2-tr1)]];
		Print["transfer time: ",niceTime[(tt2-tt1)]];
	];
]


ReadFToolRequested[requestedInts_,filename_]:=Module[{stream,int,rhs,rules},
If[!FileExistsQ[filename],Print["requested int file does not exist"];Return[{}]];
stream=OpenRead[filename];
rules={};
ReadString[stream,"Int"];
While[True,
	int=ReadString[stream,"->"];
	If[(int===EndOfFile),Break[]];
	int=StringDelete[int,{"\n"," "}];
	If[(StringTake[int,3]=!="Int"),Break[]];
	int=ToExpression[int];
	rhs=ReadString[stream,"\n"];
	If[(rhs===EndOfFile)||(rhs==="{}} "),Break[]];
	rhs=StringDrop[rhs,-1];
	If[MemberQ[requestedInts,int],
		AppendTo[rules,ToString[int]<>rhs];
	];
];
Close[stream];
If[Length[rules]=!=Length[requestedInts],Print["WARNING, some integrals not found in table"]];
Return[rules];
]


(* writes the IBP tables of the daughter sectors of a given parent ReductionSector 'sec' into the .tmp file *)
transferDaughterInfo[sec_]:=Block[{tr1,tr2,tt1,tt2,tw1,tw2},
	{id,secID}=LookupSectorID[sec];
	Print["combining .tmp files to prepare FLAME backward run ",sec, " ",{id,secID}];
	tr1=AbsoluteTime[]; (*adds to $FToolTime *)
		tabParent=readDBFTool2[id,secID];
		daughterSectors=Select[parentDaughterRelations,#[[1]]==sec &][[;;,2]];
		Do[ {idDaughter,secIDDaughter}=LookupSectorID[secDaughter];
		     requestIntsFile=dataForwardPath[id]<>"/daughter_requests/"<>ToString[secID]<>"_idDaughter_"<>ToString[idDaughter]<>"_sec_"<>ToString[secIDDaughter]<>".m";
		     (*
		     requestInts=Get[requestIntsFile];
		     requestInts=Int@@@requestInts;
		     tabDaughter[secDaughter]=ReadFToolRequested[requestInts,ftoolTempFile[idDaughter,secIDDaughter]];
		     *)
		     tabDaughter[secDaughter]=readDBFTool2[idDaughter,secIDDaughter,requestIntsFile];
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
		r2=Flatten[Table[DeleteCases[ToExpression[tabDaughter[secDaughter],{}]],{secDaughter,daughterSectors}],1];
	
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
	
	If[$TimerDetails===True,
		Print["ftool total time: ",niceTime[(tr2-tr1)+(tw2-tw1)]];
		Print["ftool read time: ",niceTime[(tr2-tr1)]];
		Print["ftool write time: ",niceTime[(tw2-tw1)]];
		Print["transfer time: ",niceTime[(tt2-tt1)]];
	];	
]


readIBPTable[sec_]:=Block[{tr1,tr2,ti1,ti2},
	{id,secID}=LookupSectorID[sec];
	tr1=AbsoluteTime[];
		table=readDBFTool2[id,secID];
	tr2=AbsoluteTime[];    $FToolTime+=(tr2-tr1);   $FToolReadTime+=(tr2-tr1);
	
	ti1=AbsoluteTime[];
		table=DeleteCases[ToExpression[table],{}];
		IBPTable[sec]=UnmaskMasters[table];
		If[IBPTable[sec]=={},masters[sec]={},
			IBPTable[sec]=MapAt[#/.MasterIdentificationList&,IBPTable[sec],{All,2}];
			masters[sec]=IntSectorSelector[sec][ListInts[IBPTable[sec][[;;,2]]]];
		];
	
		(* check that the masters are as expected *)
		If[!ContainsExactly[masters[sec],UniqueSectorMaster[sec]],
			Print["Masters not aligned in sector ", sec," ",{id,secID},", e.g. ",Complement[masters[sec],UniqueSectorMaster[sec]][[1]] ];
		];
	
		IBPTable[sec]=Join[IBPTable[sec],Thread[masters[sec]->masters[sec]]];
		MasterMap[sec]=Quiet@MasterIdentification[sec,masters[sec]];
	
		(* generate identification rules for all equivalent sectors *)
		MasterIdentificationList=Join[MasterIdentificationList,MasterMap[sec]];
	ti2=AbsoluteTime[];    $IBPreadTime+=(ti2-ti1);
	If[$TimerDetails===True,
	  Print["IBP processing time: ",niceTime[ti2-ti1]];
	  Print["ftool read time: ",niceTime[(tr2-tr1)]];
	];
]


mappingRules[sec_]:=Block[{tt1,tt2,tw1,tw2},
	tt1=AbsoluteTime[];
		{id,secID}=LookupSectorID[sec];
		r1=Get[ruleMappingFile[id,secID]];
		intsRequested=If[r1==={},{},ListInts[r1[[;;,2]]]];
		(* for all sectors on the RHS get the corresponding IBP table *)
		r2=If[r1==={},{},Flatten[LookupIBPTable/@ListIntSectors[r1[[;;,2]]]]];
		r2=Select[r2,MemberQ[intsRequested,#[[1]]]&];

		r1Masked=If[r1==={},{},MapAt[MaskInts[#,{id,secID}]&,r1,{All,2}]];
		r2Masked=If[r2==={},{},Map[MaskInts[#[[1]],{id,secID}]->MaskInts[#[[2]],{id,1}]&,r2]];
	
		maskedRules=Join[r1Masked,r2Masked]//Union;
		maskedRules=If[maskedRules==={},{},MapAt[CollectInts,maskedRules,{All,2}]];
		Put[RuleSum2List/@maskedRules/.Int->G,ruleFile[id,secID]];
	tt2=AbsoluteTime[];   $TransferTime+=(tt2-tt1);
	
	Print["Writing masked mapping rules in sector ",sec, " ",{id,secID}];
	tw1=AbsoluteTime[];
		writeTableToGlobalStorageFTool[id,secID];
		Run["cp "<>storageTempFile[id,secID]<>" "<>dbTempFile[id,secID]];
	tw2=AbsoluteTime[];	$FToolTime+=(tf2-tf1);
	If[$TimerDetails===True,
		Print["ftool write time: ",niceTime[(tw2-tw1)]];
		Print["transferring IBP rels. time: ",niceTime[(tt2-tt1)]];
	];
]


LookupIBPTable[sec:Int[id_,inds_]]/;id<=$Shift:=IBPTable[sec];
(*IBP table for integrals with indices beyond $Shift have to be crossed appropriately *)
LookupIBPTable[sec:Int[id_,inds_]]/;id>$Shift:=LookupIBPTable[sec]=Module[{modint,theShift=getShift[id],yFlip,table},
	ti1=AbsoluteTime[];
		yFlip=(1===PadLeft[IntegerDigits[theShift,2],3][[3]]);
		modint=ModIntegrals[sec];
		table=IBPTable[modint];
		table=UnmaskMasters[table];
		If[yFlip,table=table/.y->-y];
		table=table/.Int[i_,in_]:>Int[modID[i]+$Shift*SoftMapConcatination[getShift[i],theShift],in];
		table=MapAt[MapIntegrals[#]/.MasterIdentificationList&,table,{All,2}];
	ti2=AbsoluteTime[];
	$IBPlookupTime+=(ti2-ti1);
	If[$TimerDetails===True,
		Print["LookupIBPTable time: ",niceTime[(tf2-tf1)]];
	];	
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
