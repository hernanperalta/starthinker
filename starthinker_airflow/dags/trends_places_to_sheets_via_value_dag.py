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
Trends Places To Sheets Via Values

Move using hard coded WOEID values.

Provide <a href='https://apps.twitter.com/' target='_blank'>Twitter credentials</a>.
Provide a comma delimited list of WOEIDs.
Specify Sheet url and tab to write API call results to.
Writes: WOEID, Name, Url, Promoted_Content, Query, Tweet_Volume
Note Twitter API is rate limited to 15 requests per 15 minutes. So keep WOEID lists short.

'''

from starthinker_airflow.factory import DAG_Factory
 
USER_CONN_ID = "google_cloud_default" # The connection to use for user authentication.
GCP_CONN_ID = "" # The connection to use for service authentication.

INPUTS = {
  "secret":"",
  "key":"",
  "places_dataset":"",
  "places_query":"",
  "places_legacy":False,
  "destination_sheet":"",
  "destination_tab":"",
}

TASKS = [
  {
    "twitter": {
      "auth": "service",
      "secret": {
        "field": {
          "name": "secret",
          "kind": "string",
          "order": 1,
          "default": ""
        }
      },
      "key": {
        "field": {
          "name": "key",
          "kind": "string",
          "order": 2,
          "default": ""
        }
      },
      "trends": {
        "places": {
          "single_cell": true,
          "bigquery": {
            "dataset": {
              "field": {
                "name": "places_dataset",
                "kind": "string",
                "order": 3,
                "default": ""
              }
            },
            "query": {
              "field": {
                "name": "places_query",
                "kind": "string",
                "order": 4,
                "default": ""
              }
            },
            "legacy": {
              "field": {
                "name": "places_legacy",
                "kind": "boolean",
                "order": 5,
                "default": false
              }
            }
          }
        }
      },
      "out": {
        "sheets": {
          "sheet": {
            "field": {
              "name": "destination_sheet",
              "kind": "string",
              "order": 6,
              "default": ""
            }
          },
          "tab": {
            "field": {
              "name": "destination_tab",
              "kind": "string",
              "order": 7,
              "default": ""
            }
          },
          "range": "A1"
        }
      }
    }
  }
]

DAG_FACTORY = DAG_Factory('trends_places_to_sheets_via_value', { 'tasks':TASKS }, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == "__main__":
  DAG_FACTORY.print_commandline()
