(* ::Package:: *)

$RationalNumbers=DeleteDuplicates[Rational@@@Flatten[Table[Table[{k,n-k},{k,1,n-1}],{n,1,10}],1]];
$RationalNumbers=Flatten[{0,Transpose[{$RationalNumbers,-$RationalNumbers}]}];


$EpsilonVariable=Global`ep;


$Numeric={7919,17389};


bldM[a___]:=System`BlockDiagonalMatrix[List[a]];


(* ::Title:: *)
(*Misc Tools*)


PassRuleSequence[fun_,subFun_,extra_:{}]:=Sequence@@FilterRules[DeleteDuplicatesBy[First][Join[extra,Options[fun]]],Options[subFun]];


RationalComplexity[expr_]:=Max[Abs[Cases[{expr},x:_Rational|_Integer:>Sequence[Numerator[x],Denominator[x]],Infinity]]]


MatrixResidue[A_,x_List]:=Module[{},Map[Residue[#1,x]&,A,{2}]];


MatrixToPoleData[matr_,x_]:=Module[{poleData,ld},
poleData=MatrixPoleInfo[matr,x];
If[!AllTrue[poleData[[;;,2]],#<=1&],Print["Matrix has higher-order poles."];Return[$Failed];];
ld=Association[#->MatrixResidue[matr,{x,#}]&/@poleData[[;;,1]]];
Return[ld];
]


FromPoleData[poleData_,x_]:=Module[{},
Return[Total[KeyValueMap[#2/(x-#1)&,KeyDrop[poleData,Infinity]]]];
]


(* case where the matix is passed explicitely *)
UpdateLogarithmicSystemTrafo[msystem_?AssociationQ,traf_?SquareMatrixQ]:=Module[{trafInv},
trafInv=FiniteFlow`FFInverse[traf];
Return[trafInv . # . traf&/@msystem];
]


Options[UpdateLogarithmicSystem]={"Together"->True};
UpdateLogarithmicSystem[msystem_?AssociationQ,P_?SquareMatrixQ,{x1_,x2_},OptionsPattern[]]:=Module[{r1,r2,toret,r1Transformed,r2Transformed,nn=Length[P],id,mxi1,mxi2},
id=IdentityMatrix[nn];
{r1,r2}=msystem/@{x1,x2};
(* residue was not present *)
If[Head[r1]===Missing,r1=ConstantArray[0,{nn,nn}]];
If[Head[r2]===Missing,r2=ConstantArray[0,{nn,nn}]];

mxi1=If[Complement[Keys[msystem],{x1,x2,Infinity}]=={},ConstantArray[0,{nn,nn}],Sum[(msystem[xi](x1 - x2))/(x1 - xi) ,{xi,Complement[Keys[msystem],{x1,x2,Infinity}]}]];
mxi2=If[Complement[Keys[msystem],{x1,x2,Infinity}]=={},ConstantArray[0,{nn,nn}],Sum[ (msystem[xi]*(x2 - x1))/(x2 - xi),{xi,Complement[Keys[msystem],{x1,x2,Infinity}]}]];

r1Transformed=r1-P+P . r1+P . r2-r1 . P-r2 . P+P . mxi1 . (id-P);
r2Transformed=r2+P-P . r1-P . r2+r1 . P+r2 . P+(id-P) . mxi2 . P;

toret=Association[{x1->r1Transformed,x2->r2Transformed}];
toret=Association[toret,Association@Table[xi->(id +(-x1+x2)/(x1-xi)P) . msystem[xi] . (id+(-x2+x1)/(x2-xi)P),{xi,Complement[Keys[msystem],{x1,x2,Infinity}]}]];
(* pole at infinity *)
toret=Association[toret,Infinity->-Total[Values[toret]]];
If[OptionValue["Together"],toret=Map[Together,toret];];

Return[toret];
];


UpdateLogarithmicSystem[msystem_?AssociationQ,P_?SquareMatrixQ,{\[Infinity],x2_},OptionsPattern[]]:=Module[{r2,toret,r2Transformed,nn=Length[P],id,mxi2},
id=IdentityMatrix[nn];
r2=msystem[x2];

(* residue was not present *)
If[Head[r2]===Missing,r2=ConstantArray[0,{nn,nn}]];


mxi2=If[Complement[Keys[msystem],{x2,Infinity}]=={},ConstantArray[0,{nn,nn}],Sum[ msystem[xi]/(x2-xi),{xi,Complement[Keys[msystem],{x2,Infinity}]}]];
r2Transformed=r2+P-P . r2+r2 . P+(id-P) . mxi2 . P;

toret=Association[{x2->r2Transformed}];
toret=Association[toret,Association@Table[xi->(id-(1-xi+x2)P) . msystem[xi] . (id+(1-xi+x2)/(xi-x2) P),{xi,Complement[Keys[msystem],{x2,Infinity}]}]];
(* pole at infinity *)
toret=Association[toret,Infinity->-Total[Values[toret]]];
If[OptionValue["Together"],toret=Map[Together,toret];];
Return[toret];
];


UpdateLogarithmicSystem[msystem_?AssociationQ,P_?SquareMatrixQ,{x1_,\[Infinity]},OptionsPattern[]]:=Module[{r1,toret,r1Transformed,nn=Length[P],id,mxi1},
id=IdentityMatrix[nn];
r1=msystem[x1];

(* residue was not present *)
If[Head[r1]===Missing,r1=ConstantArray[0,{nn,nn}]];

mxi1=If[Complement[Keys[msystem],{x1,Infinity}]=={},ConstantArray[0,{nn,nn}],Sum[ msystem[xi]/(x1-xi) ,{xi,Complement[Keys[msystem],{x1,Infinity}]}]];
r1Transformed=r1-P+P . r1-r1 . P+P . mxi1 . (id-P);
toret=Association[{x1->r1Transformed}];
toret=Association[toret,Association@Table[xi->(id-((1+x1-xi)/(x1-xi))P) . msystem[xi] . (id-(1+x1-xi)P),{xi,Complement[Keys[msystem],{x1,Infinity}]}]];
(* pole at infinity *)
toret=Association[toret,Infinity->-Total[Values[toret]]];
If[OptionValue["Together"],toret=Map[Together,toret];];
Return[toret];
];


MatrixPolePositions[matr_?SquareMatrixQ,x_]:=Flatten[x/.Solve[#==0]&/@Select[matr//MatrixDenominators,!FreeQ[#,x]&]]


MatrixPoleInfo[matr_,var_]:=Module[{
pp=Flatten[var/.Solve[#==0]&/@Select[MatrixDenominators[matr],!FreeQ[#,var]&]],
toret
},
toret={#,MatrixPoleOrder[matr,{var,#}]}&/@pp;
toret=Join[toret,{{Infinity,2+Max[Flatten[Exponent[Series[matr,var->Infinity],var,Max]]]}}]
]


ReconstructAffine[{x1_,f1_},{x2_,f2_}]:={(f2*x1-f1*x2)/(x1-x2),(f1-f2)/(x1-x2)};


Options[EigenvaluesAffine]={"NumPoint"->$Numeric};
EigenvaluesAffine[matr_?SquareMatrixQ,var_,OptionsPattern[]]:=Module[{x1,x2,m1,m2,ev1,ev2,toret},
{x1,x2}=OptionValue["NumPoint"];
{m1,m2}={matr/.var->x1,matr/.var->x2};
{ev1,ev2}=Eigenvalues/@{m1,m2};
toret=Flatten[MapThread[{1,var} . ReconstructAffine[{x1,#1},{x2,#2}]&,Transpose[{{ev1,ev2}}]]];
toret=Simplify[toret];
Return[toret]; 
]


LogDEEigenvalueDataDiff[{{matr_?SquareMatrixQ,x_}}]:=Flatten[Abs[LogDEEigenvalueData[{{matr,x}}][[;;,1]]/.ep->0]]//Total


Options[JordanDecompositionAffineNumeric]={"NumPoint"->$Numeric[[1]]};
JordanDecompositionAffineNumeric[mat_?SquareMatrixQ,ep_,opt:OptionsPattern[]]:=Module[{nn=Length[mat],evs,reconstructEv,j,u},
evs=Union@Simplify@EigenvaluesAffine[mat,ep];
{j,u}=JordanDecomposition[mat/.ep->OptionValue["NumPoint"]];

(* lift the numeric eigenvalues back to analytic*)
reconstructEv[num_]:=Extract[evs,FirstPosition[evs/.ep->OptionValue["NumPoint"],num]];
u=MapAt[reconstructEv,u,Table[{i,i},{i,1,nn}]];

Return[{j,u}];
]


LeftInvariantSubspaceQ[matr_,subsp_]:=MatrixRank[Join[Transpose[matr . subsp],Transpose[subsp]]]-MatrixRank[subsp]===0;
RightInvariantSubspaceQ[matr_,subsp_]:=MatrixRank[Join[subsp . matr,subsp]]-MatrixRank[subsp]===0;


LeftSubspaceFromList[list_]:=Join@@@Transpose[list[[;;,2]]];
RightSubspaceFromList[list_]:=Join@@list[[;;,2]];


LeftEigenvaluesFromList[list_]:=Flatten[Table[#[[1]],Length[Transpose[#[[2]]]]]]&/@list;
RightEigenvaluesFromList[list_]:=Flatten[Table[#[[1]],Length[#[[2]]]]]&/@list;


Options[InvariantSubspacesLRNumeric]={"NumPoint"->$Numeric[[1]]};
InvariantSubspacesLRNumeric[matr_?SquareMatrixQ,OptionsPattern[]]:=Module[{
nn=Length[matr],
j,jT,u,jblocks={},
a=1,b=1,possibleIndices,
left,right
},

{j,u}=JordanDecompositionAffineNumeric[matr,Global`ep,"NumPoint"->OptionValue["NumPoint"]];
jT=Transpose[Inverse[j]] . Reverse[IdentityMatrix[nn]];

Do[If[
(* zero's mark the start of a new block*)
i==nn||u[[i,i+1]]===0,
AppendTo[jblocks,{a,b}];
{a,b}={i+1,i+1};,
b++;
],{i,1,nn}];

possibleIndices=Join[{{}},Range[#1,Range[#1,#2]]]&@@@jblocks;
possibleIndices=Flatten[Outer[List,Sequence@@possibleIndices,1],Length[possibleIndices]-1];
(* Remove the triavial invariant space *)
possibleIndices=MapAt[DeleteCases[#,{}]&,possibleIndices,{All}];
possibleIndices=DeleteCases[possibleIndices,{}];

(* Sort the blocks in the transposed matrix such that they are in the same order *)
jT=jT . IdentityMatrix[nn][[Flatten[Range@@@Reverse[jblocks]]]];

left=MapAt[{First[Diagonal[u][[#]]],j[[;;,#]]}&,possibleIndices,{All,All}];
right=MapAt[{First[Diagonal[u][[#]]],Transpose[jT[[;;,#]]]}&,possibleIndices,{All,All}];
Return[{left,right}]
]


Options[InvariantSubspacesLR]={"FiniteFlow"->True,"MaxPrimes"->500,"MaxDegree"->500};
InvariantSubspacesLR[matr_?SquareMatrixQ,OptionsPattern[]]:=Module[{
nn=Length[matr],
j,jT,u,jblocks={},
a=1,b=1,possibleIndices,
left,right
},

(* jordan decomposition of transpose follows trivially *)
If[OptionValue["FiniteFlow"]===True,
{j,u}=FFJordanDecompositonAffine[matr,Global`ep,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]];
jT=Transpose[FiniteFlow`FFInverse[j,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]]] . Reverse[IdentityMatrix[nn]];
,
{j,u}=JordanDecomposition[matr];
jT=Transpose[Inverse[j]] . Reverse[IdentityMatrix[nn]];
];

Do[If[
(* zero's mark the start of a new block*)
i==nn||u[[i,i+1]]===0,
AppendTo[jblocks,{a,b}];
{a,b}={i+1,i+1};,
b++;
],{i,1,nn}];

possibleIndices=Join[{{}},Range[#1,Range[#1,#2]]]&@@@jblocks;
possibleIndices=Flatten[Outer[List,Sequence@@possibleIndices,1],Length[possibleIndices]-1];
(* Remove the triavial invariant space *)
possibleIndices=MapAt[DeleteCases[#,{}]&,possibleIndices,{All}];
possibleIndices=DeleteCases[possibleIndices,{}];

(* Sort the blocks in the transposed matrix such that they are in the same order *)
jT=jT . IdentityMatrix[nn][[Flatten[Range@@@Reverse[jblocks]]]];

left=MapAt[{First[Diagonal[u][[#]]],j[[;;,#]]}&,possibleIndices,{All,All}];
right=MapAt[{First[Diagonal[u][[#]]],Transpose[jT[[;;,#]]]}&,possibleIndices,{All,All}];
Return[{left,right}]
]


Options[LeftInvariantSubspacesByEigenvalue]={"FiniteFlow"->True,"MaxPrimes"->500,"MaxDegree"->500};
LeftInvariantSubspacesByEigenvalue[matr_?SquareMatrixQ,evs_List,OptionsPattern[]]:=Module[{
nn=Length[matr],
j,jT,u,jblocks={},
a=1,b=1,possibleIndices,
left,right
},

{j,u}=FFJordanDecompositonByEigenvalueAffine2[matr,Global`ep,evs,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]];

nn=Length[u];

Do[If[
(* zero's mark the start of a new block*)
i==nn||u[[i,i+1]]===0,
AppendTo[jblocks,{a,b}];
{a,b}={i+1,i+1};,
b++;
],{i,1,nn}];

possibleIndices=Join[{{}},Range[#1,Range[#1,#2]]]&@@@jblocks;
possibleIndices=Flatten[Outer[List,Sequence@@possibleIndices,1],Length[possibleIndices]-1];
(* Remove the triavial invariant space *)
possibleIndices=MapAt[DeleteCases[#,{}]&,possibleIndices,{All}];
possibleIndices=DeleteCases[possibleIndices,{}];

Return[MapAt[{First[Diagonal[u][[#]]],j[[;;,#]]}&,possibleIndices,{All,All}]]
]


Options[RightInvariantSubspacesByEigenvalue]={"FiniteFlow"->True,"MaxPrimes"->200,"MaxDegree"->200};
RightInvariantSubspacesByEigenvalue[matr_?SquareMatrixQ,evs_List,opt:OptionsPattern[]]:=MapAt[Transpose,LeftInvariantSubspacesByEigenvalue[Transpose[matr],evs,opt],{All,All,2}];


Residue2[expr_,{x_,x0_}]:=Cancel[((x-x0)expr)]/.x->x0;


Options[BalanceEigenvaluesPoleData]={"FiniteFlow"->True,"MaxPrimes"->500,"MaxDegree"->500,"Verbose"->False,"Variable"->Global`x,"SpuriousPole"->False};
BalanceEigenvaluesPoleData[poleData_,OptionsPattern[]]:=Module[{
poleDataTrim,
lm,poleMatrices,poleMatrixInf,
InvRight,InvLeft,
toSel,pos,neg,nn=Length[poleData[[1]]],nRat,
eigenvaluePos,eigenvalueNeg,
candNeg,candPos,is,
invSpaceR,invSpaceL,
r1,r2,proj,tr,trInverse,inner,
evLeft,evRight,evs,evQuality,mL,mR,poleLeft,poleRight,isL,isR,
maxLeft,maxRight,rightSpace,
improvementPos,improvementNeg,
allPairs,thePair,pairFoundNumeric,pairFoundAnalytic,
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
NDet,
t0,tt0,
nTime=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[#], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]&,
TogetherFkt,InverseFkt,matrNew,
leftSpace,spuriousPolePos,polePositions,poleDataNew,
xx=OptionValue["Variable"]
},

{t0,tt0}={AbsoluteTime[],AbsoluteTime[]};


If[OptionValue["FiniteFlow"]===True,
(*TogetherFkt=FFTogether[#,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]]&;*)
TogetherFkt=Together;
InverseFkt=FiniteFlow`FFInverse[#,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]]&;,
TogetherFkt=Together;
InverseFkt=Inverse;
];

NDet[expr_]:=Det[expr/.$EpsilonVariable->$Numeric[[1]]];

polePositions=Keys[poleData];
VerbosePrint["Matrix has poles at ",polePositions];

(* We only have to consider poles that are not in epsilon form *)
poleDataTrim=Select[poleData,!ContainsOnly[EigenvaluesAffine[#,ep]/.ep->0,{0}]&];

evs=EigenvaluesAffine[#,ep]&/@Values[poleDataTrim];

If[!AllTrue[Flatten[evs],MatchQ[#,_.+_.*ep|_?IntegerQ]&],
Print["HERE"];
Print["Eigenvalues are ill-formed: ",evs];
Abort[];
];

(* if eigenvalues are in epsilon form, we are done. *)
If[poleDataTrim===Association[],
	VerbosePrint["All eigenvalues are proportional to epsilon"]; 
	Return[{poleData,IdentityMatrix[nn]}];
];

(* if all eigenvalues are half-integers we are stuck ans might need to rationalize *)
If[ContainsOnly[Flatten[Floor[Abs[evs/.ep->0]]],{0}],
	VerbosePrint["All eigenvalues are in [-1/2,1/2]"]; 
	Return[{poleData,IdentityMatrix[nn]}];
];

If[!AllTrue[Flatten[evs],MatchQ[#,Optional[_?NumberQ]+Optional[Optional[_?NumberQ]*Global`ep]]&],Print["Eigenvalues are ill-formed: ",evs];Return[$Failed];];

VerbosePrint["Eigenvalues: ",Thread[Keys[poleDataTrim]->evs]];

VerbosePrint["Preparation time: ",nTime[t0-AbsoluteTime[]]];
t0=AbsoluteTime[];

(* The round makes it ingnore the 1/2's. Eigenvalues corresponding to right space U are increased by 1,
 evs of VT are lowered by 1 *)

evQuality=Floor[Abs[#]]&;

VerbosePrint["Total eigenvalue complexity: ",Total[evQuality/@(evs/.ep->0),-1]];

improvementPos[subsp_]:=Module[
{evvs=Flatten[Table[#[[1]],Length[Transpose[#[[2]]]]]&/@subsp/.ep->0]},
Return[Total[evQuality/@evvs]-Total[evQuality/@(evvs+1)]]
];

improvementNeg[subsp_]:=Module[
{evvs=Flatten[Table[#[[1]],Length[#[[2]]]]&/@subsp]/.ep->0},
Return[Total[evQuality/@evvs]-Total[evQuality/@(evvs-1)]]
];

(* 
	===================== NUMERIC RUN =====================
*)

(* Compute invariant subspaces. Left and right spaces are related, so we can save some computation time. *)
VerbosePrint["Performing numeric run"];
VerbosePrint["Constructing invariant spaces (numeric) "];
{InvLeft,InvRight}={{},{}};

Do[
{isL,isR}=InvariantSubspacesLRNumeric[poleDataTrim[pole]];
InvLeft=Join[InvLeft,{pole,improvementPos[#],#}&/@isL];
InvRight=Join[InvRight,{pole,improvementNeg[#],#}&/@isR];
VerbosePrint["Done constructing invariant spaces for pole ",pole];
,{pole,Keys[poleDataTrim]}];


VerbosePrint["Number of eigenspaces {left,right}:",{Length@InvLeft,Length@InvRight}];

allPairs=Flatten[Outer[List,Sequence@@{InvLeft,InvRight},1],1];

(* exlude pairs that correspond to the same pole *)
allPairs=Select[allPairs,#[[1,1]]=!=#[[2,1]]&];

(* exclude spaces that don't have the same size *)
(*allPairs=Select[allPairs,Dimensions[LeftSubspaceFromList[#[[1,3]]]]===Reverse[Dimensions[RightSubspaceFromList[#[[2,3]]]]]&];*)

allPairs=Select[allPairs,Total[Length[#[[2]]]&/@#[[2,3]]]==Total[Dimensions[#[[2]]][[2]]&/@#[[1,3]]]&];

(* Sort the pairs for their potential for improvement. Drop all that don't improve *)
allPairs=Select[allPairs,#[[1,2]]+#[[2,2]]>0&];
allPairs=SortBy[allPairs,{-(#[[1,2]]+#[[2,2]]),Total[Length[#[[2]]]&/@#[[2,3]]]}&];

VerbosePrint["Considering ",Length[allPairs]," pairs of eigenspaces."];

Do[
	invSpaceL=LeftSubspaceFromList[ppair[[1,3]]];
	invSpaceR=RightSubspaceFromList[ppair[[2,3]]];
	
	inner=invSpaceR . invSpaceL;
	
	(* To construct a projector the invariant spaces cannot be orthogonal *)
	If[NDet[inner]===0,VerbosePrint["Skipping subspaces that are partially orthogonal."]; Continue[];];
	VerbosePrint["Improvement ",{ppair[[1,2]],ppair[[2,2]]}];
	VerbosePrint["Dimension of space: ",Dimensions[invSpaceR][[1]]];
	
	poleLeft=ppair[[1,1]];
	poleRight=ppair[[2,1]];
	
	VerbosePrint["Pole left: ",poleLeft," Eigenvalues: ",LeftEigenvaluesFromList[ppair[[1,3]]]];
	VerbosePrint["Pole right: ",poleRight," Eigenvalues: ",RightEigenvaluesFromList[ppair[[2,3]]]];
	
	thePair=ppair;
	Goto[pairFoundNumeric];
,{ppair,allPairs}];

VerbosePrint["No match found!"];

(* 
	===================== SPURIOUS POLE =====================
*)
If[!OptionValue["SpuriousPole"],	
	VerbosePrint["Cannot balance without introducing spurious pole."]; 
	Return[{poleData,IdentityMatrix[nn]}];
];

(* Pick a new position for the pole *)
spuriousPolePos=DeleteCases[$RationalNumbers,Alternatives@@polePositions][[1]];
VerbosePrint["Introducing a spurious pole at position ",spuriousPolePos];

(* find the space that is worst numerically *)

{maxLeft,maxRight}={First@MaximalBy[InvLeft,#[[2]]&],First@MaximalBy[InvRight,#[[2]]&]};

VerbosePrint["Comparing ",maxLeft[[2]]," ",maxRight[[2]]];

If[maxRight[[2]]<=maxLeft[[2]],
	{poleLeft,leftSpace}=maxLeft[[{1,3}]];

	VerbosePrint["Raising pole at positon ",poleLeft];
	evLeft=Union[Flatten[LeftEigenvaluesFromList[leftSpace]]];

	mL=poleDataTrim[poleLeft];
	VerbosePrint["Constructing invariant spaces (analytic) "];
	InvLeft={poleLeft,improvementPos[#],#}&/@LeftInvariantSubspacesByEigenvalue[mL,evLeft,"FiniteFlow"->True];
	VerbosePrint["Done constructing invariant spaces for pole ",poleLeft];
	(* find the left space that is worst, analytically *)
	invSpaceL=LeftSubspaceFromList[First[MaximalBy[InvLeft,#[[2]]&]][[3]]];
	(* We use a simple space. TODO: There might be unfortunate cases where this is orthogonal to the other space, however we don't just want to make it too complicated *)
	(*invSpaceR=Table[KroneckerDelta[i,j],{i,1,Dimensions[invSpaceL][[2]]},{j,1,Dimensions[invSpaceL][[1]]}];*)
	invSpaceR=Transpose[invSpaceL];
	
	inner=invSpaceR . invSpaceL;
	{r1,r2}={spuriousPolePos,poleLeft};
	,
	(* otherwise the same but for the right space*)
	{poleRight,rightSpace}=maxRight[[{1,3}]];
	VerbosePrint["Lowering pole at positon ",poleRight];
	(*Print[InvRight];*)
	evRight=Union[Flatten[RightEigenvaluesFromList[rightSpace]]];
	mR=poleDataTrim[poleRight];
	VerbosePrint["Constructing invariant spaces (analytic) "];
	InvRight={poleRight,improvementPos[#],#}&/@RightInvariantSubspacesByEigenvalue[mR,evRight,"FiniteFlow"->True];
	VerbosePrint["Done constructing invariant spaces for pole ",poleRight];
	(* find the right space that is worst, analytically *)
	invSpaceR=RightSubspaceFromList[First[MaximalBy[InvRight,#[[2]]&]][[3]]];
	(* We use a simple space *)
	(*invSpaceL=Transpose@Table[KroneckerDelta[i,j],{i,1,Dimensions[invSpaceR][[1]]},{j,1,Dimensions[invSpaceR][[2]]}];*)
	invSpaceL=Transpose[invSpaceR];
	
	inner=invSpaceR . invSpaceL;
	{r1,r2}={poleRight,spuriousPolePos};
];


Goto[pairFoundAnalytic];

(* 
	===================== ANALYTIC RUN =====================
*)

(* If we found a pair of subspaces we continue here *)
Label[pairFoundNumeric];

VerbosePrint["Numeric run time: ",nTime[t0-AbsoluteTime[]]];
t0=AbsoluteTime[];

VerbosePrint["Now looking for an analytic match."];
evLeft=Union[Flatten[LeftEigenvaluesFromList[thePair[[1,3]]]]];
evRight=Union[Flatten[RightEigenvaluesFromList[thePair[[2,3]]]]];

(* Find the corresponding matrices. Here we don't have to look at all residues. *)
mL=poleDataTrim[poleLeft];
mR=poleDataTrim[poleRight];

VerbosePrint["Constructing invariant spaces (analytic) "];

(* TODO: We also have acces to the info of the size of the eigenspaces, but this is a minor improvement *)

InvLeft={poleLeft,improvementPos[#],#}&/@LeftInvariantSubspacesByEigenvalue[mL,evLeft,"FiniteFlow"->OptionValue["FiniteFlow"]];
VerbosePrint["Done constructing invariant spaces for pole ",poleLeft];
InvRight={poleRight,improvementNeg[#],#}&/@RightInvariantSubspacesByEigenvalue[mR,evRight,"FiniteFlow"->OptionValue["FiniteFlow"]];
VerbosePrint["Done constructing invariant spaces for pole ",poleRight];
(* same filtering as above *)
allPairs=Flatten[Outer[List,Sequence@@{InvLeft,InvRight},1],1];

(* exlude pairs that correspond to the same pole *)
allPairs=Select[allPairs,#[[1,1]]=!=#[[2,1]]&];
(* exclude spaces that don't have the same size *)
allPairs=Select[allPairs,Total[Length[#[[2]]]&/@#[[2,3]]]==Total[Dimensions[#[[2]]][[2]]&/@#[[1,3]]]&];
(* We know how much the improvememnt should be. This is correleated with the size mentionend in the TODO above. *)

allPairs=Select[allPairs,(#[[1,2]]==thePair[[1,2]]&&#[[2,2]]==thePair[[2,2]])&];
VerbosePrint["Considering ",Length[allPairs]," pairs of eigenspaces."];

Do[
	invSpaceL=LeftSubspaceFromList[ppair[[1,3]]];
	invSpaceR=RightSubspaceFromList[ppair[[2,3]]];
	
	inner=invSpaceR . invSpaceL;
	
	(* To construct a projector the invariant spaces cannot be orthogonal *)
	If[NDet[inner]===0,VerbosePrint["Skipping subspaces that are partially orthogonal."]; Continue[];];
	VerbosePrint["Improvement ",{ppair[[1,2]],ppair[[2,2]]}];
	VerbosePrint["Dimension of space: ",Dimensions[invSpaceR][[1]]];
	
	{poleLeft,poleRight}={ppair[[1,1]],ppair[[2,1]]};
	
	VerbosePrint["Pole left: ",poleLeft," Eigenvalues:",LeftEigenvaluesFromList[ppair[[1,3]]]];
	VerbosePrint["Pole right: ",poleRight," Eigenvalues:",RightEigenvaluesFromList[ppair[[2,3]]]];
	
	thePair=ppair;
	{r1,r2}={thePair[[2,1]],thePair[[1,1]]};
	Goto[pairFoundAnalytic];
,{ppair,allPairs}];

VerbosePrint["No match found!"];
Return[$Failed];

(* If we found a pair of subspaces we continue here *)
Label[pairFoundAnalytic];

VerbosePrint["Analytic run time: ",nTime[t0-AbsoluteTime[]]];
t0=AbsoluteTime[];

(* build up the projector *)
VerbosePrint["Building the projector"];
proj= TogetherFkt[invSpaceL . InverseFkt[TogetherFkt[inner]] . invSpaceR];

Switch[True,
r1==Infinity,
	tr=IdentityMatrix[nn]-proj+(xx-r2)*proj;
	trInverse=IdentityMatrix[nn]-proj+1/(xx-r2)*proj,
r2==Infinity,
	tr=IdentityMatrix[nn]-proj+1/(xx-r1)*proj;
	trInverse=IdentityMatrix[nn]-proj+(xx-r1)*proj;,
True,
	tr=IdentityMatrix[nn]-proj+(xx-r2)/(xx-r1)*proj;
	trInverse=IdentityMatrix[nn]-proj+(xx-r1)/(xx-r2)*proj;
];

VerbosePrint["Projector build time: ",nTime[t0-AbsoluteTime[]]]; 
t0=AbsoluteTime[];

(* Update the matrix *)
VerbosePrint["Transforming matrix"];

poleDataNew=UpdateLogarithmicSystem[poleData,proj,{r1,r2}];

VerbosePrint["Transformation time: ",nTime[t0-AbsoluteTime[]]];

(* Statistics *)
VerbosePrint["Total time: ",nTime[tt0-AbsoluteTime[]]];

Return[{poleDataNew,trInverse}];
]


InvariantSubspaces[matr_?SquareMatrixQ]:=Module[{j,u,nn=Length[matr],jblocks={},a=1,b=1,possibleIndices},
{j,u}=JordanDecomposition[matr];
Do[If[
(* zero's mark the start of a new block*)
i==nn||u[[i,i+1]]===0,
AppendTo[jblocks,{a,b}];
{a,b}={i+1,i+1};,
b++;
],{i,1,nn}];
possibleIndices=Join[{{}},Range[#1,Range[#1,#2]]]&@@@jblocks;
possibleIndices=Flatten[Outer[Join,Sequence@@possibleIndices,1],Length[possibleIndices]-1];
Return[{Transpose[j][[#]],Diagonal[u][[#]]}&/@possibleIndices]
]


Options[BalanceEigenvaluesRecursively]={"FiniteFlow"->True,"MaxSteps"->50,"MaxPrimes"->500,"MaxDegree"->500,"Verbose"->False,"Variable"->Global`x,"SpuriousPole"->False};
BalanceEigenvaluesRecursively[poleData_?AssociationQ,opt:OptionsPattern[]]:=Module[{dim,tcnt=0,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,ld,tmp,tt,ttot},
dim=poleData[[1]]//Length;
ld=poleData;
ttot=IdentityMatrix[dim];

While[True,
	VerbosePrint["Step: ",tcnt];
	(* TODO: Handle passing down Options by FilterRules *)
	tmp=BalanceEigenvaluesPoleData[ld,PassRuleSequence[BalanceEigenvaluesRecursively,BalanceEigenvaluesPoleData,{opt}]];
	If[tmp[[2]]===IdentityMatrix[dim],Break[]];
	{ld,tt}=tmp;
	ttot=Together[ttot . tt];
	tcnt++;

	If[tcnt>OptionValue["MaxSteps"],
	 Print["Could not balance eigenvalues in ",OptionValue["MaxSteps"]," steps."];Return[$Failed];]
];
Return[{ld,ttot}];
]


(* ::Title:: *)
(*Factor Epsilon*)


(* ::Code::Initialization::"Tags"-><|"UppercaseVariable" -> <|Enabled -> False|>, "UnusedVariable" -> <|"Module" -> <|Enabled -> False|>|>|>:: *)
Options[FactorEpsilonMatrixPoleData]:={"ApplyFunction"-> Together,"MaxPrimes"->200,"MaxDegree"-> 200,"\[Mu]"->Automatic,"Verbose"->False};
FactorEpsilonMatrixPoleData[poleData_,ep_,opt:OptionsPattern[]]:=Module[{toret,
eqns,sol,trafParametrized,zeroPos,nn=Length[poleData[[1]]],blocks,nblocks,zeroRl,residues,TT,possiblemu,traf,trafInv,NDet,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},
(* Adjust eventually *)
blocks=={{1,nn}};
(*nblocks=Length@DEBlocks[matr];*)
nblocks=1;
NDet[expr_]:=Det[expr/.ep->$Numeric[[1]]];
VerbosePrint["test"];

zeroRl=Thread[Flatten[Position[Table[Boole[i>= j],{i,1,nblocks},{j,1,nblocks}],0]/. {xx_,y_}:> Outer[TT,Range@@blocks[[xx]],Range@@blocks[[y]]]]-> 0];
trafParametrized=Table[TT[i,j],{i,1,nn},{j,1,nn}]/.zeroRl;
residues=Values[poleData];

possiblemu=DeleteCases[$RationalNumbers,Alternatives@@Union@Flatten[ep/.Solve[#==0]&/@(Union[Flatten[MatrixDenominators/@residues]])]];
possiblemu=DeleteCases[possiblemu,0];

Do[
eqns=Flatten@Table[((r/ep) . trafParametrized)-(trafParametrized . (r/ep/.ep-> mu)),{r,residues}];
VerbosePrint["Constructed ",Length[eqns]," eqns"];
sol=FiniteFlow`FFSparseSolve[DeleteCases[Thread[eqns==0],True],Variables[trafParametrized],"ApplyFunction"-> OptionValue["ApplyFunction"],"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"-> OptionValue["MaxDegree"]];
If[sol===FiniteFlow`FFImpossible||sol===$Failed,
VerbosePrint["No solution.",sol];
Continue[];
,

traf=trafParametrized/.sol;
If[NDet[traf]==0,
VerbosePrint["Transformation is not invertible."];
Continue[];
];

VerbosePrint["Factor epsilon at \[Mu] = ",mu];
Break[]];
,{mu,possiblemu}];

Do[
	Do[
		If[NDet[traf/.var->rat]=!=0,
		VerbosePrint["Assigning ",var," ",rat];
		traf=traf/.var->rat;
		Break[];
		];
	,{rat,$RationalNumbers}];
,{var,DeleteCases[Variables[traf],ep]}];

VerbosePrint["Transforming matrix"];

trafInv=FiniteFlow`FFInverse[traf,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"-> OptionValue["MaxDegree"],"ApplyFunction"-> Together];

toret=trafInv . # . traf&/@poleData;

Return[{toret,traf}];
]


LogarithmicCFMatrices2[matr_?MatrixQ, x_Symbol] := Module[{polyList = MatrixDenominators[matr, ep], quol,list = {}},
  Do[
   Do[
   quol=Check[QuolyMod[matr poly, x -> poly],Return[$Failed]];
    list = Join[list, {x^k/poly -> Coefficient[quol, x, k]}];
    , {k, 0, Exponent[poly, x, Max] - 1}]
   , {poly, polyList}];
  Return[Association[list]];
  ]


(* ::Code::Initialization::"Tags"-><|"UppercaseVariable" -> <|Enabled -> False|>, "UnusedVariable" -> <|"Module" -> <|Enabled -> False|>|>|>:: *)
Options[FactorEpsilon]:={"ApplyFunction"-> Together,"MaxPrimes"->200,"MaxDegree"-> 200,"\[Mu]"->Automatic,"Verbose"->False};
FactorEpsilon[matr_?SquareMatrixQ,ep_Symbol,opt:OptionsPattern[]]:=Module[{toret,
eqns,sol,trafParametrized,zeroPos,nn=Length[matr],blocks,nblocks,zeroRl,residues,TT,possiblemu,poleData,traf,trafInv,NDet,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},
(* Adjust eventually *)
blocks=DEBlocks[matr];
nblocks=Length@DEBlocks[matr];
(*nblocks=Length@DEBlocks[matr];*)

NDet[expr_]:=Det[expr/.ep->$Numeric[[1]]];

zeroRl=Thread[Flatten[Position[Table[Boole[i>= j],{i,1,nblocks},{j,1,nblocks}],0]/. {xx_,y_}:> Outer[TT,Range@@blocks[[xx]],Range@@blocks[[y]]]]-> 0];
trafParametrized=Table[TT[i,j],{i,1,nn},{j,1,nn}]/.zeroRl;

poleData=LogarithmicCFMatrices2[matr,x];

residues=Values[poleData];

possiblemu=DeleteCases[$RationalNumbers,Alternatives@@Union@Flatten[ep/.Solve[#==0]&/@(Union[Flatten[MatrixDenominators/@residues]])]];
possiblemu=DeleteCases[possiblemu,0];

Do[
eqns=Flatten@Table[((r/ep) . trafParametrized)-(trafParametrized . (r/ep/.ep-> mu)),{r,residues}];
eqns=DeleteCases[Thread[eqns==0],True];
VerbosePrint["Constructed ",Length[eqns]," eqns"];
sol=FiniteFlow`FFSparseSolve[eqns,Variables[trafParametrized],"ApplyFunction"-> OptionValue["ApplyFunction"],"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"-> OptionValue["MaxDegree"]];
If[sol===FiniteFlow`FFImpossible||sol===$Failed,Print[sol];Continue[];];
traf=trafParametrized/.sol;
If[NDet[traf]==0,
VerbosePrint["Transformation is not invertible."];
Continue[];
];
VerbosePrint["Factor epsilon at \[Mu] = ",mu];
Break[];
,{mu,possiblemu}];

Do[
	Do[
		If[NDet[traf/.var->rat]=!=0,
		VerbosePrint["Assigning ",var," ",rat];
		traf=traf/.var->rat;
		Break[];
		];
	,{rat,$RationalNumbers}];
,{var,DeleteCases[Variables[traf],ep]}];

VerbosePrint["Transforming matrix"];

trafInv=FiniteFlow`FFInverse[traf,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"-> OptionValue["MaxDegree"],"ApplyFunction"-> Together];

toret=trafInv . # . traf&/@poleData;

Return[{toret,traf}];
]


(* ::Code::Initialization::"Tags"-><|"UppercaseVariable" -> <|Enabled -> False|>, "UnusedVariable" -> <|"Module" -> <|Enabled -> False|>|>|>:: *)
Options[FactorEpsilon]:={"ApplyFunction"-> Together,"MaxPrimes"->200,"MaxDegree"-> 200,"\[Mu]"->Automatic,"Verbose"->False,"DoChecks"->False,"Blocks"-> True,"SectorList"-> None};
FactorEpsilon[residues:{Repeated[_?SquareMatrixQ]},ep_Symbol,opt:OptionsPattern[]]:=Module[{toret,evs,
eqns,sol,trafParametrized,zeroPos,nn,blocks,nblocks,zeroRl,TT,possiblemu,poleData,traf,trafInv,NDet,
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,foundmu,foundrat},
nn=Length[residues[[1]]];
(* TODO: This is a hack, adjust eventually *)
blocks=DEBlocks[Sum[RandomInteger[10000000]rr,{rr,residues}]];
If[OptionValue["SectorList"]=!=None,blocks=OptionValue["SectorList"]];
nblocks=Length@blocks;
VerbosePrint[blocks];

If[OptionValue["DoChecks"],
	evs=EigenvaluesAffine[#,ep]&/@residues;
	If[!AllTrue[Flatten[evs],MatchQ[#,Optional[_?NumberQ]+Optional[Optional[_?NumberQ]*ep]]&],
		Print["Not all eigenvalues are in ",ep ,"-form: ",evs];
		Return[$Failed];
	];
];

NDet[expr_]:=Det[expr/.ep->$Numeric[[1]]];


zeroRl=Thread[Flatten[Position[Table[Boole[i>= j],{i,1,nblocks},{j,1,nblocks}],0]/. {xx_,y_}:> Outer[TT,Range@@blocks[[xx]],Range@@blocks[[y]]]]-> 0];
trafParametrized=Table[TT[i,j],{i,1,nn},{j,1,nn}];

If[OptionValue["Blocks"],
trafParametrized=trafParametrized/.zeroRl;
];

(* mu cannot be set to a value for which the matrix has poles *)
possiblemu=DeleteCases[$RationalNumbers,Alternatives@@Union@Flatten[ep/.Solve[#==0]&/@(Union[Flatten[MatrixDenominators/@residues]])]];
possiblemu=DeleteCases[possiblemu,0];

Do[
	eqns=Flatten@Table[((r/ep) . trafParametrized)-(trafParametrized . (r/ep/.ep-> mu)),{r,residues}];
	eqns=DeleteCases[Thread[eqns==0],True];
	VerbosePrint["Constructed ",Length[eqns]," eqns"];
	sol=FiniteFlow`FFSparseSolve[eqns,Variables[trafParametrized],PassRuleSequence[FactorEpsilon,FiniteFlow`FFSparseSolve,{opt}]];
	If[(* No solution, try different mu *)
		sol===FiniteFlow`FFImpossible||sol===$Failed,
		Print[sol]; Continue[];
	];
	traf=trafParametrized/.sol;
	VerbosePrint["Variables remaining:",Variables[traf]];
	
	If[NDet[traf]==0,
		VerbosePrint["Transformation is not invertible."];
		Continue[];
	];
	VerbosePrint["Factor epsilon at \[Mu] = ",mu];
	Goto[foundmu];
,{mu,possiblemu}];
Return[$Failed];
Label[foundmu];
(* Assigning values for the free parameters by looping and tryin all simple rational numbers. *)
Do[
	Do[
		If[NDet[traf/.var->rat]=!=0,
			VerbosePrint["Assigning ",var," -> ",rat];
			traf=traf/.var->rat;
			Goto[foundrat];
		];
	,{rat,$RationalNumbers}];
	VerbosePrint["Cannot assign parameters such that transformation is invertible."];
	Return[$Failed];
	Label[foundrat];
,{var,DeleteCases[Variables[traf],ep]}
];

Return[traf];
]


(* ::Title:: *)
(*Pole Reduction*)


Balance[P_,{x_,x1_,\[Infinity]},c_:1]:=(IdentityMatrix[Length[P]]-P)+c/(x-x1)*P;
Balance[P_,{x_,\[Infinity],x2_},c_:1]:=(IdentityMatrix[Length[P]]-P)+c(x-x2)*P;
Balance[P_,{x_,x1_,x2_},c_:1]:=(IdentityMatrix[Length[P]]-P)+c (x-x2)/(x-x1)*P;


MatrixPoleOrder[mat_,{x_,x0_}]:=-Min[Exponent[Series[mat,x->x0],x-x0,Min]];
(*MatrixPoleOrder[mat_,{x_,Infinity}]:=-Max[Exponent[Series[mat,x->Infinity],x,Max]];*)
MatrixPoleOrder[mat_,{x_,Infinity}]:=Max[Exponent[Series[mat,x->\[Infinity]],x,Max]]+2;


LeadingMatrix[mat_,{x_,x0_}]:=SeriesCoefficient[mat,{x,x0,-MatrixPoleOrder[mat,{x,x0}]}];
LeadingMatrix[mat_,{x_,Infinity}]:=SeriesCoefficient[mat,{x,Infinity,2-MatrixPoleOrder[mat,{x,Infinity}]}];


Options[ReducePoleTransformation]={"Verbose"->False};
ReducePoleTransformation[matr_?SquareMatrixQ,x_,OptionsPattern[]]:=Module[{
nn=Length[matr],poleData,
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
x1,x2,A0,B0,B0temp,
otherPolesToChoose,
nullsp,m,posInvSubsets,db,pos,dualv,proj,travo,iss,gmatTemp,gmat,gdet,lc,
tr,trInverse,
evs
},
poleData=MatrixPoleInfo[matr,x];
VerbosePrint["Poles and order: ",poleData];

If[AllTrue[poleData[[;;,2]],#<=1&],
VerbosePrint["All poles are regular. "];
Return[IdentityMatrix[nn]];
];


x1=MaximalBy[poleData,Last][[1,1]];
VerbosePrint["Will lower order of pole at position ",x," = ",x1];

A0=LeadingMatrix[matr,{x,x1}];
nullsp=NullSpace[A0];
m=Length[nullsp];

otherPolesToChoose=DeleteCases[poleData[[;;,1]],x1];
VerbosePrint["Will chose pole among ",x," = ",otherPolesToChoose];

lc=Infinity;

(* loop over the poles to find the one that gives the simplest balance *)
Do[
	B0temp=LeadingMatrix[matr,{x,xx}];
	
	(* TODO: some of these functions have become very problem specific. 
	We might want to create a setup that checks certain criteria or at least gives the option to disable assumptions (like affine eigenvalues)
	For example here we previously used posInvSubsets=Select[InvSubspaces[Transpose[B0temp]],Length[#]==m&], which is much slower, but generic
	  *)
	evs=Union[EigenvaluesAffine[B0temp,Global`ep]];
	(*
	posInvSubsets=RightSubspaceFromList/@RightInvariantSubspacesByEigenvalue[B0temp,evs];
	(* Choosing only subspaces that have the same length as the null space *)
	posInvSubsets=Select[posInvSubsets,Length[#]==m&];
	*)
	posInvSubsets=Select[InvSubspaces[Transpose[B0temp]],Length[#]==m&];
	(*Global`bbbOld=Select[InvSubspaces[Transpose[B0temp]],Length[#]==m&];*)

	VerbosePrint["For pole ",x," = ",xx," we have ",Length@posInvSubsets," invariant spaces."];
	Do[
		gmatTemp=Outer[#1 . #2&,nullsp,issTemp,1,1];
		(* among all basis choose the one with the simplest gram matrix. Heuristically this will give the simplest final result *)
		gdet=FiniteFlow`FFTogether[Det[gmatTemp/.Global`ep->$Numeric[[1]]]];
		If[gdet==0,Continue[];];
		If[LeafCount[gmatTemp]<lc,
			lc=LeafCount[gdet];
			iss=issTemp;
			x2=xx;
			gmat=gmatTemp;
		];
	,{issTemp,posInvSubsets}];
,{xx,otherPolesToChoose}];

If[lc==Infinity,VerbosePrint["Could not find a matching subspace."]; Return[$Failed];];

VerbosePrint["Chose the pole at ",x," = ",x2];
(* build a dual basis using the gram *)
gmat=FiniteFlow`FFTogether[gmat];
dualv=FiniteFlow`FFInverse[Transpose[gmat]] . iss;

proj=Sum[KroneckerProduct[nullsp[[i]],dualv[[i]]],{i,1,m}];

Switch[True,
x1==Infinity,
	tr=IdentityMatrix[nn]-proj+(x-x2)*proj;
	trInverse=IdentityMatrix[nn]-proj+1/(x-x2)*proj,
x2==Infinity,
	tr=IdentityMatrix[nn]-proj+1/(x-x1)*proj;
	trInverse=IdentityMatrix[nn]-proj+(x-x1)*proj;,
True,
	tr=IdentityMatrix[nn]-proj+(x-x2)/(x-x1)*proj;
	trInverse=IdentityMatrix[nn]-proj+(x-x1)/(x-x2)*proj;
];

Return[tr];

]


Options[ReducePoleRecursive]={"Verbose"->False,"MaxSteps"->50,"FiniteFlow"->True ,"MaxPrimes"->Automatic,"MaxDegree"->Automatic};
ReducePoleRecursive[matr_?SquareMatrixQ,x_,OptionsPattern[]]:=Module[{
nn=Length[matr],tcnt,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
tmp,TogetherFkt,ttot,de
},

If[OptionValue["FiniteFlow"]===True,
(*TogetherFkt=FFTogether[#,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]]&;*)
TogetherFkt=FiniteFlow`FFTogether[#,"MaxPrimes"->OptionValue["MaxPrimes"],"MaxDegree"->OptionValue["MaxDegree"]]&;,
TogetherFkt=Together;
];

tcnt=0;
ttot=IdentityMatrix[nn];
de=matr;
While[True,
	VerbosePrint["Step: ",tcnt];
	tmp=ReducePoleTransformation[de,x,"Verbose"->OptionValue["Verbose"]];
	tmp=TogetherFkt[tmp];
	If[tmp===IdentityMatrix[nn],
	VerbosePrint["Done." ];
	Break[]
	];
	(* TODO: pass down rules *)
	de=INITIAL`basisChange[de,tmp,x];
	ttot=Together[ttot . tmp];
	tcnt++;
	If[tcnt>OptionValue["MaxSteps"],Print["Could not reduce all poles in ",OptionValue["MaxSteps"]," steps."]; Return[$Failed];]
];

Return[{de,ttot}];

]


(* ::Title:: *)
(*Misc*)


CheckEpsilonFormPoleData[poleData_,ep_]:=Module[{},
AllTrue[Flatten[EigenvaluesAffine[#,ep]&/@Values[poleData]],MatchQ[#,_.*ep|0]&]
];


EigenvalueStatistics[poleData_]:=EigenvaluesAffine[#,Global`ep]&/@poleData;


(* ::Title:: *)
(*Clean-up*)


FactorMatrices[matrList_:{Repeated[_?SquareMatrixQ]}]:=Module[{tt,jj,TT,mats,nn=Length[First@matrList],gen},
(* Find matrices that commute with every matrix in the input. *)
tt=Table[TT[i,j],{i,1,nn},{j,1,nn}];
tt=tt/.First[Quiet@Solve[(tt . #-# . tt&/@matrList)==0,Union[Cases[tt,_TT,Infinity]]]];
(*  Remove the trivial cases. *)
gen=DeleteCases[Coefficient[tt,#]&/@Union[Cases[tt,_TT,Infinity]],_?DiagonalMatrixQ];
If[gen=={},Return[IdentityMatrix[nn]]];
(* Select the most complicated and bring it to jordan form.  *)
gen=MaximalBy[gen,MatrixRank][[1]];
jj=JordanDecomposition[gen][[1]];
Return[jj];
]


FactorBlocksStep[matr_?SquareMatrixQ,x_Symbol]:=Module[{tt,jj,TT,mats,nn=Length[matr],gen},
mats=Values[MatrixToPoleData[matr,x]]/.ep->1;
tt=Table[TT[i,j],{i,1,nn},{j,1,nn}];
tt=tt/.First[Quiet@Solve[(tt . #-# . tt&/@mats)==0,Union[Cases[tt,_TT,Infinity]]]];
gen=DeleteCases[Coefficient[tt,#]&/@Union[Cases[tt,_TT,Infinity]],_?DiagonalMatrixQ];
If[gen=={},Return[IdentityMatrix[nn]]];
gen=MaximalBy[gen,MatrixRank][[1]];
jj=JordanDecomposition[gen][[1]];
Return[jj];
];


FactorBlocks[matr_?SquareMatrixQ,x_Symbol]:=Module[{nn,tm,traTot,nBl,tra},
(* Recursive version of FactorBlocksStep since in general there are multiple blocks*)
nn=Length[matr];
tm=matr;
traTot=IdentityMatrix[nn];
nBl=1;
Do[
tra=FactorBlocksStep[tm,x];
If[tra==IdentityMatrix[nn],Break[]];
tm=Together[Inverse[tra] . tm . tra];
If[nBl<Length[DirectSumBlocks[tm]],
traTot=traTot . tra;
nBl=Length[DirectSumBlocks[tm]];
,
Break[]
];

,{ii,1,nn}];
Return[traTot]
]



LinIndep[vlist_]:=Extract[vlist,FirstPosition[#1,1,Nothing]&/@RowReduce[Transpose[vlist/.ep->$Numeric[[1]]]]];
(*Stabilize[mm_][v_:{__}]:=FixedPoint[LinIndep@Join[#,Join@@Table[(a.#&)/@#,{a,mm}]]&,{v}];*)


Stabilize[mm_:{Repeated[_?SquareMatrixQ]}][vSpace_:{Repeated[_List]}]:=FixedPoint[LinIndep@Join[#,Join@@Table[(a . #&)/@#,{a,mm}]]&,vSpace];


SimpleEigenvectors[matr_?SquareMatrixQ]:=Module[{esys=Eigensystem[matr],spos},
esys=Transpose[DeleteCases[Transpose[esys],{_,{Repeated[0]}}]];
spos=Cases[Tally[esys[[1]]],{v_,1}:>v];
Return[esys[[2]][[Flatten[Position[esys[[1]],Alternatives@@spos]]]]]
]


(* ::Title:: *)
(*QuolyMod*)


QuolyMod[quoly_,poly:Except[_Rule|_List],x_Symbol]:=QuolyMod[quoly,x->poly];


QuolyMod[quoly_List,args__]:=QuolyMod[#,args]&/@quoly;
QuolyMod[quoly_,list_List]:=Fold[QuolyMod,quoly,list];


QuolyMod[quoly_,x_Symbol->0]:=quoly;


QuolyMod[quoly_,x_Symbol->poly_]:=Module[{num,den},
{num,den}=Through[{Numerator,Denominator}@Together@quoly];
Together@PolynomialRemainder[InvertMod[den,poly,x]*num,poly,x]
]


QuolyMod[a:(_Integer|_Rational),p_?PrimeQ]:=Module[{num,den},
{num,den}=Through[{Numerator,Denominator}@a];
Mod[InvertMod[den,p]*num,p]
]


PolynomialPoleOrder[matr_?MatrixQ,poly_]:=-Min[Flatten[Map[Cases[FactorList[#],{poly,n_}:>n]&,matr,{2}]]]


(* ::Title:: *)
(*Off-diagonal stuff*)


(* ::Chapter:: *)
(*Individual steps *)


(* TODO: A and C should be passed down since they don't change, C ant trafo should be updated *)
Options[FuchsifyOffDiagonalSectorPoleStep]={"MaxPrimes"->1000,"MaxDegree"-> 200,"ApplyFunction"-> Together,"Verbose"->False};
FuchsifyOffDiagonalSectorPoleStep[matr_?SquareMatrixQ,x_Symbol->Poly_,n1_Integer,n2_Integer,opt:OptionsPattern[]]:=Module[{k0,tans,eqs,sol,trafo,DD,t0,nTime=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[#], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]&,
Amat,Cmat,Dmat,
AmatLeading,DmatLeading,CmatLeading,
tmat,DtmatLeading,
vars=DeleteCases[Variables[matr],x],rk=Exponent[Poly,x,Max],
expansionCFs,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},

(* Numerically determine the order of the pole *)
VerbosePrint["Polynomial has rank: ",rk];
k0=PolynomialPoleOrder[matr/.Thread[vars->Table[RandomInteger[10000],Length[vars]]],Poly];
VerbosePrint["Reducing pole of order: ",k0];

If[k0<= 1,
(* No higher order poles at the given position  *)
VerbosePrint["No higher order poles."];
Return[IdentityMatrix[n1+n2]]
];
VerbosePrint["Extracting matrices "];
t0=AbsoluteTime[];
(* 
split the matix into blocks M = {{a,0},{c,d}}. 
A and D have simple poles *)
 Check[
AmatLeading=QuolyMod[matr[[1;;n1,1;;n1]] Poly, x -> Poly];
DmatLeading=QuolyMod[matr[[n1+1;;-1,n1+1;;-1]] Poly, x -> Poly];
(* C has a pole of order k0 *)
CmatLeading=QuolyMod[matr[[n1+1;;-1,1;;n1]] Poly^k0, x -> Poly];
,
Print["Found unexpected pole."];
tempDump={matr,Poly};
Abort[];
Return[$Failed]
];
VerbosePrint["Time spent expanding: ",nTime[t0-AbsoluteTime[]]];

tmat = Table[Sum[DD[r][i, j]/(Poly^(k0 - 1))x^r, {r, 0,rk-1}], {i, 1, n2}, {j, 1, n1}];
DtmatLeading=QuolyMod[D[tmat,x]Poly^k0, x -> Poly];

eqs=Table[
Coefficient[CmatLeading,x,pow]+Sum[Sum[
Coefficient[DmatLeading,x,k-r] . Table[DD[r][i, j],{i,1,n2},{j,1,n1}]-Table[DD[r][i, j],{i,1,n2},{j,1,n1}] . Coefficient[AmatLeading,x,k-r],
{r,0,Min[k,rk-1]}]Coefficient[PolynomialMod[x^k,Poly],x,pow],{k,0,2*rk}]-Coefficient[DtmatLeading,x,pow],
{pow,0,rk-1}];

eqs=Flatten[eqs];
eqs=DeleteCases[eqs,0];
VerbosePrint["Number of equations: ",Length[eqs]];
sol=FiniteFlow`FFDenseSolve[Thread[eqs==0],Union@Cases[eqs,DD[_][__],Infinity],PassRuleSequence[FuchsifyOffDiagonalSectorPoleStep,FiniteFlow`FFDenseSolve,{opt}]];
VerbosePrint["Time spent solving: ",nTime[t0-AbsoluteTime[]]];
Return[ArrayFlatten[{{IdentityMatrix[n1],0},{tmat/.Dispatch[sol],IdentityMatrix[n2]}}]];
]


FuchsifyOffDiagonalSectorPoleStep[matr_?SquareMatrixQ,{x_Symbol,Infinity},n1_Integer,n2_Integer,opt:OptionsPattern[]]:=Module[{k0,tans,eqs,sol,
Amat,Cmat,Dmat
,trafo,DD,t0,
nTime=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[#], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]&,
vars=DeleteCases[Variables[matr],x],
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},
(* TODO: We should fix the  MatrixPoleOrder function at some point *)
k0=Max[Exponent[Series[matr/.Thread[vars->Table[RandomInteger[10000],Length[vars]]],x->\[Infinity]],x,Max]]+2;
VerbosePrint["Reducing pole of order: ",k0];

If[k0<= 1,
(* No higher order poles at the given position  *)
VerbosePrint["No higher order poles."];
Return[IdentityMatrix[n1+n2]]
];

(* series expand *)
VerbosePrint["Expanding matrices "];
t0=AbsoluteTime[];
(* This seems faster than SeriesCoefficient. *)
Amat=Coefficient[Map[Series[#,x->Infinity]&,matr[[1;;n1,1;;n1]],{2}],x,-1];
Dmat=Coefficient[Map[Series[#,x->Infinity]&,matr[[n1+1;;-1,n1+1;;-1]],{2}],x,-1];
Cmat=Coefficient[Map[Series[#,x->Infinity]&,matr[[n1+1;;-1,1;;n1]],{2}],x,k0-2];

(*
Amat=SeriesCoefficient[matr[[1;;n1,1;;n1]],{x,Infinity,1}];
Cmat=SeriesCoefficient[matr[[n1+1;;-1,1;;n1]],{x,Infinity,2-k0}];
Dmat=SeriesCoefficient[matr[[n1+1;;-1,n1+1;;-1]],{x,Infinity,1}];
*)

VerbosePrint["Time spent expanding: ",nTime[t0-AbsoluteTime[]]];
t0=AbsoluteTime[];

tans=Table[DD[i,j],{i,1,n2},{j,1,n1}];

eqs=Flatten[Cmat+Dmat . tans-tans . Amat-(k0-1)tans];
eqs=DeleteCases[eqs,0];
VerbosePrint["Number of equations: ",Length[eqs]];

sol=FiniteFlow`FFDenseSolve[Thread[eqs==0],Union@Cases[eqs,_DD,Infinity],PassRuleSequence[FuchsifyOffDiagonalSectorPoleStep,FiniteFlow`FFDenseSolve,{opt}]];
VerbosePrint["Time spent solving: ",nTime[t0-AbsoluteTime[]]];
Return[ArrayFlatten[{{IdentityMatrix[n1],0},{(x)^(k0-1) tans/.Dispatch[sol],IdentityMatrix[n2]}}]];
]


(* ::Chapter:: *)
(*Loop over steps for sector*)


(* TODO: Since off-diagonal steps (for a single sector) commute, we should organize things around the different poles, otherwise we include daugther sectors that don't talk to a given pole, thereby unescessarily enlargening our ansatz *)


Options[FuchsifyOffDiagonalSector]={"MaxSteps"->50,"MaxPrimes"->1000,"MaxDegree"-> 200,"ApplyFunction"-> Together,"Verbose"->False};
FuchsifyOffDiagonalSector[matr_?SquareMatrixQ,x_Symbol,sec_:{_,_},opt:OptionsPattern[]]:=Module[{
matrNum,vars,
posibleToClean,min=sec[[1]],max=sec[[2]],secLower,secToClean,smallMatrix,s1,s2=Range@@sec,n1,n2,tra,
polyList,traTot,
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},
(* Numerical version of the matix to simplify some steps *)
vars=Complement[Variables[matr],{x}];

matrNum=matr/.Thread[vars->Table[RandomInteger[10000],Length[vars]]];

secLower=DEBlocks[matrNum[[1;;min-1,1;;min-1]]];
secToClean=Select[secLower,!FuchsianQ[matrNum[[s2,Range@@#]],x]&];
(* ToDo, this should be determined pole-by-pole, otherwise *)
VerbosePrint["Non-fuchsian daughter sectors: ",secToClean];
If[secToClean==={},Return[IdentityMatrix[Length[matr]]]];

polyList=MatrixDenominators[matrNum,Global`ep];
VerbosePrint["Denominators are: ",polyList];

s1=Flatten[Range@@@secToClean];
{n1,n2}=Length/@{s1,s2};
smallMatrix=matr[[Join[s1,s2],Join[s1,s2]]];
traTot=IdentityMatrix[n1+n2];

(* trafos *)
Do[
VerbosePrint["Balancing pole in polynomial ",poly];
tra=FuchsifyOffDiagonalSectorPole[smallMatrix,x->poly,n1,n2,PassRuleSequence[FuchsifyOffDiagonalSector,FuchsifyOffDiagonalSectorPole,{opt}]];
traTot=tra . traTot
,{poly,polyList}
];

VerbosePrint["Balancing pole at Infinity "];
tra=FuchsifyOffDiagonalSectorPole[smallMatrix,{x,Infinity},n1,n2,PassRuleSequence[FuchsifyOffDiagonalSector,FuchsifyOffDiagonalSectorPole,{opt}]];
traTot=tra . traTot;

Return[MakeBigTrafo[traTot,Length[matr],Join[s1,s2]]];
]


Options[FuchsifyOffDiagonalSectorPole]={"MaxSteps"->50,"MaxPrimes"->1000,"MaxDegree"-> 200,"ApplyFunction"-> Together,"Verbose"->False};
FuchsifyOffDiagonalSectorPole[mat_?SquareMatrixQ,pp:(x_Symbol->Poly_)|{x_Symbol,Infinity},n1_Integer,n2_Integer,opt:OptionsPattern[]]:=
Module[{step=1,trafo,trafoTot,nn=Length[mat],matTemp=mat,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&},
	trafoTot=IdentityMatrix[nn];
	(* Loop while poles can be reduces *)
	While[step<=OptionValue["MaxSteps"],
		VerbosePrint["step ",step];
		trafo=FuchsifyOffDiagonalSectorPoleStep[matTemp,pp,n1,n2,PassRuleSequence[FuchsifyOffDiagonalSectorPole,FuchsifyOffDiagonalSectorPoleStep,{opt}]];
		If[trafo==IdentityMatrix[nn] (* ReducePoleOffDiagonalStep returns identity matrix if nothing to be done. *),
			 VerbosePrint["Finished in step ",step,"."]; 
			 Break[];
		];
		
		(* basisChange function wants Together *)
		trafo=FiniteFlow`FFTogether[trafo,PassRuleSequence[FuchsifyOffDiagonalSectorPole,FiniteFlow`FFTogether,{opt}]];
		matTemp=INITIAL`basisChange[matTemp,trafo,x,PassRuleSequence[FuchsifyOffDiagonalSectorPole,INITIAL`basisChange,{opt}]];
		trafoTot=FiniteFlow`FFTogether[trafo . trafoTot,PassRuleSequence[FuchsifyOffDiagonalSectorPole,FiniteFlow`FFTogether,{opt}]];
		step++;
	];
	Return[trafoTot];
]


(* ::Chapter:: *)
(*Loop over sectors*)


Options[FuchsifyOffDiagonal]={"MaxSteps"->50,"MaxPrimes"->1000,"MaxDegree"-> 200,"ApplyFunction"-> Together,"Verbose"->False};
FuchsifyOffDiagonal[matr_?SquareMatrixQ,x_Symbol,opt:OptionsPattern[]]:=Module[{
nn=Length[matr],
bl=DEBlocks[matr],
mp,tt0,ttTotal0,sec,
deTemp,trafo,trafoTot,
sectorStart,sectorEnd,
VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
niceTime=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[#], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]&
},
ttTotal0=AbsoluteTime[];
deTemp=matr;
trafoTot=IdentityMatrix[nn];

VerbosePrint["Sectors are ",bl];



(* Determine how many sectors are already fuchsian *)
mp=MaximalFuchsian[matr,x];

If[mp==nn,Return[{matr,IdentityMatrix[nn]}]];

sectorStart=Position[bl,SelectFirst[bl,MemberQ[Range@@#,mp]&]][[1,1]]+1;
sectorEnd=Length[bl];

Do[
	sec=bl[[cnt]];
	VerbosePrint["Fuchsification of sector ",sec];
	trafo=FuchsifyOffDiagonalSector[deTemp,x,sec,PassRuleSequence[FuchsifyOffDiagonal,FuchsifyOffDiagonalSector,{opt}]];
	trafo=FiniteFlow`FFTogether[trafo,PassRuleSequence[FuchsifyOffDiagonal,FiniteFlow`FFTogether,{opt}]];
	
	tt0=AbsoluteTime[];
	VerbosePrint["OffDiagonalTranformation time: ",niceTime[AbsoluteTime[]-tt0]];
	(* updating transformation and matrix *)
	trafoTot=FiniteFlow`FFTogether[trafoTot . trafo,PassRuleSequence[FuchsifyOffDiagonal,FiniteFlow`FFTogether,{opt}]];
	(*
	aa=MaximalFuchsian[INITIAL`basisChange[matr/.ep->199,trafoTot/.ep->199,x,PassRuleSequence[FuchsifyOffDiagonal,INITIAL`basisChange,{opt}]],x];
	bb=sec[[2]];
	Print["Fuchsian up to: ",aa];
	Print["Should be: ",bb];
	
	If[bb>aa,
	xxx={trafo,trafoTot,deTemp,dmatOld,trafoTotOld};
	Abort[];];
	*)
	deTemp=INITIAL`basisChange[deTemp,trafo,x,PassRuleSequence[FuchsifyOffDiagonal,INITIAL`basisChange,{opt}]];
	VerbosePrint["basis change time: ",niceTime[AbsoluteTime[]-tt0]];
,{cnt,Range[sectorStart,sectorEnd]}];
VerbosePrint["Total time: ",niceTime[AbsoluteTime[]-ttTotal0]];
Return[{deTemp,trafoTot}];
]


(* ::Title:: *)
(*Automatic*)


Options[Canonicalize]={
"RationalParametrization"->None,
"Verbose"->False,
"FiniteFlow"->True,
"MaxPrimes"->500,
"MaxDegree"-> 500,
"MaxSteps"->50};
Canonicalize[matr_?SquareMatrixQ,var_Symbol,opt:OptionsPattern[]]:=Module[{
rvar,rPara=OptionValue["RationalParametrization"],de1,de2,de3,tt1,tt2,tt4,tt5,ld1,ld2,ld3,ld4,ld5,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
trafo,epsFactorization,doRationalize},
doRationalize=OptionValue["RationalParametrization"]=!=None;
If[doRationalize,
	rvar=Variables[rPara[[2]]][[1]];
	VerbosePrint["Using rational parametrization: ",rPara];
	VerbosePrint["Variable: ",rvar];,
	VerbosePrint["No rational parametrization provided"];
	rvar=var;
	rPara=var->var;
];

If[!ContainsAll[{Global`ep,var},Variables[matr]],Print["Found unknown variable ",Variables[matr]];Return[$Failed]];

If[MatchQ[matr,{Repeated[{Repeated[0]}]}],Return[{MatrixToPoleData[matr,rvar],IdentityMatrix[Length[matr]]}]];

VerbosePrint["System of size ",Length[matr]];

(* Remove higher-order poles *)
VerbosePrint["Reducing higher-order poles."];
{de1,tt1}=ReducePoleRecursive[matr,var,PassRuleSequence[Canonicalize,ReducePoleRecursive,{opt}]];

(* Convert matrix to logarithmic system data *)
VerbosePrint["Balancing eigenvalues."];
ld1=MatrixToPoleData[de1,var];
(* at this point we only introduce spurious poles if there is no rational transformation, otherwise we do this later when we balance in the rational parametrization. *)
{ld2,tt2}=BalanceEigenvaluesRecursively[ld1,"Variable"->var,PassRuleSequence[Canonicalize,BalanceEigenvaluesRecursively,{opt}],"SpuriousPole"->doRationalize];
VerbosePrint[EigenvalueStatistics[ld2]];

If[!doRationalize,
	(* without rational parametrization we can skip to the end *)
	ld5=ld2;
	tt4=IdentityMatrix[Length[matr]];
	Goto[epsFactorization];
];

(* Rationalize *)
VerbosePrint["Rationalizing."];
de2=FromPoleData[ld2,var];

VerbosePrint["done."];
de3=Together@Simplify[(D[rPara[[2]],rvar]de2/.rPara)];

VerbosePrint["Simplifying."];
(* matrices can be complex *)
ld3=Simplify/@ComplexExpand/@MatrixToPoleData[de3,rvar];

(* balance *)
VerbosePrint["Balancing eigenvalues in rational parametrization."];
{ld4,tt4}=BalanceEigenvaluesRecursively[ld3,"Variable"->rvar,PassRuleSequence[Canonicalize,BalanceEigenvaluesRecursively,{opt}],"SpuriousPole"->True];
VerbosePrint[EigenvalueStatistics[ld4]];

Label[epsFactorization];

{ld5,tt5}=Together@FactorEpsilonMatrixPoleData[ld4,Global`ep,PassRuleSequence[Canonicalize,FactorEpsilonMatrixPoleData,{opt}]];

trafo=Together[tt1 . tt2 . tt4 . tt5/.rPara];

Return[{ld5,trafo}];

]


StableSubspaces[mats:{Repeated[_?SquareMatrixQ]}]:=Module[{posibleEvs,trafs,matNew},

posibleEvs=Join@@(SimpleEigenvectors/@mats);
trafs=DeleteDuplicates[Stabilize[mats][{#}]&/@posibleEvs];

Print[Length[trafs]];

Return[trafs];

trafs=Join[NullSpace[#],#]&/@trafs;
trafs=Transpose/@trafs;
Return[trafs];
];


RationalCleanMatrix2[mats:{Repeated[_?SquareMatrixQ]}]:=Module[{posibleEvs,trafs,matsNew,toret,cc,compl},

posibleEvs=Join@@(SimpleEigenvectors/@mats);
trafs=DeleteDuplicates[Stabilize[mats][{#}]&/@posibleEvs];


trafs=Join[NullSpace[#],#]&/@trafs;

trafs=Transpose/@trafs;
compl=Infinity;
(* find the one that is simplest *) 
Do[
	matsNew=Together[tt . # . Inverse[tt]]&/@mats;
	cc=RationalComplexity[matsNew];
	If[cc<compl,
		compl=cc;
toret=tt;
	];
,
{tt,trafs}];

Return[toret];
]


RationalCleanMatrix[matr_?SquareMatrixQ,x_]:=Module[{mats,posibleEvs,trafs,matNew},
mats=FullSimplify[Values[MatrixToPoleData[matr,x]]/.ep->1];

posibleEvs=Join@@(SimpleEigenvectors/@mats);
trafs=DeleteDuplicates[Stabilize[mats][{#}]&/@posibleEvs];

trafs=Join[NullSpace[#],#]&/@trafs;
trafs=Transpose/@trafs;
matNew=INITIAL`basisChange[matr,#,x,"Variables"->{x,ep}]&/@trafs;
Return[trafs[[Position[matNew,MinimalBy[matNew,RationalComplexity][[1]]][[1,1]]]]];
]


CleanInverseTravo[tr_,blks_]:=Module[{d1,d2,mm,cleanTr},
cleanTr=System`BlockDiagonalMatrix@@Table[
mm=Factor@Together[tr[[Range@@bl,Range@@bl]]];
d1=DiagonalMatrix[1/CommonFactor[#,"ExcludeVar"->{x,ep}]&/@mm];
d2=1/CommonFactor[d1 . mm//Together//Factor//Flatten,"ExcludeVar"->{x}]IdentityMatrix[bl[[2]]-bl[[1]]+1];
d1 . d2
,{bl,blks}];
Return[cleanTr . tr//Together];
]


Options[RationalCleanMatrixAndTrafo]={"Verbose"->False};
RationalCleanMatrixAndTrafo[matr_?SquareMatrixQ,tr_?SquareMatrixQ,x_,OptionsPattern[]]:=Module[{de1,de2,de3,de4,tr2,tr3,tr4,trAll,trAllClean,VerbosePrint=If[OptionValue["Verbose"],Print[##]]&,
trAllInv,trAll2Inv,trAll2,de5,trAllCleanInv},
VerbosePrint["Step 1"];
If[MatchQ[matr,{Repeated[{Repeated[0]}]}],Return[{matr,IdentityMatrix[Length[matr]]}]];
de1=INITIAL`basisChange[matr,tr,x];

If[MatchQ[de1,{Repeated[{Repeated[0]}]}],Return[{de1,tr}]];
tr2=FactorBlocks[de1,x];

VerbosePrint["Step 2"];
de2=INITIAL`basisChange[de1,tr2,x];

tr3=System`BlockDiagonalMatrix@@(RationalCleanMatrix[#,x]&/@SplitMatrixByBlocksDiagonal[de2]);
de3=INITIAL`basisChange[de2,tr3,x];
VerbosePrint["Step 3"];
tr4=System`BlockDiagonalMatrix@@(JordanDecomposition[MatrixResidue[#,{x,1}]/ep][[1]]&/@SplitMatrixByBlocksDiagonal[de3]);
trAll=Together[tr . tr2 . tr3 . tr4];
trAllClean=Together[trAll . CleanTrafo[trAll,DirectSumBlocks[de3],"KinematicVariables"->{x}]];
de4=INITIAL`basisChange[matr,trAllClean,x];

VerbosePrint["Step 4"];

trAllCleanInv=FiniteFlow`FFInverse[trAllClean,"MaxDegree"->300,"MaxPrimes"->400];

trAll2Inv=CleanInverseTravo[trAllCleanInv,DirectSumBlocks[de4]];
trAll2=FiniteFlow`FFInverse[trAll2Inv,"MaxDegree"->300,"MaxPrimes"->400]//Together;


de5=INITIAL`basisChange[matr,trAll2,x];

Return[{de5,trAll2}];
]
