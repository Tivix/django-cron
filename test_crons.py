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


class Test5minsCronJob(CronJobBase):
    code = 'test_run_every_mins'
    schedule = Schedule(run_every_mins=5)

    def do(self):
        pass


class TestRunAtTimesCronJob(CronJobBase):
    code = 'test_run_at_times'
    schedule = Schedule(run_at_times=['0:00', '0:05'])

    def do(self):
        pass


class Wait3secCronJob(CronJobBase):
    code = 'test_wait_3_seconds'
    schedule = Schedule(run_every_mins=5)

    def do(self):
        sleep(3)
