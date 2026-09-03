(* ::Package:: *)

DefConstant/@{mbar[1],mbar[2],mq2,y,m[1],m[2],t,s12,\[Sigma]};


DefConstant/@{qcnt,pcnt};


SoftScalinqKin={l[i_]:> qcnt*l[i],q-> qcnt*q,mq2-> qcnt^2*mq2,t-> qcnt^2*t};


(* ::Input::Initialization:: *)
Scaleq[expr_]:=expr/.{mq2-> qcnt^2*mq2,x_l:>qcnt*x,q-> qcnt*q };


ExternalRepl={
IP[p[1],p[1]]-> m[1]^2,
IP[p[2],p[2]]-> m[2]^2,
IP[p[3],p[3]]-> m[2]^2,
IP[p[1],p[2]]-> 1/2(s12-m[1]^2-m[2]^2),
IP[p[1],p[3]]-> 1/2(-s12-t+m[1]^2+m[2]^2),
IP[p[2],p[3]]-> 1/2(t-2m[2]^2)
}/.t-> -mq2;


ToBarredVariables={
p[1]-> -(pbar[1]-q/2),
p[2]-> -(pbar[2]+q/2),
p[3]-> pbar[2]-q/2,
p[4]-> pbar[1]+q/2
};
ToUnBarredVariables={
pbar[1]-> -p[1]-(p[2]+p[3])/2,pbar[2]-> -p[2]+(p[2]+p[3])/2,q-> -p[2]-p[3]
};


cons={
Sq[pbar[1]]-> mbar[1]^2,
Sq[pbar[2]]-> mbar[2]^2,
IP[pbar[1],pbar[2]]-> y*mbar[1]*mbar[2],
Sq[q]-> -mq2,
IP[pbar[1],q]-> 0,
IP[pbar[2],q]-> 0
};


consRescaled={
Sq[u[1]]-> 1,
Sq[u[2]]-> 1,
IP[u[1],u[2]]-> y,
Sq[q]-> -1,
IP[u[1],q]-> 0,
IP[u[2],q]-> 0
};


(* ::Input::Initialization:: *)
uCheck[1]=(u[1]-u[2]*y)/(1-y^2);
uCheck[2]=(u[2]-u[1]*y)/(1-y^2);


(* ::Input::Initialization:: *)
BarToUnbar={
mbar[i_]:> m[i]Sqrt[1+mq2/(4m[i]^2)],
y-> (\[Sigma]-mq2/(4m[1]m[2]))/Sqrt[(1+mq2/(4m[1]^2))*(1+mq2/(4m[2]^2))]
};


(* ::Input::Initialization:: *)
UnbarToBar={
s12-> mbar[1]^2+mbar[2]^2+2mbar[1]*mbar[2]*y,m[i_]:>  mbar[i]Sqrt[1-mq2/(4mbar[i]^2)],p12-> mq2/4+y mbar[1] mbar[2]
};


(* ::Input::Initialization:: *)
MapToSoftMap[map_]:=Module[{toret},
toret=Thread[{pbar[1],pbar[2],q}-> Simplify[{pbar[1],pbar[2],q}/.ToUnBarredVariables/.map/.ToBarredVariables]];
Return[Union[toret,toret/.pbar-> u,Thread[{mbar[1],mbar[2]}-> Refine[{Sqrt[Sq[pbar[1]]],Sqrt[Sq[pbar[2]]]}/.toret/.cons,mbar[1]>0&&mbar[2]>0]]]];
]


(* ::Input::Initialization:: *)
ToSoftVariables[expr_]:=expr/.ToBarredVariables/.cons/.m[i_]:> Sqrt[mbar[i]^2-mq2/4];


(* ::Input::Initialization:: *)
ExtractLeading[prop_]:=Module[{toret},
toret=ToSoftVariables[prop];
toret=Scaleq[toret]//Simplify;
toret=(leadingSeries[#,{qcnt,0}]&/@toret)/.qcnt-> 1;
Return[toret];
]


(*
IdentityMap={p[1]->p[1],p[2]->p[2],p[3]->p[3],p[4]->p[4]};
Twist={p[1]->p[4],p[2]->p[2],p[3]->p[3],p[4]->p[1]};
VerticalFlip={p[1]->p[2],p[2]->p[1],p[3]->p[4],p[4]->p[3]};
HorizontalFlip={p[1]->p[4],p[4]->p[1],p[2]->p[3],p[3]->p[2]};

AllMaps=Thread[p/@Range[4]->#]&/@Fold[Flatten[{#1,#1/.#2},1]&,{p/@Range[4]},{Twist,VerticalFlip,HorizontalFlip}];
AllSoftMaps=MapToSoftMap/@AllMaps;
*)


SoftMapID[map_]:=Switch[{u[1],u[2],q}/.map,
(* identity *)
{u[1],u[2],q},0,
(* twist *)
{-u[1],u[2],q},1 ,
(* flip vertical *)
{u[2],u[1],-q},2 ,
(* twist, flip horizontal  *)
{-u[2],u[1],-q},3 ,
(* horizontal *)
{-u[1],-u[2],q},4,
(* twist, flip horizontal  *)
{u[1],-u[2],q},5,
(* flip vertical, flip horizontal  *)
{-u[2],-u[1],-q},6,
(* twist, flip vertical, flip horizontal  *)
{u[2],-u[1],-q},7
];

(*crossingQ[map_]:=OddQ[SoftMapID[map]]*)

crossingQ[map_]:=1===PadLeft[IntegerDigits[SoftMapID[map],2],3][[3]]
upDownQ[map_]:=1===PadLeft[IntegerDigits[SoftMapID[map],2],3][[2]];
leftRightQ[map_]:=1===PadLeft[IntegerDigits[SoftMapID[map],2],3][[1]];


SoftMapFromID[id_]:=Part[
{{u[1]->u[1],u[2]->u[2],q->q},
{u[1]->-u[1],u[2]->u[2],q->q},
{u[1]->u[2],u[2]->u[1],q->-q},
{u[1]->-u[2],u[2]->u[1],q->-q},
{u[1]->-u[1],u[2]->-u[2],q->q},
{u[1]->u[1],u[2]->-u[2],q->q},
{u[1]->-u[2],u[2]->-u[1],q->-q},
{u[1]->u[2],u[2]->-u[1],q->-q}}
,id+1];


(*
IdentityMap={p[1]->p[1],p[2]->p[2],p[3]->p[3],p[4]->p[4],m[1]->m[1],m[2]->m[2]};
Twist={p[1]->p[4],p[2]->p[2],p[3]->p[3],p[4]->p[1],m[1]->m[1],m[2]->m[2]};
VerticalFlip={p[1]->p[2],p[2]->p[1],p[3]->p[4],p[4]->p[3],m[1]->m[2],m[2]->m[1]};
HorizontalFlip={p[1]->p[4],p[4]->p[1],p[2]->p[3],p[3]->p[2],m[1]->m[1],m[2]->m[2]};
AllMaps=Thread[Join[p/@Range[4],{m[1],m[2]}]->#]&/@Fold[Flatten[{#1,#1/.#2},1]&,{Join[p/@Range[4],{m[1],m[2]}]},{Twist,VerticalFlip,HorizontalFlip}];
*)
MapFromID[id_]:=Part[{
{p[1]->p[1],p[2]->p[2],p[3]->p[3],p[4]->p[4],m[1]->m[1],m[2]->m[2]},
{p[1]->p[4],p[2]->p[2],p[3]->p[3],p[4]->p[1],m[1]->m[1],m[2]->m[2]},
{p[1]->p[2],p[2]->p[1],p[3]->p[4],p[4]->p[3],m[1]->m[2],m[2]->m[1]},
{p[1]->p[3],p[2]->p[1],p[3]->p[4],p[4]->p[2],m[1]->m[2],m[2]->m[1]},
{p[1]->p[4],p[2]->p[3],p[3]->p[2],p[4]->p[1],m[1]->m[1],m[2]->m[2]},
{p[1]->p[1],p[2]->p[3],p[3]->p[2],p[4]->p[4],m[1]->m[1],m[2]->m[2]},
{p[1]->p[3],p[2]->p[4],p[3]->p[1],p[4]->p[2],m[1]->m[2],m[2]->m[1]},
{p[1]->p[2],p[2]->p[4],p[3]->p[1],p[4]->p[3],m[1]->m[2],m[2]->m[1]}
},id+1];


ConcatinateMaps[m1_,m2_]:=MapAt[#/.m2&,m1,{All,2}]


multiplicationTable=Table[SoftMapID[ConcatinateMaps[SoftMapFromID[i],SoftMapFromID[j]]],{i,0,7},{j,0,7}]

SoftMapConcatination[i_,j_]:=Part[multiplicationTable,i+1,j+1];


InverseSoftMapID[id_]:=SoftMapID[MapToSoftMap[Reverse/@MapFromID[id]]]


modID[id_]:=Mod[id,$Shift,1];
ModIntegrals[expr_]:=expr/.Int[id_,inds_]:>Int[modID[id],inds];
getShift[id_]:=Floor[(id-1)/$Shift];
ToTwoIndex[id_Integer]:={Mod[id,$Shift,1],Floor[(id-1)/$Shift]};
ToOneIndex[{id_Integer,n_Integer}]:=id+n $Shift;
ToTwoIndexInt[expr_]:=expr/.Int[id_Integer,inds_]:>Int[ToTwoIndex[id],inds];
ToOneIndexIndexInt[expr_]:=expr/.Int[{id_Integer,n_Integer},inds_]:>Int[ToOneIndex[{id,n}],inds];
