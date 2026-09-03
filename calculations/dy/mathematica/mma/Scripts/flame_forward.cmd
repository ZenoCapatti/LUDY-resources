#!/bin/csh -f
#  flame_forward.cmd
#
#  UGE job for Run_Forward_FLAME_Hoffman built Tue Nov 28 21:17:47 PST 2023
#
#  The following items pertain to this script
#  Use current working directory
#$ -cwd
#  input           = /dev/null
#  output          = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID
#$ -o /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID
#  error           = Merged with joblog
#$ -j y
#  The following items pertain to the user program
#  user program    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/Run_Forward_FLAME_Hoffman.m
#  arguments       = $1 $2
#  program input   = Specified by user program
#  program output  = Specified by user program
#  Resources requested
#$ -pe shared 16
#$ -l mb=1,mbs=16,h_data=110G,h_rt=336:00:00,highp
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
# Initialization for parallel execution
#
  unalias *
  set qqversion = 
  set qqapp     = "math threads"
  set qqmtasks  = 16
  set qqexedir  = /u/local/apps/mathematica/currentbern/Executables
  set qqjob     = Run_Forward_FLAME_Hoffman
  set qqidir    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  set qqodir    = /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  cd /u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  source /u/local/bin/qq.sge/qr.runtime
  if ($status != 0) exit (1)
#
  echo "MATH (parallel) UGE" job for Run_Forward_FLAME_Hoffman built Tue Nov 28 21:17:47 PST 2023
  echo ""
  echo "  MATH (parallel) directory:"
  echo "    "$qqexedir
  echo "  Run_Forward_FLAME_Hoffman directory:"
  echo "    "/u/project/bern/eherrman/fire_mapping_git/mma/Scripts
  echo "  Submitted to UGE:"
  echo "    "$qqsubmit
  echo "  Run_Forward_FLAME_Hoffman 16-way parallel job configuration"
  echo ""
#
  echo ""
  echo "Run_Forward_FLAME_Hoffman started on:   "` hostname -s `
  echo "Run_Forward_FLAME_Hoffman started at:   "` date `
  echo ""
#
# load the job environment:
#
  source /u/local/Modules/default/init/modules.csh
#
# Edit the line below as needed:
  module load gcc/11.3.0
#
# Run the user program
#
  set OMP_NUM_THREADS = 16
  echo math "$1 $2" \< Run_Forward_FLAME_Hoffman.m \> ./logs/flame_forward.o.$JOB_ID
  echo ""
retry:
  /u/local/apps/mathematica/currentbern/Executables/math $1 $2 < /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/Run_Forward_FLAME_Hoffman.m  > /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/./logs/flame_forward.o.$JOB_ID
#
#
  echo ""
  echo "Run_Forward_FLAME_Hoffman finished at:  "` date `
#
# Cleanup after parallel execution
#
  source /u/local/bin/qq.sge/qr.runtime
#
  echo "-------- /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID --------" >> /u/local/apps/queue.logs/math.log.parallel
  if (`wc -l /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID  | awk '{print $1}'` >= 1000) then
        head -50 /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID >> /u/local/apps/queue.logs/math.log.parallel
        echo " "  >> /u/local/apps/queue.logs/math.log.parallel
        tail -10 /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID >> /u/local/apps/queue.logs/math.log.parallel
  else
        cat /u/project/bern/eherrman/fire_mapping_git/mma/Scripts/logs/flame_forward.j.$JOB_ID >> /u/local/apps/queue.logs/math.log.parallel
  endif
  exit (0)
