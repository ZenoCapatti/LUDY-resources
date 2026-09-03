(* ::Package:: *)

BeginPackage["GraphTools`"];


Needs["IGraphM`"];


MassiveGraphQ::usage = "Checks if Graph is massive."


graphPlotMR::usage = "Plot graph."


GraphPlotPM::usage = "A more readable graph printout for graphs with two massive lines."


conventionalGraphMR::usage = "Get a mathematica form of the graph."


SolveMC::usage = "Solve momentum conservation."
SolveMCIntermsOf::usage ="";


MCEquations::usage = "The equations obtained from momentum conservation in each vertex."


CollapseLineMR::usage = "Returns a graph with line i collapsed."


FindLoops::usage =  "Returns a list of all cycles."


FindUniqueLoops::usage = "Returns a list of generating cycles, i.e. the \"loops\" of the graph."


LoopCount::usage = "Returns the number of loops of the graph."


isomorphismRule::usage = "isomorphismRule[graph1,graph2] returns a list of isomorphisms between graph1 and graph2."


automorphismRule::usage = "isomorphismRule[graph] returns a list of automorphisms of graph."


isomorphicQ::usage = "Checks if two graphes are isomorphic to each other.";


GetRepresentativeGraph::usage = "GetRepresentativeGraph[graph,graphList] picks the first graph from graphlist that is isomorphic to graph."


LoopMomentaGraph::usage = "Gives the loop momenta of the graph." 


GetMasses::usage = "Gives the masses of the graph."


ConvertGraph::usage = "Converts graphs between conventions used by various people."


GetPropagators::usage = "Assembles propagators for the diagram."


GetSinglePropagator::usage = "Assembles propagators for the diagram."


AllLines::usage = "Internal and external lines of the graph";
ExternalLines::usage = "External lines of the graph.";
InternalLines::usage = "Internal lines of the graph."


DanglingLines::usage = "Dangling lines of the graph, i.e. lines that are neither external nor part of a loop."


DoubledLines::usage = "Returns a list of list of lines which have the same momenta (up to sign flowing through them)"


MGCountDoubledLines::usage = "";
MGHasDoubledLine::usage = "";


NeclaceGraphQ::usage = "Checks a well-formed graph."


CollapsedExternalQ::usage = "";


mergeGraphs::usage = "Merge graphs into one containing all lines."


LabelMap::usage = "LabelMap[map][graph] applies map to the graph."


MGEdgeConnectivity::usage = "Gives the degree of connectedness of the graph, ignoring external lines. Equivalently a graph g is MGEdgeConnectivity[g]-particle reducibile. "


ExternalNodes::usage ="";


InternalNodes::usage = "";


CountExternalNodes::usage ="";


CountInternalNodes::usage = "";


ExtractSubGraph::usage ="";


FactorGraphPartition::usage ="";


FactorGraph::usage ="";


FactorizableGraphQ::usage ="";


SubLoopGraphs::usage ="";


MGCountInternal::usage = "";


MGCountExternal::usage = "";


CollapseDangling::usage = "Contract all dangling lines in the graph."


CollapseDoubled::usage = "Contract all doubled lines in the graph"


ExternalOS::usage ="";


GraphVars;


MGCountDangling::usage = "";


MGCubicGraphQ::usage = "";


MGCubicGraphNoDanglingQ::usage = "";


MGCubicGraphNoDanglingAndDoubleQ::usage="";


MGHasDanglingLine::usage ="";


MGUniqueID::usage = "Produces an unique identifier for a graph."; 


MGUniqueWithLabelID::usage = "Produces an unique identifier for a graph keeping the external labels intact."; 


LinesWithMass::usage = "LinesWithMass[m][graph] returns the list of all lines in graph that have mass m. In case m is a list returns all lines with any of the masses."


graphPlotMR2;


MGGraphPlot;
MGEdgeTaggedGraph;


FindLoopParametrization;
SolveParentMCThroughDaughter;


CutList::usage ="";


Begin["`Private`"];


(* ::Section:: *)
(*Drawing*)


colorsMR[i_]:=Piecewise[{{Black,i==0},{Red,i==1},{Blue,i==2},{ColorData["BrightBands"][0.2*i],i>2}}];


Options[MGGraphPlot]={"ShowDetails"-> True};
MGGraphPlot[graphData_,opt:OptionsPattern[]]:=GraphPlot[MGEdgeTaggedGraph[graphData]];


Options[MGEdgeTaggedGraph]={"ShowDetails"-> True};
MGEdgeTaggedGraph[graphData_,OptionsPattern[]]:=Module[{cGraph,edges,labels,styles,labelededges},
cGraph=conventionalGraphMR[graphData];
edges=cGraph[[;;,1]];
labels=If[OptionValue["ShowDetails"],cGraph[[;;,2,1]],Table[None,Length[cGraph]]];
styles=If[Length[#]>1,colorsMR[#[[2]]],colorsMR[0]]&/@cGraph[[;;,2]]/.Global`m->Identity;
labelededges=MapThread[Style[Labeled[#,#2],#3]&,{edges,labels,styles}];
Return[EdgeTaggedGraph[labelededges,EdgeLabels->"Name",ImageSize->Medium,GraphLayout->"SpringElectricalEmbedding"]];
]


Options[graphPlotMR]:={"HighlightMasses"-> True,"SimpleLabels"->True ,"ShowDetails"-> True};
graphPlotMR[graphData_,op:OptionsPattern[]]/;KeyExistsQ[graphData,"Graph"]:=graphPlotMR[graphData["Graph",op]];
graphPlotMR[graphData_,OptionsPattern[]]:=Module[{masses=GetMasses[graphData],massiveLines,cGraph,coloring,edgeLabel,gr},
cGraph=conventionalGraphMR[graphData];
If[!MassiveGraphQ[graphData],cGraph=MapAt[Join[#,{0}]&,cGraph,{All,2}]];
coloring=Automatic;
If[MassiveGraphQ[graphData]&&OptionValue["HighlightMasses"],
massiveLines=Table[First/@Cases[cGraph,{_,{___,ma,___}}],{ma,masses}];
coloring=Flatten[Thread/@Thread[massiveLines-> colorsMR/@Range[Length[massiveLines]]]]
];
edgeLabel=Automatic;

gr=If[OptionValue["ShowDetails"],
Map[{Style[#[[1]],colorsMR[#[[2,2]]/.Global`m[i_]:> i/.Missing["KeyAbsent",_]:>0]],#[[2,1]]}&,cGraph],
Map[Style[UndirectedEdge@@#[[1]],colorsMR[#[[2,2]]/.Global`m[i_]:> i/.Missing["KeyAbsent",_]:>0]]&,cGraph]
];
gr=Graph[gr[[;;,1]]];
Graph[gr,VertexCoordinates->GraphEmbedding[gr,"SpringElectricalEmbedding"]]
];


Options[graphPlotMR2]:={"HighlightMasses"-> True,"SimpleLabels"->True ,"ShowDetails"-> True};
graphPlotMR2[graphData_,op:OptionsPattern[]]/;KeyExistsQ[graphData,"Graph"]:=graphPlotMR[graphData["Graph",op]];
graphPlotMR2[graphData_,OptionsPattern[]]:=Module[{masses=GetMasses[graphData],massiveLines,cGraph,coloring,edgeLabel,gr},
cGraph=conventionalGraphMR[graphData];

Return[cGraph];

If[!MassiveGraphQ[graphData],cGraph=MapAt[Join[#,{0}]&,cGraph,{All,2}]];
coloring=Automatic;
If[MassiveGraphQ[graphData]&&OptionValue["HighlightMasses"],
massiveLines=Table[First/@Cases[cGraph,{_,{___,ma,___}}],{ma,masses}];
coloring=Flatten[Thread/@Thread[massiveLines-> colorsMR/@Range[Length[massiveLines]]]]
];
edgeLabel=Automatic;

gr=If[OptionValue["ShowDetails"],
Map[{Style[#[[1]],colorsMR[#[[2,2]]/.Global`m[i_]:> i/.Missing["KeyAbsent",_]:>0]],#[[2,1]]}&,cGraph],
Map[Style[UndirectedEdge@@#[[1]],colorsMR[#[[2,2]]/.Global`m[i_]:> i/.Missing["KeyAbsent",_]:>0]]&,cGraph]
];
gr=Graph[gr[[;;,1]]];
Graph[gr,VertexCoordinates->GraphEmbedding[gr,"SpringElectricalEmbedding"]]
];


Options[GraphPlotPM]={"ShowDetails"-> True,"Wiggle"->0 };
GraphPlotPM[graph_,OptionsPattern[]]:=Module[{mass1,mass2,external=ExternalLines[graph],massless,cGraph=conventionalGraphMR[graph],undirectedGraph,vrules,gg,vLabel,mass1U,mass2U,pp1,pp2,pp3,pp4,nn},
undirectedGraph=UndirectedEdge@@@First/@cGraph;
{mass1,mass2}={Cases[cGraph,{e_,{_,Global`m[1]}}:> e],Cases[cGraph,{e_,{_,Global`m[2]}}:> e]};
{mass1U,mass2U}={UndirectedEdge@@@mass1,UndirectedEdge@@@mass2};
{pp1,pp4}=Select[VertexList[mass1U],VertexOutDegree[mass1U,#]==1&];
{pp2,pp3}=Select[VertexList[mass2U],VertexOutDegree[mass2U,#]==1&];
massless=First/@Cases[cGraph,{_,{_,0}}];
vLabel=Thread[Extract[cGraph,{All,1}]-> Extract[cGraph,{All,2,1}]];
nn=OptionValue["Wiggle"];
vrules=Join[
Thread[First[FindPath[UndirectedEdge@@@mass1,pp1,pp4]]-> Table[{x,1/2+nn-RandomReal[2nn]},{x,-1,1,2/(Length[mass1])}]],
Thread[First[FindPath[UndirectedEdge@@@mass2,pp2,pp3]]-> Table[{x,-1/2+nn-RandomReal[2nn]},{x,-1,1,2/(Length[mass2])}]]
];
gg=Join[
Thread[Style[massless,Black]],
Thread[Style[mass1,Red]],
Thread[Style[mass2,Blue]]
];
If[!OptionValue["ShowDetails"],gg=MapAt[UndirectedEdge@@#&,gg,{All,1}]];
vLabel=Join[
Cases[cGraph,{e_,{l_,Global`m[1]}}:>( e-> l)],
Cases[cGraph,{e_,{l_,Global`m[2]}}:>( e-> l)],
Cases[cGraph,{e_,{l_,0}}:> (e-> l)]
];
If[OptionValue["ShowDetails"]===True,
	Return[Graph[gg,VertexCoordinates->vrules,EdgeLabels->vLabel]],
Return[Graph[gg,VertexCoordinates->vrules]]
];
]


(* ::Section:: *)
(*General Graph Properties*)


MassiveGraphQ[graphData_]:=KeyExistsQ[graphData,"Masses"];


NeclaceGraphQ[expr_]:=Module[{toret=False},If[AssociationQ[expr],If[KeyExistsQ[expr,"Neclace"],toret=True;]]; Return[toret]];


CollapsedExternalQ[graph_]:=Module[{elines=ExternalLines[graph]},
AnyTrue[ExternalNodes[graph],Count[#,_?(MemberQ[elines,#|-#]&)]>1&]];


AllLines[graph_]:=-Cases[Union@Flatten[graph["Neclace"]],-_|_?Negative];


ExternalLines[graph_]:=Module[{AllMomenta,Incoming,Outgoing},
AllMomenta=Union[Flatten[Select[graph["Neclace"],(Length[#]==1)&]]];
Outgoing=-Cases[AllMomenta,-_|_?Negative];
Incoming=Complement[AllMomenta,-Outgoing];
Return[Union[Incoming,Outgoing]];
];


InternalLines[graph_]:=Complement[AllLines[graph],ExternalLines[graph]];


DanglingLines[graph_]:=Module[{loopMoms=Union@@Extract[FindUniqueLoops[graph],{All,All,2,1}]},
(* A dangeling line is internal, but not a loop *)
Return[Complement[InternalLines[graph],loopMoms]]
]


DoubledLines[graph_]:=Module[{mc=SolveMC[graph],internal=InternalLines[graph]},
Return[Select[Gather[internal,Simplify[#1-#2/.mc]===0||Simplify[#1+#2/.mc]===0&],Length[#]>1&]];
]


LinesWithMass[m_List][graph_]:=Union[LinesWithMass[#][graph]&/@m];
LinesWithMass[m_][graph_]:=Module[{},
(* If there is no mass info we either return the full graph or nothing *)
If[!KeyExistsQ[graph,"Masses"],
If[m===0,Return[AllLines[graph]],{}]
];
Cases[Normal[graph["Masses"]],HoldPattern[x_-> m]:> x]
]


(*DoubledLines[graph_]:=Module[{mcEqns=MCEquations[graph]},
Select[Gather[InternalLines[graph],(PolynomialMod[#1-#2,mcEqns]===0||PolynomialMod[#1+#2,mcEqns]===0)&],Length[#]>1&]
]*)


MGCountDoubledLines[graph_]:=Length[DoubledLines[graph]];
MGHasDoubledLine[graph_]:=MGCountDoubledLines[graph]>0;


ExternalNodes[graph_]:=Module[{},
Return[Select[graph["Neclace"],(!FreeQ[#,Alternatives@@ExternalLines[graph]]&&Length[#]>1)&]];
]


GraphVars[gr_]:=Module[{ilines=InternalLines[gr]},
Return[Map[LorentzVectorUtils`Sq[Total[Complement[#,Join[ilines,-ilines]]]]&,ExternalNodes[gr]]];
]


InternalNodes[graph_]:=Module[{},
Return[Select[graph["Neclace"],Length[#]>1&]];]


CountExternalNodes[graph_]:=Length[ExternalNodes[graph]];


CountInternalNodes[graph_]:=Length[InternalNodes[graph]]


MGCountInternal[graph_]:=Length[InternalLines[graph]];


MGCountExternal[graph_]:=Length[ExternalLines[graph]];


MGCountDangling[graph_]:=Length[DanglingLines[graph]];


MGEdgeConnectivity[Graph_]/;NeclaceGraphQ[Graph]:=Module[{gg=DeleteCases[Graph["Neclace"],{_}],lines,sGraph},
(* directly construct a graph with truncated external lines and no orientation. *)
lines=InternalLines[Graph];
sGraph=Table[UndirectedEdge[Position[gg,line,2][[1,1]], Position[gg,-line,2][[1,1]]],{line,lines}];
Return[EdgeConnectivity[sGraph]];
];


MGHasDanglingLine[graph_]:=MGCountDangling[graph]>0;


MGCubicGraphQ[graph_]:=AllTrue[InternalNodes[graph],Length[#]==3&];
MGCubicGraphNoDanglingQ[graph_]:=MGCubicGraphQ[graph]&&!MGHasDanglingLine[graph];


MGCubicGraphNoDanglingAndDoubleQ[graph_]:=MGCubicGraphQ[graph]&&!MGHasDanglingLine[graph]&&!MGHasDoubledLine[graph];


(* ::Section:: *)
(*Getters*)


GetMasses[graphData_]:=If[KeyExistsQ[graphData,"Masses"],Union@Cases[Values[graphData["Masses"]],_Global`m,Infinity],{}]


Options[GetPropagators]={"LabelList"-> False,"SolveMC"-> True}
GetPropagators[graph_,OptionsPattern[]]:=Module[{labs=InternalLines[graph],masses,mc},
masses=If[KeyExistsQ[graph,"Masses"],graph["Masses"]/@labs,Table[0,Length[labs]]];
mc=If[OptionValue["SolveMC"],SolveMC[graph],{}];
If[OptionValue["LabelList"],
Return[Table[{labs[[ii]],LorentzVectorUtils`Sq[labs[[ii]]/.mc]-masses[[ii]]^2},{ii,1,Length[labs]}]]
];
Table[LorentzVectorUtils`Sq[labs[[ii]]/.mc]-masses[[ii]]^2,{ii,1,Length[labs]}]
]


GetSinglePropagator[graph_,l_]:=
If[MassiveGraphQ[graph],
LorentzVectorUtils`Sq[l]-(l/.graph["Masses"]/.l->0)^2,
LorentzVectorUtils`Sq[l]
]


GetSinglePropagator[graph_, lineList_List]:=GetSinglePropagator[graph,#]&/@lineList;


ExternalOS[graph_]:=Module[{ext=ExternalLines[graph],masses=If[KeyExistsQ[graph,"Masses"],graph["Masses"],0&]},
Return[LorentzVectorUtils`Sq[#]-(masses[#]^2)&/@ext/.Missing["KeyAbsent",_]:>0];
]


(* ::Section:: *)
(*Momentum Conservation*)


MCEquations[graph_]:=Plus@@@Select[graph["Neclace"],Length[#]>1&];


SolveMC[graph_,vars_:{}]:=Module[{externalRules,internalRules,externalMC,internalMC,iMoms,internalVars,externalVars},
(* sort user-chosen variables to the back *)
externalVars=SortBy[ExternalLines[graph],MemberQ[vars,#]&];
externalRules=Select[graph["Neclace"],Length[#]==1&];
externalMC=Quiet[ Solve[0==Total@Flatten[externalRules],externalVars],Solve::svars];
internalRules=Complement[graph["Neclace"],externalRules];
iMoms=SortBy[InternalLines[graph],MemberQ[vars,#]&];
internalMC=Quiet[ Solve[(Total/@internalRules/.externalMC)==0,iMoms],Solve::svars];
Return[Flatten@Join[externalMC,internalMC]]
]


SolveMCIntermsOf[graph_,vars_]:=Module[{},
	Quiet[
	First@Solve[MCEquations[graph]==0,Join[ExternalLines[graph],SortBy[InternalLines[graph],!MemberQ[vars,#]&]]]
	,{Solve::svars}]
]


(* ::Section:: *)
(*Graph Manipulations*)


CollapseLineNeclace[sgraph_, lineList_List]:=Fold[CollapseLineNeclace,sgraph,lineList];
CollapseLineNeclace[sgraph_,line_]:=Module[{toret},
toret=sgraph;
   toret = toret /. {a1___, {b2___, line, b1___}, a2___, {b4___, -line, b3___},
                       a3___} :> {a1, {b1, b2, b3, b4}, a2, a3};
   toret = toret /. {a1___, {b2___, -line, b1___}, a2___, {b4___, line, b3___},
                       a3___} :> {a1, {b1, b2, b3, b4}, a2, a3};
   toret = toret /. {a1___,{b1___, line, b2___, -line, b3___}, a2___}:> {a1,{b1,b2,b3},a2};
   toret = toret /. {a1___,{b1___, -line, b2___, line, b3___}, a2___}:> {a1,{b1,b2,b3},a2};
Return[toret];
]


CollapseLineMR[graphData_,lineList_List]:=Module[{newGraph,newMasses},
newGraph=Association["Neclace"-> CollapseLineNeclace[graphData["Neclace"],lineList]];
If[KeyExistsQ[graphData,"Masses"],
newGraph=Append[newGraph,"Masses"-> KeyDrop[graphData["Masses"],lineList]]];
Return[newGraph]
];
CollapseLineMR[graphData_,line_]:=CollapseLineMR[graphData,{line}];


mergeGraphs[graphList_List]:=Merge[graphList,Join@@#&]


LabelMap[map_][graph_]:=Module[{labelMap=MapAt[#/.-x_:> x&,map,{All,2}],nec,mass},
nec=graph["Neclace"]/.map;
If[MassiveGraphQ[graph],
mass=Association@KeyValueMap[((#1/.labelMap)->(#2/.map) )&,graph["Masses"]];
Return[Association["Neclace"-> nec,"Masses"-> mass]];
];
Return[Association["Neclace"-> nec]];
];


CollapseDangling[graph_]:=CollapseLineMR[graph,DanglingLines[graph]];


CollapseDoubled[graph_]:=CollapseLineMR[graph,Flatten[Drop[#,1]&/@DoubledLines[graph]]];


Loop related functions


(* TODO: this function has a weird logic, bases on the head p. 
This should never be done, instead GetExternalLines should be used if nescessary*)


(* also instead of the auxilarry head one can directly do sequence@@{ i++;..}*)


FindUniqueLoops[graph_]:=Module[{ii=0,cGraph=DeleteCases[conventionalGraphMR[graph],{__,{Global`p[_],_}}],toret,x,rr},
toret=cGraph/.{DirectedEdge[a_,b_],c_}:>(ii++;rr[DirectedEdge[a,x[ii]],DirectedEdge[x[ii],b]]);
toret=toret/.rr-> Sequence;
toret=FindFundamentalCycles[UndirectedEdge@@@toret];
toret=Union@Cases[#,_x,Infinity]&/@toret/.x-> Identity;
toret=cGraph[[#]]&/@toret;
Return[toret];
]


FindLoops[graph_]:=Module[{ii=0,cGraph=DeleteCases[conventionalGraphMR[graph],{__,{Global`p[_],_}}],toret,x,rr},
toret=cGraph/.{DirectedEdge[a_,b_],c_}:>(ii++;rr[DirectedEdge[a,x[ii]],DirectedEdge[x[ii],b]]);
toret=toret/.rr-> Sequence;
toret=FindCycle[UndirectedEdge@@@toret,Infinity,All];
toret=Union@Cases[#,_x,Infinity]&/@toret/.x-> Identity;
toret=cGraph[[#]]&/@toret;
Return[toret];
]


LoopCount[graph_]:=Return[Length[FindUniqueLoops[graph]]];


SubLoopGraphs[graph_]:=ExtractSubGraph[graph,#]&/@Extract[FindLoops[graph],{All,All,2,1}];


ExtractSubGraph[graph_,lines_]:=Module[{toret,truncatedExternal},
toret=Select[graph["Neclace"],!FreeQ[#,Alternatives@@lines]&];
truncatedExternal={-#}&/@List@@Total[toret,2];
toret=Association["Neclace"-> Join[toret,truncatedExternal]];
If[MassiveGraphQ[graph],AssociateTo[toret,"Masses"-> KeyTake[graph["Masses"],AllLines[toret]]]];
Return[toret];
];


FactorGraphPartition[graph_]:=Module[{loops=Extract[FindUniqueLoops[graph],{All,All,2,1}],toret},
(* if loops intersect they belong to the same subgraph *)
Return[DeleteDuplicates/@(loops//.{a___,l1_List,b___,l2_List,c___}/;IntersectingQ[l1,l2]:> {a,Join[l1,l2],b,c})];
]


FactorGraph[graph_]:=ExtractSubGraph[graph,#]&/@FactorGraphPartition[graph];


FactorizableGraphQ[graph_]:=Length[FactorGraphPartition[graph]]>1;


(* ::Section:: *)
(*Graph Isomorphisms *)


EdgeFlips[eL1_,eL2_]:=Module[{toret={}},
Do[AppendTo[toret,Piecewise[{{1,eL1[[ii]]===eL2[[ii]]},{-1,eL1[[ii]]===(eL2[[ii]]/.DirectedEdge[a_,b_]:>  DirectedEdge[b,a])}},$Failed]
]
,{ii,1,Length[eL1]}];
Return[toret];
]


(* helper function that reinstates signs in maps *)


MapToSignedMap[map_,cGraph1_,cGraph2_]:=Module[{lineMap,nodeMap,lms,remappedLines,mapSigns,signFlipMap,perm},
lms=Cases[cGraph1,_Global`l|_Global`p,Infinity]//Union;
lineMap=KeyTake[map,lms];
nodeMap=Complement[map,lineMap];
perm=FindPermutation[Part[cGraph1,All,2,1]/.map,Part[cGraph2,All,2,1]];
remappedLines=Permute[Part[cGraph1,All,1],perm]/.nodeMap;
mapSigns=EdgeFlips[remappedLines,First/@cGraph2];
signFlipMap=Thread[Part[cGraph2,All,2,1]-> mapSigns*Part[cGraph2,All,2,1]];
Return[KeyValueMap[#1-> (#2/.signFlipMap)&,map]];
]


Options[isomorphismRule]={"MassFlip"->True,"AllowedExternalMappings"-> All,"SortRules"-> False}; 
isomorphismRule[graph1_,graph2_,OptionsPattern[]]:=Module[{sgraph1,sgraph2,egraph1,egraph2,masses1,masses2,lms,ext,coloring1,coloring2,rules,allowedMaps=OptionValue["AllowedExternalMappings"],allMasses={0},allMap,lineMap,nodeMap,perm,remappedLines,mapSigns},
If[Xor[MassiveGraphQ[graph1],MassiveGraphQ[graph1]],Return[{}]];
{sgraph1,sgraph2}=conventionalGraphMR/@{graph1,graph2};
egraph1=UndirectedEdge@@@(sgraph1/.{DirectedEdge[a_,b_],{lab_,___}}:>Sequence[ DirectedEdge[a,lab],DirectedEdge[lab,b]]);
egraph2=UndirectedEdge@@@(sgraph2/.{DirectedEdge[a_,b_],{lab_,___}}:>Sequence[ DirectedEdge[a,lab],DirectedEdge[lab,b]]);
lms=AllLines[graph1];
ext=ExternalLines[graph1];
{coloring1,coloring2}={None,None};
If[MassiveGraphQ[graph1]&&MassiveGraphQ[graph2],
masses1=Extract[sgraph1,{All,2,2}];
coloring1=Riffle[masses1,masses1];
coloring1=If[OptionValue["MassFlip"],coloring1/.Global`m[i_]-> 1,coloring1/.Global`m-> Identity];
masses2=Extract[sgraph2,{All,2,2}];
coloring2=Riffle[masses2,masses2];
coloring2=If[OptionValue["MassFlip"],coloring2/.Global`m[i_]-> 1,coloring2/.Global`m-> Identity];
allMasses=Union[allMasses,masses1,masses2];
];
(* now we generate the isomorphism using IGraph *)
allMap=IGVF2FindIsomorphisms[{Graph@egraph1,"EdgeColors"->coloring1},{Graph@egraph2,"EdgeColors"->coloring2}];
(* reinstate signs using helper function MapToSignedMap  *)
rules=MapToSignedMap[#,sgraph1,sgraph2]&/@allMap;
(* We only want the rules associated to the loop momenta  *)
rules=KeyTake[rules,lms];
rules=Switch[OptionValue["AllowedExternalMappings"],
(* filter out rules that map external lines*)
None,Select[rules,And@@KeyValueMap[SameQ,KeyTake[#,ext]]&],
All,rules,
Blank[],Select[rules,MemberQ[allowedMaps,Sort@KeyTake[#,ext]]&]
];
rules=Table[{rl,Union@KeyValueMap[(#1/.graph1["Masses"])->  (Assuming[Thread[allMasses>= 0],Simplify@Abs[#2/.graph2["Masses"]]])&,rl]},{rl,rules}];
(* check if mass relabeling is valid *)
rules=Select[rules,Sort[First/@#[[2]]]===allMasses&];
If[OptionValue["SortRules"],
(* sort such that rules with less mass flips are first *)
rules=SortBy[rules,-Count[Subtract@@@Last[#],0]&];
];
(* remove trivial relabeling and append mass rules to association *)
rules=Map[KeyDrop[Association[#],0]&,rules];
Return[rules];
]


Options[automorphismRule]={"MassFlip"->True,"AllowedExternalMappings"-> All,"SortRules"-> False}; 
automorphismRule[graph_,opt:OptionsPattern[]]:=isomorphismRule[graph,graph,opt];


Options[isomorphicQ]={"MassFlip"->True,"AllowedExternalMappings"-> All}; 
isomorphicQ[graph1_,graph2_,opt:OptionsPattern[]]:=
Module[{},
If[MGCountInternal[graph1]!= MGCountInternal[graph2],Return[False]];
If[MGCountExternal[graph1]!= MGCountExternal[graph2],Return[False]];
Return[Length[isomorphismRule[graph1,graph2,opt]]>0
]];


GetRepresentativeGraph[graph_,graphList_List]:=SelectFirst[graphList,isomorphicQ[graph,#]&];


VertexIdentifier[vert_]:=Module[{toret={},vertRest=vert,moms,ext,ii},
For[ii=1,ii<= Length[vert],
moms=Cases[vertRest[[ii]],{_,_}];
ext=Complement[vertRest[[ii]],moms];
AppendTo[toret,Join[SortBy[{ii+Position[vertRest[[ii+1;;-1]],#[[1]]][[1,1]],#[[2]]}&/@moms,First],ext]];
vertRest=vertRest/.Thread[moms-> Sequence[]];
ii++;];
Return[toret];
]


MGUniqueID[graph_]:=Module[{internal=InternalLines[graph],external=ExternalLines[graph],verts,vertsGather,massAssoc=graph["Masses"],masses,lengthPreservingPerms,nn,fkt},
masses=Union[Values[massAssoc]];
(* distinguish vertices as much as possible to avoid considering to much permutations *)
fkt={Length[#],Table[Count[#,mmm,{2}],{mmm,masses}],Table[Count[#,mmm,{1}],{mmm,masses}],Intersection[external,#]}&;
verts=Select[graph["Neclace"],Length[#]>1&] /.KeyTake[massAssoc,external]/.Thread[#-> {#,massAssoc[#]}&/@internal]/.-x_:> x;
verts=SortBy[verts,fkt];
vertsGather=
GatherBy[verts,fkt];
nn=Length[vertsGather];
lengthPreservingPerms=If[
Length[vertsGather]>1,
Flatten[Outer[Join,Sequence@@(Permutations/@vertsGather),1],nn-1],
Permutations[verts]
];
Return[Sort[VertexIdentifier/@lengthPreservingPerms][[1]]];
]


MGUniqueWithLabelID[graph_]:=Module[{internal=InternalLines[graph],external=ExternalLines[graph],verts,vertsGather,massAssoc=graph["Masses"],masses,lengthPreservingPerms,nn},
masses=Values[massAssoc];
verts=Select[graph["Neclace"],Length[#]>1&] /.Thread[#-> {#,massAssoc[#]}&/@internal]/.-x_:> x;
verts=SortBy[verts,{Length[#],Table[Count[#,mmm],{mmm,external}],Intersection[external,#]}&];
vertsGather=
GatherBy[verts,{Length[#],Table[Count[#,mmm],{mmm,masses}],Intersection[external,#]}&];
nn=Length[vertsGather];
lengthPreservingPerms=If[
Length[vertsGather]>1,
Flatten[Outer[Join,Sequence@@(Permutations/@vertsGather),1],nn-1],
Permutations[verts]
];
Return[Sort[VertexIdentifier/@lengthPreservingPerms][[1]]];
]


(* ::Section:: *)
(*Cuts*)


(* ::Input::Initialization:: *)
CutList[graph_,externals_List]:=Module[{gg=conventionalGraphMR[graph],externalsComplement,e1,e2,e3,e4,v1,v2,gr1,gr2,cuts,edGraphs,ed1,ed2},
externalsComplement=Complement[ExternalLines[graph],externals];
e1=Cases[gg,{_,{Alternatives@@externals,_}}];
e2=Cases[gg,{_,{Alternatives@@externalsComplement,_}}];

gr1=UndirectedEdge@@@gg[[;;,1]];

ed1=e1[[;;,1,2]];
ed2=e2[[;;,1,2]];

(*Glue the external points*);
gr2=gr1/.Thread[e1[[;;,1,2]]->v1];
gr2=gr2/.Thread[e2[[;;,1,2]]->v2];
cuts=IGraphM`IGFindMinimalCuts[Graph[gr2],v1,v2];
(*Print[cuts];*);
cuts=Map[Select[#,FreeQ[#,v1|v2]&]&,cuts];
edGraphs=EdgeDelete[Graph[gr1],#]&/@cuts;
(*Print[HighlightGraph[Graph[gr1],#]&/@cuts]*);
cuts=Select[cuts,MatchQ[(ConnectedComponents@EdgeDelete[Graph[gr1],#]),{a_,b_}/;ContainsAll[a,ed1]&&ContainsAll[b,ed2]||ContainsAll[b,ed1]&&ContainsAll[a,ed2]]&];
cuts=cuts/.UndirectedEdge[a_,b_]:>UndirectedEdge@@Sort[{a,b}];

Return[Cases[gg/.DirectedEdge[a_,b_]:>UndirectedEdge@@Sort[{a,b}],{Alternatives@@#,_}][[;;,2,1]]&/@cuts];
]


(* ::Section::Closed:: *)
(*Conversions between different notations*)


conventionalGraphMR[graphData_]:=Module[{gg=graphData["Neclace"],loopMoms=AllLines[graphData],massAsso},
If[KeyExistsQ[graphData,"Masses"],massAsso=graphData["Masses"],massAsso[x_]:=Sequence[]];
Return[Table[{DirectedEdge[Position[gg,line,2][[1,1]], Position[gg,-line,2][[1,1]]],{line,massAsso[line]}},{line,loopMoms}]]
]


ConvertGraph["Enrico"-> "Me"][gr_]:=Module[{gg=gr[[1]],external,internal,map,masses},
external=Abs/@Flatten@Cases[gg,{_}];
internal=Complement[Union[Cases[gg,_?Positive,Infinity]],external];
map=Join[Thread[external->  Global`p/@external],Thread[(-external)->-( Global`p/@external)],Thread[internal->  Global`l/@internal],Thread[(-internal)->-( Global`l/@internal)]];
If[Length[gr]>1,
masses=KeyMap[#/.map&,gr[[2]]];
Return[Association["Neclace"-> gg/.map,"Masses"-> masses]];,
Return[Association["Neclace"-> gg/.map]];
];
]


StrandManipulation[strand_]:=Module[{toret,f},
toret=MapAt[f[#,-#]&,strand,Position[strand,_?IntegerQ,1]]/.f-> Sequence;
toret=toret/.CaravelGraph`Leg[a_,___]:> -a/.CaravelGraph`Bead-> Sequence;
Partition[Delete[toret,{{1},{-1}}],3]
]


CaravelGraphToNeclaceOld[cGraph_]:=Module[{strands,toret,f,NeclGraph={},ii=1000,nds,lll,ext,massrepls},
ext=Cases[cGraph,_CaravelGraph`Leg,Infinity];
strands=Cases[cGraph,_CaravelGraph`Strand,Infinity]/.CaravelGraph`Link[CaravelGraph`LoopMomentum[i_],j_]:>lll[Sign[i]( Abs[i]+100),j]/.CaravelGraph`Link[j_]:>lll[ ii++,j]/.CaravelGraph`Strand-> List;
massrepls=Association[Join[(Cases[strands,_lll,Infinity]//Union)/.{lll[i_,0]:> (Abs[i]-> 0), lll[i_,j_]:> ( Abs[i]->  Global`m[j])},ext/.CaravelGraph`Leg[a_,b_]:> If[b>0,a-> Global`m[b],a-> 0]]];
strands=strands/.lll[a_,_]:> a;
nds=Cases[cGraph,_CaravelGraph`Node,Infinity];
If[Length[nds]==2,
toret={
Join[nds[[1]]/.CaravelGraph`Leg[a_,b_]:> -a/.CaravelGraph`Node-> List,First/@strands],
Join[nds[[2]]/.CaravelGraph`Leg[a_,b_]:> -a/.CaravelGraph`Node-> List,-Last/@strands]
};
Return[{Join[List[First[#]]&/@ext,toret,Join@@(StrandManipulation/@strands)],massrepls}];
,
toret={
Join[nds[[1]]/.CaravelGraph`Leg[a_,b_]:> -a/.CaravelGraph`Node-> List,Join[First/@strands,-Last/@strands]]
};
Return[{Join[List[First[#]]&/@ext,toret,Join@@(StrandManipulation/@strands)],massrepls}];
];
];
ConvertGraph["Caravel"-> "Enrico"][cGraph_]:=CaravelGraphToNeclaceOld[cGraph]/.{i_Integer/;Abs[i]<= 4:> -i}/.Global`m[-i_]:> Global`m[i];


ConvertGraph["Caravel"-> "Me"][cGraph_]:=ConvertGraph["Enrico"-> "Me"][ConvertGraph["Caravel"-> "Enrico"][cGraph]]


(*FindLoopParametrization[graph_]:=ChooseMomentaWithoutRepetition[Extract[FindUniqueLoops[graph],{All,All,2,1}]]*)
FindLoopParametrization[graph_]:=Intersection[Variables[SolveMC[graph][[;;,2]]],InternalLines[graph]];


SolveParentMCThroughDaughter[parent_,daughter_]:=Module[{vars},
vars=Join[Complement[InternalLines[parent],FindLoopParametrization[daughter]],{ExternalLines[parent][[-1]]}];
First@Solve[MCEquations[parent]==0,vars]
];


End[];


EndPackage[];
