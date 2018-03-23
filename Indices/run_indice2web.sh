#!/usr/bin/env bash
export ORACLE_HOME=/home/oracle11/app/oracle/product/11.1.0
cd /home/xair/partage/ExportWEB/
python indice2web.py

wget -q -O /dev/null --no-check-certificate "https://admin:voyelle@airbreizh.voyelle.mobi/wp-cron.php?import_key=bw84C_Y&import_id=3&action=trigger"

#if [ -a "/home/xair/partage/ExportWEB/trigger" ]
#then
#python indice2web.py
#rm "/home/xair/partage/ExportWEB/trigger"
#fi
