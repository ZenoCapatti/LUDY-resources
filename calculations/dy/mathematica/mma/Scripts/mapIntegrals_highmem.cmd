#!/bin/csh -f
#  mapIntegrals.cmd
#
#  UGE job for mapIntegrals built Fri Dec  1 16:18:52 PST 2023
#
#  The following items pertain to this script
#  Use current working directory
#$ -cwd
#  input           = /dev/null
#  output          = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/mapIntegrals.joblog.$JOB_ID
#$ -o /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/mapIntegrals.joblog.$JOB_ID
#  error           = Merged with joblog
#$ -j y
#  The following items pertain to the user program
#  user program    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.m
#  arguments       = $1 $2 $3 $4 $5 $6
#  program input   = Specified by user program
#  program output  = Specified by user program
#  Resources requested
#
#$ -l mb=1,h_data=256G,h_rt=336:00:00,highp
# #
#  Name of application for log
#$ -v QQAPP=math
#  Email address to notify
#$ -M eherrman@mail
#  Notify at beginning and end of job
#$ -m n
#  Job is not rerunable
#$ -r n
#
# Initialization for serial execution
#
  unalias *
  set qqversion = 
  set qqapp     = "math serial"
  set qqidir    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  set qqjob     = mapIntegrals
  set qqodir    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  cd     /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  source /u/local/bin/qq.sge/qr.runtime
  if ($status != 0) exit (1)
#
  echo "UGE job for mapIntegrals built Fri Dec  1 16:18:52 PST 2023"
  echo ""
  echo "  mapIntegrals directory:"
  echo "    "/u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  echo "  Submitted to UGE:"
  echo "    "$qqsubmit
  echo "  SCRATCH directory:"
  echo "    "$qqscratch
#
  echo ""
  echo "mapIntegrals started on:   "` hostname -s `
  echo "mapIntegrals started at:   "` date `
  echo ""
#
# Run the user program
#
  echo math "$1 $2 $3 $4 $5\" \< mapIntegrals.m \> $6
  echo ""
retry:
  /u/local/apps/mathematica/currentbern/Executables/math $1 $2 $3 $4 $5 < /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.m > $6
#
  echo ""
  echo "mapIntegrals finished at:  "` date `
#
# Cleanup after serial execution
#
  source /u/local/bin/qq.sge/qr.runtime
#
  echo "-------- /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.joblog.$JOB_ID --------" >> /u/local/apps/queue.logs/math.log.serial
  if (`wc -l /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.joblog.$JOB_ID  | awk '{print $1}'` >= 1000) then
        head -50 /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.joblog.$JOB_ID >> /u/local/apps/queue.logs/math.log.serial
        echo " "  >> /u/local/apps/queue.logs/math.log.serial
        tail -10 /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.joblog.$JOB_ID >> /u/local/apps/queue.logs/math.log.serial
  else
        cat /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/mapIntegrals.joblog.$JOB_ID >> /u/local/apps/queue.logs/math.log.serial
  endif
