from time import sleep

from django_cron import CronJobBase, Schedule


class TestSucessCronJob(CronJobBase):
    code = 'test_success_cron_job'
    schedule = Schedule(run_every_mins=0)

    def do(self):
        pass


class TestErrorCronJob(CronJobBase):
    code = 'test_error_cron_job'
    schedule = Schedule(run_every_mins=0)

    def do(self):
        raise Exception()


class TestSleepingCronJob(CronJobBase):
    code = 'test_sleeping_cron_job'
    schedule = Schedule(run_every_mins=0)

    def do(self):
        print 'do: start'
        sleep(1)
        print 'do: end'
