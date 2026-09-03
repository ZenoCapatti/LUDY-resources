(* ::Package:: *)

Table[Print[{ri,$CommandLine[[ri]]}],{ri,1,Length[$CommandLine]}];


intFilePath=$CommandLine[[-5]];
$Shift=ToExpression[$CommandLine[[-4]]];
toolboxPath=$CommandLine[[-3]];
remapDataPath=$CommandLine[[-2]];
ruleMappingFilePath=$CommandLine[[-1]];


intsToMap=Get[intFilePath];


Print["# of integrals to map: ",Length[intsToMap]];
Print["$Shift: ",$Shift];
Print["toolboxPath: ",toolboxPath];
Print["remapDataPath: ",remapDataPath];
Print["ruleMappingFile: ",ruleMappingFilePath];


Global`$FIREMathPath="/dev/null";
Global`$FIREBinPath="/dev/null";


Get[FileNameJoin[{toolboxPath,"mma",#}]]&/@{
"LorentzVectorUtils.wl",
"IntegralTools.wl",
"TwoBodyKinematics.wl"
};


niceTime[mmaTime_]:=StringRiffle[Riffle[PadLeft[IntegerDigits[Round[mmaTime], MixedRadix[{24, 60, 60}]],3],{"Hours", "Minutes", "Seconds"}]]


ti=AbsoluteTime[];


SetRemapData[Get[remapDataPath]];
Print["remapdata loaded!"]


(* expresses integrals in a mapping sector in terms of integrals in Unique Sectors *)
rhs=CollectInts[MapIntegrals[intsToMap]];
Put[Thread[intsToMap->rhs],ruleMappingFilePath];
Put[ModIntegrals[ListInts[rhs]],intFilePath];
tf=AbsoluteTime[];
Print["mapping time: ",niceTime[(tf-ti)]];

Print["done mapping all integrals of: ",intFilePath];
Quit[];
