import os
import sys
import findspark
import argparse
from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from datetime import date, timedelta, datetime
from pathlib import Path
from resources import replay_config
from util.azure_utils import copy_data, delete_data
from util.postgres_utils import executeQuery
from util.replay_utils import push_data, getDates, getBackUpDetails, getKafkaTopic, getInputPrefix, restoreBackupData, backupData, deleteBackupData, getFilterStr, getFilterDetails

start_time = datetime.now()
print("Started at: ", start_time.strftime('%Y-%m-%d %H:%M:%S'))
parser = argparse.ArgumentParser()
parser.add_argument("container", type=str, help="the data container")
parser.add_argument("prefix", type=str, help="replay data prefix")
parser.add_argument("start_date", type=str, help="YYYY-MM-DD, replay start date")
parser.add_argument("end_date", type=str, help="YYYY-MM-DD, replay end date")
parser.add_argument("kafka_broker_list", type=str, help="kafka broker details")
parser.add_argument("delete_backups", type=str, default="False", help="boolean flag whether to delete backups")

args = parser.parse_args()
container = args.container
prefix = args.prefix
start_date = args.start_date
end_date = args.end_date
kafka_broker_list = args.kafka_broker_list
delete_backups = args.delete_backups

config_json = replay_config.init()

dateRange = getDates(start_date, end_date)
try:       
    filterString = getFilterStr(getFilterDetails(config_json, prefix))
    for date in dateRange:
        try:
            input_prefix = getInputPrefix(config_json, prefix)
            if delete_backups == "True":
                sinkSourcesList = getBackUpDetails(config_json, prefix)
                # take backups before replay
                print("Taking backups before starting replay")
                copy_data(container, input_prefix, 'backup-{}'.format(input_prefix), date)
                delete_data(container, input_prefix, date)
                backupData(sinkSourcesList, container, date)
                print("Taking backups completed. Starting data replay")
                kafkaTopic = getKafkaTopic(config_json, prefix)
                try:
                    backup_prefix = 'backup-{}'.format(input_prefix)
                    push_data(kafka_broker_list, kafkaTopic, container, backup_prefix, date, filterString)
                    print("Data replay completed")
                except Exception:
                    #restore backups if replay fails 
                    print("Error while data replay, restoring backups") 
                    copy_data(container, 'backup-{}'.format(input_prefix), input_prefix, date)
                    delete_data(container, 'backup-{}'.format(input_prefix), date)
                    restoreBackupData(sinkSourcesList, container, date)
                    print("Error while data replay, backups restored") 
                    log.exception()        
                    raise  
                # delete backups and disable segments after replay
                print("Data replay completed. Deleting backups and druid segments")
                delete_data(container, 'backup-{}'.format(input_prefix), date)
                deleteBackupData(sinkSourcesList, container, date)
                print("Data replay completed. Deleted backups and druid segments")   
            else:
                if "failed" in prefix:
                    kafkaTopic = getKafkaTopic(config_json, prefix)
                    push_data(kafka_broker_list, kafkaTopic, container, prefix, date, filterString)
                else:  
                    backup_dir = 'backup-{}'.format(input_prefix)
                    copy_data(container, input_prefix, backup_dir, date)
                    delete_data(container, input_prefix, date)
                    kafkaTopic = getKafkaTopic(config_json, prefix)
                    try:
                        push_data(kafka_broker_list, kafkaTopic, container, backup_dir, date, filterString)
                        print("Data replay completed")
                        delete_data(container, 'backup-{}'.format(input_prefix), date)
                    except Exception as e: 
                        print(str(e))
                        print("Error while data replay, restoring backups")
                        copy_data(container, 'backup-{}'.format(input_prefix), input_prefix, date)
                        delete_data(container, 'backup-{}'.format(input_prefix), date) 
        except Exception as ex:
            print("Replay failed for {}. Continuing replay for remaining dates".format(date.strftime('%Y-%m-%d')))
            print(str(ex))
            pass
except Exception:
        raise







