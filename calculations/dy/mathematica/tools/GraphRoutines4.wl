(* ::Package:: *)

(* ::Input::Initialization:: *)
BeginPackage["GraphRoutines`"]
Print["The documented functions in this package are: \n ?FindVertices \n ?FindVerticesForced \n ?FindLabeledDiagram \n ?Contract2SubDiagram \n ?FindIsomorphismsAndShifts \n ?MapToTopTopologies \n !!! GraphRoutines needs the package IGraphM which can be downloaded from https://github.com/szhorvat/IGraphM. !!! \n "];
Needs["IGraphM`"];
FindVertices::usage="FindVertices[propagators,external,NumberOfLoops]: \n Constructs the set of vertices (e.g. V(k1,-(k2+p2),k2,p2), ...) which describe the associated graph completely. If no vertices are found the function returns {}. \n \n INPUT: \n propagators: List of momenta as appearing in the propagators under consideration. \n E.g. \!\(\*FractionBox[\(1\), \(k^2 - m^2\)]\)*\!\(\*FractionBox[\(1\), \(\((k + p)\)^2\)]\) -> {k,k+p}<->Input! \n \n external: List of all external momenta carried by all external legs. Every momentum has to be incomming and momentum conservation has to be fulfilled. \n E.g.: Two-Point-Function: {p,-p} \n E.g.: Four-Point-Function: {p1,p2,p3,-p1-p2-p3} \n \n NumberOfLoops: number of loops.";
FindVerticesForced::usage="FindVerticesForced[propagators,external,NumberOfLoops]: \n Constructs the set of vertices (e.g. V(k1,-(k2+p2),k2,p2), ...) which describe the associated graph completely. If no vertices are found the for the given external momenta, the function tries all possible combinations of external momenta to construct an associated set of vertices. (If external is a  four-point-function: {p1,p2,p3,-p1-p2-p3} but the underlying graph corresponds to the 3-pt function {p1+p2,p3,-p1-p2+p3} it will give the vertices of the 3-point function.) \n \n INPUT: \n propagators: List of momenta as appearing in the propagators under consideration. \n E.g. \!\(\*FractionBox[\(1\), \(k^2 - m^2\)]\)*\!\(\*FractionBox[\(1\), \(\((k + p)\)^2\)]\) -> {k,k+p}<->Input! \n \n external: List of all external momenta carried by all external legs. Every momentum has to be incomming and momentum conservation has to be fulfilled. \n E.g.: Two-Point-Function: {p,-p} \n E.g.: Four-Point-Function: {p1,p2,p3,-p1-p2-p3} \n \n NumberOfLoops: number of loops.";
FindLabeledDiagram::usage="FindLabeledDiagram[vertices,propagators,external,labels (optional), printDiagram (optional), ImageSize (optional), Title (optional)]: \n Creates a labeled graph in Mathematica-readable format. \n \n INPUT: \n vertices: Set of vertices as found by the function FindVertices[] \n propagaters: See ?FindVertices \n external: See ?FindVertices \n labels (optional): list of labels associated to the propagators. Default: {}<-> momenta carried by the propagators. \n printDiagram (optional): Printing the diagram. Default: 1. If PrintDiagram != 1, no diagram will be printed. \n ImageSize (optional): Size of image with. Default: Full. \n Title (optional): Title of Image. Default: \"\" "
Contract2SubDiagram::usage="Contract2SubDiagram[Contractions,TopTopoGraph,NumberExtMomentaTopTopo, printDiagram (optional), ImageSize (optional)]: \n Creates contraction graphs in Mathematica-readable format . \n \n INPUT: \n Contractions: Sets of integers which define contractions. Intergers<=0->Contractions,Intergers>0->No Contractions. Entries beyond the number of internal edges of the top-topology are allowed but will not be considered. \n Example1: {{1,5,-1,0,3,...}}->{{1,1,0,0,1,...}}: One sub-diagram with the contracted internal edges 3,4.\n Example2: {{1,2,-1,0,1,...},{-1,1,1,1,2,...}}->{{1,1,0,0,1,...},{0,1,1,1,1,...}}: Two sub-diagrams with the contracted internal edges 3,4 and 1 respectively  \n TopTopoGraph: Directed graph of the top-topology in mathematica readable format. The first NumberExtMomentaTopTopo entries have to be the external legs. (E.g. output from FindLabeledDiagram) \n NumberExtMomentaTopTopo: Number of external legs of the top-topology. \n printDiagram (optional): Printing the diagram. Default: 1. If PrintDiagram != 1, no diagram will be printed. \n ImageSize (optional): Size of image with. Default: Full. "
FindIsomorphismsAndShifts::usage =
"FindIsomorphismsAndShifts[ext ,propagators ,loopNumber ,cuts (optional), crossing (optional) ]: 
 Finds isomorphisms between Feynman diagrams and gives the shifts of the associated momenta. \n THIS ROUTINE NEEDS THE PACKAGE IGraphM WHICH CAN BE DOWNLOADED FROM https://github.com/szhorvat/IGraphM 


INPUT:
ext: List of all external momenta carried by all external legs. Every momentum has to be incomming and the have to fulfill momentum conservation \n E.g.: Three-Point-Function: {p1,p2,-p1-p2}

propagators: List of propagtors {momenta,mass} as appearing in the topologies under consideration (not squared!). For 2 topologies write e.g. {{{k1,m1},{k1-p12,m2}},{{k1-p12,0},{k1,m1}}}

loopNumber: Number of loops

cuts (optional, Default={} (no cuts)): List cotaining the postions of cut propagators in \"momenta\". 

crossing (optional, Default={}: allow no crossing symmetries): List of pairs of external momenta for which crossings are allowed. Sign has to be consistent with \"ext\".
								E.g.: g(p1)g(p2)->g(p3)H: ext={p1,p2,-p3,-p1-p2+p3} and crossing={{p1,p2},{p1,-p3},{p2,-p3}}  (allow all gluons to be interchanged)

E.g.: 
momenta={{{k1,m},{k2,0},k3,0},-k2-p1,0},{-k2+k3-p1,0},{-k1+k2-k3+p1,0},{-k3-p2,0},{k1-p1-p2,0},{k1-k2-p1-p2,0},{-k1+p2,0}},{{k1,m},{k2,0},{k3,0},{-k3-p1,0},{-k1+p1,0},{-k2-p2,0},{-k2+k3-p2,0},{k1-p1-p2,0},{k1-k2-p1-p2,0},{-k1+k2-k3+p2,0}}}
cuts={{1,8},{1,8}} (first diagram: propagators 1 and 8 are cut; second diagram: propagators 1 and 8 are cut) \n 



E.g.: 
Three-Point-Function: ext={p1,p2,-p1-p2}, crossing={{p1,p2}} (allow p1<>p2 crossing) 


OUTPUT: {{{isomorphic diagrams},{momenta diagram 1},{momenta diagram 2},{permutation cycle for propagators}, {shifts}},...,{...}}
{isomorphic diagrams}: List of two indices {i1,i2} which are the positions of the diagrams in the input list. 
E.g. {1,5}: The diagram defined as the first entry of the input list is isomorphic to the diagram defined by the fifth entry of the input list.

{propagators diagram 1 (2)}: propagators of the first (second) entry in the input list

{permutation cycle for propagators}: cycle which orders the propagators in {momenta diagram 1} such that their position is the same as in {momenta diagram 2}.

{shifts}: shifts which have to be applied that {momenta diagram 1}=={momenta diagram 2} (explicit mapping under considerations of tagged edges (cuts, masses, etc))

(*Input: *)
external={p1+p2,-p1-p2};
propagators={{{k3,0},{k2+p2,0},{k1+k2-k3+p2,0},{k1+p1+p2,0},{k1,mH}},{{k1,mH},{k3,0},{-k2-p1,0},{-k1+k2-k3+p1,0},{k1-p1-p2,0}}};
loopNumber=3;
masses={{0,0,0,0,mH},{mH,0,0,0,0}};
crossing={{p1+p2,-p1-p2}}; 
cuts={{4,5},{1,5}};
(* Find isomorphism and shifts. *)
iso=FindIsomorphismsAndShifts[external,propagators,loopNumber,cuts,crossing]
(* result: {{{1,2},{{k3,0},{k2+p2,0},{k1+k2-k3+p2,0},{k1+p1+p2,0},{k1,mH}},{{k1,mH},{k3,0},{-k2-p1,0},{-k1+k2-k3+p1,0},{k1-p1-p2,0}},Cycles[{{1,2,3,4,5}}],{{-p1-p2->-p1-p2,p1+p2->p1+p2},{k1->-k1,k2->k2+p1-p2,k3->k3}}}}*)
(* permute and apply shifts *)
diag1=Permute[iso[[1,2]],iso[[1,-2]]]/. iso[[1,-1,1]]/. iso[[1,-1,2]]
(* Output: {{-k1,mH},{k3,0},{k2+p1,0},{-k1+k2-k3+p1,0},{-k1+p1+p2,0}} *)
(* Test if (diagram 1 == diagram 2) after application of shift and permutation *)
diag1^2==iso[[1,3]]^2//FullSimplify
(* Output: True *)
(* Attention: The first entry in {isomorphic diagrams} will always be mapped to the second entry. *)

"
MapToTopTopologies::usage =
"MapToTopTopologies[ext_,toposToMapTo_, toposToBeMapped_,loopNumber_, crossing_:{} (optional)]: 
 Finds isomorphisms between Feynman diagrams and gives the shifts of the associated momenta. If a topology(i) in the list props_ is a subtopology of another topology(j) in the list props_, the mapping will be found  \n THIS ROUTINE NEEDS THE PACKAGE IGraphM WHICH CAN BE DOWNLOADED FROM https://github.com/szhorvat/IGraphM 


INPUT:
ext: List of all external momenta carried by all external legs. Every momentum has to be incomming and the have to fulfill momentum conservation \n E.g.: Three-Point-Function: {p1,p2,-p1-p2}

toposToMapTo: Topologies to map to. List of propagtors {momenta,mass} as appearing in the topologies under consideration (not squared!). For 2 topologies write e.g. {{{k1,m1},{k1-p12,m2}},{{k1-p12,0},{k1,m1}}}
toposToToBeMapped_: Topologies which are mapped to \"toposToMapTo\". List of propagtors {momenta,mass} as appearing in the topologies under consideration (not squared!). For 2 topologies write e.g. {{{k1,m1},{k1-p12,m2}},{{k1-p12,0},{k1,m1}}}

loopNumber: Number of loops

crossing (optional, Default={}: allow no crossing symmetries): List of pairs of external momenta for which crossings are allowed. Sign has to be consistent with \"ext\".
								E.g.: g(p1)g(p2)->g(p3)H: ext={p1,p2,-p3,-p1-p2+p3} and crossing={{p1,p2},{p1,-p3},{p2,-p3}}  (allow all gluons to be interchanged)
"
topoToBeMapped::usage="see ?MapToTopTopologies"
topTopo::usage="see \"toposToMapTo\" in ?MapToTopTopologies"
Begin["`Private`"]
(* Finds isomorphisms between Feynman diagrams and gives the shifts of the associated external momenta. Needs: IGraphM`*)

FindIsomorphismsAndShifts[ext_,propagators_,loopNumber_,cuts_:{},crossing_:{{1,1}}]:=Block[
{momenta,masses,massesTemp,extTags,extRule,extTagsTemp,cutsTemp=cuts,cutsPos,posExtTag,x,i,posMasses,vert,diag,diagLabeled,diagLabeledOld,vertInt,graph,from,to,addLength,insertionVertices,graphIsomorph,isomorphisms,g1,g2,asc1,asc2,shifts,dummy,ExtShifts,rule,diagTemp1,diagTemp2,cycle,explicitShift,SolveLoop,s1,s2,loopShift,c,tag,extagReplacement,vertPara,diagPara,extContracted,result,cleanExtShift},
     masses=propagators[[All,All,2]];
     momenta=propagators[[All,All,1]];
diagLabeledOld=momenta;
massesTemp=masses;
(* That function solves the problem of mapping loop momenta for the explicit momentum space shifts (only works with correctly mapped propagators)*)
SolveLoop[prop1_List,prop2_List,loopMom_List,ruleExt_]:=SolveLoop[prop1,prop2,loopMom,ruleExt]=Module[
	{keyLoop=loopMom,valLoop=Unique[loopMom],ruleLoop,sol,testSol,n,r},
	ruleLoop=Thread[Rule[keyLoop,valLoop]];
	Do[
  r=ruleExt[[n]];
		sol=Solve[Thread[(prop1/.r/.ruleLoop)==prop2 ],Values[ruleLoop]];
		If[sol!={},
			Break[]
	]
	,{n,1,Length@ruleExt}];
	sol=sol/.Reverse/@ruleLoop;
	sol=Join[{r},{sol[[1]]}]
];

(* Safety nets for correct input *)
If[Total@ext!=0,
 Print["Momentum conservation for external momenta violated!"];
Abort[]
]; 

If[Length@massesTemp!=Length@momenta&&massesTemp!={},
 Print["masses has to be an array of the same dimension as momenta or {}"];
Abort[]
]; 

If[crossing=!={{1,1}},
If[!ContainsAll[ext,Union@(Flatten@crossing)],
Print["Crossings are indcompatible with the momentum definition of the external legs!"];
Abort[]
]
];


(* generate external tagging (for momenta)*)
If[crossing==={},
extTags=Array[Unique[tag],Length@ext]
,
extagReplacement=(Flatten@(crossing/. {a_,b_}/;!ListQ[a]:>Rule[a,b]))/. Rule[-a_,b_]:>Rule[a,-b];

      extTags=ext //. extagReplacement;
extRule=Thread@Rule[DeleteDuplicates@extTags,Array[Unique[tag],Length@(DeleteDuplicates@extTags)]];
     extTags=extTags /.extRule
];

extTagsTemp=extTags;
If[Length@cutsTemp!=Length@momenta&&cutsTemp!={},
 Print["cuts has to be a list of the same length as momenta or {}"];
Abort[]
]; 
If[cutsTemp==={}&&massesTemp==={}&&extTagsTemp==={},
	extTagsTemp=ConstantArray[dummy,Length@ext];
];
If[cutsTemp==={}&&Variables@massesTemp==={}&&extTagsTemp==={},
	extTagsTemp=ConstantArray[dummy,Length@ext];
];
If[massesTemp==={},
	massesTemp=ConstantArray[{},Length@momenta]
];
If[cutsTemp==={},
	cutsTemp=ConstantArray[{},Length@momenta]
];

(* Represent unique features of an edge (masses, cuts) by a unique primenumber. If an edge carries a mass Subscript[m, i] and is cut, the primenumbers corresponding to the Subscript[m, i ]and the cut will be multiplied (<-> unique number representing properties of an edge/propagator). cutPos will have the shape {position of propagator in input-list, unique number clarifying its properties}  *)
cutsPos=cutsTemp/.x_Integer-> {x+Length@ext,Prime[Length@Variables@massesTemp+1+Length@Variables@extTagsTemp]}; (* cuts *)
Do[ (* flag for external edges *)
	posExtTag[i]=Flatten@Position[extTagsTemp,x_/;TrueQ[x==(Variables@extTagsTemp)[[i]]],Heads->False];
	posExtTag[i]=posExtTag[i]/.x_Integer-> {x,Prime[i]}
,{i,1,Length[Variables@extTagsTemp]}];

Do[ (* flags for cuts *)
	cutsPos=Join[posExtTag[i],#]&/@cutsPos
,{i,1,Length[Variables@extTagsTemp]}];

(* flags for masses *)
Do[
	posMasses[i]=Flatten@Position[#,x_/;TrueQ[x==(Variables@massesTemp)[[i]]],{1},Heads->False]&/@massesTemp;
	posMasses[i]=posMasses[i]/.x_Integer-> {x+Length@ext,Prime[i+Length@Variables@extTagsTemp]}
,{i,1,Length[Variables@massesTemp]}];

(* multiply prime numbers for muliple tags (e.g. massive and cut *)
Do[
	cutsPos=MapThread[Join,{cutsPos,posMasses[i]}]
,{i,1,Length[Variables@massesTemp]}];

Do[
	cutsPos[[j]]=Sort[cutsPos[[j]],#1[[1]]<#2[[1]]&];
	Do[
		If[cutsPos[[j,k]][[1]]==cutsPos[[j,k+1]][[1]]
			,cutsPos[[j,k+1]]={cutsPos[[j,k+1]][[1]],cutsPos[[j,k]][[2]]*cutsPos[[j,k+1]][[2]]};
			cutsPos[[j,k]]={}
		]
	,{k,1,Length@cutsPos[[j]]-1}]
,{j,1,Length@momenta}];

cutsPos=cutsPos/. {}-> Nothing;

(* construct vertices *)

vertPara=ParallelMap[FindVerticesForced[#,ext,loopNumber]&,momenta];
    
Do[
	
	diagLabeled[i]=FindLabeledDiagram[vertPara[[i,1]],momenta[[i]],vertPara[[i,2]],{},0];
(*  Print[{vertPara[[i,1]],momenta[[i]],vertPara[[i,2]]}];
	Print[diagLabeled[i]];*)
	diagLabeledOld[[i]]=diagLabeled[i]/. Rule-> TwoWayRule;


	 (* if the graph has less external momenta than in input: e.g. contraction occured, fix labeling for extags *)
	extContracted=Cases[((diagLabeled[i])[[All,2]]),x_/;FreeQ[x,Alternatives@@Complement[Variables@((diagLabeled[i])[[All,2]]),Variables@ext]],{1}];

If[Length@extContracted<Length@ext,

cutsPos[[i]]=Drop[cutsPos[[i]],Length@ext];
cutsPos[[i,All,1]]=cutsPos[[i,All,1]]+(Length@extContracted-Length@ext); (*less external edges --> edge numbering has to be adjusted *);
(*Print[extContracted /. extagReplacement/. extRule];*)

extTags=extContracted //. extagReplacement/. (extRule//. Rule[-a_,b_]:>Rule[a,-b] )/. Table[Rule[(Variables@(Values@extRule))[[count]],Prime[count]],{count,Length@(Variables@(Values@extRule))}]//Abs;
(*Print[extTags];*)
cutsPos[[i]]=Join[Table[{count,extTags[[count]]},{count,Length@extTags}],cutsPos[[i]]] (* find new external taggings*)

];


Do[
	diagLabeledOld[[i,cutsPos[[i,j,1]]]]=Append[diagLabeledOld[[i,cutsPos[[i,j,1]]]],cutsPos[[i,j,2]]];
	,{j,1,Length@cutsPos[[i]]}];
	diag[i]={extContracted,diagLabeled[i][[All,1]]}; (* get graphs without labels: {number external legs, graph} *)

,{i,1,Length[momenta]}];


(* Replace every edge which is carrying a tagging by an edge with the corresponding number (<- product of previously computed primenumbers in the second entry of cutPos) of two-valent vertex insertions *)

Do[
	vertInt=cutsPos[[z]];
	graph[z]=diag[z][[2]];
	from=Keys[graph[z]];
	to=Values[graph[z]];
	addLength=0;
	Do[
		insertionVertices=Range[Length@DeleteDuplicates@Union[from,to]+1,Length@DeleteDuplicates@Union[from,to]+vertInt[[l,2]]];
		from=Flatten@Insert[from,insertionVertices,vertInt[[l,1]]+addLength+1];
		to=Flatten@Insert[to,insertionVertices,vertInt[[l,1]]+addLength];
		addLength=addLength+Length@insertionVertices;
	,{l,1,Length@vertInt}];
	graph[z]=Flatten@Thread[Rule[from,to]];
(*Print["\n"];
Print[vertInt];
Print[diag[z]];
Print[graph[z]];
Print["\n"];*)
	graph[z]=ToExpression[StringReplace[ToString[graph[z]],"->"->"<->"]];

,{z,1,Length@momenta}];

(* isomorphic feynman diagrams are related by shifts and relabelings *)
(* check for isomorphisms between topologies *)
graphIsomorph=Table[IGIsomorphicQ[Graph@graph[i],Graph@graph[j]],{i,1,Length[momenta]},{j,1,Length[momenta]}]//LowerTriangularize;

isomorphisms=(Position[graphIsomorph,True]/. {i_,i_}-> Nothing);
(*Print[isomorphisms];  (* delete identity *)*)
shifts=ConstantArray[0,Length[isomorphisms]];
Do[
	(* get isomorphism for graphs which are isomorphic; IGVF2 needed for multi-edge graphs: 
	There is no algorithm working for multi-edge graphs directly. Therefore translate into edge-colored simple graphs! *)
	g1=Graph@graph[isomorphisms[[i,1]]];
	g2=Graph@graph[isomorphisms[[i,2]]];
(*Print[{graph[isomorphisms[[i,1]]],graph[isomorphisms[[i,2]]]}];*)
	(* The color is the multiplicity of the edge e.g.: g1Multiedge={1\[TwoWayRule]4,1\[TwoWayRule]4} --> g1ColouredSimple={1\[TwoWayRule]4\[Rule]2}*)
	asc1=Counts[Sort/@EdgeList[g1]];
	asc2=Counts[Sort/@EdgeList[g2]];
	(* find the isomorphisms: Mapping of vertices {#number ext. legs, isomorphism}*)
	shifts[[i]]={{(diag[isomorphisms[[i,1]]])[[1]],(diag[isomorphisms[[i,2]]])[[1]]},IGVF2FindIsomorphisms[{Graph[VertexList[g1],Keys[asc1]],"EdgeColors"->asc1},{Graph[VertexList[g2],Keys[asc2]],"EdgeColors"->asc2}]};
,{i,1,Length[isomorphisms]}];

(*Print[shifts];*)
(* get permutations of external edges *)
ExtShifts=Table[Normal@shifts[[isoCount,2]]/. Rule[a_,b_]/;(a>Length[shifts[[isoCount,1,1]]]||b>Length[shifts[[isoCount,1,1]]])->Nothing,{isoCount,Length@isomorphisms}];
(*Print[ExtShifts];*)
ExtShifts=Table[ExtShifts[[isoCount]]/.Rule[ext1_Integer,ext2_Integer]:>Rule[shifts[[isoCount,1,1,ext1]],shifts[[isoCount,1,2,ext2]]],{isoCount,Length@isomorphisms}];
(*Print[ExtShifts];*)
(* remove nonsense shifts involving higher degree permutations like p1\[Rule]p2, p2\[Rule]p1, -p2\[Rule]-p2, -p1\[Rule] -p1 : If we consider forward scattering I've to think about that again*)
Do[
	Do[
	(* find unphysical shifts *)
		If[Simplify@(((Values@ExtShifts[[i,j]])/. Join[ExtShifts[[i,j]],Reverse/@ExtShifts[[i,j]]])-Keys@(ExtShifts[[i,j]]))===ConstantArray[0,Length@ExtShifts[[i,j]]]
			,ExtShifts[[i,j]]=ExtShifts[[i,j]];
				shifts[[i,2,j]]=shifts[[i,2,j]]
			, ExtShifts[[i,j]]={};
			shifts[[i,2,j]]={}
		]
	,{j,1,Length[ExtShifts[[i]]]}]
,{i,1,Length@ExtShifts}];


ExtShifts=DeleteDuplicates/@ExtShifts;
shifts=DeleteDuplicates/@shifts;


(* Delete unphysical isomorphisms between diagramms *)
isomorphisms[[Flatten@Position[ExtShifts,{{}}]]]=Nothing;
If[Length@isomorphisms==0
		,(*PrintTemporary[" No isomorphisms found :("];*) 
	  Return[{{}}]
];
(* Print[ToString[Length@isomorphisms]<>" isomorphisms found."];*)
(* Delete unphysical shifts *) 
ExtShifts=ExtShifts/.{{}}-> Nothing/. {}-> Nothing;
shifts=shifts/.{{}}-> Nothing/. {}-> Nothing;

ExtShifts=Table[{Join[ExtShifts[[shiftCount,1]],Reverse/@(ExtShifts[[shiftCount,1]])]//Union//Sort},{shiftCount,Length@ExtShifts}]/. Rule[-x_,y_]:>Rule[x,-y];

(* rewrite ExtShift as single momenta mapping *)
cleanExtShift[exShift_]:=Block[{exSol,exRule,exEQ},
exRule=Thread@Rule[Variables@(Values@exShift),Unique[Variables@(Values@exShift)]];
exEQ=(Keys@exShift)==(Values@exShift//.exRule);
(*Print[Thread@exEQ];*)
exSol=Flatten@((Quiet[Solve[Thread@exEQ,Variables@(Keys@exShift) ]]));
(*Print[exSol];*)
exSol=Thread@Rule[Keys@exSol,(Values@exSol/.Reverse/@exRule)];
(*Print[exSol];*)
exSol
];
ExtShifts=Table[{cleanExtShift[ExtShifts[[shiftCount,1]]]},{shiftCount,Length@ExtShifts}];

(*(* only one shift needed *)
ExtShifts=ExtShifts[[All,1]];
shifts=shifts[[All,1]];*)

(* Compute the permutation which brings the ordering of the propagators of graph 1 into the propagator ordering of graph 2 *)
cycle=ConstantArray[1,Length@shifts];
loopShift=ConstantArray[1,Length@shifts];
explicitShift=ConstantArray[1,Length@shifts];
Do[

	rule=Thread[Rule[Flatten@Keys[shifts[[j,2,1]]],Flatten@Values[shifts[[j,2,1]]]]]; (* we only need one isomorphism! *)
       diagTemp1=diagLabeledOld[[isomorphisms[[j,1]]]];
	diagTemp2=diagLabeledOld[[isomorphisms[[j,2]]]];
(*Print[{diagTemp1,diagTemp2,rule}];*)
(*Print[rule];
Print[diagTemp1];
Print[diagTemp2];*)
	diagTemp1[[All,1]]=diagTemp1[[All,1]]/.rule ; (* relabel vertices *)
(*Print[diagTemp1];*)
	(* Find permutation which translates graph 1 into graph 2 after applying the vertex mapping (set labels to {} ) *)
	c=Complement[(diagTemp1 /.Thread[diagTemp1[[All,2]]->ConstantArray[{},Length@diagTemp1]]),(diagTemp2 /.Thread[diagTemp2[[All,2]]->ConstantArray[{},Length@diagTemp2]])];
	If[c!={},
		diagTemp1=diagTemp1/.Thread[Rule[c[[All,1]],Reverse/@c[[All,1]]]]
	];
	cycle[[j]]=FindPermutation[(diagTemp1 /.Thread[diagTemp1[[All,2]]->ConstantArray[{},Length@diagTemp1]]),(diagTemp2 /.Thread[diagTemp2[[All,2]]->ConstantArray[{},Length@diagTemp2]])];
(*Print[diagTemp1];*)
(*
Print[cycle];
Print["diagtemp1"];
Print[diagTemp1];
Print["diagtemp2"];
Print[diagTemp1];
	*)
s1=Permute[diagTemp1[[All,2]],cycle[[j]]];
	s2=diagTemp2[[All,2]];
	s1[[Length@(diag[isomorphisms[[j,1]]][[1]])+1;;All]]=s1[[Length@ext+1;;All]]^2;
	s2[[Length@(diag[isomorphisms[[j,1]]][[1]])+1;;All]]=s2[[Length@ext+1;;All]]^2;
	
	loopShift[[j]]=Flatten@SolveLoop[s1,s2,Complement[Variables@s1,Variables@ext],ExtShifts[[j]](*Variables@ext*)];
(*Print["loop-shift"];
Print[loopShift[[j]]];
Print[s1];
Print[s2];
Print["-------------------------------------------------------\n"];
(*Print["loopShift"];*)
Print[loopShift[[j]]];*)
	s1=s1/.loopShift[[j]];
(*
Print["s1:"];
Print[s1];
Print["s2:"];
Print[s2];
Print["\n"];
	*)
(*If[(s1==s2//FullSimplify),
		PrintTemporary["Mapping "<>ToString[j]<>" out of "<>ToString[Length@isomorphisms]<> " found :)"]
	];*)
If[(s1!=s2//FullSimplify),
		Print["Mapping "<>ToString[j]<>" out of "<>ToString[Length@isomorphisms]<> " not found :(. Check code"](*;
Print[s1];
Print[s2]*)
	];
(* Remove external legs from cycle *)
	cycle[[j]]=cycle[[j]]/. a_Integer/;a<Length@(diag[isomorphisms[[j,1]]][[1]]):>Nothing/. a_Integer:> a-Length@diag[isomorphisms[[j,1]]][[1]] 
	,{j,1,Length@isomorphisms}];



result=Transpose@{isomorphisms,propagators[[isomorphisms[[All,1]]]],propagators[[isomorphisms[[All,2]]]],cycle,loopShift};
(* remove redundant isomoprhisms *)
Do[
Do[
result[[resCount2,1]]=result[[resCount2,1]] /. {a_,b_}/; a==result[[resCount,1,1]]&&b>result[[resCount,1,2]]:>{0,0}
,{resCount2,resCount+1,Length@result}]
,{resCount,1,Length@result-1}];
result=result/. {{0,0},a___}:>Nothing
]


FindVerticesForced[Mprop_,Mext_,numLoops_]:=Block[{momentaPartitioning,vert},
momentaPartitioning[{x_}]:={{{x}}};
momentaPartitioning[{r__,x_}]:=Join@@(ReplaceList[#,{{b___,{S__},a___}:>{b,{S,x},a},{S__}:>{S,{x}}}]&/@momentaPartitioning[{r}]);
Do[
vert=FindVertices[Mprop,Plus@@@(mom),numLoops];

If[Length@vert!=0,
vert={vert,Plus@@@mom};
Break[]
]
,{mom,Reverse@momentaPartitioning[Mext]}];
If[vert=!={},
vert=vert,
vert={{},{}}
];
vert
]
MapToTopTopologies[ext_,topTopos_,props_,loopNumber_,crossing_:{{1,1}}]:=
Block[{extReplacement,propsOrdered,depth,generateContractions,isos,subtopoCandidates,posIntTopTopos,topoToBeMapped,topTopo},
(*props:List of form {PropagatorsTopo1,PropagatorsTopo2,...}:PropagatorsTopo1={{momenta1,masses1},{momenta2,masses2},{momenta3,masses3},...}*)
(* function that generates  all possible contractions*)
	generateContractions[momenta_,numProps_]:=
	Block[{candidates,pos},
	candidates=(Times[momenta,#]&/@Permutations[Join[ConstantArray[0,Length@momenta-numProps],ConstantArray[1,numProps]]])/. {0,0}:>Nothing;
	candidates=Transpose@({candidates,(ParallelMap[FindVerticesForced[#,ext,loopNumber]&,candidates[[All,All,1]]])[[All,2]]})/.{a_,{}}/;ListQ[a]:>Nothing;
	pos=(FindIsomorphismsAndShifts[ext,candidates[[All,1]],loopNumber,{},crossing]);
	
	If[pos=!={{}},
	candidates=Delete[candidates,Transpose@{pos[[All,1,1]]}];
	];
	(*Print[candidates];*)
	candidates[[All,1]]
	
	];
	


(* depth measures number of nested list*)
depth[{}]:=2;
depth[list_List]:=1+Max[Map[depth,list]];
depth[_]:=1;




(* Safety nets for correct input *)
 If[Total@ext!=0,
 Print["Momentum conservation for external momenta violated!"];
Abort[]
]; 
If[!IntegerQ[loopNumber],
 Print["Loop number has to be an integer"];
Abort[]
]; 
If[crossing=!={{1,1}},
If[!ContainsAll[ext,Union@(Flatten@crossing)],
Print["Crossings are indcompatible with the momentum definition of the external legs!"];
Abort[]
]
];

extReplacement=Flatten@(crossing/. {a_,b_}/;!ListQ[a]:>Rule[a,b]);
(* order top topos by number of props *)
propsOrdered=Reverse@(SortBy[topTopos,Length]);

If[Length@propsOrdered>1&&FreeQ[FindVerticesForced[#,ext,loopNumber]&/@propsOrdered,{}], (* allow for completed topologies *)
isos=FindIsomorphismsAndShifts[ext,propsOrdered,loopNumber,{},crossing];
If[isos=!={{}},
propsOrdered=Delete[propsOrdered,Transpose@{isos[[All,1,1]]}];
]
];

isos=ConstantArray[{},Length@props];
Do[
Do[
	If[Length@(props[[propCount]])>Length@(propsOrdered[[topCount]]),
	Break[]
	];
	subtopoCandidates=generateContractions[propsOrdered[[topCount]],Length@props[[propCount]]];
(*		Print["here"];*)
	isos[[propCount]]=FindIsomorphismsAndShifts[ext,Join[subtopoCandidates,{props[[propCount]]}],loopNumber,{},crossing];
	(*Print[isos[[propCount]]];*)
	If[isos[[propCount]]=!={{}},
	(*Print["here"];*)
	isos[[propCount]]={{propCount,topCount},isos[[propCount,1,-1]]};
	Break[]
	]
,{topCount,Length@propsOrdered}]
,{propCount,Length@props}];
posIntTopTopos[int_]:=Position[topTopos,propsOrdered[[int]],Heads->False];
isos=isos/.{int1_Integer,int2_Integer}:>{topoToBeMapped@@{{int1}},topTopo@@(posIntTopTopos[int2])};
isos
]

FindVertices[Mprop_,Mext_,numLoops_]:=Module[{MpropTemp=Mprop,loopMom,tadpoleSave,numLoopsTemp=numLoops,MpropMinus,Mall,lAll,numProp,numVertex,MaxValency ,subsetsExt,pos,vertExt,numExt,MaxValencyRemaining,Mremaining,numVertexRemaining,vertInt,vertices,CountingEdges,vertExtSets,x},
(* SUBMODULES *)
(* Take care of tadpoles *)
loopMom=Complement[Union@(Variables@Mprop),Union@(Variables@Mext)];
If[Length@loopMom!=numLoops,
	(*Print["Not enough or to many loop-Momenta for "<>ToString@numLoops<>" integrals!"];*)
	Return[{}]
];

tadpoleSave=Flatten@Table[
			If[
				Length@Complement[Mprop,(Mprop //.countLoopMom :> 0)]==1,
			Complement[Mprop,(Mprop //.countLoopMom :> 0)],
			{}
			]
		,{countLoopMom,loopMom}];
If[Length@tadpoleSave>0,
	MpropTemp=Intersection[MpropTemp,MpropTemp /. Thread[Rule[tadpoleSave,ConstantArray[0,Length@tadpoleSave]]]]
	];
numLoopsTemp=numLoops-Length@tadpoleSave;


(* This is a test function which counts the edges of a graph and if it is connected *)
CountingEdges[vert_,ext_]:=CountingEdges[vert,ext]=Module[{Admat,vertTemp},
	(* Construct adjacency matrix *)
	vertTemp=vert;
	Do[vertTemp[[k]]=Complement[vert[[k]],ext],{k,1,Length[vert]}]; (* no internal edges carrying internal momenta *)
	Admat=ConstantArray[0,{Length[vertTemp],Length[vertTemp]}]; (* adjacency matrix *)
	Do[
		Do[
			If[(Length[Union[vertTemp[[i]],-vertTemp[[j]]]]<(Length[vertTemp[[i]]]+Length[vertTemp[[j]]]))
				,Admat[[i,j]]=(Length[vertTemp[[i]]]+Length[vertTemp[[j]]])-Length[Union[vertTemp[[i]],-vertTemp[[j]]]];
			];
		,{j,i,Length[vertTemp]}]
	,{i,1,Length[vertTemp]}];
	(*Print[GraphPlot[Admat,DirectedEdges\[Rule] True,MultiedgeStyle->.3,SelfLoopStyle\[Rule]All,ImageSize\[Rule]Small]];*)
	{Plus@@Flatten[Admat],ConnectedGraphQ[AdjacencyGraph[Admat,DirectedEdges->False]]}
];
(* this function constructs possible sets of vertices *)
vertExtSets[Ls:{{__List}..}/;ArrayDepth@Ls>=2]:=vertExtSets[Ls]=Module[{k,a,kRange,aRange,tab,j},
		k=Length@Ls;(* number of external momenta *)
		a=Length@First@Ls-1; (* Maximal vallency *)
		kRange=Range@k;
		(* all possile combinations of combining vertices \[Rule] create indices *)
		tab=Table[IntegerPartitions[j,{k},a+1],{j,k,k+a}];
		(*Convert partitions to compositions:*)
		tab=Join@@tab ;
		(*Get positions,in input,of (Subscript[l,1,j1],Subscript[l,2,j2],...,Subscript[l,k,jk]) sub-lists with compatible elements:*)
		tab=Permutations/@tab;
		tab=Join@@tab;
		tab=Transpose@{kRange,#}&/@tab;
		(*Extract compatible sub-lists and get all combinations of their elements (sub-sub-lists):*)
		tab=Tuples@Extract[Ls,#]&/@tab;
		tab=Join@@tab (* basically flatten *)
];

(* ACTUAL VERTICES CONSTRUCTION *)
MpropMinus=-MpropTemp;(* sign of momenta in propagators *)
numExt=Length[Mext]; (* number of external verices *)
Mall=Join[Mext,MpropTemp,MpropMinus]; (* All vertices have to be build up from that set *)
lAll=numExt+2*numProp; (* length of the set of {external}U{propagator}U{-propagator} *)
numProp=Length[MpropTemp]; (*number of propagators *)
vertices={};
(* number of verices V for a connected graph with L loops and E internal edges: V=E-L+1 (connencted=>+1) 
See: Bolobas, "Modern Graph Theory", Chap. II.3, Theorem 9 *)
numVertex=numProp-numLoopsTemp+1; 
(* A Vertex has to be more than 3-valent \[Rule] Minimal Valency=3
Compute maximal Valency: *)
MaxValency=lAll-3*numVertex;

(* FIND VERTICES CONNECTED TO EXTERNAL LINES *)
 (* breaks if vertices with to high valency of vertices needs to be <3 to construct a graph *)
vertExt=ConstantArray[0,{Length[Mext]}];
pos=ConstantArray[0,{Length[Mext]}];

Do[ (* loop over external momenta *)
	vertExt[[i]]={};
	Do[ (* loop for the valency *)
		subsetsExt[j]=Subsets[Join[MpropTemp,-MpropTemp],{j}];
		pos[[i]]=Position[Plus@@@subsetsExt[j],-Mext[[i]],{1}];(* Momentum conservation *)
		If[Length[pos[[i]]]>0
			,pos[[i]]= Prepend[Mext[[i]]]/@Extract[subsetsExt[j],pos[[i]]]
		];
		vertExt[[i]]=Append[vertExt[[i]],pos[[i]]];
		,{j,2,2+MaxValency}];
,{i,1,numExt}];

(* Find sets of vertices *)
vertExt=vertExtSets[vertExt];

vertExt=vertExt /. {}-> Nothing;
If[vertExt!={}, (* safety break *)
	(* set of external vertices must involve all external momenta *)
	vertExt=Replace[vertExt,x_/;Length@x<numExt-> Nothing,{1}];
	(* Remove vertices which include the same propagator *)
	vertExt=Replace[vertExt,x_/;Length@(Union@@x)<Length@(Join@@x)-> Nothing,{1}];
	(* CONSTRUCT INTERNAL VERTICES *)
	If[Length[vertExt]!= 0,(* safety break *)
		Do[ (* loop over possible sets external vertices *)
			(* if there are no internal vertices needed *)
			If[Length[vertExt[[i]]]==numVertex&&Complement[Mall,Flatten[vertExt[[i]]]]=={}
				,vertices=vertExt[[i]];Break[]
			];
	(* Internal vertices *)
	(* remaining set of propgators to build up internal vertices *) 
			Mremaining=Complement[Mall,Flatten[vertExt[[i]]]]; 
			numVertexRemaining=numVertex-numExt;
			MaxValencyRemaining=Length[Mremaining]-3 (numVertex-numExt);
			If[MaxValencyRemaining<0
				,Continue[]
			 ];
			pos=ConstantArray[0,{MaxValencyRemaining+1}];
			Do[ (* loop for the valency *)
				subsetsExt[j]=Subsets[Mremaining,{j}];
				pos[[j-2]]=Position[Plus@@@subsetsExt[j],0,{1}];(* Momentum conservation *)
				If[Length[pos[[j-2]]]>0
					,pos[[j-2]]= Extract[subsetsExt[j],pos[[j-2]]]
				];
			,{j,3,3+MaxValencyRemaining}];
			(* Remove vertices which include the same propagator *)
			vertInt=Join@@pos /. {}-> Nothing;
			If[Length[vertInt]<numVertexRemaining
				,Continue[]
			];	  
			vertInt=Subsets[vertInt,{numVertexRemaining}];
			(* Remove vertices which include the same propagator (to high valency covered here as well) *)
			vertInt=Replace[vertInt,x_/;Length@(Union@@x)<Length@(Join@@x)-> Nothing,{1}];
			(* Remove vertices with valency to low *)
			vertInt=Replace[vertInt,x_/;Length@(Union@@x)<Length@Mremaining-> Nothing,{1}];

			Do[ (* loop over possible sets of internal vertices *)
				If[CountingEdges[Join[vertExt[[i]],vertInt[[k]]],Mext][[1]]==Length[MpropTemp] &&CountingEdges[Join[vertExt[[i]],vertInt[[k]]],Mext][[2]]==True
					,vertices=Join[vertExt[[i]],vertInt[[k]]]; Break[];
				]
			,{k,1,Length[vertInt]}];
			If[vertices!= {},
				Break[]
			];
		,{i,1,Length[vertExt]}];
	];
];
If[Length@tadpoleSave>0&&Length@vertices>0,
	vertices[[1]]=Join[vertices[[1]],tadpoleSave,-tadpoleSave]
];
vertices
]

(* DRAWING DIAGRAMMS *)
FindLabeledDiagram[vertices_,Mprop_,Mext_,labelsDef_:{}, printDiag_:1,imSize_:Full,title_:""]:=Module[{Mall,labels,vertExternal,vertTemp,graph,edges,order,v},
Mall=Join[-Mext,Mext,Mprop,-Mprop];

If[labelsDef=={}
,labels=Join[-Mext,Mext,Mprop,-Mprop];
 ,If[Length[labelsDef]!=Length[Mprop],
Print["Not enough labels for the propagtors. Default labeling chosen."];
 labels=Join[-Mext,Mext,Mprop,-Mprop]; 
,labels=Join[-Mext,Mext,labelsDef,-labelsDef]; 
]
];

vertExternal=Table[-{Mext[[i]]},{i,1,Length[Mext]}];
vertTemp=vertices;
vertTemp=Join[vertExternal,vertTemp];
graph={};
Do[
Do[

If[Length[Union[vertTemp[[i]],-vertTemp[[j]]]]<(Length[vertTemp[[i]]]+Length[vertTemp[[j]]])&&((SubsetQ[Mext,Intersection[vertTemp[[i]],-vertTemp[[j]]]]==False) ||(Length[vertTemp[[i]]]==1&&Length[vertTemp[[j]]]>1))
(* The second condition is for forward scattering: Do not connect Vertex(-p) and Vertex(p) by an edge carrying p *)
,edges=DeleteDuplicates[Intersection[vertTemp[[i]],-vertTemp[[j]]],#1===-#2&];
 If[Length[vertTemp[[i]]]>1,
 edges=Complement[edges,Mext]
  ]; (* No internal edges carrying only external momenta *)
Do[ 
graph=Append[graph,{i->j (*ToString[vertTemp[[i]]]->ToString[vertTemp[[j]]]*),{Extract[labels,Position[Mall,edges[[k]],{1}][[1]]],edges[[k]]}}]
,{k,1,Length[edges]}]
];
,{j,i,Length[vertTemp]}]
,{i,1,Length[vertTemp]}];
(* order diagram with respect to propergators *)
order=Range@Length[Mext];
Do[order=Append[order,Position[graph[[All,2,2]]^2,_?(#==Mprop[[j]]^2||#==(-Mprop[[j]])^2&)]],{j,1,Length[Mprop]}];
graph=graph[[Flatten@order]];
graph[[All,2,2]]=Nothing;
graph=Flatten[#,1]&/@graph;
If[printDiag==1
,Print[Labeled[GraphPlot[graph,Method->{"SpringElectricalEmbedding", "RepulsiveForcePower" -> -1.55},EdgeRenderingFunction->({{RGBColor[0.22,0.34,0.63],Arrowheads[0.015],Arrow[#]},If[#3=!=None,Text[#3,Mean[#1],Background->White],{}]}&),MultiedgeStyle->.3,SelfLoopStyle->All,ImageSize->imSize],title,Top]]
];
graph
]
Contract2SubDiagram[mis_,topGraph_,extNumberTopTopo_,printDiag_:1,imSize_:Full]:=Block[{graph=topGraph,gTemp,temp,imgTemp,subGraphs,labels,tempMI,propNumber,title},
(* creates all graphs of the topologies by contraction internal edges. *)
(* MIs: is list of master integrals as given by Kira. Last entry of every MI is its sector ID *)
(* topograph is the directed graph of the top-topology, the last n-entries are the n external legs. *)
(* propNumber is number of propagators of the top topology *)
(* extNumber is number of external lines *)
subGraphs={};
propNumber=Length[topGraph]-extNumberTopTopo;
tempMI=mis;
tempMI=tempMI/. x_/; x<0 -> 0/. x_ /;x>1 -> 1; (* remove numerators *)
tempMI=DeleteDuplicates[tempMI ]; (* find relevant ``topologies'' *)
Do[title[k]="SecID: "<>ToString[Dot[Table[2^(j-1),{j,1,propNumber}],tempMI[[k,1;;propNumber]]]]<>"; SubTopo: "<>ToString[tempMI[[k]]],{k,1,Length[tempMI]}];


tempMI=Join[ConstantArray[1,extNumberTopTopo],#]&/@tempMI;(*prepend external lines*)
Do[(* loop over subtopologies *)
gTemp=graph;
If[Depth[gTemp[[1]]]<3 (* Create Labels if neccessary *)
,gTemp=Transpose[{gTemp}]; graph=Transpose[{graph}];
Do[gTemp[[i]]=Append[gTemp[[i]],Subscript["D",ToString[i-extNumberTopTopo]]],{i,extNumberTopTopo+1,Length[gTemp]}];
Do[graph[[i]]=Append[graph[[i]],Subscript["D",ToString[i-extNumberTopTopo]]],{i,extNumberTopTopo+1,Length[graph]}];
Do[gTemp[[i]]=Append[gTemp[[i]],Subscript["ext",ToString[i]]],{i,1,extNumberTopTopo}];
Do[graph[[i]]=Append[graph[[i]],Subscript["ext",ToString[i]]],{i,1,extNumberTopTopo}];
];

temp={};
(* CONTRACTION=DELETION+MERGING *)
Do[(* loop over contractions *)
(* DELETION *)
If[tempMI[[j,i]]<= 0,
gTemp=DeleteCases[gTemp,graph[[i]]];
temp=Join[temp,{graph[[i]]}];
]
,{i,1,propNumber+extNumberTopTopo}];
(* MERGING (propagator can be dressed (dashed, colored, etc ) *)
Do[gTemp=gTemp/. temp[[i,1]]; temp=temp /.temp[[i,1]],{i,1,Length[temp]}];
(*Drawing diagram *)
If[printDiag==1,
Print[Labeled[GraphPlot[gTemp,Method->{"SpringElectricalEmbedding", "RepulsiveForcePower" -> -1.55},EdgeRenderingFunction->({{RGBColor[0.22,0.34,0.63],Arrowheads[0.015],Arrow[#]},If[#3=!=None,Text[#3,Mean[#1],Background->White],{}]}&),MultiedgeStyle->.3,SelfLoopStyle->All,ImageSize->imSize],title[j],Top]]];
subGraphs=Append[subGraphs,gTemp];
,{j,1,Length[tempMI]}];
subGraphs
]
End[]
EndPackage[]






