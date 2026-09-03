(* ::Package:: *)

BeginPackage["IntegralTools`"];


CreateTempDirectories; ClearTempDirectories;


IntsToRandom;


InitializeTopology::usage = "Set up a family of integrals";
IntegralFamilyQ;
AddIntegralFamily;
RemoveIntegralFamily;
ToProps::usage = "ToProps[id] gives a rule from scalar products to propagators of topology id if defined.";
Props::usage = "ToProps[id] gives the propagators of topology id if they have been defined.";
nProps;
TopoData;
AssociatedGraph;
$IntegralFamilies;


GraphForInt::usage = "Gives a graph for the integral.";
DisplayInt::usage = "Shows a picture of the integral, if possible."
DisplayInt2;
DisplayIntPM;
ClearDisplayInt;


ListInts::usage = "Lists all integrals in the given expression.";
CountInts::usage = "Counts number of distinct integrals in the given expression."
ListIntsAndCoefficients;
CollectInts;
IntFamily;
ListIntFamilies::usage = "Lists all integral families in the given expression."
IntFamilySelector;
IntSector;
ListIntSectors;
IntSectorSelector::usage ="Select all integrals that are in the given sector specified through Int[id,inds], where inds is a list of 1 and 0's.";
IntIndices;
IntDenominator;
IntNumerator;
IntLevel;
ListIntLevels;
IntLevelSelector;
rCnt::usage = "Total denominator power";
IntCountDenom;
sCnt::usage = "Tensor rank";
IntCountNumer;
dCnt::usage = "Total number of dots";
IntCountDots;
IntComplexity;
RSDmax::usage = "Maximal values of r,s,d in a given list of indices.";
IntRSDmax;
SortIntsByLevel;


IndicesToString;IntToString;


SubSectorQ;
GetSubsectors;
SubSectorsByCriterion;
SubSectorsByRESTRICTIONS;
GetSpanningSectors;
GetPDRSectors;
GetMaximalSectors;


GenerateSeedIntegrals::usage = "GenerateSeedIntegrals[sector,n] generates a list of tensors of up to rank n in the given sector.";
GenerateSeedIntegralsWithDots::usage = "GenerateSeedIntegrals[sector,c] generates a list of integrals with tensors and dots up to complexity c in the given sector.";


GetUF::usage= "GetUF[internal,external,propagator,replacements]";


IntToProps;
IntToPropsExplicit;
ToFIREG4;
ToFIREG5;
ToFIREGFORM;
ExpandLeadingPropagators::usage = "ExpandLeadingPropagators[props,scaling,cnt] expand props to leading order in cnt under scaling."


SectorToBinary;
BinaryToSector;
ConvertNotation;
ToIntNotation;
ToFIRENotation;


ApplyCuts;
ApplyRestrictions;
RuleFromCut;
RESTRICTIONSFromCut;


SetRemapData;
SetCut;
MapSingleIntegral;
MapIntegralsStep;
MapIntegrals;
MapIntegralsStepCut;
MapIntegralsCut;
MapIntegralsCutStep;
$RemapData;
AutomorphismOrbit;
SetAutoData;
$AutoData;
$AllSectors; $RepresentativeSectors; $MappedSectors;


FIREInputString; 
PrepareFIRE;
PrepareFIREFromInput;
RunFIRE;
RunFIRE2;
FIREConfigString;
ExportIntegralsFIRE;
ListFIREReduced
LoadFIRETable;
ListFIREMasters;
KillDenominatorFIRE;
TableContainsIntegralsQ;
ReadFToolOutput;
RuleFromRESTRICTIONS;
SelectByRESTRICTIONS;
ZeroOnRESTRICTIONSQ;
LoadFIRETableByIntegral::usage="LoadTableFIREByIntegral[filename,integralList] where integralList is of the form {id,{...}}."
GetFIREKeys;
LoadTableFIREKey;
GetFIREKeyTable;
RuleSum2List::usage="Converts a replacement rule to a the input format used by FIRE. G[...]-> {...}";
SubRESTRICTIONQ;
GetSpanningRESTRICTIONS;
RESTRICTIONSAnd;
RESTRICTIONSOr;


ImportKiraIntegrals;
KiraIBPString;
KiraIntegralfamiliesString;
KiraKinematicsString;
PrepareKira;
KiraJobString;
ExportIntegralsKira;


ToIndexShift;
ProduceSingleIBP; GetIBP; GetIBPNoD;
ProduceSingleLI; GetLI;


(* heads *)
$IntHead=Global`Int;
$propHead=Global`propagator;
$FIREIntHead=Global`G;


pySecDecGenerateString;pySecDecIntegrateString;


(* baths to binaries *)


$IntegralToolsBaseDirectory;
$IntegralToolsTempDirectory;
$IntegralToolsKiraDirectory;
$IntegralToolsFIREDirectory;
$IntegralToolsPySecDecDirectory;


$MathKernelPath;


Begin["Private`"]


(* ::Section::Closed:: *)
(*File paths and temp files *)


Do[
If[!FileExistsQ[ReleaseHold[bin]],
Print["Could not locate file ",bin]],
{bin,{HoldForm[Global`$FIREMathPath],HoldForm[Global`$FIREBinPath]}}
]


If[!ValueQ[$MathKernelPath],$MathKernelPath=First@FileNames[FileNameJoin[{$InstallationDirectory, "*/MathKernel"}]]]


If[!ValueQ[$IntegralToolsBaseDirectory],
$IntegralToolsBaseDirectory=Switch[True,
(* .nb *)
$Notebooks,NotebookDirectory[], 
(* .wls *)
Length[$ScriptCommandLine]>0,FileNameDrop[ExpandFileName[First[$ScriptCommandLine]],-1]~~"/",
(* .m *)
Length[$CommandLine]>0, DirectoryName @ $InputFileName,
True,Print["Could not locate script directory"]
];
];


$IntegralToolsTempDirectory=FileNameJoin[{$IntegralToolsBaseDirectory,"temp"}];
$IntegralToolsKiraDirectory=FileNameJoin[{$IntegralToolsTempDirectory,"kira"}];
$IntegralToolsFIREDirectory=FileNameJoin[{$IntegralToolsTempDirectory,"FIRE"}];
$IntegralToolsPySecDecDirectory=FileNameJoin[{$IntegralToolsTempDirectory,"pySecDec"}];


CreateTempDirectories[]:=
Do[Quiet[CreateDirectory[dir],{CreateDirectory::eexist}],
{dir,{$IntegralToolsTempDirectory,$IntegralToolsKiraDirectory,$IntegralToolsFIREDirectory,$IntegralToolsPySecDecDirectory}}];


ClearTempDirectories[]:=Do[
Quiet[DeleteDirectory[dir,DeleteContents->True],DeleteDirectory::"nodir"];
,{dir,{$IntegralToolsTempDirectory,$IntegralToolsKiraDirectory,$IntegralToolsFIREDirectory,$IntegralToolsPySecDecDirectory}}]


(* ::Section:: *)
(*Misc*)


Options[IntsToRandom]={"PrimeRange"->100000}
IntsToRandom[expr_,OptionsPattern[]]:=Module[{ints=ListInts[expr]},
Return[expr/.Association[Thread[ints->Table[RandomPrime[OptionValue["PrimeRange"]],Length[ints]]]]];
]


(* ::Section:: *)
(*Topology setup*)


If[!ValueQ[$IntegralFamilies],
$IntegralFamilies={};
Protect[$IntegralFamilies];
];


Options[InitializeTopology]={
	"ID"-> 0,
	"Name"-> "default",
	"FIREProblemID"-> None,
	"LoopMom"-> {Global`k},
	"Internal"->Nothing,
	"External"->Nothing,
	"Replacements"->{},
	"RESTRICTIONS"->{},
	"TopSector"->None,
	"CreateSectorData"->False,
	"CreateTempDirectories"->False,
	"Graph"-> None,
	"Verbose"-> False,
	"PrepareFIRE"->False,
	"ComputeUF"->False,
	"RegLine"->None,
	"NonzeroSectors"->None,
	"Derivatives"->False,
	"FIREPrepareOptions"->{Global`AutoDetectRestrictions->True,Global`LI->True,Global`Parallel->True}
};
InitializeTopology[props_,OptionsPattern[]]:=Module[{id=OptionValue["ID"],int,allVectors,loopVectors,MaskLV,extVectors,extVar,variables,dotVars,reps,restrictions,
externalIP,rr,c,IPReplacements,ExternalGram,ExternalGramInv,indep,Jac,dRules},

(* add to list of integrals *)
AddIntegralFamily[id];

Props[id]=props;
nProps[id]=Length[props];

(* ********************************
TopoData[id] is a container of all the information
******************************** *)
TopoData[id]=Association["ID"->OptionValue["ID"]];

AssociateTo[TopoData[id],"Propagators"->props];

Switch[
{OptionValue["Internal"]===Nothing,OptionValue["External"]===Nothing},
(* everything *)
{False,False},
allVectors=Join[OptionValue["Internal"],OptionValue["External"]];
loopVectors=OptionValue["Internal"];
extVectors=OptionValue["External"];
,
(* external momenta *)
{True,False},
allVectors=Cases[props,_LorentzVectorUtils`IP,Infinity]/.LorentzVectorUtils`IP-> Sequence//Union;
loopVectors=Complement[allVectors,OptionValue["External"]];
extVectors=OptionValue["External"];
,
(* loop momenta *)
{False,True},
allVectors=Cases[props,_LorentzVectorUtils`IP,Infinity]/.LorentzVectorUtils`IP-> Sequence//Union;
loopVectors=OptionValue["Internal"];
extVectors=Complement[allVectors,loopVectors];
,
(* nothing *)
{True,True},
allVectors=Cases[props,_LorentzVectorUtils`IP,Infinity]/.LorentzVectorUtils`IP-> Sequence//Union;
loopVectors=Select[allVectors,!FreeQ[#,Alternatives@@OptionValue["LoopMom"]]&];
extVectors=Complement[allVectors,loopVectors];
];
If[OptionValue["Verbose"],
Print[Length[allVectors]," vectors: ",allVectors];
Print[Length[loopVectors]," loop vectors: ",loopVectors];
];

If[ValueQ[loopVectors],TopoData[id]=Association[TopoData[id],"Internal"->loopVectors]];
If[ValueQ[extVectors],TopoData[id]=Association[TopoData[id],"External"->extVectors]];


(*********************************
 The RESTRICTIONS as used by FIRE and also as an option to specify non-zero sectors. 
******************************** *)

restrictions=OptionValue["RESTRICTIONS"];

(*********************************
 Option to add a heavy line. That is a line that cannot be pinched.
******************************** *)

If[OptionValue["RegLine"]=!=None,
(* Remove RESTRICTIONS related to the 'heavy' lines as these can never be removed. *)
	restrictions=Select[restrictions,!MemberQ[#[[OptionValue["RegLine"][[;;,1]]]],-1]&];
];
AssociateTo[TopoData[id],"RESTRICTIONS"->restrictions];

(* ********************************
 Simple options that are just passed on
 ******************************** *)
Do[
If[ValueQ[OptionValue[opt]],AssociateTo[TopoData[id],opt->OptionValue[opt]]]
,{opt,{"Name","Replacements","RegLine"}}];

(*
	Top sector. This is used for determining the non-zero sectors
*)
Switch[OptionValue["TopSector"],
	{Repeated[0|1]},AssociateTo[TopoData[id],"TopSector"->OptionValue["TopSector"]],
	_Integer,AssociateTo[TopoData[id],"TopSector"->PadRight[Table[1,OptionValue["TopSector"]],nProps[id]]],
	None,AssociateTo[TopoData[id],"TopSector"->None]
];

(* ********************************
	FIRE ID
******************************** *)
If[OptionValue["FIREProblemID"]=!=None,
	AssociateTo[TopoData[id],"FIREProblemID"->OptionValue["FIREProblemID"]],
	AssociateTo[TopoData[id],"FIREProblemID"->OptionValue["ID"]]
];

(* ********************************
 Generate list of non-zero sectors 
 ******************************** *)

If[OptionValue["CreateSectorData"]&&OptionValue["NonzeroSectors"]===None,
(* non-zero sectors. Works best if the top-sector is given explicitely *)
AssociateTo[TopoData[id],"NonzeroSectors"->
	Switch[OptionValue["TopSector"],
	None,SubSectorsByRESTRICTIONS[Table[1,nProps[id]],restrictions],
	{Repeated[0|1]},SubSectorsByRESTRICTIONS[OptionValue["TopSector"],restrictions]]
	];
	
(* Spanning sectors/cuts *)
AssociateTo[TopoData[id],"SpanningSectors"->GetSpanningSectors[TopoData[id]["NonzeroSectors"]]];
];

If[OptionValue["NonzeroSectors"]=!=None,AssociateTo[TopoData[id],"NonzeroSectors"->OptionValue["NonzeroSectors"]]];

AssociateTo[TopoData[id],"RestrictionRule"->RuleFromRESTRICTIONS[restrictions,"ID"->id]];

(* ********************************
 Determine variables in the problem 
 ******************************** *)

extVar=Union[Flatten[Outer[LorentzVectorUtils`IP,extVectors,extVectors]]];

(*variables=Variables[extVar/.TopoData[id]["Replacements"]];*)
variables=Select[Variables[{props,extVar}/.TopoData[id]["Replacements"]],FreeQ[#,Alternatives@@TopoData[id]["Internal"]]&];
(* if we add non-integer propagators the associated parameters will be treated as variables in the problem *)
If[OptionValue["RegLine"]=!=None,
	variables = Join[variables,DeleteCases[Variables[OptionValue["RegLine"][[;;,2]]],Global`d]];
];

AssociateTo[TopoData[id],"Variables"->variables];

MaskLV[expr_]:=expr/.LorentzVectorUtils`IP[a_,b_]:>ToExpression["ip"~~ToString[a/.f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]]]~~ToString[b/.f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]]]];

dotVars=LorentzVectorUtils`ListIPs[variables];
If[Length[dotVars]>0,
	reps=(#->MaskLV[#])&/@dotVars;
	If[OptionValue["Verbose"],Print["Warning: unspecified dot products. Masking them as ",reps]];
	AssociateTo[TopoData[id],"VariableMask"->reps];
	AssociateTo[TopoData[id],"MaskedVariables"->Variables[variables/.reps]];
	,
	AssociateTo[TopoData[id],"VariableMask"->{}];
	AssociateTo[TopoData[id],"MaskedVariables"->variables];	
];
AssociateTo[TopoData[id],"Replacements"->Table[dp->(dp/.TopoData[id]["Replacements"]),{dp,extVar}]];

AssociateTo[TopoData[id],"ReplacementsMasked"->Table[dp->(dp/.TopoData[id]["Replacements"]/.TopoData[id]["VariableMask"]),{dp,extVar}]];


(* ********************************
	Determine independent dot product variables.
******************************** *)

If[TopoData[id]["MaskedVariables"]=!={},
	(* Compute the jacobian of the variable transformation IP->variables. *)
	externalIP=Union[Flatten[Outer[LorentzVectorUtils`IP,TopoData[id]["External"],TopoData[id]["External"]]]];
	Jac=D[externalIP/.TopoData[id]["ReplacementsMasked"],{TopoData[id]["MaskedVariables"]}];
	(* Jacobian will in general not have full rank, because the IP's are linearly dependent. We proceed by picking a independent set *)
	indep=Extract[externalIP,FirstPosition[#,1,Nothing]&/@RowReduce[Transpose[Jac]]];
	AssociateTo[TopoData[id],"IndependentIP"->indep];,
	AssociateTo[TopoData[id],"IndependentIP"->{}]
];


(* ********************************
	variables to as dot products
******************************** *)

AssociateTo[TopoData[id],"VariablesToIP"->First@Solve[#==(#/.TopoData[id]["ReplacementsMasked"])&/@TopoData[id]["IndependentIP"],TopoData[id]["MaskedVariables"]]];

(* ********************************
	Compute U and F polynomials
******************************** *)
If[OptionValue["ComputeUF"],
	AssociateTo[TopoData[id],"UFPoly"->GetUF[loopVectors,extVectors,props,OptionValue["ReplacementsMasked"]]];
];

(* ********************************
	Temp directories for FIRE and kira
******************************** *)

If[OptionValue["CreateTempDirectories"],
	Quiet[CreateDirectory[FileNameJoin[{$IntegralToolsFIREDirectory,OptionValue["Name"]}]],{CreateDirectory::eexist}];
];

(* ********************************
	Prepare various things for IBP codes 
******************************** *)


If[OptionValue["PrepareFIRE"]===True,
	PrepareFIRE[id,"FIREPrepareOptions"->OptionValue["FIREPrepareOptions"]]
];

If[OptionValue["PrepareFIRE"]==="FilesOnly",
	PrepareFIRE[id,"Prepare"->False,"FIREPrepareOptions"->OptionValue["FIREPrepareOptions"]]
];

(* ********************************
	Add a graph. Eventually we might want the option to generate a graph, this is a bit more involved, especially with linear propagators 
******************************** *)
If[OptionValue["Graph"]=!=None,
	AssociatedGraph[id]=OptionValue["Graph"];
	AssociateTo[TopoData[id],"Graph"->OptionValue["Graph"]];
];

ToProps[id]=LorentzVectorUtils`ReplacementRulesFromPropagators[props,
	"Internal"->loopVectors,
	"External"->extVectors,
	"Verbose"-> OptionValue["Verbose"],
	"Head"->$propHead[id]
];


If[!ValueQ[TopoData[id]["Replacements"]],
	AssociateTo[TopoData[id],"Replacements"->{}];
];

If[ValueQ[TopoData[id]["Replacements"]],
	ToProps[id]=ToProps[id]/.TopoData[id]["Replacements"];
];

(* ********************************
	Derivative rules. There might be some closed formula in terms of Gram determinants, but keeping the constraints in place seems non-trivial. So we just ansatz here
******************************** *)

If[OptionValue["Derivatives"],
	Module[{OperatorAnsatz,dOPRulesVar,tosol,\[Beta],sol\[Beta],free\[Beta]},
	OperatorAnsatz[expr_]:=Sum[\[Beta][i,j]*LorentzVectorUtils`vdv[TopoData[id]["External"][[i]],TopoData[id]["External"][[j]]][expr],{i,Length@TopoData[id]["External"]},{j,Length@TopoData[id]["External"]}];
	dOPRulesVar={};
	Do[
		tosol=(D[#/.TopoData[id]["ReplacementsMasked"],var]-OperatorAnsatz[#])&/@externalIP/.TopoData[id]["Replacements"];
		sol\[Beta]=First@Quiet[Solve[tosol==0,Union[Cases[tosol,_\[Beta],Infinity]]]];
		free\[Beta]=Union[Cases[sol\[Beta][[;;,2]],_\[Beta],Infinity]];
		sol\[Beta]=Join[MapAt[#/.Thread[free\[Beta]->0]&,sol\[Beta],{All,2}],Thread[free\[Beta]->0]];
		sol\[Beta]=Simplify[sol\[Beta]/.TopoData[id]["ReplacementsMasked"]];
		AppendTo[dOPRulesVar,LorentzVectorUtils`AbstractD[var][expr_]:>Evaluate@(OperatorAnsatz[expr]/.sol\[Beta])];
	,{var,TopoData[id]["MaskedVariables"]}];

	AssociateTo[TopoData[id],"ExtDerOperators"->dOPRulesVar];

	(* generate the differential operators *)

	dRules=Table[
		Module[{RHS,LHS},
			RHS=(ToFIREG5[Sum[With[{pp=TopoData[id]["Propagators"][[k]]},-ToExpression["a"~~ToString[k]]/$propHead[id][k]* LorentzVectorUtils`AbstractD[var][pp]/.TopoData[id]["ExtDerOperators"]]/.ToProps[id]/.TopoData[id]["Replacements"],{k,1,nProps[id]}],"ID"->id,"Shift"->Table[ToExpression["a"~~ToString[i]],{i,1,nProps[id]}]]);
			LHS=LorentzVectorUtils`AbstractD[var][$IntHead[id,Table[Pattern[Evaluate[ToExpression["a"~~ToString[i]]],_],{i,1,nProps[id]}]]];
			LHS:>Evaluate[CollectInts[RHS,Simplify]]
		],
	{var,TopoData[id]["MaskedVariables"]}];
	AssociateTo[TopoData[id],"DerivativeRules"->dRules];
	]
];

];


IntegralFamilyQ[id_]:=MemberQ[$IntegralFamilies,id];


AddIntegralFamily[id_]:=Module[{},
Unprotect[$IntegralFamilies];
If[!MemberQ[$IntegralFamilies,id],$IntegralFamilies = AppendTo[$IntegralFamilies,id]];
Protect[$IntegralFamilies];
];


RemoveIntegralFamily[id_]:=Module[{},
Map[Unset,{Props[id],nProps[id],ToProps[id],TopoData[id]}];
Unprotect[$IntegralFamilies];
$IntegralFamilies=DeleteCases[$IntegralFamilies,id];
Protect[$IntegralFamilies];
];


(* ::Section:: *)
(*Functionalities related to graphs*)


(* some tools that work in conjunction with GraphTools *)


GraphForInt[$IntHead[id_,inds_,___]]/;ValueQ[AssociatedGraph[id]]:=GraphForInt[IntSector[$IntHead[id,inds]]];
GraphForInt[$IntHead[id_,inds_,___]]/;ContainsOnly[inds,{1,0}]/;ValueQ[AssociatedGraph[id]]:=GraphForInt[$IntHead[id,inds]]=GraphTools`CollapseLineMR[AssociatedGraph[id],Global`l/@Flatten[Position[inds,_?NonPositive]]];


DisplayInt[$IntHead[id_, inds_,___]] := DisplayInt[IntSector[$IntHead[id, inds]]];
DisplayInt[$IntHead[id_, inds_,___]] /; ContainsOnly[inds, {1, 0}] && ValueQ[AssociatedGraph[id]] := DisplayInt[$IntHead[id, inds]] = GraphTools`MGGraphPlot[GraphTools`CollapseLineMR[AssociatedGraph[id], Global`l /@ Flatten[Position[inds, _?NonPositive]]], "ShowDetails" -> False];


DisplayIntPM[$IntHead[id_, inds_,___]] := DisplayIntPM[IntSector[$IntHead[id, inds]]];
DisplayIntPM[$IntHead[id_, inds_,___]] /; ContainsOnly[inds, {1, 0}] && ValueQ[AssociatedGraph[id]] := DisplayIntPM[$IntHead[id, inds]] = GraphTools`GraphPlotPM[GraphTools`CollapseLineMR[AssociatedGraph[id], Global`l /@ Flatten[Position[inds, _?NonPositive]]], "ShowDetails" -> False];


ClearDisplayInt[]:=Module[{},
	(* Remove all down values that are explicit *)
	DownValues[DisplayInt] = Cases[DownValues[DisplayInt],dv_/;!StringFreeQ[ToString[HoldPattern[DisplayInt[dv]]],"_"]];
	DownValues[DisplayIntPM] = Cases[DownValues[DisplayIntPM],dv_/;!StringFreeQ[ToString[HoldPattern[DisplayIntPM[dv]]],"_"]];
	DownValues[GraphForInt] = Cases[DownValues[GraphForInt],dv_/;!StringFreeQ[ToString[HoldPattern[GraphForInt[dv]]],"_"]];
]


(*GraphForInt[int:$IntHead[id_,inds_]]/;ValueQ[AssociatedGraph[id]]&&(AssociatedGraph[id]=!=None):=GraphForInt[IntSector[int]];
GraphForInt[int:$IntHead[id_,inds_:{Repeated[0|1]}]]/;ValueQ[AssociatedGraph[id]]&&(AssociatedGraph[id]=!=None):=GraphTools`CollapseLineMR[AssociatedGraph[id],Global`l/@Flatten[Position[inds,_?NonPositive]]];

*)
(*GraphForInt[$IntHead[id_,inds_:{Repeated[0|1]}]]/;ValueQ[AssociatedGraph[id]]&&AssociatedGraph[id]=!=None = GraphTools`CollapseLineMR[AssociatedGraph[id],Global`l/@Flatten[Position[inds,_?NonPositive]]];
*)


(*DisplayInt[int:$IntHead[id_, inds_]]:=GraphTools`graphPlotMR[GraphForInt[int]];*)


DisplayInt2[int:$IntHead[id_, inds_]]:=Show[SetProperty[GraphTools`MGEdgeTaggedGraph[GraphForInt[int]],PerformanceGoal->"Quality"]];


(* ::Section:: *)
(*General property extraction*)


(* General info *)
ListInts[expr_$IntHead]:=Return[{expr}];
ListInts[expr_]:=DeleteDuplicates[Cases[expr,_$IntHead,Infinity]];

CountInts[expr_]:=Length[ListInts[expr]];


Options[ListIntsAndCoefficients]={"Function"-> Identity};
ListIntsAndCoefficients[expr_,OptionsPattern[]]:=Module[
{ints=ListInts[expr],cfs},
If[ints==={},Return[{}]];
cfs=Map[OptionValue["Function"],Normal@CoefficientArrays[expr,ints][[2]]];
Return[Transpose[{cfs,ints}]];
]


SetAttributes[CollectInts, Listable];
CollectInts[HoldPattern[SeriesData[v_,i1_,l_List,i2_,i3_,i4_]],f_:Identity]:= SeriesData[v,i1,CollectInts[l,f],i2,i3,i4];
CollectInts[expr_,f_:Identity]/;FreeQ[expr,$IntHead]:=expr;
CollectInts[expr_,f_:Identity]/;FreeQ[expr,SeriesData]:=Module[
{ints=ListInts[expr]},
Return[f[Normal[CoefficientArrays[expr,ints][[1]]]]+Map[f,Normal[CoefficientArrays[expr,ints][[2]]]] . ints];
];


(* family info *)
IntFamily[$IntHead[id_,inds_]]:=id;
IntFamily[$IntHead[id_,inds_,c__]]:=id;

ListIntFamilies[expr_]:=Union[Map[IntFamily,ListInts[expr]]];

IntFamilySelector[id_][list_]:=Select[list,IntFamily[#]==id&];
IntFamilySelector[ids_List][list_]:=Select[list,MemberQ[ids,IntFamily[#]]&];


(* sector info *)
IntSector[$IntHead[id_,inds_]]:=$IntHead[id,Boole[Thread[inds>0]]];
IntSector[$IntHead[id_,inds_,c__]]:=$IntHead[id,Boole[Thread[inds>0]],c];

ListIntSectors[expr_]:=Union[Map[IntSector,ListInts[expr]]];
ListIntSectors[expr_,Min]:=MinimalBy[ListIntSectors[expr],IntLevel];
ListIntSectors[expr_,Max]:=MaximalBy[ListIntSectors[expr],IntLevel];

IntSectorSelector[$IntHead[id_,sector_,extr___]]:=Cases[#,$IntHead[id,sector/. {1:> _?Positive,0:> _?NonPositive},extr]]&;
IntSectorSelector[sectors_List]:=Flatten[Table[IntSectorSelector[sec][#],{sec,sectors}]]&;


(* index info *)
(*IntIndices[int_$IntHead]:=IndicesFromSector[IntSector[int]];*)
IntIndices[$IntHead[_,inds_,___]]:=inds;
IndicesFromSector[sector:{_,inds:{Repeated[0|1]}}]:=inds;
IndicesFromSector[sector:$IntHead[_,inds:{Repeated[0|1]}]]:=inds;


IntDenominator[int_$IntHead]:=MapAt[HeavisideTheta[#-1/2]#&,int,{2,All}];
IntNumerator[int_$IntHead]:=MapAt[HeavisideTheta[1/2-#]#&,int,{2,All}]


(* level info *)
IntLevel[int_$IntHead]:=Count[IntIndices[int],_?Positive];

ListIntLevels[expr_]:=Union[Map[IntLevel,ListInts[expr]]];

IntLevelSelector[level_Integer][list_]:=Select[list,Count[#[[2]],_?Positive]==level&];
IntLevelSelector[levels_List][list_]:=Select[list,MemberQ[levels,Count[#[[2]],_?Positive]]&];


(* denominators. Called r in kira *)
rCnt[x_]:=Total[(HeavisideTheta[#-1/2]#)&/@x];
IntCountDenom[int_$IntHead]:=rCnt[IntIndices[int]];

(* numerators. Called s in kira *)
sCnt[x_]:=-Total[(HeavisideTheta[1/2-#]#)&/@x];
IntCountNumer[int_$IntHead]:=sCnt[IntIndices[int]];

(* dots. Called d in kira *)
dCnt[x_]:=Total[(HeavisideTheta[#-1/2](#-1))&/@x];
IntCountDots[int_$IntHead]:=dCnt[IntIndices[int]];

(* *)
RSDmax[Indices_List]:=Module[{},{Max[Total[Cases[#,_?Positive]]&/@Indices],Max[-Total[Cases[#,_?Negative]]&/@Indices],Max[Total[(Cases[#,_?(#>1&)]-1)]&/@Indices]}];
IntRSDmax[expr_]:=RSDmax[IntIndices/@ListInts[expr]]


IntComplexity[int_$IntHead]:=IntCountDots[int]+IntCountNumer[int];


SortIntsByLevel[iList_List]:=Flatten[SortBy[GatherBy[iList,IntSector],IntLevel[#[[1]]]&]];


(* ::Section:: *)
(*Things related to subsectors*)


SectorPatternQ[expr_]:=MatchQ[expr,{Repeated[0|1]}];


SubSectorQ[sector1:{Repeated[0|1]},sector2:{Repeated[0|1]}]:=
Module[{ii=1},
If[Length[sector1]!= Length[sector2],Return[False]];
While[ii<=Length[sector1], 
If[sector1[[ii]]>sector2[[ii]],Return[False];];
ii++;];
Return[True];
]


(* extract subsectors *)
GetSubsectors[sector:{Repeated[0|1]}]:=Module[{
n=Length[sector],
onePos=Flatten[Position[sector,1]]
},
Return[Table[ReplacePart[sector,Thread[onePos->pp]],{pp,Tuples[{0,1},Length[onePos]]}]]
];
GetSubsectors[$IntHead[id_,sector_List]]:=$IntHead[id,#]&/@GetSubsectors[sector];


(* tree search for sub-sectors. Criterion must be compatible, i.e. when a sector is zero all subsectors are as well. *)
SubSectorsByCriterion[sector_:{Repeated[0|1]},crit_]:=Module[{visit,visited,posPos,zeroSector,sectorConsidered},
posPos=Flatten[Position[sector,_?Positive]];
visit[{}]:=Null;
(* l is a list of integers *)
visit[l_List]/;Length[l]>0:=Module[{},
If[visited[l],Return[]];
visited[l]=True;
sectorConsidered=ReplacePart[sector,Thread[Complement[posPos,l]->0]];
zeroSector[sectorConsidered]=crit[sectorConsidered];
If[!zeroSector[sectorConsidered],Map[visit,Subsets[l,{Length[l]-1}]]];
];
visit[posPos];
(* we extract all cases that have been tagged as zero-sectors *)
Return[(Keys@Select[DownValues[zeroSector],!Values[#]&]/.zeroSector-> Identity)[[;;,1]]];
];


SubSectorsByRESTRICTIONS[sector:{Repeated[0|1]},restrictions_]:=SubSectorsByCriterion[sector,ZeroOnRESTRICTIONSQ[restrictions]];
SubSectorsByRESTRICTIONS[sector:{Repeated[0|1]},restrictions_,k_Integer]:=SubSectorsByCriterion[sector,ZeroOnRESTRICTIONSQ[restrictions][#]||Total[#]<Total[sector]-k&];
SubSectorsByRESTRICTIONS[$IntHead[id_,sector:{Repeated[0|1]}],restrictions_]:=Thread[$IntHead[id,SubSectorsByRESTRICTIONS[sector,restrictions]]];
SubSectorsByRESTRICTIONS[$IntHead[id_,sector:{Repeated[0|1]}],restrictions_,k_Integer]:=Thread[$IntHead[id,SubSectorsByRESTRICTIONS[sector,restrictions,k]]];


GetSpanningSectors[sectorList:{Repeated[$IntHead[_,{Repeated[0|1]}]]}]:=Module[{fams=ListIntFamilies[sectorList],toret},
(* Split by family and wrap head around *)
Return[Flatten[Table[
	Thread[$IntHead[id,GetSpanningSectors[IntFamilySelector[id][sectorList][[;;,2]]]]]
,
{id,fams}]]];
]


GetSpanningSectors[sectorList:{Repeated[{Repeated[0|1]}]}]:=Module[{SectorGather=SortBy[GatherBy[sectorList,Total],-Total[First[#]]&],toret},
toret=Table[
Select[SectorGather[[i]],
Function[{sec},AllTrue[Flatten[SectorGather[[i+1;;-1]],1],!SubSectorQ[#,sec]&]]]
,{i,1,Length[SectorGather]}];
toret=Flatten[toret,1];
Return[toret];
]


GetPDRSectors[sectorList:{Repeated[{Repeated[0|1]}]}]:=Module[{SectorGather=SortBy[GatherBy[sectorList,Total[#]&],-Total[#[[1]]]&],toret},
Flatten@Table[Table[
Cases[SectorGather[[i+1]],a_?(SubSectorQ[#,sec]&):>(sec->a)],{sec,SectorGather[[i]]}],{i,1,Length[SectorGather]-1}]
]


GetMaximalSectors[sectorList:{Repeated[{Repeated[0|1]}]}]:=Module[{},
	Return[GraphComputation`SourceVertexList[Graph[sectorList,GetPDRSectors[sectorList]]]];
]


(* ::Section:: *)
(*IBP related functionalities *)


GenerateSeedIntegrals[l:{Repeated[_List]},x:(n_Integer|{n_Integer,d_Integer})]:=Join@@Map[GenerateSeedIntegrals[#,x]&,l];
GenerateSeedIntegrals[l:{Repeated[_$IntHead]},x:(n_Integer|{n_Integer,d_Integer})]:=Join@@Map[GenerateSeedIntegrals[#,x]&,l];
GenerateSeedIntegrals[$IntHead[id_,sector:{Repeated[0|1]}],x:(n_Integer|{n_Integer,d_Integer})]:=$IntHead[id,#]&/@GenerateSeedIntegrals[sector,x];

GenerateSeedIntegrals[sector:{Repeated[0|1]},n_Integer]:=Module[{zeroPos,nn,indices},
	zeroPos=Flatten[Position[sector,0]];
	nn=Length[zeroPos];
	indices=Flatten[Table[Permutations/@IntegerPartitions[k,{nn},Range[0,n]],{k,0,n}],2];
	Return[Table[ReplacePart[sector,Thread[zeroPos-> -ii]],{ii,indices}]];
];

GenerateSeedIntegrals[sector:{Repeated[0|1]},{n_Integer,d_Integer}]:=Module[{zeroPos,onePos,nn0,nn1,nn,indices0,indices1,indices},
	zeroPos=Flatten[Position[sector,0]];
	onePos=Flatten[Position[sector,1]];
	
	nn0=Length[zeroPos];
	nn1=Length[onePos];
	nn=nn0+nn1;
	
	indices0=Flatten[Table[Permutations/@IntegerPartitions[k,{nn0},Range[0,n]],{k,0,n}],2];
	indices1=Flatten[Table[Permutations/@IntegerPartitions[k,{nn1},Range[0,d]],{k,0,d}],2];
	
	indices=Flatten[Outer[Join,indices0,indices1,1],1];
	Return[Normal[SparseArray[Join[Thread[zeroPos->-#[[1;;nn0]]],Thread[onePos->1+#[[nn0+1;;-1]]]]]]&/@indices];
]


GenerateSeedIntegralsWithDots[l:{Repeated[_List]},n_]:=Join@@Map[GenerateSeedIntegralsWithDots[#,n]&,l];
GenerateSeedIntegralsWithDots[l:{Repeated[_$IntHead]},n_]:=Join@@Map[GenerateSeedIntegralsWithDots[#,n]&,l];
GenerateSeedIntegralsWithDots[$IntHead[id_,sector:{Repeated[0|1]}],n_]:=$IntHead[id,#]&/@GenerateSeedIntegralsWithDots[sector,n];
GenerateSeedIntegralsWithDots[sector:{Repeated[0|1]},complexity_]:=Module[
{zeroPos,onePos,nn,indicesAll},
zeroPos=Flatten[Position[sector,0]];
onePos=Flatten[Position[sector,1]];
nn=Length[zeroPos];
indicesAll=Flatten[Table[Permutations/@IntegerPartitions[k,{Length[sector]},Range[0,complexity]],{k,0,complexity}],2];
Return[Normal[SparseArray[Join[Thread[zeroPos->-#[[1;;nn]]],Thread[onePos->1+#[[nn+1;;-1]]]]]]&/@indicesAll];
]


(* ::Section:: *)
(*Functionalities related to graph polynomials*)


Options[GetUF]={"FeynmanParameter"-> Global`x};
GetUF[internal_,external_,propagator_,replacements_,OptionsPattern[]]:=Module[{x=OptionValue["FeynmanParameter"],nLoops=Length[internal],temp,quadraticData,QQ,QQInv,LL,CC,U,F},
temp=propagator . (x/@Range[Length[propagator]]);
LorentzVectorUtils`LScalarQ[x[_]]^=True;
(* completing the square *)
{CC,LL,QQ}=Normal@CoefficientArrays[temp/.LorentzVectorUtils`IP-> Times,internal,"Symmetric"->True];
CC=temp/.Alternatives@@internal:> 0;
QQInv=Inverse[QQ];
U=Det[QQ]/.replacements;
F=U(CC-1/4*Sum[QQInv[[i,j]]LorentzVectorUtils`IP[LL[[i]],LL[[j]]],{i,1,nLoops},{j,1,nLoops}]/.replacements);
Return[{U,F}];
]


(* ::Section:: *)
(*Functionalities related to propagators*)


IntToProps[expr_]:=expr/.$IntHead[id_,inds_,___]/;IntegralFamilyQ[id]:>Times@@($propHead[id][#]&/@Range[nProps[id]]^(-inds));
IntToPropsExplicit[expr_]:=expr/.$IntHead[id_,inds_,___]/;IntegralFamilyQ[id]:>Times@@(Props[id]^(-inds));


SetAttributes[ToFIREG4, Listable];
Options[ToFIREG4] = {"ID" -> 1, "PropagatorHead" -> $propHead, 
   "HeadFunction" -> Automatic, "Dimension" -> Automatic, 
   "DoCheck" -> False, "SplitPrefactor" -> False,"ApplyFunction"-> Identity,
   "Shift" -> None
   };
ToFIREG4[expr_, OptionsPattern[]] := 
 Module[{ToFIREGHelp, propagatorVars, toret, ToCheck,dim,headFunction,numRepl,$ChecksFailed=False,iShift},
 (* check if dimension of family is specified *)
 If[OptionValue["Dimension"] === Automatic,
    If[!ValueQ[nProps[OptionValue["ID"]]], Print["Either set nProps[", OptionValue["ID"],"] or pass \"Dimensions\" options."]; Return[] ,dim = nProps[OptionValue["ID"]]],
    dim = OptionValue["Dimension"]];
 If[!(Element[dim,PositiveIntegers] === True),Print["Incorrect dimension setting. Found ", dim]; Return[]];
 iShift=If[OptionValue["Shift"]===None,Table[0,dim],OptionValue["Shift"]];
 (* the propagator variables *)
 propagatorVars = OptionValue["PropagatorHead"][OptionValue["ID"]] /@ Range[dim];
 (* create a monomial list and convert it to FIRE notation. We keep prefactors and integrals split at first *)
 headFunction=If[OptionValue["HeadFunction"] === Automatic,$IntHead[OptionValue["ID"],#]&,OptionValue["HeadFunction"]];
 toret = {OptionValue["ApplyFunction"][#/.Thread[propagatorVars-> 1]],headFunction[-Exponent[#,propagatorVars]+iShift]}&/@Global`MonomialListWithNegative[expr,propagatorVars];
 (* Check if conversion was succesful. 1.) converting back. 2.) Check that all variables are substituted *)
 If[OptionValue["DoCheck"],
  numRepl=Thread[propagatorVars->(Prime[100+20*#]&/@Range[dim])];
   ToCheck =  expr - (toret /. headFunction[inds_] :>  Times@@(propagatorVars^(-inds+iShift)));
    (* substitute numerical variables *)
   If[! (Simplify[ToCheck/.numRepl] === 0), $ChecksFailed = True ; Print[ToCheck] ];
   If[! FreeQ[toret, Alternatives@@propagatorVars], 
    Print["Not all variables converted. ", Union@Cases[toret, propagatorVars, Infinity]];
    $ChecksFailed = True ;
    ];
   If[!$ChecksFailed,Print["Checks passed!"]]
  ];
 (* Recombine everything if requested *)
 If[OptionValue["SplitPrefactor"],Return[toret]];
 toret = Total[Times@@#&/@toret];  
 Return[toret];
 ];


SetAttributes[ToFIREG5, Listable];
Options[ToFIREG5] = {"ID" -> 1, "PropagatorHead" -> $propHead, 
   "HeadFunction" -> Automatic, "Dimension" -> Automatic, "SplitPrefactor" -> False, "ApplyFunction"-> Identity,
   "Shift" -> None
   };
ToFIREG5[expr_, OptionsPattern[]] := 
 Module[{ToFIREGHelp, propagatorVars, propagatorVarsAndInv, Inv, toret, dim, headFunction, iShift, posListConversion, cfArr},
 (* check if dimension of family is specified *)
 If[OptionValue["Dimension"] === Automatic,
    If[!ValueQ[nProps[OptionValue["ID"]]], Print["Either set nProps[", OptionValue["ID"],"] or pass \"Dimensions\" options."]; Return[$Failed] ,dim = nProps[OptionValue["ID"]]],
    dim = OptionValue["Dimension"]];
 If[Element[dim,Integers] =!= True , Print["Incorrect dimension setting. Found ", dim]; Return[$Failed]];
 iShift = If[OptionValue["Shift"] === None, Table[0,dim], OptionValue["Shift"]];
 (* the propagator variables *)
 propagatorVars = OptionValue["PropagatorHead"][OptionValue["ID"]] /@ Range[dim];
 propagatorVarsAndInv=Join[propagatorVars,Inv/@propagatorVars];
 (* This function is a bit convoluted. It takes the non-zero positions and converts them to an association of the form var_no_n \[Rule] power_of_var. Then it packs it into a sparsearray of twice the length, because of the negative variables. Finally we split the list and subtract followed by converting to a list. *)
 posListConversion[x_] := iShift-Normal[Subtract@@Partition[SparseArray[Normal[Counts[x]], 2dim], dim]];
 cfArr=CoefficientArrays[expr/.Power[x_,n_]/;n<0:> Power[Inv[x],-n], propagatorVarsAndInv];
 headFunction=If[OptionValue["HeadFunction"] === Automatic, $IntHead[OptionValue["ID"],#]&, OptionValue["HeadFunction"]];
 (* Keep prefactors and integrals separate at first. *)
 toret = Flatten[Table[{Extract[ca,#],headFunction[posListConversion[#]]}&/@ca["NonzeroPositions"],{ca,Drop[cfArr,1]}],1];
 toret = Prepend[toret,{cfArr[[1]],headFunction[iShift+Table[0,dim]]}];
 toret = toret/.(Inv :> (Power[#,-1]&));
 (* Apply a function if requested *)
 If[OptionValue["ApplyFunction"] =!= Identity,toret = MapAt[OptionValue["ApplyFunction"],toret,{All,1}]];
 (* Recombine everything if requested *)
 If[OptionValue["SplitPrefactor"],Return[toret],Return[Total[Times@@@toret]]];
 ];


SetAttributes[ToFIREGFORM, Listable];
Options[ToFIREGFORM]={"ID"->1,"PropagatorHead"->$propHead,"HeadFunction"->Automatic,"Dimension"->Automatic,"SplitPrefactor"->False,"ApplyFunction"->Identity,"Shift"->None};
ToFIREGFORM[expr_,OptionsPattern[]]:=Module[
{
dim=nProps[OptionValue["ID"]],
formString,toFireString,
formScriptPath=FileNameJoin[{$IntegralToolsTempDirectory,"ToFIREFORM-"~~CreateUUID[]~~".frm"}],
outFile=FileNameJoin[{$IntegralToolsTempDirectory,"ToFIREGout.m"}],
vars,
maskVar,
ret,
toret
},
If[!FileExistsQ[Global`$FORMBinPath],Print["Could not locate FORM binary"];Return[$Failed];];

toFireString=StringRiffle[Table["p"~~ToString[OptionValue["ID"]]~~"n"~~ToString[k]~~"^n"~~ToString[k]~~"?",{k,1,dim}],{"id ","*",""}]~~" = "~~ StringRiffle[Table["-n"~~ToString[k],{k,1,dim}],{"Int(",",",")"}]~~";\n";

(* mask the remaining variables for form *)
vars=DeleteCases[Variables[expr],OptionValue["PropagatorHead"][OptionValue["ID"]][_]];
maskVar=Table[vars[[k]]->ToExpression["v"~~ToString[k]],{k,Length[vars]}];

formString=StringJoin[
	StringRiffle[Table["n"~~ToString[k],{k,1,dim}],{"Symbols ",",",";\n"}],
	StringRiffle[Table["p"~~ToString[OptionValue["ID"]]~~"n"~~ToString[k],{k,1,dim}],{"Symbols ",",",";\n"}],
	If[Length[vars]>1,StringRiffle[Table["v"~~ToString[k],{k,1,Length[vars]}],{"Symbols ",",",";\n"}],""],
	"Functions Int;\n",
	"Local expr = "~~ToString[InputForm[expr/.maskVar/.OptionValue["PropagatorHead"][OptionValue["ID"]][k_]:>ToExpression["p"~~ToString[OptionValue["ID"]]~~"n"~~ToString[k]]]]~~";\n",
	toFireString,
	"\n",
	"Format mathematica;",
	".sort\n",
	"#write <"~~outFile~~"> \"%e\",expr;\n",
	"\n.end"
];

Export[formScriptPath,formString,"String"];
ret=RunProcess[{Global`$FORMBinPath, formScriptPath}, ProcessDirectory->$IntegralToolsTempDirectory];
DeleteFile[formScriptPath];

If[ret["ExitCode"]=!=0,Print["ERROR: running FORM failed!"]; Print[ret["StandardOutput"]]; Print[ret["StandardError"]]; Return[$Failed]];

toret=Import[outFile,"String"];
DeleteFile[outFile];

toret=StringDelete[toret,{";",WhitespaceCharacter}];
toret=ToExpression[toret];
toret=toret/.(Reverse/@maskVar);
toret=toret/.$IntHead[inds__]:>$IntHead[OptionValue["ID"],List[inds]];
(*toret=ToExpression@StringDrop[toret,-3]/.Int[inds__]:>Int[OptionValue["ID"],List[inds]];*)
Return[toret];
];


ExpandLeadingPropagators[props_List,scaling_:{RepeatedNull[_Rule]},cntPara_]:=Module[{},
Normal[Series[props/.scaling,cntPara->0]]/.cntPara->1
]


(* ::Section:: *)
(*Functionalities related to cuts*)


ApplyCuts[expr_]:=expr/.$IntHead[id_,inds_,"Cut"-> cinds_]/; !And@@Thread[inds[[cinds]]>0]:> 0


ApplyRestrictions[expr_]:=Module[{fams=ListIntFamilies[expr],rls},
rls=DeleteCases[TopoData[#]["RestrictionRule"]&/@fams,_Missing];
Return[Fold[#1/.#2&,expr,TopoData[#]["RestrictionRule"]&/@fams]]
]


RuleFromCut[int_$IntHead]:=RuleFromCut[IntIndices[int],"ID"->IntFamily[int]]


Options[RuleFromCut]={"ID"->1,"Head"->Automatic};
RuleFromCut[sector:{Repeated[0|1]},OptionsPattern[]]:=Module[{cutPos=Flatten[Position[sector,1]],size=Length[sector],head},
If[OptionValue["Head"]===Automatic,head=$IntHead[OptionValue["ID"],#1]&,head=OptionValue["Head"];];
head[Table[Pattern[Evaluate[ToExpression["a"~~ToString[i]]],_],{i,1,size}]]/;Evaluate[(Or@@(ToExpression["a"~~ToString[#]]<=0&/@cutPos))]->0
]


RESTRICTIONSFromCut[int_$IntHead]:=RESTRICTIONSFromCut[IntIndices[int]];
RESTRICTIONSFromCut[sector:{Repeated[0|1]}]:=Module[{cutPos=Flatten[Position[sector,1]],size=Length[sector]},
Return[Table[-UnitVector[size,k],{k,cutPos}]]
]


(* ::Section:: *)
(*Functionalities related to sector mapping *)


Do[If[!ValueQ[e],e={};Protect[e];],{e,{$RemapData,$AllSectors,$RepresentativeSectors,$MappedSectors}}];


SetRemapData[reData_Association]:=Module[{sampleInts},
Unprotect[$RemapData,$AllSectors,$RepresentativeSectors,$MappedSectors];
$RemapData=reData;
If[reData=!=Association[],
	$AllSectors=Keys[reData];
	$RepresentativeSectors=PositionIndex[reData[[;;,"Representative"]]]["Self"];
	$MappedSectors=Complement[$AllSectors,$RepresentativeSectors];,
	(* If no data is provided initialize empty *)
	{$AllSectors,$RepresentativeSectors,$MappedSectors}={{},{},{}};
];
(* Initialize integral families that are present in the remap data. *)
If[$AllSectors=!={},
	sampleInts=DeleteDuplicatesBy[$AllSectors,First];
	(If[!IntegralFamilyQ[#[[1]]], AddIntegralFamily[#[[1]]]; nProps[#[[1]]] = Length[#[[2]]];])&/@sampleInts;
];
Protect[$RemapData,$AllSectors,$RepresentativeSectors,$MappedSectors];
];


SetCut[cutSector_:$IntHead[___]]:=Module[{
remapDataCut=$RemapData,cutSectorMapped=MapIntegrals[cutSector],fams,
cutIntImages,zeroContributionFamilies,cutRulesAll,cutRestr,sectorsOnCut
},
(* find all images of the cut sector *)
cutIntImages=Append[Keys@Select[$RemapData,#["Representative"]==cutSectorMapped&],cutSectorMapped];
(* combined cut rules *)
fams=ListIntFamilies[cutIntImages];
sectorsOnCut={};
Do[
(* cut sector might appear in multiple ways in a given family *)
cutRestr=RESTRICTIONSOr@@(RESTRICTIONSFromCut/@IntFamilySelector[id][cutIntImages]);
sectorsOnCut=Join[sectorsOnCut,Select[IntFamilySelector[id][$AllSectors],!ZeroOnRESTRICTIONSQ[cutRestr][#]&]];
,{id,fams}];
(* by default, MapIntegrals sets all unknown integrals to zero.*)
(* all families that don't talk to the cut are set to zero *)
remapDataCut=KeyTake[$RemapData,sectorsOnCut];
SetRemapData[remapDataCut];
]


Options[MapSingleIntegral]={"FORM"->False};
MapSingleIntegral[int_:$IntHead[___],OptionsPattern[]]:=Module[{sec=IntSector[int],propMap,rep,repID,ToFIRE=If[OptionValue["FORM"]===True,ToFIREGFORM,ToFIREG5]},
rep=Lookup[$RemapData,sec];
(* if the sector is not in the list of nonzero sectors return 0 *)
If[Head[rep]===Missing,Return[0]];
propMap=rep["MapToRepresentative"]["PropagatorMap"];
If[rep["Representative"]=="Self",Return[int]];
Return[ToFIRE[IntToProps[int]/.propMap,"ID"->rep["Representative"][[1]]]];
];
(* Here we have introduced a collect after every step, this makes the mapping go faster *)
MapIntegralsStep[expr_,opt:OptionsPattern[]]:=CollectInts[expr/.x_$IntHead:>MapSingleIntegral[x,opt]];
MapIntegrals[expr_]:=FixedPoint[MapIntegralsStep,expr];


(* TODO: the code should figure out itself if the integral has a cut. *)
Options[MapSingleIntegralCut]={"FORM"->False};
MapSingleIntegralCut[int_:$IntHead[___],OptionsPattern[]]:=Module[{
sec=IntSector[int][[1;;2]],
propMap,rep,repID,ToFIRE=If[OptionValue["FORM"]===True,ToFIREGFORM,ToFIREG5],
ctLines,ctLinesTarget
},
rep=Lookup[$RemapData,sec];
ctLines=int[[3]];

If[!AllTrue[IntIndices[int][[ctLines]],#>0&],Return[0]];

(* if the sector is not in the list of nonzero sectors return 0 *)
If[Head[rep]===Missing,Return[0]];

propMap=rep["MapToRepresentative"]["PropagatorMap"];
If[rep["Representative"]=="Self",Return[int]];

(* Map The cut lines *)
ctLinesTarget=Sort[propMap[[ctLines]][[;;,2]]/.$propHead[_]:>Identity];

Return[ToFIRE[IntToProps[int]/.propMap,"ID"->rep["Representative"][[1]]]/.$IntHead[id_,inds_]:>If[AllTrue[inds[[ctLinesTarget]],Positive],$IntHead[id,inds,ctLinesTarget],0]];
];
(* Here we have introduced a collect after every step, this makes the mapping go faster *)
MapIntegralsStepCut[expr_,opt:OptionsPattern[]]:=CollectInts[expr/.x_$IntHead:>MapSingleIntegralCut[x,opt]];
MapIntegralsCut[expr_]:=FixedPoint[MapIntegralsStepCut,expr];


If[!ValueQ[$AutoData],
	$AutoData={};
	Protect[$AutoData];
];
SetAutoData[autoData_]:=Module[{},
Unprotect[$AutoData];
$AutoData=autoData;
Protect[$AutoData];
]


AutomorphismOrbit[int_$IntHead]:=Module[{sec=IntSector[int],dat,maps,repID},
dat=Lookup[$AutoData,sec];
Return[Table[ToFIREG5[IntToProps[int]/.map["PropagatorMap"],"ID"->sec[[1]]],{map,dat["Maps"]}]];
]


(* ::Section:: *)
(*Notation Maps*)


SectorToBinary[sector:{Repeated[0|1]}]:=(2^Range[0,Length[sector]-1]) . sector;
BinaryToSector[b_Integer,k_Integer]:=PadRight[Reverse@IntegerDigits[b,2],k];


ConvertNotation["FIRE"->"Int"][expr_]:=expr /. {$FIREIntHead :> $IntHead};
ConvertNotation["Int"->"FIRE"][expr_]:=expr /. {$IntHead:>$FIREIntHead };


ToIntNotation[expr_]:=expr/.ConvertNotation["FIRE"->"Int"];


ToFIRENotation[expr_]:=expr/. ConvertNotation["Int"->"FIRE"];


IndicesToString[indices:{Repeated[_Integer]}]:=StringRiffle[StringReplace[ToString/@indices,"-"->"m"],""];


IntToString[int_]:="Int_"<>IndicesToString[IntIndices[int]];


(* ::Section:: *)
(*Functionalities related to FIRE*)


FIREInputString[id_]:=Module[{ToFireForm,string,dotVars},If[!IntegralFamilyQ[id],
Print["Initialize topology ",id, " first."];
Return;
];
ToFireForm[expr_]:=expr/.{f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]],LorentzVectorUtils`IP:>Times};

string="TopoID = " ~~ToString[TopoData[id]["FIREProblemID"]]~~";\n";
string=string~~"Internal = "~~ToString[InputForm@ToFireForm[TopoData[id]["Internal"]]]~~";\n";
string=string~~"External = "~~ToString[InputForm@ToFireForm[TopoData[id]["External"]]]~~";\n";
string=string~~"Propagators = "~~ToString[InputForm@ToFireForm[TopoData[id]["Propagators"]]]~~";\n";
If[TopoData[id]["Replacements"]=!={},
string=string~~"Replacements = "~~ToString[InputForm@ToFireForm[MapAt[#/.TopoData[id]["VariableMask"]&,TopoData[id]["ReplacementsMasked"],{All,2}]]]~~";\n"
];
If[TopoData[id]["RESTRICTIONS"]=!={},
string=string~~"RESTRICTIONS = "~~ToString[InputForm@ToFireForm[TopoData[id]["RESTRICTIONS"]]]~~";\n"
];
If[TopoData[id]["TopSector"]=!=None,
string=string~~"TopSector = "~~ToString[InputForm@ToFireForm[TopoData[id]["TopSector"]]]~~";\n"
];
Return[string];
]


Options[PrepareFIRE]={"Prepare"->True,"ConfigOptions"->{},"FIREPrepareOptions"->{}};
PrepareFIRE[id_,OptionsPattern[]]:=Module[{tmpdir,
FIREdir=FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"]}],
FIREinputFile,
FIREperpareFile,
stringPepare,
startFile,
cmd,
tmp
},
FIREinputFile=FileNameJoin[{FIREdir,"FIREinput.m"}];
FIREperpareFile=FileNameJoin[{FIREdir,"FIREprepare.m"}];
startFile=FileNameJoin[{FIREdir,TopoData[id]["Name"]~~".start"}];

Quiet[CreateDirectory[FIREdir],{CreateDirectory::eexist}];
Export[FileNameJoin[{FIREdir,"FIREinput.m"}],FIREInputString[id],"String"];

(* FIRE needs Mathematica to produce the start file. *)	
If[!FileExistsQ[$MathKernelPath],
	Print["Could not locate Mathematica. $MathKernelPath = ",$MathKernelPath];
	Return[];
];

(* We need the Mathematica version of FIRE *)
If[!FileExistsQ[Global`$FIREMathPath],
	Print["Could not locate Mathematica FIREX.m. Please set $FIREMathPath to a valid path."];
	Return[];
];

(* Config file *)
If[TopoData[id]["TopSector"]=!=None,
	problemString=ToString[TopoData[id]["FIREProblemID"]]~~" |"~~ToString[Position[TopoData[id]["TopSector"],1][[-1,1]]]~~"|"~~TopoData[id]["Name"]~~".start";
	,
	problemString=ToString[TopoData[id]["FIREProblemID"]]~~" "~~TopoData[id]["Name"]~~".start"
];

(* Prepare script *)
stringPepare=StringRiffle[{
"Get[\""~~Global`$FIREMathPath~~"\"];",
"Get[\""~~FIREinputFile~~"\"];",
"PrepareIBP[];",
"Print[{Internal,External,Replacements,Propagators}];",
"If[ValueQ[TopSector],
positivePosition=Position[TopSector,1][[-1,1]];
Print[positivePosition];
Prepare["~~StringRiffle[OptionValue["FIREPrepareOptions"],","]~~",PositiveIndices\[Rule]positivePosition];,
Prepare["~~StringRiffle[OptionValue["FIREPrepareOptions"],","]~~"];
];",
"SaveStart[\""~~FIREdir~~"/"~~TopoData[id]["Name"]~~"\","~~ToString[TopoData[id]["FIREProblemID"]]~~"]"
},"\n\n"];

Export[FileNameJoin[{FIREdir,"FIREprepare.m"}],stringPepare,"String"];

If[OptionValue["Prepare"],
	If[!FileExistsQ[startFile],
		WriteString["stdout","Runing FIRE preparation step for topology ",TopoData[id]["Name"],". "];
		cmd=$MathKernelPath<> " -script "<>"\""<>FIREperpareFile<>"\"";
		tmp=RunProcess[{"bash","-l","-c",cmd}];
		
		
		(* Check if .start file has been created *)
		If[FileExistsQ[startFile],
			WriteString["stdout"," done.\n"],
			WriteString["stdout"," failed to prepare.\n"];
			WriteString["stdout",tmp["StandardOutput"]];
		];
		,Print["Start file exists."]
	];
];



Export[FileNameJoin[{FIREdir,TopoData[id]["Name"]~~".config"}],
	FIREConfigString[
	"folder"->FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"]}],
(*	"storage"->FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"],"storage"}],*)
	"output"->TopoData[id]["Name"]~~".tables",
	"problem"->problemString,
	"variables"->StringRiffle[Prepend[TopoData[id]["MaskedVariables"],Global`d],", "]
	],"String"
];

]


Options[PrepareFIREFromInput]={"FIREPrepareOptions"->{Global`AutoDetectRestrictions->True,Global`LI->True,Global`Parallel->True}};
PrepareFIREFromInput[filename_,OptionsPattern[]]:=Module[{stringPrepare,FIREPrepareFile,dir=FileNameDrop[filename,-1]},

(* FIRE needs Mathematica to produce the start file. *)	
If[!FileExistsQ[$MathKernelPath],
	Print["Could not locate Mathematica. $MathKernelPath = ",$MathKernelPath];
	Return[];
];

(* We need the Mathematica version of FIRE *)
If[!FileExistsQ[Global`$FIREMathPath],
	Print["Could not locate Mathematica FIREX.m. Please set $FIREMathPath to a valid path."];
	Return[];
];
FIREPrepareFile=FileNameJoin[{dir,"FIREprepare.m"}];
stringPrepare=StringRiffle[{
"Get[\""~~Global`$FIREMathPath~~"\"];",
"Get[\""~~filename~~"\"];",
"PrepareIBP[];",
"Print[{Internal,External,Replacements,Propagators}];",
"If[ValueQ[TopSector],
positivePosition=Position[TopSector,1][[-1,1]];
Print[positivePosition];
Prepare["~~StringRiffle[OptionValue["FIREPrepareOptions"],","]~~",PositiveIndices\[Rule]positivePosition];,
Prepare["~~StringRiffle[OptionValue["FIREPrepareOptions"],","]~~"];
];",
"SaveStart[\""~~dir~~"/Diag\"~~ToString[TopoID],TopoID];"
},"\n\n"];

Export[FIREPrepareFile,stringPrepare,"String"];
Run[$MathKernelPath~~" -script "~~FIREPrepareFile];
DeleteFile[FIREPrepareFile];

Return[];
]


Options[ExportIntegralsFIRE]={"NameFunction"->("ToReduce.m"&)}
ExportIntegralsFIRE[iList_List,OptionsPattern[]]:=Module[{families=ListIntFamilies[iList],folder,toExport},
Do[
folder=FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[fam]["Name"]}];
Print[folder];
toExport=Cases[iList,$IntHead[fam,inds_]:>{TopoData[fam]["FIREProblemID"],inds}];
If[toExport==={},Continue[]];
If[DirectoryQ[folder],
Export[FileNameJoin[{folder,OptionValue["NameFunction"][fam]}],toExport]
]
,{fam,families}];
Return[];
]


(* FIRE is sensitive to the order of the options. This list fixes the order *)
FIREConfigOptionOrder={ 
"database",
"storage",
"compressor",
"ordering",
"even",
"odd",
"prime",
"bucket",
"pos_pref",
"threads",
"fthreads",
"variables",
"start",
"folder",
"problem",
"masters",
"lbases",
"preferred",
"integrals",
"output"
};

Options[FIREConfigString]={
"database"->None,
"storage"->None,
"ordering"->None,
"compressor"-> None,
"prime"-> None,
"threads"-> 6,
"fthreads"-> 6,
"problem"-> "1 default.start",
"output"->"default.tables",
"folder"->$IntegralToolsBaseDirectory,
"integrals"-> "ToReduce.m",
"lbases"-> None,
"config"-> "default.config",
"variables"-> "d",
"even"-> None,
"odd"-> None,
"pos_pref"-> None,
"bucket"-> None,
"masters"->None,
"preferred"->None,
"lbases"->None,
(* #start command *)
"start"->""
 };
FIREConfigString[OptionsPattern[]]:=Module[{options,string={},folder,optionOrder,map,toret},
map=Table[opt->OptionValue[opt],{opt,FIREConfigOptionOrder}];
(* remove unspecified options *)
map=DeleteCases[map,HoldPattern[_->None]];
(* add slashes at the end if they are missing *)

map=Fold[MapAt[AppendSlashIfNescessary,#1,#2]&,Association[map],Intersection[{"storage","folder"},Keys[map]]];

(* add whitespaces and # to conform with FIRE syntax and make readable *)
toret=KeyValueMap[StringPadRight["#"~~#1,20]~~ToString[#2]&,map];
toret=StringRiffle[toret,"\n"];
Return[toret];
];
AppendSlashIfNescessary=If[StringTake[#,-1]=!="/",#~~"/",#]&;


(*Options[RunFIRE]={"Flags"->""};
RunFIRE[id_,OptionsPattern[]]:=
Module[{configFile=FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"],TopoData[id]["Name"]~~".config"}]},

If[!FileExistsQ[configFile], 
Print["Missing config file.",configFile];
Return[$Failed];
];

If[!FileExistsQ[Global`$FIREBinPath], 
Print["Could not locate FIRE binary."];
Return[$Failed];
];
(* drop .config. The quotes are for to treat cases like whitespaces in filenames *)
Run[Global`$FIREBinPath~~OptionValue["Flags"]~~" -c '"~~StringDrop[configFile,-7]~~"'"]
]*)


Options[RunFIRE]={"PrintLog"->0};
RunFIRE[id_,OptionsPattern[]]:=
Module[{
	baseDir=FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"]}],
	configFile,bashFile,proc,line,tt0,nTime=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[#], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]&,exitCode},

	configFile=FileNameJoin[{baseDir,TopoData[id]["Name"]~~".config"}];
	bashFile=FileNameJoin[{baseDir,"run_"~~TopoData[id]["Name"]~~".sh"}];
	
	If[!FileExistsQ[configFile], 
		Print["Missing config file.",configFile];
		Return[$Failed];
	];
	
	If[!FileExistsQ[Global`$FIREBinPath], 
		Print["Could not locate FIRE binary."];
		Return[$Failed];
	];
	
	(* Write a bash script to run *)
	Export[bashFile,"#!/bin/bash
	cd '"<>baseDir<>"'
	'"<>AbsoluteFileName[Global`$FIREBinPath]<>"' -c "<>TopoData[id]["Name"]<>"
	exit_code=$?
	echo __EXIT_CODE__:$exit_code
	exit $exit_code
	","String"];
	Print["Starting FIRE run for ",TopoData[id]["Name"]];
	tt0=AbsoluteTime[];
	proc=StartProcess[{"bash",bashFile}];
	While[ProcessStatus[proc] === "Running",
		line = ReadLine[proc];
		While[line =!= EndOfFile,
			If[StringStartsQ[line,"__EXIT_CODE__:"],exitCode = ToExpression@StringReplace[line,"__EXIT_CODE__:"->""],
				If[(* Print specific FIRE printouts *)
					OptionValue["PrintLog"]>10||
					StringStartsQ[line,"FINISHED LEVEL"|"STARTING LEVEL"]&&OptionValue["PrintLog"]>5||
					StringStartsQ[line,"Master integrals:"]&&OptionValue["PrintLog"]>1
				,Print[line]];
			];
		line = ReadLine[proc];
		]
	];
	
	Print["FIRE run completed. ",nTime[tt0-AbsoluteTime[]]];
	KillProcess[proc];
	If[exitCode=!=0 , Return[$Failed]];
]


Options[LoadFIRETable]={"JoinTerms"-> True,"ApplyFunction"-> Identity,"Head"-> $IntHead};
LoadFIRETable[filename_String,OptionsPattern[]] := 
   Module[{temp, GGG, data, Func}, data = Get[filename]; 
   If[data===$Failed,Return[$Failed]];
   Func=OptionValue["ApplyFunction"];
     temp = ({GGG[##1[[1]]], ({GGG[##1[[1]]], ##1[[2]]} & ) /@ 
          ##1[[2]]} & ) /@ data[[1]]; 
     ((GGG[##1[[1]]] =OptionValue["Head"][##1[[2,1]], ##1[[2,2]]]) & ) /@ data[[2]]; 
     temp = temp; Clear[GGG]; temp = DeleteCases[temp, {a_, {{a_, "1"}}}]; 
     temp = ({##1[[1]], ({##1[[1]], ToExpression[##1[[2]]]} & ) /@ 
          ##1[[2]]} & ) /@ temp; 
     temp = ({##1[[1]], ({##1[[1]], Func[##1[[2]]]} & ) /@ 
          ##1[[2]]} & ) /@ temp; If[OptionValue["JoinTerms"], 
      temp = ({##1[[1]], Apply[Times, ##1[[2]], {1}]} & ) /@ temp; 
       temp = ({##1[[1]], Plus @@ ##1[[2]]} & ) /@ temp; ]; 
     Apply[Rule, temp, {1}]]


LoadFIRETable[id_Integer,opt:OptionsPattern[]]:=Module[{fname,table},
fname=FileNameJoin[{$IntegralToolsFIREDirectory,TopoData[id]["Name"],TopoData[id]["Name"]~~".tables"}];
If[!FileExistsQ[fname],Return[$Failed]];
table=LoadFIRETable[fname,opt];
If[table==={},Return[{}]];
If[KeyExistsQ[TopoData[id],"VariablesToIP"],
table=MapAt[#/.TopoData[id]["VariablesToIP"]&,table,{All,2}];
];
Return[table];
]


ListFIREMasters[filename_String] := Module[{data, temp}, 
    data = Get[filename]; temp = Select[data[[1]], 
       Length[##1[[2]]] == 1 && ##1[[2,1,1]] == ##1[[1]] & ]; 
     temp = First /@ temp; (Cases[data[[2]], {##1, _}][[1,2]] & ) /@ temp]


ListFIREReduced[filename_String]:=Module[{data},
data=Get[filename];
Last/@(data[[-1]])
]


GetFIREKeys[filename_String,ints_List]:=Module[{str,keys,rr},
Module[{},str=OpenRead[filename];
ReadString[str,"},
    {"];
ReadString[str,"{"];
rr=ToExpression["{"~~ReadString[str,EndOfFile]][[1]];
       keys=Select[rr,MemberQ[ints,#[[2]]]&][[;;,1]];
];
Close[str];
Return[keys]
]


LoadTableFIREKey[filename_String,Fkeys_List]:=Module[{Hed,a,b,c,d,str},
Hed={};
str=OpenRead[filename];
While[True,
(* Making use of the structure of the .tables files*)
a=ReadString[str,"\n        {"];
b=ReadString[str,"\n            {"];
c=ReadString[str,"\n            }"];
d=ReadString[str,"\n        }"];

If[a===EndOfFile,Break[]];
b=StringDelete[b,{"{",",",WhitespaceCharacter}];
c=c~~"}";
If[MemberQ[Fkeys,b],AppendTo[Hed,{b,c}]];
];
Return[Hed];
];


GetFIREKeyTable[filename_String]:=Module[{str},
str=OpenRead[filename];
ReadString[str,"},
    {"];
ReadString[str,"{"];
Return["{"~~ReadString[str,EndOfFile]];
]


Options[LoadFIRETableByIntegral]={"JoinTerms"-> True,"ApplyFunction"-> Identity,"Head"-> $FIREIntHead};
LoadFIRETableByIntegral[filename_String,ints_List,OptionsPattern[]]:=Module[{keyMap,keysToTake,toret},
keyMap=MapAt[ToString,ToExpression[GetFIREKeyTable[filename]][[1]],{All,1}];
keysToTake=Select[keyMap,MemberQ[ints,#[[2]]]&][[;;,1]];
keyMap=Association[Rule[#[[1]],OptionValue["Head"]@@#[[2]]]&/@keyMap];
toret=ToExpression[LoadTableFIREKey[filename,keysToTake]];
toret={ToString[#[[1]]],If[#[[2]]=={},0,({ToString[#1],ToExpression[#2]})&@@@#[[2]]]}&/@toret/.keyMap;
If[OptionValue["JoinTerms"], 
 toret = MapAt[Total[Times@@@#]&,toret,{All,2}]]; 
Return[Apply[Rule, toret, {1}]]
]


TableContainsIntegralsQ[filename_String,ints_List]:=If[FileExistsQ[filename],ContainsAll[ListFIREReduced[filename],ints],False];


ReadFToolOutput[filename_String]:=
Module[{toret},
toret=StringCases[Import[filename,"String"],Longest["{"~~__]];
(* The 0 rules are not written in a readable format.*)
toret=StringReplace[toret,"-> ,"->"-> 0 ,"];
toret=DeleteCases[ToExpression[toret][[1]],{}];
Return[toret]
]


ClearAll[RuleFromRESTRICTIONS];
Options[RuleFromRESTRICTIONS] = {"ID" -> 1, "Head" -> Automatic};
RuleFromRESTRICTIONS[{}, OptionsPattern[]] := {};
RuleFromRESTRICTIONS[rest_, OptionsPattern[]] := Module[{size = Length[rest[[1]]], head, restr},
(* catch the case that has only 0's. This is a trivial restriction *)
restr = DeleteCases[rest,{Repeated[0]}];
  If[OptionValue["Head"] === Automatic,
   head = $IntHead[OptionValue["ID"], #] &,
   head = OptionValue["Head"];
   ];
  Return[head[Table[Pattern[Evaluate@ToExpression["a" ~~ ToString[i]], Blank[]], {i, 1, size}]] /; Evaluate[Reduce@Not[And @@ Table[Or @@ (Global`a @@ # > 0 & /@ Position[r, -1]), {r, restr}] /. Global`a[i_] :> ToExpression["a" ~~ ToString[i]]]] ->  0] ;
  ]


SelectByRESTRICTIONS[iList_List,restrictions_List]:=Module[{},
Return[Select[iList,!ZeroOnRESTRICTIONSQ[restrictions][#]&]]
]


ZeroOnRESTRICTIONSQ[Restr_List][$IntHead[id_,sector:{Repeated[0|1]}]]:=ZeroOnRESTRICTIONSQ[Restr][sector];
ZeroOnRESTRICTIONSQ[Restr_List][sector:{Repeated[0|1]}]:=Module[{toret=False},
Do[
If[Reduce[sector . r>= 0],toret=True; Break[];];
,{r,Restr}];
Return[toret];
];


SubRESTRICTIONQ[restr1_:{(0|-1)..},restr2_:{(0|-1)..}]:=Module[{Private`ii=1},If[Length[restr1]!=Length[restr2],Return[False]];While[Private`ii<=Length[restr1],If[restr1[[Private`ii]]>restr2[[Private`ii]],Return[False];];Private`ii++;];Return[True];]


GetSpanningRESTRICTIONS[restrictionList_List]:=Module[{restrictionGather=SortBy[GatherBy[DeleteDuplicates[restrictionList],Total],Total@*First]},
Return@Flatten[Table[
Select[restrictionGather[[i]],
Function[{res},AllTrue[Flatten[restrictionGather[[i+1;;-1]],1],!SubRESTRICTIONQ[res,#]&]]]
,{i,1,Length[restrictionGather]}],1];
]


RESTRICTIONSAnd[rest___]:=Join@@List[rest];


RESTRICTIONSOr[]:={};
RESTRICTIONSOr[r1_]:=r1;
RESTRICTIONSOr[r1_,r2_]:=GetSpanningRESTRICTIONS[Flatten[Outer[Sign@*Plus,r1,r2,1],1]];
RESTRICTIONSOr[r1_,r2_,rest__]:=RESTRICTIONSOr[RESTRICTIONSOr[r1,r2],rest];


(* Function provided by A. Smirnov *)
Options[RuleSum2List]={"Head"->$IntHead};
RuleSum2List[relation_List,o:OptionsPattern[]]:=RuleSum2List[relation,OptionsPattern[]]&/@relation;
RuleSum2List[HoldPattern[int_->0],OptionsPattern[]]:=int->{};
RuleSum2List[relation_Rule,OptionsPattern[]] :=
  Module[{temp}, temp = Collect[Last[relation], OptionValue["Head"]];
   temp = If[Head[temp] === Plus, List @@ temp, {temp}];
   temp = If[Head[##] === OptionValue["Head"],
       {1, ##},
       {## /. OptionValue["Head"][___] -> 1, Cases[##, OptionValue["Head"][___]][[1]]}
       ] & /@ temp;
   temp = {Plus @@ ##[[2]], ##[[1]]} & /@
     Reap[Sow[##[[1]], ##[[2]]] & /@ temp, _, List][[2]];
   Rule[First[relation], temp]];


KillDenominatorFIRE[x_] := Expand[Together[PolynomialLCM @@ Denominator /@ (List @@ x)*x]]


(* ::Section:: *)
(*Functionalities related to kira*)


ImportKiraIntegrals[filename_]:=ToExpression@StringSplit[Import[filename,"String"],"\n"];


Options[KiraIBPString]={"Head"-> Global`G};
KiraIBPString[expr_,OptionsPattern[]]:=Module[{ints=Cases[expr,_Global`IndexShift,Infinity]//Union,toret},
toret={ToString@(InputForm[#]/.Global`IndexShift-> OptionValue["Head"])<>"*("<>ToString@InputForm@(Expand@Coefficient[expr,#]/.Global`a[i_]:> ToExpression["a"<>ToString[i-1]])<>")"}&/@ints;
toret=StringJoin@@@toret;
toret=StringRiffle[toret,{"","\n",""}];
toret=StringDelete[toret," "];
Return[toret]
]


KiraIntegralfamiliesString[id_]:=Module[{ToKiraForm},
ToKiraForm[expr_]:=expr/.{f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]],LorentzVectorUtils`IP:>Times};
StringJoin[
"  - name: \"",TopoData[id]["Name"],"\"\n",
"    loop_momenta: ",StringRiffle[ToKiraForm@TopoData[id]["Internal"],{"[",",","]"}],"\n",
"    top_level_sectors: ",StringRiffle[TopoData[id]["TopSector"],{"[\"b","","\"]"}],"\n",
StringRiffle["      - [ \""~~ToString[InputForm[#]]~~"\" ,"~~"0]"&/@ToKiraForm[TopoData[id]["Propagators"]],{"    propagators:\n","\n",""}]
]
]


KiraKinematicsString[id_]:=Module[{ToKiraForm},
ToKiraForm[expr_]:=expr/.{f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]],LorentzVectorUtils`IP:>Times};
StringJoin[{
"kinematics:\n",
"  incoming_momenta: ",StringRiffle[TopoData[id]["External"]//ToKiraForm,{"[",",","]"}],"\n",
"  outgoing_momenta: []\n",
"  kinematic_invariants:\n",
StringRiffle[TopoData[id]["Variables"],{"      - [",",0]\n      - [",",0]"}],"\n",
"  scalarproduct_rules:\n",
StringRiffle[TopoData[id]["Replacements"]/.HoldPattern[LorentzVectorUtils`IP[a_,b_]->c_]:>"      - [["~~ToString[ToKiraForm[a]]~~","~~ToString[ToKiraForm[b]]~~"],"~~ToString[InputForm[c]]~~"]",{"","\n",""}]
}]
]


Options[KiraJobString]={"r"->9,"s"->4,"d"->2};
KiraJobString[id_,OptionsPattern[]]:=Module[{},
StringJoin[{
"jobs:
 - reduce_sectors:
    reduce:
     - {sectors: ",
StringRiffle[TopoData[id]["TopSector"],{"[b","","],"}],
" r: ",ToString@OptionValue["r"],",",
" s: ",ToString@OptionValue["s"],",",
" d: ",ToString@OptionValue["d"],"}\n",
"    select_integrals:\n",
"     select_mandatory_list:
      - ["~~TopoData[id]["Name"]~~",ToReduce]\n",
"    set_zero_sectors: {files: [zeroSectors]}\n",
"    run_initiate: true
    run_triangular: true
    run_back_substitution: true\n",
" - kira2math:\n",
"     target:
      - ["~~TopoData[id]["Name"]~~",ToReduce]\n"
    }
    ]
]


Options[PrepareKira]={};
PrepareKira[id_,OptionsPattern[]]:=Module[{tmpdir,
KiraDir=FileNameJoin[{$IntegralToolsKiraDirectory,TopoData[id]["Name"]}],
configDir
},
configDir=FileNameJoin[{KiraDir,"config"}];
(* Create Config folder *)
Quiet[CreateDirectory[configDir,CreateIntermediateDirectories->True],{CreateDirectory::eexist}];
Export[FileNameJoin[{configDir,"integralfamilies.yaml"}],"integralfamilies:\n"~~KiraIntegralfamiliesString[id],"String"];
Export[FileNameJoin[{configDir,"kinematics.yaml"}],KiraKinematicsString[id],"String"];
Export[FileNameJoin[{KiraDir,"jobs.yaml"}],KiraJobString[id],"String"];
]


Options[ExportIntegralsKira]={"NameFunction"->("ToReduce"&)}
ExportIntegralsKira[iList_List,OptionsPattern[]]:=Module[{families=ListIntFamilies[iList],folder,head},
Do[
folder=FileNameJoin[{$IntegralToolsKiraDirectory,TopoData[fam]["Name"]}];
Print[folder];
head=ToExpression[TopoData[fam]["Name"]];
If[DirectoryQ[folder],
Export[FileNameJoin[{folder,OptionValue["NameFunction"][fam]}],StringRiffle[Cases[iList,$IntHead[fam,inds_]:>head@@inds],"\n"],"String"]
]
,{fam,families}];
Return[];
]


(* ::Section:: *)
(*Functionalities related to IBP*)


Options[ToIndexShift]={"Head"-> Global`propagator,"FIREHead"->Global`IndexShift,"Dimension"-> Global`numOfProps,"DoCheck"-> False};
ToIndexShift[expr_,OptionsPattern[]]:=Module[{SingleFactorToIndexShift,invPropagator,toret,ToCheck},
SingleFactorToIndexShift[e1_]:=Global`IndexShift@@(-Exponent[e1,OptionValue["Head"]/@Range[OptionValue["Dimension"]]])(e1/.OptionValue["Head"][i_]:> 1);
toret=expr/.Power[OptionValue["Head"][i_],n_]/;n<0:> 1/Power[invPropagator[i],n];
toret=MonomialList[toret,Join[OptionValue["Head"]/@Range[OptionValue["Dimension"]],invPropagator/@Range[OptionValue["Dimension"]]]];
toret=toret/.invPropagator[i_]:> 1/OptionValue["Head"][i];
toret=Total[SingleFactorToIndexShift/@toret];
If[OptionValue["DoCheck"],
ToCheck=expr-(toret/.Global`IndexShift[inds___]:>  (1/Times@@((OptionValue["Head"]/@Range[OptionValue["Dimension"]])^List[inds])));
ToCheck=Simplify[ToCheck];
If[!(ToCheck===0),
Print["Check failed!"];
Print[ToCheck],
Print["Check passed!"];
]
];
Return[toret];
]


Options[ProduceSingleIBP]={"Head"-> Global`propagator,"IndexVariable"-> Global`a};
ProduceSingleIBP[v1_,v2_,props_,OptionsPattern[]]:=Module[{toprp=LorentzVectorUtils`ReplacementRulesFromPropagators[props,"Overcomplete"->True]},
Return[ToIndexShift[(Total@Table[-OptionValue["IndexVariable"][i]/ OptionValue["Head"][i]*LorentzVectorUtils`vdv[v1,v2][props[[i]]],{i,1,Length[props]}]/.toprp)+Global`d*Boole[SameQ[v1,v2]],
"Head"-> OptionValue["Head"],
"Dimension"-> Length[props]]]
]


GetIBP[int_,ext_,prop_,rep_]:=Module[{},
Return[ProduceSingleIBP[#1,#2,prop]&@@@Union@@Outer[List,Join[ext,int],int]/.rep];
]


GetIBPNoD[int_, ext_, prop_, repl_] := Module[{ibplist = {}, uneqPairs, divergences, travediv},
  (* normal ibps*)
  ibplist = ProduceSingleIBP[#1, #2, prop] & @@@ Select[Union @@ Outer[List, Join[ext, int], int], ! (SameQ @@ #) &];
  divergences = ProduceSingleIBP[#, #, prop] & /@ int;
  travediv = 1/Length[int]*Total[divergences];
  ibplist = Join[ibplist, Simplify[Drop[divergences, -1] - travediv]] /. repl;
  Return[ibplist];
  ]


(* ::Input::Initialization:: *)
Options[ProduceSingleLI]={"Head"-> Global`propagator,"IndexVariable"-> Global`a};
ProduceSingleLI[v1_,v2_,props_,int_,OptionsPattern[]]:=Module[{toprp=LorentzVectorUtils`ReplacementRulesFromPropagators[props]},
ToIndexShift[Sum[-OptionValue["IndexVariable"][i]/ OptionValue["Head"][i]*Sum[(LorentzVectorUtils`IP[v1,iv]LorentzVectorUtils`vdv[v2,iv][props[[i]]]-LorentzVectorUtils`IP[v2,iv]LorentzVectorUtils`vdv[v1,iv][props[[i]]]),{iv,int}],{i,1,Length[props]}]/.toprp,"Head"-> OptionValue["Head"],"Dimension"-> Length[props]]
]


GetLI[int_,ext_,prop_,rep_]:=Module[{},
Return[ProduceSingleLI[#1,#2,prop,int]&@@@Subsets[ext,{2}]/.rep];
]


(* ::Section:: *)
(*Functionalities related to pySecDec*)


BalancedBracketQ[string_]:=StringCount[string,"("]==StringCount[string,")"];
StringIndent[expr_String]:=StringRiffle[StringSplit[expr,"\n"],{"\t","\n\t",""}];


pySecDecPropagatorString[propagators_List]:=StringReplace[ToString/@CForm/@propagators,"Power("~~(a__/;BalancedBracketQ[a])~~",2)":> "("~~a~~")**2"];


pySecDecReplacementsString[replacements_List]:=Module[{Toret},
Toret=replacements/.Rule-> List;
Toret=ToString/@(CForm/@Toret);
Toret=StringReplace[Toret,"Power("~~(a__/;BalancedBracketQ[a])~~",2)":> a~~"*"~~a];
Toret=StringReplace[Toret,"List("~~(a__/;BalancedBracketQ[a])~~","~~(b__/;BalancedBracketQ[b])~~")":> "('"~~a~~"',"~~If[StringMatchQ[b,NumberString],b,"'"~~b~~"'"]~~")"];
Return[Toret]
]


pySecDecLoopIntegralFromPropagatorsString[internal_List,external_List,propagators_List,replacements_List,indices:{Repeated[_Integer]}]:=Module[{QuoteRiffle,CodeString},
QuoteRiffle[list_List]:=StringRiffle[list,{"[ '","' , '","' ],\n"}];
CodeString=
StringJoin[
{"LoopIntegralFromPropagators(","\n",
"\tloop_momenta = " , StringRiffle[internal,{"[ '","' , '","' ],\n"}],
"\texternal_momenta = " , StringRiffle[external,{"[ '","' , '","' ],\n"}],
"\tpropagators  = " , StringRiffle[pySecDecPropagatorString[propagators],{"[ '","' , '","' ],\n"}],
"\tpowerlist  = " , StringRiffle[indices,{"[ "," , "," ],\n"}],
"\treplacement_rules = " , StringRiffle[pySecDecReplacementsString[replacements],{"[ "," , "," ],\n"}],
")"}
];
Return[CodeString];
]


pySecDecLoopIntegralFromPropagatorsString2[internal_List,external_List,propagators_List,replacements_List,indices:{Repeated[_Integer]}]:=Module[{QuoteRiffle,CodeString},
QuoteRiffle[list_List]:=StringRiffle[list,{"[ '","' , '","' ],\n"}];
Print["Warning: We hardcoded massless kinematics in an attempt to fix CForm producing expressions not readable by python"];
CodeString=
StringJoin[
{"LoopIntegralFromPropagators(","\n",
"\tloop_momenta = " , StringRiffle[internal,{"[ '","' , '","' ],\n"}],
"\texternal_momenta = " , StringRiffle[external,{"[ '","' , '","' ],\n"}],
"\tpropagators  = " , StringRiffle[pySecDecPropagatorString[propagators],{"[ '","' , '","' ],\n"}],
"\tpowerlist  = " , StringRiffle[indices,{"[ "," , "," ],\n"}],
"\treplacement_rules = [ ('p1*p1',0) , ('p1*p2','s/2') , ('p1*p3','(-s - t)/2') , ('p2*p2',0) , ('p2*p3','t/2') , ('p3*p3',0) ]\n",
")"}
];
Return[CodeString];
]


Options[pySecDecLoopPackageString]={"LoopIntegralName"->"li"};
pySecDecLoopPackageString[name_String,variables_List,prefactor_,order_Integer,formOptLevel:0|1|2|3|4,decompositionMethod:"iterative"|"geometric",contourDeformation_?BooleanQ,OptionsPattern[]]:=Module[{CodeString},
CodeString=
StringJoin[
{"loop_package(","\n",
"name = '" , name,"',\n",
"loop_integral = " , OptionValue["LoopIntegralName"],",\n",
"real_parameters = " , StringRiffle[variables,{"[ '","' , '","' ]"}],",\n",
"additional_prefactor = '" , prefactor,"',\n",
"requested_orders = [" , ToString[order],"],\n",
"form_optimization_level = " , ToString[formOptLevel],",\n",
"decomposition_method = '" , decompositionMethod,"',\n",
"contour_deformation = " , ToString[contourDeformation],",\n",
")"}
];
Return[CodeString];
]


(*
pySecDecReplacementsString[IP[a_,b_]->c_]:=Module[{},
	"('"~~ToString[InputForm[a]]~~"*"~~ToString[InputForm[b]]~~"','"~~ToString[InputForm[c]]~~"')"
]*)


Options[pySecDecGenerateString]={"pyhtonEnv"->"#!/usr/bin/env python3"};
pySecDecGenerateString[internal_List,external_List,propagators_List,replacements_List,variables_List,indices:{Repeated[_Integer]},order_Integer,formOptLevel:0|1|2|3|4,decompositionMethod:"iterative"|"geometric",contourDeformation_?BooleanQ,OptionsPattern[]]:=Module[{CodeString},
CodeString=OptionValue["pyhtonEnv"]<>"\n";
CodeString=CodeString~~"import pySecDec as psd\n\n";
CodeString=CodeString~~"if __name__ == \"__main__\":\n\n";
CodeString=CodeString<>
StringIndent[StringJoin[{
"li = psd.",pySecDecLoopIntegralFromPropagatorsString[internal,external,propagators,replacements,indices],"\n\n",
"psd.",pySecDecLoopPackageString["Int_"<>IndicesToString[indices],variables,"exp ("~~ToString[Length[internal]]~~"*S.EulerGamma*eps)",order,formOptLevel,decompositionMethod,contourDeformation]
}]];
Return[CodeString]
]


Options[pySecDecIntegrateString]={
"pyhtonEnv"->"#!/usr/bin/env python3",
"minn"->10^6,
"verbosity"->2,
"maxeval"->10000000,
"epsrel"->0.001,
"Integrator"->"Qmc"};
pySecDecIntegrateString[libraryPath_String,points:{Repeated[{RepeatedNull[_?NumericQ]}]},OptionsPattern[]]:=Module[{CodeString},
CodeString=OptionValue["pyhtonEnv"]<>"\n";
CodeString=CodeString<>"from pySecDec.integral_interface import IntegralLibrary
import sympy as sp\n";
CodeString=CodeString<>"from pySecDec.integral_interface import series_to_mathematica\n\n";
CodeString=CodeString<>"if __name__ == \"__main__\":\n\n";
CodeString=CodeString<>"\tintegral = IntegralLibrary('"~~libraryPath~~"')\n";
If[OptionValue["Integrator"]==="Qmc",    CodeString = CodeString<>StringRiffle[ #<>" = "<>ToString[OptionValue[#]]&/@{"verbosity","minn","maxeval","epsrel"},{"\tintegral.use_Qmc(",", ",")\n"}]];
(* Integration String *)
CodeString=CodeString<>"\tpoints = "<>StringRiffle[StringRiffle[#,{"[",",","]"}]&/@points,{"[",",","]"}]<>"\n";
CodeString=CodeString<>"\tvalList =[]\n";
CodeString=CodeString<>"\tfor point in points:
\t\t# integrate
\t\tstr_integral_without_prefactor, str_prefactor, str_integral_with_prefactor = integral(real_parameters = point)
\t\t# convert to mathematica format. First entry is value, second is error 
\t\tcoord = '{'+str('{'+','.join(map(str, point))+'}')+','+series_to_mathematica(str_integral_with_prefactor)[0]+','+series_to_mathematica(str_integral_with_prefactor)[1]+'}'
\t\tvalList.append(coord)\n";
CodeString=CodeString<>"\toutString='{'+','.join(valList)+'}'
\tout_file = open(\"Output.txt\",\"w\")
\tout_file.write(outString)
\tout_file.close()";

Return[CodeString]
]


Options[PreparePySecDec]={"form_optimization_level"->4,"decomposition_method"->"geometric","contour_deformation"->False};
PreparePySecDec[int_Int,espOrder_Integer,OptionsPattern[]]:=Module[{id=IntFamily[int],ToFireForm,codeString,dir},
ToFireForm[expr_]:=expr/.{f_[x_Integer]:>ToExpression[ToString[f]~~ToString[x]],LorentzVectorUtils`IP:>Times};
codeString=pySecDecGenerateString@@(
ToFireForm[{
TopoData[id]["Internal"],
TopoData[id]["External"],
TopoData[id]["Propagators"],
TopoData[id]["Replacements"],
TopoData[id]["Variables"],
IntIndices[int],
espOrder,
OptionValue["form_optimization_level"],
OptionValue["decomposition_method"],
OptionValue["contour_deformation"]
}]//Factor);
dir=FileNameJoin[{$IntegralToolsPySecDecDirectory,TopoData[id]["Name"],IntToString[int]}];
If[!DirectoryQ[dir],CreateDirectory[dir]];
Export[FileNameJoin[{dir,"generate.py"}],codeString,"String"];
]


(* ::Section::Closed:: *)
(*End*)


End[];


EndPackage[];
