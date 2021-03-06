#!/usr/bin/env bash
set -e
# Configurations
druidCoordinatorIP=""
dataSourceName="content-model-snapshot"
today=`date +%Y-%m-%d`
interval="2019-01-01_$today"
now=`date +%Y-%m-%d-%s`
home=`echo $HOME`
ingestionSpecFilePath="${home}/etl-jobs-1.0/druid_models/content_index_batch.json"
jobJarPath="${home}/etl-jobs-1.0/etl-jobs-1.0.jar"
jobConfPath="${home}/etl-jobs-1.0/resources/ESCloudUploader.conf"

# get list of segments from content model snapshot datasource
bkpIFS="$IFS"
segmentIds=$(curl -X 'GET' -H 'Content-Type:application/json' http://${druidCoordinatorIP}:8081/druid/coordinator/v1/metadata/datasources/${dataSourceName}/segments)
IFS=',]['
read -r -a array <<< ${segmentIds}
IFS="$bkpIFS"

# start the spark script to fetch Elasticsearch data and write it to a file and upload to cloud
spark/bin/spark-submit \
--conf spark.driver.extraJavaOptions="-Dconfig.file=${jobConfPath}" \
--class org.ekstep.analytics.jobs.ESCloudUploader \
${jobJarPath}

printf "\n>>> submit ingestion task to Druid!\n"

# submit task to start batch ingestion
curl -X 'POST' -H 'Content-Type:application/json' -d @${ingestionSpecFilePath} http://${druidCoordinatorIP}:8090/druid/indexer/v1/task


for index in "${!array[@]}"
do
    val=( $(eval echo ${array[index]}) )
    printf "\n>>> Disabling segment id: $val \n"
    # disable older segments
    curl -X 'DELETE' -H 'Content-Type:application/json' http://${druidCoordinatorIP}:8081/druid/coordinator/v1/datasources/${dataSourceName}/segments/$val
done

printf "\n>>> Deleting segments from interval $interval \n"

# delete older segments
curl -X 'DELETE' -H 'Content-Type:application/json' http://${druidCoordinatorIP}:8081/druid/coordinator/v1/datasources/${dataSourceName}/intervals/${interval}

printf "\n>>> success!\n"


