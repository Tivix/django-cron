
Summary of my fork changes
=======================
- Access to change CronJobManager from django settings if required.

```python
CRON_MANAGER = 'path.to.custom.MyManager'
```

---
- Add day config to CronJob schedule:

```python
day_of_month='*',  # cron format: '*/3' '5,15,25' or list: [1] * 31
month_numbers='*',  # cron format: '*/3' '5,15,25' or list: [1] * 12
day_of_week='*',  # cron format: '*/3' '5,15,25' or list: [1] * 7
```

Example:
```python
from django_cron import CronJobBase, Schedule

class ExampleCronJob(CronJobBase):
    RUN_AT_TIMES = ['10:10', '22:10']
    schedule = Schedule(run_at_times=RUN_AT_TIMES, day_of_week='2')
    code = 'cron.ExampleCronJob'
    def do(self):
        pass

```

---
- Add a method to CronJob to get future run times in future by this parameters:
`from_datetime` and `to_datetime`

---
- Move should_run_now method to CronJob to override it if required.

Example: 

```python
from django_cron import CronJobBase, Schedule

class TestCronJob(CronJobBase):
    RUN_AT_TIMES = ['10:10', '22:10']
    schedule = Schedule(
        run_at_times=RUN_AT_TIMES,
        # day_of_week='*/2',
    )

    code = 'demo.TestCronJob'

    def do(self):
        print('do TestCronJob')
        return f'do TestCronJob at {datetime.now()}'

    def should_run_now(self, force=False):
        print('override should_run_now in cron job')
        '''
        if some_conditions_to_avoid_run_job:
            return False
        '''
        return super(TestCronJob, self).should_run_now(force=force)

```
