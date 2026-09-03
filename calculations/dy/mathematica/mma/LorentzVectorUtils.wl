(* ::Package:: *)

BeginPackage["LorentzVectorUtils`"];


IP::usage = "P\[CenterDot]Q represents the inner product of the vectors P and Q.";
IP4; IPeps;
Sq::usage = "The square of the vector P.";
DefLVector::usage = "Define lorentz vector.";
DefConstant::usage = "Define a constant.";
ZeroComponent::usage = "ZeroComponent[P] represents the zero component [P\!\(\*SubscriptBox[\(]\), \(0\)]\) of the vector P.";
SpatialComponent::usage = "SpatialComponent[P] represents represents the spatial component  \!\(\*OverscriptBox[\(P\), \(\[RightVector]\)]\)  of the vector P.";
SplitComponent::usage = "SplitComponent[x] splits spatial and temporal part of scalar products in x.";
ConstantQ::usage = "ConstantQ[x] returns true if x is a constant."
LScalarQ::usage = "LScalarQ[x] returns true if x is lorentz scalar."
LVectorQ::usage = "LVectorQ[x] returns true if x is lorentz vector."
vdv::usage = "vdv[P,Q] Represents the derivative operator P\[CenterDot]\!\(\*SubscriptBox[\(\[PartialD]\), \(Q\)]\)"
AbstractD::usage = "AbstractD[x] Represents the derivative operator \!\(\*SubscriptBox[\(\[PartialD]\), \(x\)]\)"


MassiveMomQ::usage ="MassiveMomQ[P] checks if the momentum is massive."
MasslessMomQ::usage ="MassiveMomQ[P] checks if the momentum is massless."


MakeMassive::usage ="MakeMassive[P] sets the momentum P to massive."
MakeMassless::usage ="MakeMassless[P] sets the momentum P to massless."


ReplacementRulesFromPropagators::usage ="Construct a replacement list of scalar products to propagators. "


ISPFromPropagators::usage=" returns a set of propagators and ISP's."


Spaa::usage = "Spaa[i,j] represents the angle bracket \[LeftAngleBracket]i,j\[RightAngleBracket]."
Spbb::usage = "Spbb[i,j] represents the square bracket [i,j]."
Gam::usage = "Gam[i,j] represents the outer product lorentz vector \[LeftAngleBracket]i|\[Gamma]|j]."
ConjugateBrackets::usage  = "ConjugateBrackets[x] returns x with angle and square brackets interchanged."


mass::usage ="mass[i] represents the mass of particle i, \!\(\*SubscriptBox[\(m\), \(i\)]\)=(\!\(\*SuperscriptBox[SubscriptBox[\(p\), \(i\)], \(2\)]\)\!\(\*SuperscriptBox[\()\), \(1/2\)]\).";
massSq::usage ="massSq[i] represents the mass square of particle i, \!\(\*SuperscriptBox[SubscriptBox[\(m\), \(i\)], \(2\)]\)=\!\(\*SuperscriptBox[SubscriptBox[\(p\), \(i\)], \(2\)]\)."


mom::usage = "mom[i,j] represents the Mandelstam invariant \!\(\*SubscriptBox[\(s\), \(ij\)]\) := (\!\(\*SubscriptBox[\(p\), \(i\)]\)+\!\(\*SubscriptBox[\(p\), \(j\)]\)\!\(\*SuperscriptBox[\()\), \(2\)]\)"


Epsilon::usage = "Epsilon[\!\(\*SubscriptBox[\(v\), \(1\)]\),...,\!\(\*SubscriptBox[\(v\), \(n\)]\)] represents the epsilon tensor contracted with vectors. \[Epsilon](\!\(\*SubscriptBox[\(v\), \(1\)]\),,\!\(\*SubscriptBox[\(v\), \(n\)]\)) := \!\(\*SubscriptBox[\(\[Epsilon]\), \(\(\*SubscriptBox[\(\[Mu]\), \(1\)] ... \) \*SubscriptBox[\(\[Mu]\), \(n\)]\)]\)\!\(\*SuperscriptBox[SubscriptBox[\(v\), \(1\)], SubscriptBox[\(\[Mu]\), \(1\)]]\)...\!\(\*SuperscriptBox[SubscriptBox[\(v\), \(n\)], SubscriptBox[\(\[Mu]\), \(n\)]]\)"


ConjugateEpsilon::usage ="ConjugateEpsilon[x] flips the sign of the Epsilon tensor"


Gram::usage = "Gram[\!\(\*SubscriptBox[\(v\), \(1\)]\),...,\!\(\*SubscriptBox[\(v\), \(n\)]\)] represents the gram determinant Det[{\!\(\*SubscriptBox[\(v\), \(i\)]\)\[CenterDot]\!\(\*SubscriptBox[\(v\), \(j\)]\)\!\(\*SubscriptBox[\(}\), \(ij\)]\)]."


TwoRowGram::usage = "Gram[{\!\(\*SubscriptBox[\(v\), \(1\)]\),...,\!\(\*SubscriptBox[\(v\), \(n\)]\)},{\!\(\*SubscriptBox[\(w\), \(1\)]\),...,\!\(\*SubscriptBox[\(w\), \(n\)]\)}] represents the gram determinant Det[{\!\(\*SubscriptBox[\(v\), \(i\)]\)\[CenterDot]\!\(\*SubscriptBox[\(w\), \(j\)]\)\!\(\*SubscriptBox[\(}\), \(ij\)]\)]."


EvaluateGramDets::usage = "Evaluate Gram determinants.";


ExpandMandelstams::usage "ExpandMandelstams[x] expands the Mandelstam invariants in x according to \!\(\*SubscriptBox[\(s\), \(ij\)]\) -> (\!\(\*SubscriptBox[\(p\), \(i\)]\)+\!\(\*SubscriptBox[\(p\), \(j\)]\)\!\(\*SuperscriptBox[\()\), \(2\)]\)."


nLegs::usage = "nLegs represents the number of external momenta. Used for cyclicity. "


ScaleLG::usage = "ScaleLG[x] applies little group scaling according to \[LeftAngleBracket]i| -> \!\(\*SubscriptBox[\(\[Lambda]\), \(i\)]\)\[LeftAngleBracket]i|, [i| -> \!\(\*SuperscriptBox[SubscriptBox[\(\[Lambda]\), \(i\)], \(-1\)]\)[i| to x."


LGScale::usage = "LGScale[i] represents the scaling parameter \!\(\*SubscriptBox[\(\[Lambda]\), \(i\)]\) used in ScaleLG."


ApplySpinorHelicityRules::usage = "ApplySpinorHelicityRules[x] applies Fiertz identites to x."


SpinorHelicityRules::usage = "Spinor Helicity rules."


ContractBracketsDef::usage = "Contract Bracket Rules"


NCM::usage = "Abstract non-commutative multiplication."


NCMPower::usage = "Abstract non-commutative power."


ContractBrackets::usage = "ContractBrackets[x] attempts to express Spinor brackets in terms of Mandelstams"


LorentzTrace::usage = "Trace."


Slashed::usage = "Feynman slash notation."


DualMomenta::usage = "DualMomoment[{\!\(\*SubscriptBox[\(p\), \(1\)]\),...,\!\(\*SubscriptBox[\(p\), \(n\)]\)}] gives dual momenta \!\(\*SubscriptBox[\(v\), \(1\)]\),...,\!\(\*SubscriptBox[\(v\), \(n\)]\), such that \!\(\*SubscriptBox[\(p\), \(i\)]\).\!\(\*SubscriptBox[\(v\), \(j\)]\)=\!\(\*SubscriptBox[\(\[Delta]\), \(ij\)]\)"


DecomposeVector::usage = "DecomposeVector[v,{\!\(\*SubscriptBox[\(p\), \(1\)]\),...,\!\(\*SubscriptBox[\(p\), \(n\)]\)}] writes v as a linear combination of \!\(\*SubscriptBox[\(p\), \(1\)]\),..., \!\(\*SubscriptBox[\(p\), \(n\)]\), assuming that v lies in the span of \!\(\*SubscriptBox[\(p\), \(1\)]\),..., \!\(\*SubscriptBox[\(p\), \(n\)]\)."


ListIPs::usage = "";


IPEquations::usage = "";


SolveIPCoefficients::usage = "";


MGenExplicit::usage = "Explicit form of the Hermitian Lorentz-generators (\!\(\*SuperscriptBox[\(M\), \(\[Mu]\[Nu]\)]\)\!\(\*SuperscriptBox[SubscriptBox[\()\), \(\*SubscriptBox[\(\[Alpha]\), \(1 ... \)] \*SubscriptBox[\(\[Alpha]\), \(s\)]\)], \(\*SubscriptBox[\(\[Beta]\), \(1 ... \)] \*SubscriptBox[\(\[Beta]\), \(s\)]\)]\) = 2is \!\(\*SubsuperscriptBox[\[Delta], \((\!\(\*SubscriptBox[\(\[Alpha]\), \(1\)]\)\),\([\[Mu]\)]\)\!\(\*SuperscriptBox[\(\[Eta]\), \(\(\(\[Nu]\)\(]\)\) \((\*SubscriptBox[\(\[Beta]\), \(1\)]\)\)]\)\!\(\*SubsuperscriptBox[\[Delta], \(\!\(\*SubscriptBox[\(\[Alpha]\), \(2\)]\)\),\(\!\(\*SubscriptBox[\(\[Beta]\), \(2\)]\)\)]\)...\!\(\*SubsuperscriptBox[\[Delta], \(\!\(\*SubscriptBox[\(\[Alpha]\), \(s\)]\)\),\(\!\(\*SubscriptBox[\(\[Beta]\), \(s\)]\)\)]\)."


$MetricSign=-1;
$AutoSimplifyEpsilon=True;


Begin["`Private`"];


If[!ValueQ[$LVectors],$LVectors={};Protect[$LVectors]];
If[!ValueQ[$LScalars],$LScalars={};Protect[$LScalars]];
If[!ValueQ[$Constants],$Constants={};Protect[$Constants]];\.b4


LVectorQ[a_+b_]:=And[LVectorQ[a],LVectorQ[b]];
LVectorQ[Cross[a_,b_]]:=And[LVectorQ[a],LVectorQ[b]];
LVectorQ[a_*b_]:=And[LScalarQ[a],LVectorQ[b]]||And[LVectorQ[a],LScalarQ[b]];
LVectorQ[p_]:=MemberQ[$LVectors,p];


ConstantQ[p_]/;NumericQ[p]:=True;
ConstantQ[a_+b_]:=And[ConstantQ[a],ConstantQ[b]];
ConstantQ[a_*b_]:=And[ConstantQ[a],ConstantQ[b]];
ConstantQ[Times[a_,b_]]:=And[ConstantQ[a],ConstantQ[b]];
ConstantQ[Power[a_,n_]]:=And[ConstantQ[a],ConstantQ[n]];
ConstantQ[p_]/;FreeQ[p,Plus|Times|Power]:=MemberQ[$Constants,p];
ConstantQ[f_[p_]]:=ConstantQ[p];


LScalarQ[p_]/;ConstantQ[p]:=True;
LScalarQ[a_+b_]:=And[LScalarQ[a],LScalarQ[b]];
LScalarQ[a_*b_]:=And[LScalarQ[a],LScalarQ[b]];
LScalarQ[Times[a_,b_]]:=And[LScalarQ[a],LScalarQ[b]];
LScalarQ[Power[a_,n_]]:=And[LScalarQ[a],LScalarQ[n]];
LScalarQ[p_]/;FreeQ[p,Plus|Times|Power]:=MemberQ[$LScalars,p];


DefLVector[p_]:=Module[{},
If[!LVectorQ[p],Unprotect[$LVectors];AppendTo[$LVectors,p];Protect[$LVectors];];
]


DefLScalar[p_]:=Module[{},
If[!LScalarQ[p],Unprotect[$LScalars];AppendTo[$LScalars,p];Protect[$LScalars];];
]


DefConstant[p_]:=Module[{},
If[!ConstantQ[p],Unprotect[$Constants];AppendTo[$Constants,p]; Protect[$Constants];];
]


(* ::Section:: *)
(*Vectors*)


(* Inner product *)


Attributes[IP]^={Orderless};
IP[P_,0]:=0;
IP[0,P_]:=0;
IP[P1_+P2_,Q_]:=IP[P1,Q]+IP[P2,Q];
IP[P_,Q1_+Q2_]:=IP[P,Q1]+IP[P,Q2];
IP[a_?LScalarQ*P_,Q_]:=a*IP[P,Q];
IP[P_,a_?LScalarQ*Q_]:=a*IP[P,Q];
LScalarQ[IP[___]]^=True;
IP/:MakeBoxes[IP[P_,Q_],form_]:=RowBox[{MakeBoxes[P,form],"\[CenterDot]",MakeBoxes[Q,form]}]


Expand[IP[P_,Q_]]^:=IP[Expand[P],Expand[Q]];


(* Square *)
Sq[P_]:=IP[P,P];


(* 4-dim Inner product *)


Attributes[IP4]^={Orderless};
IP4[P_,0]:=0;
IP4[0,P_]:=0;
IP4[P1_+P2_,Q_]:=IP4[P1,Q]+IP4[P2,Q];
IP4[P_,Q1_+Q2_]:=IP4[P,Q1]+IP4[P,Q2];
IP4[a_?LScalarQ*P_,Q_]:=a*IP4[P,Q];
IP4[P_,a_?LScalarQ*Q_]:=a*IP4[P,Q];
LScalarQ[IP4[___]]^=True;
IP4/:MakeBoxes[IP4[P_,Q_],form_]:=RowBox[{MakeBoxes[P,form],"\!\(\*SubscriptBox[\(\[CenterDot]\), \(4\)]\)",MakeBoxes[Q,form]}]


Expand[IP4[P_,Q_]]^:=IP4[Expand[P],Expand[Q]];


(* Square *)
Sq4[P_]:=IP4[P,P];


(* (d-4)-dim Inner product *)


Attributes[IPeps]^={Orderless};
IPeps[P_,0]:=0;
IPeps[0,P_]:=0;
IPeps[P1_+P2_,Q_]:=IPeps[P1,Q]+IPeps[P2,Q];
IPeps[P_,Q1_+Q2_]:=IPeps[P,Q1]+IPeps[P,Q2];
IPeps[a_?LScalarQ*P_,Q_]:=a*IPeps[P,Q];
IPeps[P_,a_?LScalarQ*Q_]:=a*IPeps[P,Q];
LScalarQ[IPeps[___]]^=True;
IPeps/:MakeBoxes[IPeps[P_,Q_],form_]:=RowBox[{MakeBoxes[P,form],"\!\(\*SubscriptBox[\(\[CenterDot]\), \(d - 4\)]\)",MakeBoxes[Q,form]}]


Expand[IPeps[P_,Q_]]^:=IPeps[Expand[P],Expand[Q]];


(* Square *)
IPeps[P_]:=IPeps[P,P];


(* ::Section:: *)
(*Tools associated with propagators *)


ReplacementRulesFromPropagators::NoInverse="Linear inverse does not exist.";
ReplacementRulesFromPropagators::LenghtMismatch="Number of propagators does not match numeber of scalar products.";
Options[ReplacementRulesFromPropagators]={"Head"->Global`propagator ,"Internal"->Nothing ,"External"->Nothing,"LoopMom"->{Global`k},"DoCheck"-> False,"Verbose"-> False,"Overcomplete"->False};
ReplacementRulesFromPropagators[props_,OptionsPattern[]]:=Module[{allVectors,loopVectors,allSkp,loopSkp,mat,rest,pvars,rl,checkVal},
(* Depending on user input determine external and loop momenta. Default is to select based on expressions that appear in propagator list *)

Switch[
{OptionValue["Internal"]===Nothing,OptionValue["External"]===Nothing},
(* everything *)
{False,False},
allVectors=Join[OptionValue["Internal"],OptionValue["External"]];
loopVectors=OptionValue["Internal"];,
(* external momenta  *)
{True,False},
allVectors=Union[Cases[props,_IP,Infinity]/.IP-> Sequence,OptionValue["External"]];
loopVectors=Complement[allVectors,OptionValue["External"]];
,
(* loop momenta *)
{False,True},
allVectors=Cases[props,_IP,Infinity]/.IP-> Sequence//Union;
loopVectors=OptionValue["Internal"];
,
(* nothing *)
{True,True},
allVectors=Cases[props,_IP,Infinity]/.IP-> Sequence//Union;
loopVectors=Select[allVectors,!FreeQ[#,Alternatives@@OptionValue["LoopMom"]]&];
];
If[OptionValue["Verbose"],
Print[Length[allVectors]," vectors: ",allVectors];
Print[Length[loopVectors]," loop vectors: ",loopVectors];
];

(* Build scalar products *)
allSkp=Union@Flatten@Outer[IP,allVectors,allVectors];
loopSkp=Select[allSkp,!FreeQ[#,Alternatives@@(loopVectors)]&];

If[OptionValue["Verbose"],
Print[Length[allSkp]," scalar products: ",allSkp];
Print[Length[loopSkp]," loop scalar products: ",loopSkp];
];

(*
If[Length[loopSkp]!= Length[props],
Message[ReplacementRulesFromPropagators::LenghtMismatch];
Return[$Failed];
];*);

(* Improved version for linear case
{rest,mat}=Normal@CoefficientArrays[props,loopSkp];
If[Det[mat]==0,
Message[ReplacementRulesFromPropagators::NoInverse];
Return[$Failed];
];
rl=Thread[loopSkp-> (Inverse[mat].(OptionValue["Head"]/@Range[Length[props]]-rest))];
*)


	
(* There's an issue if the propagators are overcomplete *)

(* Finding the independent propagators *)
indepPos = Flatten[FirstPosition[#,1,Nothing]&/@RowReduce[Transpose[CoefficientArrays[props,loopSkp][[2]]]]];
If[OptionValue["Verbose"],Print["Propagators ",indepPos," are independent."]];

pvars=OptionValue["Head"]/@indepPos;

rl=Solve[props[[indepPos]]==Thread[OptionValue["Head"][indepPos]],loopSkp];

(*indepPropagators=loopProps[[Flatten[FirstPosition[#,1,Nothing]&/@RowReduce[Transpose[CoefficientArrays[props,Union[Cases[props,IP[_k,_],Infinity]]][[2]]]]]]]*)


If[rl==={},
	Message[ReplacementRulesFromPropagators::NoInverse];
	Return[$Failed];,
	rl = First[rl];
	rl = Normal[KeyDrop[rl,pvars]];
];

If[!ContainsAll[Keys[rl],loopSkp],
	Message[ReplacementRulesFromPropagators::NoInverse];
	Return[$Failed];
];

rl = Normal[KeyTake[rl,loopSkp]];
(* Check if rule is valid *)
If[OptionValue["DoCheck"],
checkVal=rl/.Rule-> Subtract;
checkVal=Simplify[checkVal/.OptionValue["Head"]-> (Part[props,#]&)];
If[checkVal===Table[0,Length[loopSkp]],
Print["Check passed!"],
Print["Check failed! Got ",checkVal ];
]
];
Return[rl];
];


Options[ISPFromPropagators]={ "Internal"->Nothing ,"External"->Nothing,"LoopMom"->{Global`k},"DoCheck"-> False,"Verbose"-> False};
ISPFromPropagators[props_,OptionsPattern[]]:=Module[{allVectors,loopVectors,allSkp,loopSkp,mat,rest,rl,checkVal,variableOvercomplete,linsys},
(* Depending on user input determine external and loop momenta. Default is to select based on expressions that appear in propagator list *)
Switch[
{OptionValue["Internal"]===Nothing,OptionValue["External"]===Nothing},
(* everything *)
{False,False},
allVectors=Join[OptionValue["Internal"],OptionValue["External"]];
loopVectors=OptionValue["Internal"];,
(* external momenta  *)
{True,False},
allVectors=Union[Cases[props,_IP,Infinity]/.IP-> Sequence,OptionValue["External"]];
loopVectors=Complement[allVectors,OptionValue["External"]];
,
(* loop momenta *)
{False,True},
allVectors=Cases[props,_IP,Infinity]/.IP-> Sequence//Union;
loopVectors=OptionValue["Internal"];
,
(* nothing *)
{True,True},
allVectors=Cases[props,_IP,Infinity]/.IP-> Sequence//Union;
loopVectors=Select[allVectors,!FreeQ[#,Alternatives@@OptionValue["LoopMom"]]&];
];
If[OptionValue["Verbose"],
Print[Length[allVectors]," vectors: ",allVectors];
Print[Length[loopVectors]," loop vectors: ",loopVectors];
];
(* Build scalar products *)
allSkp=Union@Flatten@Outer[IP,allVectors,allVectors];
loopSkp=Select[allSkp,!FreeQ[#,Alternatives@@(loopVectors)]&];
(* select the independent variables *)
variableOvercomplete=Join[props,loopSkp];
linsys=CoefficientArrays[variableOvercomplete,loopSkp][[2]];
Return[Extract[variableOvercomplete,FirstPosition[#,1,Nothing]&/@RowReduce[Transpose[linsys]]]];
]


(* ::Section::Closed:: *)
(*Gamma Matrices*)


(* Non-commutative multiplication *)


(* ::Input::Initialization:: *)
ClearAll[NCM];
Attributes[NCM]={Flat,OneIdentity};
NCM[a___,b_+c_,d___]:=NCM[a,b,d]+NCM[a,c,d];
NCM[a___,-b_,c___]:=-NCM[a,b,c];
NCM[a___,k_*b_,c___]/;NumericQ[k]||ConstantQ[k]:=k*NCM[a,b,c];
NCM[a___,1,b___]:=NCM[a,b];
NCM[a___,0,b___]:=0;
NCM[k_,b_]/;NumericQ[k]||ConstantQ[k]:=k*b;
NCM[b_,k_]/;NumericQ[k]||ConstantQ[k]:=k*b;
NCM/:MakeBoxes[NCM[a_,b_],Form_]:=RowBox[{MakeBoxes[a,Form],".",MakeBoxes[b,Form]}];
NCM/:MakeBoxes[NCM[a_],Form_]/;FreeQ[a,NCM]:=MakeBoxes[a,Form];


(* Non-commutative power *)


(* ::Input::Initialization:: *)
NCMPower[x_,1]:=x;
NCMPower[x_,n_]:=NCM[x,NCMPower[x,n-1]];


(* The Lorentz trace *)


(* ::Input::Initialization:: *)
NCMCoefficient[expr_,a_]:=Module[{HoldNCM,toret},
toret=expr/.NCM[Longest[x__]]:> HoldNCM[x];
toret=toret/.{HoldNCM[Longest[b__],a]:> HoldNCM[b],HoldPattern[HoldNCM[x___]]:> 0};
toret=toret/.HoldNCM:> NCM;
Return[toret];
]


(* The Lorentz trace*)


(* ::Input::Initialization:: *)
LorentzTrace[a_+b_]:=LorentzTrace[a]+LorentzTrace[b];
LorentzTrace[k_*a_]/;ConstantQ[k]:=k*LorentzTrace[a];
ConstantQ[LorentzTrace[___]]^=True;
LorentzTrace/:MakeBoxes[LorentzTrace[a_],Form_]:=RowBox[{"Tr(",MakeBoxes[a,Form],")"}];


(* Slashed matrices *)
Slashed[a_+b_]:=Slashed[a]+Slashed[b];
Slashed[k_*a_]/;NumericQ[k]:=k*Slashed[a];
Slashed/:MakeBoxes[Slashed[i_],Form_]:=OverlayBox[{MakeBoxes[i],"/"}];


(* ::Section:: *)
(*Invariants*)


(* Masses *)
mass[i_]/;i>nLegs:=mass[i-nLegs];
LScalarQ[mass[i_]]^=True;
mass/:MakeBoxes[mass[i_],Form_]:=SubscriptBox["m",MakeBoxes[i,Form]];
massSq[i_]/;i>nLegs:=massSq[i-nLegs];
LScalarQ[massSq[i_]]^=True;


(* Masses *)


(* Per default all massles*)
MassiveMomQ[P_]:=False;
MasslessMomQ[P_]:=!MassiveMomQ[P];
MakeMassive[P_]:=Module[{},MassiveMomQ[P]^=True];
MakeMassless[P_]:=Module[{},MassiveMomQ[P]^=False];


(* Mandelstam invariants *)


Attributes[mom]={Orderless};
mom[i_,j_]/;i>nLegs:=mom[i-nLegs,j];
mom[i_,j_]/;j>nLegs:=mom[i,j-nLegs];
mom[i_,i_]:=4mass[i]^2;
LScalarQ[mom[__]]^=True;
mom/:MakeBoxes[mom[i_,j_],Form_]:=SubscriptBox["s",RowBox[{MakeBoxes[i,Form],MakeBoxes[j,Form]}]]


(* Epsilon tensor *)


LScalarQ[Epsilon[i__]]^=True;

Epsilon[i__]/;!OrderedQ[{i}]:=Signature[{i}] Epsilon@@Sort[{i}];
Epsilon[___,i_,___,i_,___]:=0;
Epsilon[a___,i_Plus,b___]:=Total[Epsilon[a,#,b]&/@(List@@i)];
Epsilon[a___,c_*i_,b___]/;LScalarQ[c]:=c*Epsilon[a,i,b];

Unprotect[Power];
(* This should be done in a more satisfying with a hard set when a function is called similiar to contractions *)
Power[Epsilon[i__],n_Integer]/;n>=2&&$AutoSimplifyEpsilon:=$MetricSign*Gram[List[i]]Epsilon[i]^(n-2);
Protect[Power];
Unprotect[Times];
(* This should be done in a more satisfying with a hard set when a function is called similiar to contractions *)
Times[Epsilon[i__],Epsilon[j__]]/;$AutoSimplifyEpsilon:=$MetricSign*TwoRowGram[List[i],List[j]];
Protect[Times];
Epsilon/:MakeBoxes[Epsilon[i__],Form_]:=RowBox[{"\[Epsilon](",Sequence@@Riffle[MakeBoxes[#,Form]&/@List[i],{","}],")"}]


EvaluateGramDets[expr_]:=expr/.{Gram[i_]:> Det[Outer[IP,i,i]],TwoRowGram[i_,j_]:>Det[ Outer[IP,i,j]]};


ConjugateEpsilon[x_]:=x/.Epsilon[i___]:> -Epsilon[i];


EpsilonSimplify[x_]:=Module[{toret,num,denom},
toret=Together[x];
num=Simplify[Expand[Numerator[toret]*ConjugateEpsilon[Denominator[toret]]]/.grRule];
denom=Simplify[Expand[Denominator[toret]*ConjugateEpsilon[Denominator[toret]]]/.grRule];
toret=Collect[num/denom,_Epsilon,Simplify];
Return[toret];
]


(* ::Section::Closed:: *)
(*Derivatives *)


(* abstract derivative operator satisfying Leibniz rule *)


AbstractD[var_][x_]/;NumericQ[x]:=0;
AbstractD[var_][var_]:=1;
AbstractD[var_][x_+y_]:=AbstractD[var][x]+AbstractD[var][y];
AbstractD[var_][x_*y_]:=AbstractD[var][x]*y+x*AbstractD[var][y];
AbstractD[var_][Power[x_,n_]]:=n*Power[x,n-1]AbstractD[var][x];
AbstractD[var_]/:MakeBoxes[AbstractD[var_],Form_]:=SubscriptBox["\[PartialD]",MakeBoxes[var,Form]];


Clear[vdv];
deltavv[v1_,v2_]:=Boole@SameQ[v1,v2];
Clear[vdv];
vdv[v1_,v2_][x_]/;ConstantQ[x]:=0;
vdv[c_*v1_,v2_][x_]/;LScalarQ[c]:=c*vdv[v1,v2][x];
vdv[v1_+v2_,v3_][x_]:=vdv[v1,v3][x]+vdv[v2,v3][x];
vdv[v1_,v2_][x_*y_]:=vdv[v1,v2][x]*y+x*vdv[v1,v2][y];
vdv[v1_,v2_][x_+y_]:=vdv[v1,v2][x]+vdv[v1,v2][y];
vdv[v1_,v2_][Power[E,x_]]:=Power[E,x]*vdv[v1,v2][x];
vdv[v1_,v2_][Power[x_,n_]]/;ConstantQ[n]:=n*Power[x,n-1]vdv[v1,v2][x];
vdv[v1_,v2_]/:MakeBoxes[vdv[v1_,v2_],Form_]:=RowBox[{MakeBoxes[v1,Form],"\[CenterDot]",SubscriptBox["\[PartialD]",MakeBoxes[v2,Form]]}];
vdv[v1_,v2_][IP[v3_,v4_]]:=deltavv[v2,v3]IP[v1,v4]+deltavv[v2,v4]IP[v1,v3];
vdv[v1_,v2_][f_[x_]]:=vdv[v1,v2][x]Derivative[1][f][x]


(* ::Section:: *)
(*NR decomposition*)


(* Zero component of a vector *)
ZeroComponent[P1_+P2_]:=ZeroComponent[P1]+ZeroComponent[P2];
ZeroComponent[a_?LScalarQ *P_]:=a*ZeroComponent[P];
ZeroComponent/:MakeBoxes[ZeroComponent[P_],form_]:=SubscriptBox[RowBox[{"[",MakeBoxes[P],"]"}],"0"];


(* Spatial component of a vector *)
ToCanonical[SpatialComponent[x_]]^:=SpatialComponent[x];
SpatialComponent[P1_+P2_]:=SpatialComponent[P1]+SpatialComponent[P2];
SpatialComponent[a_?LScalarQ *P_]:=a*SpatialComponent[P];


DisplayVector[v_[i_],form_]:=SubscriptBox[MakeBoxes[OverVector[v]],ToString[i]];
DisplayVector[v_,form_]:=MakeBoxes[OverVector[v],form];
SpatialComponent/:MakeBoxes[SpatialComponent[P_],form_]:=DisplayVector[P,form];


(* Split components of vector into space and time *)
SplitComponent[a_*b_]:=SplitComponent[a]*SplitComponent[b];
SplitComponent[a_+b_]:=SplitComponent[a]+SplitComponent[b];
SplitComponent[Power[a_,n_]]/;LScalarQ[n]:=Power[SplitComponent[a],n];
SplitComponent[IP[P_,Q_]]:=ZeroComponent[P]ZeroComponent[Q]+$MetricSign*IP[SpatialComponent[P],SpatialComponent[Q]];
SplitComponent[a_]/;FreeQ[a,IP]:=a;


(* ::Input::Initialization:: *)
DualMomenta[vList_]:=Module[{gramInv},
gramInv=Simplify@Inverse@Outer[IP,vList,vList];
Return[gramInv . vList];
]


(* ::Input::Initialization:: *)
DecomposeVector[v_,vList_]:=Module[{duals=DualMomenta[vList]},Total[(IP[v,#]&/@vList)*duals]];


ListIPs[expr_]:=DeleteDuplicates[Cases[expr,_IP,Infinity]];


(* ::Section:: *)
(*Lorentz Generator*)


(* ::Input::Initialization:: *)
(* see e.g. (2.10) *)
MGenExplicit[\[Mu]_,\[Nu]_][{},{}]:= 0;
MGenExplicit[\[Mu]_,\[Nu]_][\[Alpha]_List,\[Beta]_List]:=Module[{toret,perm\[Alpha]=Permutations[\[Alpha]],perm\[Beta]=Permutations[\[Beta]],s=Length[\[Alpha]]},
toret=I*s*(IP[\[Mu],\[Alpha][[1]]]IP[\[Nu],\[Beta][[1]]]Product[IP[\[Alpha][[i]],\[Beta][[i]]],{i,2,Length[\[Alpha]]}]-
IP[\[Nu],\[Alpha][[1]]]IP[\[Mu],\[Beta][[1]]]Product[IP[\[Alpha][[i]],\[Beta][[i]]],{i,2,Length[\[Alpha]]}]);
toret=1/Length[perm\[Alpha]]Sum[toret/.Thread[\[Alpha]-> ppp],{ppp,perm\[Alpha]}];
toret=1/Length[perm\[Beta]]Sum[toret/.Thread[\[Beta]-> ppp],{ppp,perm\[Beta]}];
Return[toret];
];


End[];


EndPackage[];
