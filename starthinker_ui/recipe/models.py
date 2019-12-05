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

import pytz
import json
import functools
from datetime import date, datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils.text import slugify

from starthinker.util.project import project
from starthinker_ui.account.models import Account, token_generate
from starthinker_ui.project.models import Project
from starthinker_ui.recipe.scripts import Script
from django.template.defaultfilters import slugify

JOB_INTERVAL_MS = float(800) # milliseconds 
JOB_LOOKBACK_MS = 5 * JOB_INTERVAL_MS # 4 seconds ( must guarantee to span several pings )
JOB_RECHECK_MS = 30 * 60 * 1000 # 30 minutes


def utc_milliseconds(timestamp=None):
  if timestamp is None: timestamp = datetime.utcnow()
  epoch = datetime.utcfromtimestamp(0)
  return int((timestamp - epoch).total_seconds() * 1000)


def utc_to_timezone(timestamp, timezone):
  if timestamp: return timestamp.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
  else: return None


def time_ago(timestamp):
  ago = ''
  seconds = (datetime.utcnow() - timestamp).total_seconds()

  if seconds is None:
    ago = 'Unknown'
  elif seconds == 0:
    ago = 'Just Now'
  else:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 60)

    if d: ago += '%d Days ' % d
    if h: ago += '%d Hours ' % h
    if m: ago += '%d Minutes ' % m
    if ago == '' and s: ago = '1 Minute Ago'
    else: ago += 'Ago'

  return ago


def reference_default():
  return token_generate(Recipe, 'token', 32)

class Recipe(models.Model):
  account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True)
  token = models.CharField(max_length=8, unique=True)
  reference = models.CharField(max_length=32, unique=True, default=reference_default)

  project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)

  name = models.CharField(max_length=64)
  active = models.BooleanField(default=True)
  manual = models.BooleanField(default=False)

  week = models.CharField(max_length=64, default=json.dumps(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))
  hour = models.CharField(max_length=128, default=json.dumps([3]))

  timezone = models.CharField(max_length=32, blank=True, default='America/Los_Angeles')

  tasks = models.TextField()

  job_done = models.BooleanField(blank=True, default=False)
  job_status = models.TextField(default='{}')
  worker_uid = models.CharField(max_length=128, default='')
  worker_utm = models.BigIntegerField(blank=True, default=0)

  def __str__(self):
    return self.name

  def __unicode__(self):
    return self.name

  def slug(self):
    return slugify(self.name)

  def save(self, *args, **kwargs):
    self.get_token()
    self.get_reference()
    super(Recipe, self).save(*args, **kwargs)

  def uid(self):
    #return "UI-RECIPE-%s" % (self.pk or 'NEW')
    return self.pk or 'NEW'

  def link_edit(self):
    return '/recipe/edit/%d/' % self.pk

  def link_delete(self):
    return '/recipe/delete/%d/' % self.pk

  def link_run(self):
    return '/recipe/run/%d/' % self.pk if self.pk else ''

  def link_cancel(self):
    return '/recipe/cancel/%d/' % self.pk if self.pk else ''

  def link_json(self):
    return '/recipe/json/%d/' % self.pk if self.pk else ''

  def link_colab(self):
    return '/recipe/colab/%d/' % self.pk if self.pk else ''

  def link_airflow(self):
    return '/recipe/airflow/%d/' % self.pk if self.pk else ''

  def link_start(self):
    return '%s/recipe/start/' % settings.CONST_URL

  def link_stop(self):
    return '%s/recipe/stop/' % settings.CONST_URL

  def is_running(self):
    return self.get_log()['status'] == 'RUNNING'

  def get_token(self):
    if not self.token: self.token = token_generate(Recipe, 'token')
    return self.token

  def get_reference(self):
    if not self.reference: self.reference = token_generate(Recipe, 'reference', 32)
    return self.reference

  def get_values(self):
    constants = {
      'recipe_project':self.get_project_identifier(),
      'recipe_name':slugify(self.name),
      'recipe_token':self.get_token(),
      'recipe_timezone':self.timezone,
      'recipe_email':self.account.email if self.account else None,
      'recipe_email_token': self.account.email.replace('@', '+%s@' % self.get_token()) if self.account else None,
    }
    tasks = json.loads(self.tasks or '[]')
    for task in tasks: task['values'].update(constants)
    return tasks

  def set_values(self, scripts):
    self.tasks = json.dumps(scripts)

  def get_hours(self):
    return [int(h) for h in json.loads(self.hour or '[]')]

  def get_days(self):
    return json.loads(self.week or '[]')

  def get_icon(self): return '' #get_icon('')

  def get_credentials_user(self):
    return self.account.get_credentials_path() if self.account else '{}'

  def get_credentials_service(self):
    return self.project.service if self.project and self.project.service else '{}'

  def get_project_identifier(self):
    return self.project.get_project_id() if self.project else ''

  def get_scripts(self):
    for value in self.get_values():  yield Script(value['tag'])

  def get_json(self, credentials=True):
    return Script.get_json(
        self.uid(),
        self.get_project_identifier(),
        self.get_credentials_user() if credentials else '',
        self.get_credentials_service() if credentials else '',
        self.timezone,
        self.get_days(),
        self.get_hours(),
        self.get_values()
      )

  def activate(self):
    self.active = True
    self.save(update_fields=['active'])

  def deactivate(self):
    self.active = False
    self.save(update_fields=['active'])

  def force(self):
    status = self.get_status(force=True)
    self.job_done = False
    self.job_status = json.dumps(status)
    self.worker_uid = '' # forces current worker to cancel job
    self.save(update_fields=['job_status', 'job_done', 'worker_uid'])

  def cancel(self):
    status = self.get_status()

    for task in status['tasks']:
      if not task['done']:
        task['done'] = True
        task['utc'] = str(datetime.utcnow())
        task['event'] = 'JOB_CANCEL'

    self.job_done = True
    self.job_status = json.dumps(status)
    self.worker_uid = '' # forces current worker to cancel job
    self.save(update_fields=['job_status', 'job_done', 'worker_uid'])

  # WORKER METHODS

  def get_status(self, force=False):
    recipe = self.get_json()
    recipe_day = recipe.get('setup', {}).get('day',[]) or ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # current 24 hour time zone derived frame to RUN the job
    now_tz = utc_to_timezone(datetime.utcnow(), self.timezone)
    date_tz = str(now_tz.date())
    day_tz = now_tz.strftime('%a')
    hour_tz = now_tz.hour

    # load prior status
    try: prior_status = json.loads(self.job_status)
    except ValueError: 
      prior_status = {}

    # create default status for new recipes
    prior_status.setdefault('date_tz', date_tz)
    prior_status.setdefault('force', False)
    prior_status.setdefault('day', recipe_day)
    prior_status.setdefault('tasks', [])

    # for manual recipes DO NOT CHANGE STATUS unless it is forced to run
    if self.manual and not force: 
      return prior_status
     
    # reset prior status if force or scheduled today and new 24 hour block
    if force or date_tz != prior_status.get('date_tz'):
      prior_status = { 'force':force }

    # create a vanilla status with all tasks pending ( always do this because recipe may change )
    status = {
      'date_tz':date_tz,
      'force':prior_status.get('force', False),
      'day':recipe_day,
      'tasks':[],
    }

    # create task list based on recipe json
    instances = {}
    for order, task in enumerate(recipe.get('tasks', [])):
      script, task = next(iter(task.items()))

      # if force, queue each task in sequence without hours
      if prior_status.get('force', False):
        hours = [hour_tz]

      # if schedule, take tasks with hours or no hours given defaulted to recipe wide hours
      else:
        hours = task.get('hour', recipe['setup'].get('hour', []))

      # tasks with hours = [] will be skipped unless force=True
      if hours:
        instances.setdefault(script, 0)
        instances[script] += 1
        for hour in hours:
          status['tasks'].append({
            'order':order,
            'script':script,
            'instance':instances[script],
            'hour':hour,
            'utc':str(datetime.utcnow()),
            'event':'JOB_PENDING',
            'stdout':'',
            'stderr':'',
            'done':False
          })

    # sort new order by first by hour and second by order
    def queue_compare(left, right):
      if left['hour'] < right['hour']: return -1
      elif left['hour'] > right['hour']: return 1
      else:
        if left['order'] < right['order']: return -1
        elif left['order'] > right['order']: return 1
        else: return 0

    status['tasks'].sort(key=functools.cmp_to_key(queue_compare))

    # merge old status in if it exists at this point
    for task_prior in prior_status.get('tasks', []):
      for task in status['tasks']:
        if task_prior['script'] == task['script'] and task_prior['instance'] == task['instance'] and task_prior['hour'] == task['hour']:
          task['utc'] = task_prior['utc']
          task['event'] = task_prior['event']
          task['stdout'] = task_prior['stdout']
          task['stderr'] = task_prior['stderr']
          task['done'] = task_prior['done']

    # check if done ( not today or maybe recipe changed )
    done = all([task['done'] for task in status['tasks']])
    done |= day_tz not in recipe_day
    if self.job_done != done:
      self.job_done = done
      Recipe.objects.filter(pk=self.pk).update(job_done=self.job_done)

    # check if job status changed
    if json.loads(self.job_status).get('force', False) != status.get('force', False):
      self.job_status = json.dumps(status)
      self.save(update_fields=['job_status'])

    return status


  def get_task(self):
    status = self.get_status()

    # if not done return next task prior or equal to current time zone hour
    if self.job_done == False and ( self.manual == False or status['force'] == True ):
      now_tz = utc_to_timezone(datetime.utcnow(), self.timezone)
      day_tz = now_tz.strftime('%a')
      if day_tz in status['day']:
        hour_tz = now_tz.hour
        for task in status['tasks']:
          if not task['done'] and task['hour'] <= hour_tz:
            task['recipe'] = self.get_json()
            return task

    return None


  def set_task(self, script, instance, hour, event, stdout, stderr):
    status = self.get_status()

    for task in status['tasks']:
      if task['script'] == script and task['instance'] == instance and task['hour'] == hour:
        task['utc'] = str(datetime.utcnow())
        task['event'] = event
        if stdout: task['stdout'] += stdout
        if stderr: task['stderr'] += stderr
        task['done'] = (event != 'JOB_START')

        self.job_done = all([task['done'] for task in status['tasks']])
        self.job_status = json.dumps(status, default=str)
        self.worker_utm=utc_milliseconds()
        self.save(update_fields=['worker_utm', 'job_status', 'job_done'])
        break


  def get_log(self):
    status = self.get_status()

    error = False
    timeout = False
    done = 0
    for task in status['tasks']:
      task['utc'] = datetime.strptime(task['utc'].split('.', 1)[0], "%Y-%m-%d %H:%M:%S")
      task['ltc'] = utc_to_timezone(task['utc'], self.timezone)
      task['ago'] = time_ago(task['utc'])

      if task['done']: done += 1
      if status.get('utc', task['utc']) <= task['utc']: status['utc'] = task['utc']

      if task['event'] == 'JOB_TIMEOUT': timeout = True
      elif task['event'] not in ('JOB_PENDING', 'JOB_START', 'JOB_END'): error = True

    if 'utc' not in status: status['utc'] = datetime.utcnow()
    status['utl'] = utc_to_timezone(status['utc'], self.timezone)
    status['ago'] = time_ago(status['utc'])
    status['percent'] = int(( done * 100 ) / ( len(status['tasks']) or 1 ))
    status['uid'] = self.uid()

    if timeout:
      status['status'] = 'TIMEOUT'
    elif error:
      status['status'] = 'ERROR'
    elif self.job_done:
      status['status'] = 'FINISHED'
    elif utc_milliseconds() - self.worker_utm < JOB_LOOKBACK_MS:
      status['status'] = 'RUNNING'
    elif not self.active:
      status['status'] = 'PAUSED'
    else:
      status['status'] = 'QUEUED'

    return status
