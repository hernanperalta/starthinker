###########################################################################
#
#  Copyright 2017 Google Inc.
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

from util.project import project 
from util.bigquery import datasets_create, datasets_access

def dataset():
  if project.verbose: print "DATASET", project.task['dataset']

  # create dataset
  datasets_create(project.task['auth'], project.id, project.task['dataset'])
  datasets_access(project.task['auth'], project.id, project.task['dataset'], emails=project.task.get('emails', []), groups=project.task.get('groups', []))

if __name__ == "__main__":
  project.load('dataset')
  dataset()
