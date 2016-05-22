#!/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
LOCAL_PATH=$HOME/g13bot_tools_new
#DB Maintenance splitter
cd $LOCAL_PATH && jsub -cwd -mem 512m -N g13_db_maint -o /dev/null -e /dev/null -quiet python pwb.py g13_db_maintenance.py 0
cd $LOCAL_PATH && jsub -cwd -mem 512m -N g13_db_maint -o /dev/null -e /dev/null -quiet python pwb.py g13_db_maintenance.py 1
cd $LOCAL_PATH && jsub -cwd -mem 512m -N g13_db_maint -o /dev/null -e /dev/null -quiet python pwb.py g13_db_maintenance.py 2
cd $LOCAL_PATH && jsub -cwd -mem 512m -N g13_db_maint -o /dev/null -e /dev/null -quiet python pwb.py g13_db_maintenance.py 3
cd $LOCAL_PATH && jsub -cwd -mem 512m -N g13_db_maint -o /dev/null -e /dev/null -quiet python pwb.py g13_db_maintenance.py 4
