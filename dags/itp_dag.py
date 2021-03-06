###########################################################################
# 
#  Copyright 2019 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

'''
--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer from open source: 

    pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory:

    source install/deploy.sh
    4) Composer Menu	   
    l) Install All

--------------------------------------------------------------

Browser Activity Dashboard ( 2019 )

Visualizes a client's Campaign Manager and DV360 activity by browser and device

Wait for <b>BigQuery->StarThinker Data->UNDEFINED->*</b> to be created.
Join the <a hre='https://groups.google.com/d/forum/starthinker-assets' target='_blank'>StarThinker Assets Group</a> to access the following assets
For each of the following copy and connect to the new BigQuery sources above. See <a href='https://docs.google.com/document/d/11NlVWzbw6UeSUVUeNuERZGU9FYySWcRbu2Fg6zJ4O-A/edit?usp=sharing' target='_blank'>detailed instructions</a>.
Copy <a href='https://datastudio.google.com/open/1lxRWIs3ozzWs4-9WTy3EcqMcrtYn-7nI' target='_blank'>Combined_Browser_Delivery</a>.
Copy <a href='https://datastudio.google.com/open/1CeOHxxo-yAAMWcjI1ALsu_Dv-u2W78Rk' target='_blank'>DV360_Browser_Delivery</a>.
Copy <a href='https://datastudio.google.com/open/1NlN8rel--3t9VtTuA_0y2c6dcmIYog5g' target='_blank'>CM_Browser_Delivery</a>.
Copy <a href='https://datastudio.google.com/open/1-mGW74gnWu8zKejBhfLvmgro5rlpVNkE' target='_blank'>Floodlight_Browser_Delivery</a>.
Copy <a href='https://datastudio.google.com/open/1ftGTV0jaHKwGemhSgKOcoesuWzf4Jcwd' target='_blank'>Browser Delivery Report</a>.
When prompted choose the new data sources you just created.
Or give these intructions to the client.

'''

from starthinker_airflow.factory import DAG_Factory
 
# Add the following credentials to your Airflow configuration.
USER_CONN_ID = "starthinker_user" # The connection to use for user authentication.
GCP_CONN_ID = "starthinker_service" # The connection to use for service authentication.

INPUTS = {
  'dataset': '',  # Place where tables will be written in BigQuery.
  'recipe_timezone': 'America/Los_Angeles',  # Timezone for report dates.
  'dcm_account': '',  # CM account id of client.
  'dcm_advertisers': [],  # Comma delimited list of CM advertiser ids.
  'dcm_floodlight': '',  # CM floodlight configuration id.
  'dbm_partners': [],  # DV360 partner id.
  'dbm_advertisers': [],  # Comma delimited list of DV360 advertiser ids.
}

TASKS = [
  {
    'dataset': {
      'auth': 'service',
      'dataset': {
        'field': {
          'name': 'dataset',
          'kind': 'string',
          'order': 1,
          'default': '',
          'description': 'Report suffix and BigQuery dataset to contain data.'
        }
      }
    }
  },
  {
    'dcm': {
      'auth': 'user',
      'report': {
        'account': {
          'field': {
            'name': 'dcm_account',
            'kind': 'integer',
            'order': 2,
            'default': '',
            'description': 'CM account id of client.'
          }
        },
        'filters': {
          'dfa:advertiser': {
            'values': {
              'field': {
                'name': 'dcm_advertisers',
                'kind': 'integer_list',
                'order': 3,
                'default': [
                ],
                'description': 'Comma delimited list of CM advertiser ids.'
              }
            }
          }
        },
        'body': {
          'type': 'STANDARD',
          'format': 'CSV',
          'name': {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'prefix': 'CM_Browser_Delivery_',
              'description': 'Report in CM, should be unique.'
            }
          },
          'accountId': {
            'field': {
              'name': 'dcm_account',
              'kind': 'integer',
              'order': 2,
              'default': '',
              'description': 'CM account id of client.'
            }
          },
          'criteria': {
            'dateRange': {
              'relativeDateRange': 'LAST_365_DAYS'
            },
            'dimensions': [
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:advertiser'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:advertiserId'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:campaign'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:campaignId'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:site'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:browserPlatform'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:platformType'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:date'
              }
            ],
            'metricNames': [
              'dfa:impressions',
              'dfa:clicks',
              'dfa:activityViewThroughConversions',
              'dfa:activityClickThroughConversions'
            ]
          }
        }
      }
    }
  },
  {
    'dcm': {
      'auth': 'user',
      'report': {
        'account': {
          'field': {
            'name': 'dcm_account',
            'kind': 'integer',
            'order': 2,
            'default': '',
            'description': 'CM account id of client.'
          }
        },
        'name': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'prefix': 'CM_Browser_Delivery_',
            'description': 'Report in CM, should be unique.'
          }
        }
      },
      'out': {
        'bigquery': {
          'table': 'CM_Browser_Delivery',
          'dataset': {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'order': 1,
              'default': '',
              'description': 'BigQuery dataset to contain data.'
            }
          }
        }
      }
    }
  },
  {
    'dcm': {
      'auth': 'user',
      'report': {
        'account': {
          'field': {
            'name': 'dcm_account',
            'kind': 'integer',
            'order': 2,
            'default': '',
            'description': 'CM account id of client.'
          }
        },
        'body': {
          'name': {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'prefix': 'CM_Browser_Floodlight_',
              'description': 'Report in CM, should be unique.'
            }
          },
          'type': 'FLOODLIGHT',
          'format': 'CSV',
          'accountId': {
            'field': {
              'name': 'dcm_account',
              'kind': 'integer',
              'order': 2,
              'default': '',
              'description': 'CM account id of client.'
            }
          },
          'floodlightCriteria': {
            'dateRange': {
              'relativeDateRange': 'LAST_60_DAYS'
            },
            'dimensions': [
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:advertiser'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:advertiserId'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:campaign'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:campaignId'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:date'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:browserPlatform'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:platformType'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:activity'
              },
              {
                'kind': 'dfareporting#sortedDimension',
                'name': 'dfa:activityId'
              }
            ],
            'floodlightConfigId': {
              'dimensionName': 'dfa:floodlightConfigId',
              'kind': 'dfareporting#dimensionValue',
              'matchType': 'EXACT',
              'value': {
                'field': {
                  'name': 'dcm_floodlight',
                  'kind': 'integer',
                  'order': 4,
                  'default': '',
                  'description': 'CM floodlight configuration id.'
                }
              }
            },
            'metricNames': [
              'dfa:activityClickThroughConversions',
              'dfa:activityViewThroughConversions',
              'dfa:totalConversions'
            ],
            'reportProperties': {
              'includeUnattributedCookieConversions': True,
              'includeUnattributedIPConversions': False
            }
          }
        }
      }
    }
  },
  {
    'dcm': {
      'auth': 'user',
      'report': {
        'account': {
          'field': {
            'name': 'dcm_account',
            'kind': 'integer',
            'order': 2,
            'default': '',
            'description': 'CM account id of client.'
          }
        },
        'name': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'prefix': 'CM_Browser_Floodlight_',
            'description': 'Report in CM, should be unique.'
          }
        }
      },
      'out': {
        'bigquery': {
          'table': 'CM_Browser_Floodlight',
          'dataset': {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'order': 1,
              'default': '',
              'description': 'BigQuery dataset to contain data.'
            }
          }
        }
      }
    }
  },
  {
    'dbm': {
      'auth': 'user',
      'report': {
        'filters': {
          'FILTER_PARTNER': {
            'values': {
              'field': {
                'name': 'dbm_partners',
                'kind': 'integer_list',
                'order': 5,
                'default': [
                ],
                'description': 'DV360 partner id.'
              }
            }
          },
          'FILTER_ADVERTISER': {
            'values': {
              'field': {
                'name': 'dbm_advertisers',
                'kind': 'integer_list',
                'order': 6,
                'default': [
                ],
                'description': 'Comma delimited list of DV360 advertiser ids.'
              }
            }
          }
        },
        'body': {
          'timezoneCode': {
            'field': {
              'name': 'recipe_timezone',
              'kind': 'timezone',
              'description': 'Timezone for report dates.',
              'default': 'America/Los_Angeles'
            }
          },
          'metadata': {
            'title': {
              'field': {
                'name': 'dataset',
                'kind': 'string',
                'prefix': 'DV360_Browser_Delivery_',
                'description': 'Name of report in DV360, should be unique.'
              }
            },
            'dataRange': 'LAST_365_DAYS',
            'format': 'CSV'
          },
          'params': {
            'type': 'TYPE_GENERAL',
            'groupBys': [
              'FILTER_ADVERTISER',
              'FILTER_BROWSER',
              'FILTER_MEDIA_PLAN',
              'FILTER_DATE',
              'FILTER_DEVICE_TYPE',
              'FILTER_INSERTION_ORDER',
              'FILTER_PAGE_LAYOUT'
            ],
            'metrics': [
              'METRIC_IMPRESSIONS',
              'METRIC_CLICKS',
              'METRIC_LAST_CLICKS',
              'METRIC_LAST_IMPRESSIONS',
              'METRIC_REVENUE_ADVERTISER',
              'METRIC_MEDIA_COST_ADVERTISER'
            ]
          }
        }
      }
    }
  },
  {
    'dbm': {
      'auth': 'user',
      'report': {
        'name': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'prefix': 'DV360_Browser_Delivery_',
            'description': 'DV360 report name, should be unique.'
          }
        }
      },
      'out': {
        'bigquery': {
          'table': 'DV360_Browser_Delivery',
          'dataset': {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'order': 1,
              'default': '',
              'description': 'BigQuery dataset to contain data.'
            }
          },
          'schema': [
            {
              'name': 'Advertiser',
              'type': 'STRING'
            },
            {
              'name': 'Advertiser_ID',
              'type': 'INTEGER'
            },
            {
              'name': 'Advertiser_Status',
              'type': 'STRING'
            },
            {
              'name': 'Advertiser_Integration_Code',
              'type': 'STRING'
            },
            {
              'name': 'Browser',
              'type': 'STRING'
            },
            {
              'name': 'Campaign',
              'type': 'STRING'
            },
            {
              'name': 'Campaign_ID',
              'type': 'INTEGER'
            },
            {
              'name': 'Report_Day',
              'type': 'DATE'
            },
            {
              'name': 'Device_Type',
              'type': 'STRING'
            },
            {
              'name': 'Insertion_Order',
              'type': 'STRING'
            },
            {
              'name': 'Insertion_Order_ID',
              'type': 'INTEGER'
            },
            {
              'name': 'Insertion_Order_Status',
              'type': 'STRING'
            },
            {
              'name': 'Insertion_Order_Integration_Code',
              'type': 'STRING'
            },
            {
              'name': 'Environment',
              'type': 'STRING'
            },
            {
              'name': 'Advertiser_Currency',
              'type': 'STRING'
            },
            {
              'name': 'Impressions',
              'type': 'INTEGER'
            },
            {
              'name': 'Clicks',
              'type': 'INTEGER'
            },
            {
              'name': 'Post_Click_Conversions',
              'type': 'FLOAT'
            },
            {
              'name': 'Post_View_Conversions',
              'type': 'FLOAT'
            },
            {
              'name': 'Revenue_Adv_Currency',
              'type': 'FLOAT'
            },
            {
              'name': 'Media_Cost_Advertiser_Currency',
              'type': 'FLOAT'
            }
          ]
        }
      }
    }
  },
  {
    'bigquery': {
      'auth': 'service',
      'to': {
        'table': 'Floodlight_Browser_Delivery',
        'dataset': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'order': 1,
            'default': '',
            'description': 'BigQuery dataset to contain data.'
          }
        }
      },
      'from': {
        'query': 'WITH\r\nbrowser_clean AS (\r\n  SELECT\r\n    Advertiser,\r\n    Advertiser_Id,\r\n    Campaign,\r\n    Campaign_Id,\r\n    Browser_Platform,\r\n   Activity,\r\n    Activity_ID,\r\n    CASE\r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Chrome).*") THEN "Chrome" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Firefox).*") THEN "Firefox" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Safari).*") THEN "Safari"\r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPad).*") THEN "Safari" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPad).*") THEN "Safari" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPhone).*") THEN "Safari" \r\n    ELSE "Other"\r\n    END AS Clean_Browser,\r\n    Platform_Type,\r\n    Report_Day,\r\n    View_Through_Conversions,\r\n    Click_Through_Conversions,\r\n    Total_Conversions\r\n  FROM [PARAMETER].CM_Browser_Floodlight\r\n)\r\n\r\n  SELECT\r\n    *,\r\n    CASE WHEN Platform_Type="Mobile highend: smartphone" OR Platform_Type="Mobile midrange: feature phone" OR Platform_Type="Tablet" THEN Total_Conversions ELSE 0 END AS Mobile_Convs,\r\n   CASE WHEN Platform_Type="Desktop" THEN Total_Conversions ELSE 0 END AS Desktop_Convs,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Total_Conversions ELSE 0 END AS Chrome_Convs,\r\n   CASE WHEN Clean_Browser="Safari" THEN Total_Conversions ELSE 0 END AS Safari_Convs,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Total_Conversions ELSE 0 END AS Firefox_Convs\r\n  FROM browser_clean',
        'legacy': False,
        'parameters': [
          {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'description': 'Bigquery container for data.'
            }
          }
        ]
      }
    }
  },
  {
    'bigquery': {
      'auth': 'service',
      'to': {
        'table': 'CM_Browser_Delivery',
        'dataset': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'order': 1,
            'default': '',
            'description': 'BigQuery dataset to contain data.'
          }
        }
      },
      'from': {
        'query': 'WITH\r\nbrowser_clean AS (\r\n  SELECT\r\n    Advertiser,\r\n    Advertiser_Id,\r\n    Campaign,\r\n    Campaign_Id,\r\n    Site_Dcm,\r\n    Browser_Platform,\r\n  CASE\r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Chrome).*") THEN "Chrome" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Firefox).*") THEN "Firefox" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*Safari).*") THEN "Safari"\r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPad).*") THEN "Safari" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPad).*") THEN "Safari" \r\n    WHEN REGEXP_CONTAINS(Browser_Platform, "((?i).*iPhone).*") THEN "Safari" \r\n    ELSE "Other"\r\n    END AS Clean_Browser,\r\n    Platform_Type,\r\n    Report_Day,\r\n    Impressions,\r\n    Clicks,\r\n    View_Through_Conversions,\r\n    Click_Through_Conversions\r\n  FROM [PARAMETER].CM_Browser_Delivery\r\n)\r\n\r\n SELECT\r\n    *,\r\n   CASE WHEN Platform_Type="Mobile highend: smartphone" OR Platform_Type="Mobile midrange: feature phone" OR Platform_Type="Tablet" THEN Impressions ELSE 0 END AS Mobile_Imps,\r\n   CASE WHEN Platform_Type="Desktop" THEN Impressions ELSE 0 END AS Desktop_Imps,\r\n   CASE WHEN Platform_Type="Connected TV" THEN Impressions ELSE 0 END AS CTV_Imps,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Impressions ELSE 0 END AS Chrome_Imps,\r\n   CASE WHEN Clean_Browser="Safari" THEN Impressions ELSE 0 END AS Safari_Imps,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Impressions ELSE 0 END AS Firefox_Imps\r\n  FROM browser_clean',
        'legacy': False,
        'parameters': [
          {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'description': 'Bigquery container for data.'
            }
          }
        ]
      }
    }
  },
  {
    'bigquery': {
      'auth': 'service',
      'to': {
        'table': 'DV360_Browser_Delivery',
        'dataset': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'order': 1,
            'default': '',
            'description': 'BigQuery dataset to contain data.'
          }
        }
      },
      'from': {
        'query': 'WITH\r\nbrowser_cleaned AS (\r\n  SELECT \r\n    Advertiser,\r\n    Advertiser_Id,\r\n    Advertiser_Currency,\r\n    Browser,\r\n    Campaign,\r\n    Campaign_Id,\r\n    Insertion_Order, \r\n    Insertion_Order_Id,\r\n    Report_Day,\r\n    Device_Type,\r\n    Environment,\r\n    Impressions,\r\n    Clicks,\r\n    Post_Click_Conversions,\r\n    Post_View_Conversions,\r\n    Revenue_Adv_Currency as Revenue,\r\n    Media_Cost_Advertiser_Currency,\r\n    CASE\r\n      WHEN REGEXP_CONTAINS(Browser, "((?i).*Chrome).*") THEN "Chrome" \r\n      WHEN REGEXP_CONTAINS(Browser, "((?i).*Firefox).*") THEN "Firefox" \r\n      WHEN REGEXP_CONTAINS(Browser, "((?i).*Safari).*") THEN "Safari"\r\n      ELSE "Other"\r\n      END AS Clean_Browser,\r\n    CASE \r\n      WHEN Browser="Safari 12" THEN "Safari 12"\r\n      WHEN Browser="Safari 11" THEN "Safari 11"\r\n      WHEN REGEXP_CONTAINS(Browser, "((?i).*Safari).*") AND Browser!="Safari 12" AND Browser!="Safari 11" THEN "Safari 10 & Below"\r\n      ELSE "Non Safari"\r\n    END AS ITP_Affected_Browsers\r\n   FROM [PARAMETER].DV360_Browser_Delivery \r\n)\r\n\r\n  SELECT\r\n    *,\r\n    CASE WHEN Device_Type="Smart Phone" OR Device_Type="Tablet" THEN Impressions ELSE 0 END AS Mobile_Imps,\r\n   CASE WHEN Device_Type="Desktop" THEN Impressions ELSE 0 END AS Desktop_Imps,\r\n   CASE WHEN Device_Type="Connected TV" THEN Impressions ELSE 0 END AS CTV_Imps,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Impressions ELSE 0 END AS Chrome_Imps,\r\n   CASE WHEN Clean_Browser="Safari" THEN Impressions ELSE 0 END AS Safari_Imps,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Impressions ELSE 0 END AS Firefox_Imps,\r\n    CASE WHEN Clean_Browser="Chrome" THEN Revenue ELSE 0 END AS Chrome_Rev,\r\n   CASE WHEN Clean_Browser="Safari" THEN Revenue ELSE 0 END AS Safari_Rev,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Revenue ELSE 0 END AS Firefox_Rev,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Post_Click_Conversions ELSE 0 END AS Chrome_Click_Convs,\r\n   CASE WHEN Clean_Browser="Safari" THEN Post_Click_Conversions ELSE 0 END AS Safari_Click_Convs,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Post_Click_Conversions ELSE 0 END AS Firefox_Click_Convs,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Post_View_Conversions ELSE 0 END AS Chrome_View_Convs,\r\n   CASE WHEN Clean_Browser="Safari" THEN Post_View_Conversions ELSE 0 END AS Safari_View_Convs,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Post_View_Conversions ELSE 0 END AS Firefox_View_Convs,\r\n   CASE WHEN Clean_Browser="Chrome" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS Chrome_Convs,\r\n   CASE WHEN Clean_Browser="Safari" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS Safari_Convs,\r\n   CASE WHEN Clean_Browser="Firefox" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS Firefox_Convs,\r\n   \r\n   CASE WHEN ITP_Affected_Browsers="Safari 12" THEN Impressions ELSE 0 END AS S12_Imps,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 11" THEN Impressions ELSE 0 END AS S11_Imps,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 10 & Below" THEN Impressions ELSE 0 END AS S_Imps,\r\n   CASE WHEN ITP_Affected_Browsers="Non Safari" THEN Impressions ELSE 0 END AS NS_Imps,\r\n   \r\n   CASE WHEN ITP_Affected_Browsers="Safari 12" THEN Post_Click_Conversions ELSE 0 END AS S12_Click_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 11" THEN Post_Click_Conversions ELSE 0 END AS S11_Click_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 10 & Below" THEN Post_Click_Conversions ELSE 0 END AS S_Click_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Non Safari" THEN Post_Click_Conversions ELSE 0 END AS NS_Click_Convs,\r\n   \r\n   CASE WHEN ITP_Affected_Browsers="Safari 12" THEN Post_View_Conversions ELSE 0 END AS S12_View_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 11" THEN Post_View_Conversions ELSE 0 END AS S11_View_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 10 & Below" THEN Post_View_Conversions ELSE 0 END AS S_View_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Non Safari" THEN Post_View_Conversions ELSE 0 END AS NS_View_Convs,\r\n   \r\n   CASE WHEN ITP_Affected_Browsers="Safari 12" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS S12_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 11" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS S11_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Safari 10 & Below" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS S_Convs,\r\n   CASE WHEN ITP_Affected_Browsers="Non Safari" THEN Post_Click_Conversions+Post_View_Conversions ELSE 0 END AS NS_Convs\r\n   \r\n   \r\n  FROM browser_cleaned',
        'legacy': False,
        'parameters': [
          {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'description': 'Place where tables will be written in BigQuery.'
            }
          }
        ]
      }
    }
  },
  {
    'bigquery': {
      'auth': 'service',
      'to': {
        'table': 'Combined_Browser_Delivery',
        'dataset': {
          'field': {
            'name': 'dataset',
            'kind': 'string',
            'order': 1,
            'default': '',
            'description': 'BigQuery dataset to contain data.'
          }
        }
      },
      'from': {
        'query': 'WITH cm AS ( SELECT Report_Day, CASE  WHEN Platform_Type="Desktop" THEN "Desktop" WHEN Platform_Type="Tablet" THEN "Mobile_Tablet" WHEN Platform_Type="Mobile highend: smartphone" THEN "Mobile_Tablet" WHEN Platform_Type="Mobile midrange: feature phone" THEN "Mobile_Tablet" WHEN Platform_Type="Connected TV" THEN "CTV" END AS Device_Clean, SUM(Impressions) as CM_Impressions FROM `[PARAMETER].CM_Browser_Delivery`  GROUP BY 1,2 ),  dv3 AS ( SELECT Report_Day as RD, CASE  WHEN Device_Type="Desktop" THEN "Desktop" WHEN Device_Type="Tablet" THEN "Mobile_Tablet" WHEN Device_Type="Smart Phone" THEN "Mobile_Tablet" WHEN Device_Type="Connected TV" THEN "CTV" END AS Device_Clean_DV360, SUM(Impressions) as DV360_Impressions FROM `[PARAMETER].DV360_Browser_Delivery`  GROUP BY 1,2 )  SELECT Report_Day, Device_Clean, CM_Impressions, DV360_Impressions FROM cm a JOIN dv3 b ON a.Report_Day=b.RD AND a.Device_Clean=b.Device_Clean_DV360',
        'legacy': False,
        'parameters': [
          {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'description': 'Place where tables will be written in BigQuery.'
            }
          },
          {
            'field': {
              'name': 'dataset',
              'kind': 'string',
              'description': 'Place where tables will be written in BigQuery.'
            }
          }
        ]
      }
    }
  }
]

DAG_FACTORY = DAG_Factory('itp', { 'tasks':TASKS }, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == "__main__":
  DAG_FACTORY.print_commandline()
