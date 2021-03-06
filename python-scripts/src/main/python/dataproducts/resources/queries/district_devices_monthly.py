def init():
    return """
    {
        "queryType": "groupBy",
        "dataSource": {
            "type": "table",
            "name": "telemetry-events-syncts"
        },
        "intervals": {
            "type": "intervals",
            "intervals": [
                "$start_date/$end_date"
            ]
        },
        "filter": {
            "type": "and",
            "fields": [
                {
                    "type": "in",
                    "dimension": "context_pdata_id",
                    "values": [
                        "$app",
                        "$portal"
                    ],
                    "extractionFn": null
                },
                {
                    "type": "selector",
                    "dimension": "derived_loc_state",
                    "value": "$state",
                    "extractionFn": null
                }
            ]
        },
        "granularity": {
            "type": "all"
        },
        "dimensions": [
            {
                "type": "default",
                "dimension": "derived_loc_district",
                "outputName": "District",
                "outputType": "STRING"
            }
        ],
        "aggregations": [
            {
                "fieldName": "context_did",
                "fieldNames": [
                    "context_did"
                ],
                "type": "cardinality",
                "name": "Unique Devices"
            }
        ],
        "postAggregations": [],
        "having": null,
        "limitSpec": {
            "type": "NoopLimitSpec"
        },
        "context": {},
        "descending": false
    }
    """