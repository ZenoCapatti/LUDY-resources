(* ::Package:: *)

BeginPackage["DETools`"];


DEBlocks::usage = "Returns the coupled blocks of a DE matrix.";
SortMatrix::usage = "Sort matrix to block triangular form. Uses topological sorting."


DirectSumBlocks;


ParentDaughterRelations::usage = "";
UnitizeMatrix::usage = "Returns a matrix where all non-zero entries are replaced by 1."


GetEpsilonScript::usage = "Produces a bash script for epsilon";


CheckEpsilonForm::usage = "Checks if matrix is in epsilon form"


SplitMatrixByBlocksDiagonal::usage = "takes the diagonal blocks";


CommonFactor::usage = "Determines a common overall factor for the list of rational functions.";


CleanTrafo::usage = "Clean up the transformation by factoring out common kinematic-independent factors."


MakeBigTrafo::usage = "MakeBigTrafo[Trafo,n,pos], Embedds the given matrix Trafo into a larger matrix of size n at positions indicated by pos, padding it with elements from the identity matrix." 


GetDOPVector::usage = "GetDOPVector[Ax,x] returns the linear differential operator for the matrix."


DenominatorFactors;
MatrixDenominators;


EpsilonScriptBlock;
EpsilonPrepareBlock;
AffineQ;


JordanSpaces;
InvSubspaces;


MatrixPoleOrder;
ReducePoleTransformation;


LogarithmicCFMatrices;
FactorEpsilonMatrix;


InvertMod;
PolyNumerator;


GatherByKernel;


FuchsianQ; MaximalFuchsian;


$EpsilonScript="/usr/local/bin/epsilon";
$EpsilonPrepareScript="/usr/local/bin/epsilon-prepare";
$FERMATPath="/Users/michaelruf/gits/fire/FIRE6/extra/ferm64/fer64";


Begin["`Private`"];


AffineQ[expr_,var_]:=PolynomialQ[expr,var]&&Exponent[expr,var,Max]<=1


DEBlocks[M_?SquareMatrixQ]:=Module[{n=1,blocks={},s,A,p},
	While[n<=Length[M],s=1;
	While[True,A=Map[If[#1===0,0,1]&,M[[n;;n+s-1,n+s;;All]],{2}];
		If[Flatten[A]=={}||Union[Flatten[A]]=={0},Break[]];
		p=Max[Flatten[(Position[#1,1]&)/@A]];
		s+=p;
	];
	AppendTo[blocks,{n,n+s-1}];
	n+=s;];
blocks
]


DirectSumBlocks[matr_?SquareMatrixQ]:=Module[{n,nn=Length[matr],blk},
n=1;
blk={};
While[n<=nn,
Do[
If[ContainsOnly[Flatten[matr[[n;;n+k-1,n+k;;-1]]],{0}]&&ContainsOnly[Flatten[matr[[n+k;;-1,n;;n+k-1]]],{0}],
AppendTo[blk,{n,n+k-1}];
n+=k;
Break[];
];,
{k,nn-n+1}];
];
Return[blk];
]


(* https://mathematica.stackexchange.com/questions/120433/how-to-extract-the-list-of-all-matrices-from-a-block-diagonal-matrix *)
DEBlocksDiagonal[matr_?MatrixQ]:={Min[#[[1]]],Max[#[[2]]]}&@Transpose[#["NonzeroPositions"]]&/@Values[ComponentMeasurements[Image[MorphologicalTransform[Unitize[matr]/.Unitize[_]:> 1,"BoundingBoxes"]],"Mask",CornerNeighbors->False]];


UnitizeMatrix[Matr_?MatrixQ]:=Module[{vars=Variables[Matr],randomSubst},
randomSubst=Thread[vars-> RandomReal[1,Length[vars]]];
Return[Unitize[ArrayComponents[Matr/.randomSubst]]];
]


SortMatrix[Matr_?MatrixQ]:=Module[{Msize=Length[Matr],MatrUnit=UnitizeMatrix[Matr],gr,comp,edges,perm,cond},
(* c.f. https://reference.wolfram.com/language/ref/TopologicalSort.html, applications *)
Do[MatrUnit[[i,i]]=0,{i,Length[MatrUnit]}];
gr=AdjacencyGraph[MatrUnit];
comp=ConnectedComponents[gr];
edges=Union[Cases[EdgeList[gr]/.Table[v->First[Select[comp,MemberQ[#,v]&]],{v,VertexList[gr]}],u_\[DirectedEdge]v_/;u=!=v]];
cond=Graph[comp,edges];
perm=Reverse@Permute[IdentityMatrix[Msize],FindPermutation[Range[Msize],Join@@TopologicalSort[cond]]];
Return[{perm . Matr . Inverse[perm],Inverse[perm]}];
]


ParentDaughterRelations[Matr_?MatrixQ]:=Module[{UM=UnitizeMatrix[Matr], blks=DEBlocks[Matr],BlockedMatrix,BlockReduced},
BlockedMatrix=Table[Take[UM,blks[[ii]],blks[[jj]]],{ii,1,Length[blks]},{jj,1,Length[blks]}];
BlockReduced=Map[(#/.{x_/;Reduce[x==0]:> 0,x_/;!Reduce[x==0]:> 1})&,BlockedMatrix,{2}];
Return[Rule@@@SparseArray[BlockReduced]["NonzeroPositions"]]
]


Options[GetEpsilonScript] = {
"Flag"->"--fuchsify --normalize --factorep-at -1",
"MatrixFile"-> "Ax.m",
"QueueFile"-> "out/queue",
"OutFile"-> "out/transformation.m",
"EpsilonFile"-> "out/transformation.m",
"EpsilonScript"-> $EpsilonScript,
"EpsilonPrepareScript"-> $EpsilonPrepareScript,
"MatrixTempFile"-> "out/matrix",
"FermatFile"->"enable.r3.fer"
}
GetEpsilonScript[Matr_?MatrixQ,OptionsPattern[]]:=Module[{Toret,blks=DEBlocks[Matr],ii,TheBlock},
Toret="#!/bin/bash \n\n";
Toret=Toret<>"export FERMATPATH="~~$FERMATPath~~" \n\n";
Toret=Toret<>"export FERMAT="~~$FERMATPath~~" \n\n";
Toret=Toret<>"mkdir -p out \n\n";
Toret=Toret<>OptionValue["EpsilonPrepareScript"]<>" "~~OptionValue["MatrixFile"]~~"> "~~ToString[OptionValue["MatrixTempFile"]]~~"\n\n";
Toret=Toret<>OptionValue["EpsilonScript"]<>" --echelon-fermat --timings --symbols i --load "~~ToString[OptionValue["MatrixTempFile"]]~~" "<>ToString[blks[[1]][[1]]]<>" " <>ToString[blks[[1]][[2]]]<>"\\\n";
Toret=Toret<>"\t--queue "~~ToString[OptionValue["QueueFile"]]~~"\\\n";
Toret=Toret<>"\t--fermat "~~ToString[OptionValue["FermatFile"]]~~"\\\n";

Toret=Toret<>"\t"<>OptionValue["Flag"]<>"\\\n";

(* loop through blocks *)
For[ii=2,ii<=Length[blks],
TheBlock=blks[[ii]];
Toret=Toret<>"\t--block "<>ToString[TheBlock[[1]]]<>" " <>ToString[TheBlock[[2]]]<>"\\\n";
Toret=Toret<>"\t"<>OptionValue["Flag"]<>"\\\n";
ii++;
];

Toret=Toret<>"\t--block 1 " <>ToString[blks[[-1]][[-1]]]<>"\\\n";
Toret=Toret<>"\t"<>OptionValue["Flag"]<>"\\\n";

Toret=Toret<>"\t--write "<>OptionValue["EpsilonFile"]<>"  --export "<>OptionValue["OutFile"]<>"||exit $?\n\n";
Toret=Toret<>"exit 0";

Return[Toret]
]


Options[CheckEpsilonForm]={"epVar"-> Global`ep};
CheckEpsilonForm[Matr_?MatrixQ,OptionsPattern[]]:=AllTrue[Map[(PolynomialQ[#,OptionValue["epVar"]]&&Exponent[#,OptionValue["epVar"],Min]==1&&Exponent[#,OptionValue["epVar"],Max]==1||#===0)&,Matr,{2}],Identity,2]


SplitMatrixByBlocksDiagonal[matr_?MatrixQ]:=Take[matr,#,#]&/@DEBlocks[matr];


Options[CleanTrafo]={"KinematicVariables"-> {}};
CleanTrafo[traf_,invSub_,OptionsPattern[]]:=Module[{toret},
toret=System`BlockDiagonalMatrix@@((1/CommonFactor[Flatten[traf[[Range@@#,All]]],"ExcludeVar"-> OptionValue["KinematicVariables"]]*IdentityMatrix[#[[2]]-#[[1]]+1])&/@invSub);
Return[toret];
]


Options[CommonFactor]={"ExcludeVar"-> {}};
CommonFactor[expr_,OptionsPattern[]]:=Module[{numers,denoms,tt},
tt=Together[expr];
numers=DeleteCases[Times@@Power@@@Select[FactorList[Numerator[#]],(FreeQ[#,Alternatives@@OptionValue["ExcludeVar"]]&&#[[2]]>0&)]&/@tt,0];
denoms=Times@@Power@@@Select[FactorList[Denominator[#]],(FreeQ[#,Alternatives@@OptionValue["ExcludeVar"]]&&#[[2]]>0&)]&/@expr;
AppendTo[denoms,1];
AppendTo[numers,1];
Return[(PolynomialLCM@@numers)/(PolynomialLCM@@denoms)];
]


MakeBigTrafo[smallTrafo_,n_,pos_]:=Module[{toret},
toret=IdentityMatrix[n];
If[Length[pos]!=Length[smallTrafo],Print["Size mismatch"]; Return[]];
toret[[pos,pos]]=smallTrafo;
Return[toret];
]


Options[EpsilonPrepareBlock]={
"BaseDir"->"",
"FermatPath"->"",
"EpsilonBinary"->""
};
EpsilonPrepareBlock[sector_,OptionsPattern[]]:=Module[{
matrixFilename="Matrix_"~~StringRiffle[sector,"_"]~~".m",
matrixOutFilename="out/matrix_"~~StringRiffle[sector,"_"],
queueFilename="out/queue_"~~StringRiffle[sector,"_"],
trafoFilename="out/transformation_"~~StringRiffle[sector,"_"]~~".m",
size=sector[[2]]-sector[[1]]+1
},
StringRiffle[{
"#!/bin/bash",
"#File generated by DETools.wl ",
"export BASEDIR="~~OptionValue["BaseDir"],
"export OUTDIR="~~OptionValue["BaseDir"]~~"/out",
"export FERMAT="~~OptionValue["FermatPath"],
"export MATRIXIN=$BASEDIR/Matrix_"~~StringRiffle[sector,"_"]~~".m",
"export MATRIXOUT=$OUTDIR/Matrix_"~~StringRiffle[sector,"_"],
"export QUEUE=$OUTDIR/queue_"~~StringRiffle[sector,"_"],
"export OUTEPSILON=$OUTDIR/epsilon_"~~StringRiffle[sector,"_"],
"export OUTTRAFO=$OUTDIR/transformation_"~~StringRiffle[sector,"_"]~~".m",
"export LOGFILE=$OUTDIR/log_"~~StringRiffle[sector,"_"]~~".txt",
"export FERMATENABLE=$BASEDIR/enable.r3.fer",
"",
"cd $BASEDIR",
"mkdir -p $OUTDIR",
OptionValue["EpsilonBinary"]~~" $MATRIXIN > $MATRIXOUT\n",
"exit 0"
},"\n"]
];


Options[EpsilonScriptBlock]={
"BaseDir"->"",
"FermatPath"->"",
"EpsilonBinary"->"",
"FermatFlags"->"--symbols i",
"EpsilonFlags"->"--fuchsify --normalize",
"ExtraLine"->""
};
EpsilonScriptBlock[sector_,OptionsPattern[]]:=Module[{
matrixFilename="Matrix_"~~StringRiffle[sector,"_"]~~".m",
matrixOutFilename="out/matrix_"~~StringRiffle[sector,"_"],
queueFilename="out/queue_"~~StringRiffle[sector,"_"],
trafoFilename="out/transformation_"~~StringRiffle[sector,"_"]~~".m",
size=sector[[2]]-sector[[1]]+1
},
StringRiffle[{
"#!/bin/bash",
"#File generated by DETools.wl ",
OptionValue["ExtraLine"],
"export BASEDIR="~~OptionValue["BaseDir"],
"export OUTDIR="~~OptionValue["BaseDir"]~~"/out",
"export FERMAT="~~OptionValue["FermatPath"],
"export MATRIXIN=$BASEDIR/Matrix_"~~StringRiffle[sector,"_"]~~".m",
"export MATRIXOUT=$OUTDIR/Matrix_"~~StringRiffle[sector,"_"],
"export QUEUE=$OUTDIR/queue_"~~StringRiffle[sector,"_"],
"export OUTEPSILON=$OUTDIR/epsilon_"~~StringRiffle[sector,"_"],
"export OUTTRAFO=$OUTDIR/transformation_"~~StringRiffle[sector,"_"]~~".m",
"export LOGFILE=$OUTDIR/log_"~~StringRiffle[sector,"_"]~~".txt",
"export FERMATENABLE=$BASEDIR/enable.r3.fer",
"",
"cd $BASEDIR",
"("~~OptionValue["EpsilonBinary"]~~" --timings --symbols i,r3 --load $MATRIXOUT 1 "~~ToString[size]~~" --queue $QUEUE --fermat $FERMATENABLE \
	--fuchsify --normalize\\",
"\t--write $OUTEPSILON  --export $OUTTRAFO||exit $?)> $LOGFILE",
"exit 0"
},"\n"]
];


DenominatorFactors[expr_List]:=DenominatorFactors/@expr;
DenominatorFactors[expr_Plus]:=DenominatorFactors/@List@@expr;
DenominatorFactors[expr_]:=FactorList[Denominator[expr]][[;;,1]];
MatrixDenominators[expr_?MatrixQ]:=Union[Select[Flatten[Map[DenominatorFactors,expr,{2}]],Variables[#]=!={}&]];
MatrixDenominators[expr_?MatrixQ,ep_]:=Select[MatrixDenominators[expr],Variables[#]=!={ep}&];


(*Balance[P_,{x_,x1_,\[Infinity]},c_:1]:=(IdentityMatrix[Length[P]]-P)+c/(x-x1)*P;
Balance[P_,{x_,\[Infinity],x2_},c_:1]:=(IdentityMatrix[Length[P]]-P)+c(x-x2)*P;
Balance[P_,{x_,x1_,x2_},c_:1]:=(IdentityMatrix[Length[P]]-P)+c (x-x2)/(x-x1)*P;*)


PolesPosition[m_List,x_Symbol]:=Module[{xf,t,mr},
xf=x/.#&/@Union@Flatten[Solve[#==0,x]&/@Denominators[{m},x]];
mr=Factor[m/t^2/.x->1/t];
If[Quiet[Check[mr/.t->0;False,True,Power::infy]],Sort[Append[xf,\[Infinity]]],Sort[xf]]
]


PolesPosition[ds_Association,x_Symbol]:=PolesPosition[ds[x],x]
PolesPosition[ds_?DSystemQ,x_Symbol]:=PolesPosition[ds[x],x]


JordanSpaces[mat_]:=Module[{jj,uu,jordanBlocks},
{jj,uu}=JordanDecomposition[mat];
jordanBlocks=DEBlocks[uu];
Return[Take[Transpose[jj],#]&/@jordanBlocks]
];
InvSubspaces[mat_]:=Module[{gg},
gg[x_]:=Join@@#&/@Tuples[NestList[Drop[#,-1]&,#,Length[#]-1]&/@x];
Flatten[gg/@Subsets[JordanSpaces[mat]],1]
]


MatrixPoleOrder[mat_,{x_,x0_}]:=-Min[Exponent[Series[mat,x->x0],x-x0,Min]];
LeadingMatrix[mat_,{x_,x0_}]:=SeriesCoefficient[mat,{x,x0,-MatrixPoleOrder[mat,{x,x0}]}];


(* ::Input::Initialization:: *)
FuchsianQ[expr_,x_]:=Module[{toret=True},Do[
If[
MatrixPoleOrder[expr,{x,res}]>1,toret=False; Break[]];,{res,{0,1,-1,I,Infinity}}];
Return[toret];
]


MaximalFuchsian[matr_,x_] := Module[{blk = DEBlocks[matr], pp,toret=Length[matr]},
  Do[
   pp = Flatten[Range @@@ blk[[1 ;; i]]];
   If[! FuchsianQ[matr[[pp, pp]],x],
    toret=blk[[i-1,2]];
    Break[];
    ];
   , {i, Length[blk]}];
   Return[toret];
  ]


InvertMod[poly1_,poly2_,x_]:=Module[{gcd,u,v},{gcd,{u,v}}=PolynomialExtendedGCD[poly1,poly2,x];If[FreeQ[gcd,x],u/gcd,1/0]
];
PolyNumerator[expr_,poly_,x_]:=Module[{num,den},
{num,den}=Through[{Numerator,Denominator}@Together@(expr*poly)];
Together@PolynomialRemainder[InvertMod[den,poly,x]*num,poly,x]
];
PolyNumerator[expr_?SquareMatrixQ,poly_,x_]:=Map[PolyNumerator[#,poly,x]&,expr,{2}]


LogarithmicCFMatrices[mat_?MatrixQ,x_]:=Module[{den,ansatzFunctions,mm=Together[mat]},
den=MatrixDenominators[mm,Global`ep];
Flatten[Table[Module[{pnumer=PolyNumerator[mm,poly,x]},Table[{Coefficient[pnumer,x,k],x^k/poly},{k,0,Exponent[poly,x,Max]-1}]],{poly,den}],1]
]


(*Options[FactorEpsilonMatrix]:={"ApplyFunction"-> Together,"MaxPrimes"->200,"MaxDegree"-> 200};
FactorEpsilonMatrix[matr_,opt:OptionsPattern[],x_,ep_]:=Module[{eqns,sol,trafParametrized,nn=Length[matr],blocks=DEBlocks[matr],nblocks,zeroRl,residues,\[Mu]0=13},
nblocks=Length@DEBlocks[matr];
zeroRl=Thread[Flatten[Position[Table[Boole[i>= j],{i,1,nblocks},{j,1,nblocks}],0]/. {xx_,y_}:> Outer[TT,Range@@blocks[[xx]],Range@@blocks[[y]]]]-> 0];
trafParametrized=Table[TT[i,j],{i,1,nn},{j,1,nn}]/.zeroRl;
(*residues=MatrixResidue[matr,{x,#}]&/@{0,I,-I,-1,1,(-1)^(1/3),Infinity};
residues=RearangeResidues[residues];*)
residues=LogarithmicCFMatrices[matr,x][[;;,1]];
eqns=Flatten@Table[((r/ep) . trafParametrized)-(trafParametrized . (r/ep/.ep-> \[Mu]0)),{r,residues}];
sol=FiniteFlow`FFSparseSolve[DeleteCases[Thread[eqns==0],True],Variables[trafParametrized],"ApplyFunction"-> Together,"MaxPrimes"->200,"MaxDegree"-> 200];
Return[trafParametrized/.sol/.TT[i_,i_]:> 1/._TT:> 0];
]*)


Options[GetDOPVector]={"FiniteFlow"->False,"Silent"->True,"Normalize"->True};
GetDOPVector[matr_,y_,opt:OptionsPattern[]]:=Module[{psi,nn=Length[matr],vars=Variables[matr],sol,cf,toret,rk,vec},
psi=INITIAL`psiCalc[matr,y,FilterRules[{opt},Keys[Options[INITIAL`psiCalc]]]];
rk=MatrixRank[psi/.Thread[vars->Table[RandomPrime[{1000,10000}],Length[vars]]]];
If[!OptionValue["Silent"],Print["Rank of psi matrix: ",rk]];
If[OptionValue["FiniteFlow"],
	vec=PadRight[cf/@Range[rk],nn];
	sol=FiniteFlow`FFSparseSolve[Thread[vec . psi==UnitVector[nn,1]],Variables[vec],FilterRules[{opt},Keys[Options[FiniteFlow`FFSparseSolve]]]];
	If[sol===FiniteFlow`FFMissingPrimes||sol===FiniteFlow`FFMissingPoints||sol===FiniteFlow`FFImpossible,Return[sol]];
	If[sol=={},Return[$Failed]];
	toret=(vec/.sol);,
	vec=PadRight[cf/@Range[rk],nn];
	sol=Solve[Thread[vec . psi==UnitVector[nn,1]],Variables[vec]];
	If[sol=={},Return[$Failed]];
	toret=(vec/.First[sol]);
];
toret=Prepend[-toret,1];
If[OptionValue["Normalize"],
toret=toret/toret[[rk+1]];
];
Return[toret];
]


GatherByKernel[expr_?MatrixQ,x_Symbol]:=Module[{kk,ee,kernels,mats,mRules,temp,matsAndKernels,cc,mm},
kk[a_Plus]:=kk/@a;
kk[a_*c_]/;FreeQ[c,x]:=kk[a]c;
kk[0]:=0;

ee=expr//Together//Apart[#,x]&;
ee=Map[kk,ee,{2}]//ExpandAll;
ee=ee/.kk[xx_]:>kk[Factor[xx]];
kernels=(Cases[ee,_kk,Infinity]//Union);
mats=Transpose/@(TensorTranspose[CoefficientArrays[ee,kernels][[2]]//Normal,{3,2,1}]);

mRules=First@Solve[(mm/@Range[Length[mats]] . #&/@NullSpace[Transpose[Flatten/@mats]])==0];

temp=mm/@Range[Length[mats]] . cc/@Range[Length[mats]]/.mRules;
temp=DeleteCases[{#,Coefficient[temp,#]}&/@(mm/@Range[Length[mats]]),{0,_}];
matsAndKernels=temp/.{cc[i_]:>kernels[[i]],mm[i_]:>mats[[i]]}/.kk->Identity;
matsAndKernels=DeleteCases[matsAndKernels,{_,0}];

Return[matsAndKernels];
]


End[];


EndPackage[];
