(* ::Package:: *)

Print["The documented functions in this package are: \n ?extractTensCoeff\n ?getSymNumericCoeff"];

getSymNumericCoeff::usage=" extractTensCoeff[expr_List,loopMom_List,extVect_List,consistencyCheck_:1]
	getSymNumericCoeff[tensDecomp_List,indices_]: gives the symmetric sum over the coefficients
	INPUT: 
		tensDecomp: Output of ?extractTensCoeff.
		indices: {{indices loopMom1},{indices loopMom2},...}
	OUTPUT: {Indexinformation,{numeric coefficients}}
";
extractTensCoeff::usage=" extractTensCoeff[expr_List,loopMom_List,extVect_List,consistencyCheck_:1]
	extractTensCoeff: extracts from given scalar propagators the loop-momentum tensor coefficients and returns them ordered by rank
	INPUT: 
		expr: The scalar expression on which the tensor extraction should be performed. Multiple numerators are to be given as a list. No propagators allowed.
		loopMom: LIST of loop-momenta
		extVect: LIST of all external Lorentz-vectors (also polarizations!)
		consistencyCheck (Default=1): INTEGER: 2: Run inbetween checks (for debugging);
											  1: Perform Dirac-/Lorentz-algebra and compare final result vs input expression
											  0: No-checks
	OUTPUT: Array of Dimension: rank*looptensor*numerator
	Example:
	testCoeff={SP[k1,p1]SP[p1,p2],SP[p1,p2]+SP[k1,k1]+SP[k1,k2]} (* 2 numerators, 2-loop *);
	extractTensCoeff[testCoeff,{k1,k2},{p1,p2}]				
	OUTPUT:
	{
	{{{0,0},{0,SP[p1,p2]}}}, (* rank 0 *)
	{{{1,0},{SP[p1,p2] vector[p1,lInd1[1]],0}},{{0,1},{0,0}}}, (* rank 1; {{\!\(\*SuperscriptBox[\(k1\), \(lInd1\)]\),0},{coeffNum1,coeffNum2}},{0,\!\(\*SuperscriptBox[\(k2\), \(lInd2\)]\)},{coeffNum1,coeffNum2}} ; lInd1 <> first loop-momentum, lInd2 <> second loop-momentum *)
	{{{2,0},{0,g[lInd1[1],lInd1[2]]}},{{1,1},{0,g[lInd1[1],lInd2[1]]}},{{0,2},{0,0}}} (* rank 2*)
	}
";


parentPath = $InputFileName /. "" :> NotebookFileName[] ;
parentDir = DirectoryName @ parentPath;
Get[parentDir<>"ampTools2.1.m"];
extractTensCoeff[amp_,loopMom_,extVect_,consistencyCheck_:1]:=Block[
	{maxRank,epsK1K1,SP,mySP,tensDecomp,indexSpace,allStruc,allStrucReplRule,allStrucReplRuleVals,res,dummyIndex=Unique[alpha],cleanUpRules
	,tensIndexSet=Table[ToExpression@("lInd"<>ToString@lCount),{lCount,Length@loopMom}],tensIndices,tensFinal,tensTMP
	,resTMP,replRuleTensExtraction,tens,reorderTensors,repl1,repl2,repl3,tensFinalCheck},
SetAttributes[SP,Orderless];

(* determine max tensorrank *)
maxRank=Max@@(Exponent[(amp //. f_[x__]/;!FreeQ[{x},Alternatives@@loopMom]&&StringMatchQ[ToString@f,Alternatives["vector","slash","gamma","SP"]]:>epsK1K1^Count[{x},Alternatives@@loopMom] Unique[f]),epsK1K1]);

tensDecomp=(amp//Expand)/. SP[a_,b_]^pow_/;(MemberQ[loopMom,a]||MemberQ[loopMom,b]):>mySP[{a,b},pow]; (* scalarproducts can be to higher powers *)
(* find all structures *)
allStruc=Join[
	Cases[tensDecomp,f_[x__]/;!FreeQ[{x},Alternatives@@loopMom]&&StringMatchQ[ToString@f,Alternatives["vector","slash","gamma","SP"]]:>{f[x],Count[{x},Alternatives@@loopMom]},Infinity]//Union,
	Cases[tensDecomp, mySP[x_,pow_]:>{mySP[x,pow],Count[x,Alternatives@@loopMom]*pow} ,Infinity]//Union];
	(* generate indexing *)
	allStruc[[1,-1]]={2,allStruc[[1,-1]]+1};
	Do[
	allStruc[[countStruc,-1]]={allStruc[[countStruc-1,-1,-1]]+1,allStruc[[countStruc-1,-1,-1]]+allStruc[[countStruc,-1]]}
	,{countStruc,2,Length@allStruc}];
(* define unique indices *)
allStrucReplRuleVals=Table[
	res={struc[[1]],{}};
	Do[
		res={ReplacePart[#,FirstPosition[#,x_/;MemberQ[loopMom,x]]:>dummyIndex[index]]&@(res[[1]] ),Join[res[[2]],{vector[Extract[#,FirstPosition[#,x_/;MemberQ[loopMom,x]]]&@(res[[1]] ),dummyIndex[index]]}]}
	,{index,Range[struc[[2,1]],struc[[2,-1]]]}
	];
	Times@@(Flatten@res)
	,{struc,(allStruc/. mySP[x_,pow_]:>ConstantArray[SP@@x,pow])}];
	cleanUpRules=Dispatch@{SP[x_,y_]/;(!MemberQ[Join[extVect,loopMom],x]&&!MemberQ[Join[extVect,loopMom],y]):>g[x,y],
						 SP[x_,y_]/;(!MemberQ[Join[extVect,loopMom],x]&&MemberQ[Join[extVect,loopMom],y]):>vector[y,x],
						 SP[x_,y_]/;(MemberQ[Join[extVect,loopMom],x]&&!MemberQ[Join[extVect,loopMom],y]):>vector[x,y],
						 slash[x_,ind1_,ind2_]:>gamma[ind1,x,ind2]
						 };	
allStrucReplRuleVals=allStrucReplRuleVals //.cleanUpRules ;
allStrucReplRule=Thread@(Rule[allStruc[[All,1]],allStrucReplRuleVals]);
tensDecomp=(tensDecomp//. allStrucReplRule);
(* consistency check --> new expression matches input: Extraction of loop-momenta worked *)
If[consistencyCheck>1,
	Print["check I started"];
	If[Simplify@((amp-contractSpin[tensDecomp,Join[loopMom,extVect]]) /. Thread[Rule[Join[loopMom,extVect],Array[Prime,Length@(Join[loopMom,extVect])]]])=!=ConstantArray[0,Length@amp]
		,
		Print["Error in tensor extraction: Check Input"]; Abort[]
		,
		Print["check I passed"]
	 ]
];
tensDecomp=Table[SeriesCoefficient[(tensDecomp /. vector[x_,ind_]/;MemberQ[loopMom,x]:>epsK1K1 vector[x,ind]),{epsK1K1,0,rank}],{rank,0,maxRank}];
(* consistency check --> new expression matches input: rank extraction worked *)
If[consistencyCheck>1,
	Print["check II started"];
	If[Simplify@((amp-Total@(contractSpin[tensDecomp,Join[loopMom,extVect]]) /. Thread[Rule[Join[loopMom,extVect],Array[Prime,Length@(Join[loopMom,extVect])]]]))=!=ConstantArray[0,Length@amp]
		,
		Print["Error in tensor extraction: Check Input"]; Abort[]
		,
		Print["check II passed"]
	 ]
];
(* redefine mathematica default ordering in times *)
reorderTensors[myexpr_, pats_List] :=
  Module[{h, rls},
    rls = MapIndexed[x : # :> h[#2, Replace[x, rls, -1]] &, pats];
    HoldForm @@ {myexpr /. rls} //. h[_, x_] :> x
  ];
tensFinal=Table[
	resTMP=tensDecomp[[rankCount+1]];
	Do[
	tensIndices=Table[tensIndexSet[[loopCount]][ind],{ind,1,rankCount}](*Join[{{1}},Table[Table[tensIndexSet[[loopCount]][ind],{ind,(rank+1)(rank)/2+1,(rank+1)(rank+2)/2}],{rank,0,maxRank-1}]]*);
	(*works since we defined unique indices*)
	tensTMP=Cases[tensDecomp[[rankCount+1]],vector[loopMom[[loopCount]],ind_]:>ind,Infinity]//Union;
	(*Print[tensTMP];*)
		replRuleTensExtraction=Dispatch@{
		tens[x_,y_]tens[z_,v_]:>tens[Join[x,z],Join[y,v]]		 	
	};
	repl1=f_[x___]/;(MemberQ[{slash,vector,gamma,g},Head@(f[x])]&&!FreeQ[Flatten@{x},Alternatives@@tensTMP]):>tens[{f[x]}, Cases[{x},Alternatives@@tensTMP,Infinity]];
	repl2=tens[{start___,tens[a_,x_],rest___} ,y_]:> tens[Flatten@Join[{start},{a},{rest}], Join[x,y]];
	repl3 = tens[x_,y_]/;!FreeQ[y,Alternatives@@tensTMP] :> ReplaceAll[tens[x, y],Thread@(Rule[Cases[y,Alternatives@@tensTMP,Infinity],Flatten@{tensIndices[[(*rankCount+1,*)1;;Length@Cases[y, Alternatives@@tensTMP,Infinity]]]} ] )];
	resTMP=(ReleaseHold@(ReplaceRepeated[reorderTensors[Expand[(# //.vector[loopMom[[loopCount]],ind_]-> 1 /. repl1//. repl2)],{tens}],replRuleTensExtraction])&@((resTMP)))/.repl3;  
	,{loopCount,Length@loopMom}];
	resTMP
,{rankCount,0,maxRank}];
(* order entries by loop-momenta tensors *)
tensFinal=Table[
	Table[
		{tensCoeff,(tensFinal[[rankCount+1]] //.tens[x_,ind_]/;(Count[ind,#]&/@(Blank/@(tensIndexSet[[;;Length@loopMom]]))!=tensCoeff):>0 ) }
		,{tensCoeff,Sort[(Flatten[#,1]&@(Permutations/@(PadRight[#,Length@loopMom]&/@IntegerPartitions[rankCount,Length@loopMom])))]//Reverse}]	
,{rankCount,0,maxRank}];
tensFinal=tensFinal //. tens[x_,y_]:>Times@@x;
(* consistency check --> final expression matches input *)
(* final check*)
If[consistencyCheck>=1,
	Print["Final check started"];
	(* replace integers by loop-momenta *)
	tensFinalCheck=(tensFinal//. {indX_List,{x__}}/;AllTrue[indX,IntegerQ]:>({loopMom^2 loopMom^indX,{x}}//.mom_^pow_/;MemberQ[loopMom,mom]:>(Times@@(Array[Evaluate@vector[mom,Extract[tensIndexSet,Position[loopMom, mom]][[1]][#-2]]&,pow] ))))//.vector[ll_,_[num_]]/;num <= 0:>1;
	(* restore input structure *)
	tensFinalCheck=contractSpin[(tensFinalCheck //. {loopList_List,{x__}}/;(Length@loopList==Length@loopMom && FreeQ[loopList,Alternatives@@extVect]):>(Times@@(loopList)*{x})),Join[loopMom,extVect]];
	tensFinalCheck=Total@(Total/@tensFinalCheck);
	If[Simplify@((amp-tensFinalCheck) /. Thread[Rule[Join[loopMom,extVect],Array[Prime,Length@(Join[loopMom,extVect])]]])=!=ConstantArray[0,Length@amp]
	,
	Print["Error in final check: likely a bug :("]; Abort[],
	Print["Final check passed"]
	]
	];
tensFinal
]

getSymNumericCoeff[tensDecompNum_List,indices_]:=Block[
{resTmp,res=ConstantArray[0,Length@(tensDecompNum[[1,-1]])],indSet=Permutations/@indices,indexAvatar,permAvatar,ll,indRule,
tensIndexSet=Flatten@Table[Table[ToExpression@("lInd"<>ToString@lCount<>"["<>ToString@indCount<>"]"),{indCount,Length@indices[[lCount]]}],{lCount,Length@indices}]},
	vector[x1_List,int1_Integer]:=If[int1==0,x1[[int1+1]],-x1[[int1+1]]];
	g[int1_Integer,int2_Integer]:=If[int1!=int2,0, If[int1==0,1,-1]];
	SP[x_List,y_List]:=x[[1]]*y[[1]]-x[[2]]*y[[2]]-x[[3]]*y[[3]]-x[[4]]*y[[4]];
	resTmp=Cases[tensDecompNum,{x_List,y_List}/;x===Length/@(indices),Infinity];
	(*Print[indSet];*)
	resTmp=resTmp[[All,2]];
	If[
	Union@resTmp==={0},
	Return[Join@@({sym/@indices,resTmp})]
	];
	indexAvatar=Table[Array[ll[loopCount,#]&,Length@(indSet[[loopCount]])], {loopCount,Length@indices}];
	If[Length@indices>1,
		permAvatar=((Flatten@(KroneckerProduct@@indexAvatar))/. Times:>List)/.Dispatch@(ll[i_,j_]:>indSet[[i,j]]),
		permAvatar=Flatten[indSet,1]
	  ];
	(*Print[permAvatar];*)
	res=0;
	Do[
	(*Print[indRep];*)
	indRule=Dispatch@(Thread@(Rule[tensIndexSet,(Flatten@indRep)]));
	(*Print[Normal@indRule];*)
	res=res+(resTmp//. indRule);
	,{indRep,permAvatar}];
	Join@@({sym/@indices,res})
]
