(* ::Package:: *)

basePath[i_Integer]:=FileNameJoin[{$IntegralToolsFIREDirectory,"Diag"<>ToString[i]}];


(* global config path *)
configPath[i_Integer]:=FileNameJoin[{basePath[i],"Diag"<>ToString[i]<>".config"}];


(* common storage folder *)
storagePath[i_Integer]:=FileNameJoin[{basePath[i],"storage"}];
storagePathSave[i_Integer]:=FileNameJoin[{basePath[i],"storage-save"}];

storageTempFile[i_Integer,secID_]:=FileNameJoin[{storagePath[i],StringPadLeft[ToString[secID],4,"0"]<>".tmp"}];


dbPath[i_Integer]:=FileNameJoin[{basePath[i],"db"}];
dbTempFile[i_Integer,secID_]:=FileNameJoin[{basePath[i],"db",StringPadLeft[ToString[secID],4,"0"]<>".tmp"}];


ftoolTempPath[i_]:=FileNameJoin[{basePath[i],"ftool"}];
ftoolTempFile[i_Integer,secID_Integer]:=FileNameJoin[{ftoolTempPath[i],"out_"<>ToString[secID]<>".txt"}]


rulePath[i_Integer]:=FileNameJoin[{basePath[i],"rules"}];
rulePathSave[i_Integer]:=FileNameJoin[{basePath[i],"rules-save"}];

ruleFile[i_Integer,secID_Integer]:=FileNameJoin[{rulePath[i],"rule"<>ToString[secID]<>".txt"}];
ruleMappingFile[i_Integer,secID_Integer]:=FileNameJoin[{rulePath[i],"rules_mapping"<>ToString[secID]<>".txt"}]


dataForwardPath[i_]:=FileNameJoin[{basePath[i],"data_forward"}];


logFilePath[i_]:=FileNameJoin[{basePath[i],"logs"}]
FLAMEForwardlogFile[i_Integer,secID_Integer]:=FileNameJoin[{logFilePath[i],"FLAME_forward_sector_"<>ToString[secID]<>".txt"}];
FLAMEBackwardlogFile[i_Integer,secID_Integer]:=FileNameJoin[{logFilePath[i],"FLAME_backward_sector_"<>ToString[secID]<>".txt"}];


debugPath[i_Integer]:=FileNameJoin[{basePath[i],"debug"}];
debugFileForward[i_Integer,secID_Integer]:=FileNameJoin[{debugPath[i],"table_forward_"<>ToString[i]<>"_sec_"<>ToString[secID]<>".txt"}];
debugFileBackward[i_Integer,secID_Integer]:=FileNameJoin[{debugPath[i],"table_backward_"<>ToString[i]<>"_sec_"<>ToString[secID]<>".txt"}];


(* extra FLAME paths for Hoffman run *)
FLAMEForwardSHfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","flame_"<>ToString[i]<>"_"<>ToString[secID]<>".sh"}]
FLAMEForwardHoffmanIDfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","hoffmanID_flame_"<>ToString[i]<>"_"<>ToString[secID]<>".txt"}]

FLAMEBackwardSHfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","flame_"<>ToString[i]<>"_m"<>ToString[secID]<>".sh"}]
FLAMEBackwardHoffmanIDfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","hoffmanID_flame_"<>ToString[i]<>"_m"<>ToString[secID]<>".txt"}]


(* extra Ftool paths for Hoffman run*)
FtoolReadSHfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","ftool_read_"<>ToString[i]<>"_"<>ToString[secID]<>".sh"}]
FtoolReadHoffmanIDfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","hoffmanID_ftool_read_"<>ToString[i]<>"_"<>ToString[secID]<>".txt"}]

FtoolWriteSHfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","ftool_write_"<>ToString[i]<>"_"<>ToString[secID]<>".sh"}]
FtoolWriteHoffmanIDfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","hoffmanID_ftool_write_"<>ToString[i]<>"_"<>ToString[secID]<>".txt"}]


intsToMapFile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","mapIntegrals_"<>ToString[i]<>"_"<>ToString[secID]<>".m"}]
mapIntegralsHoffmanIDfile[i_Integer,secID_Integer]:=FileNameJoin[{basePath[i],"hoffman","hoffmanID_mapIntegrals_"<>ToString[i]<>"_"<>ToString[secID]<>".txt"}]
