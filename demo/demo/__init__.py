from django_cron import CronJobManager


class MyManager(CronJobManager):

    def should_run_now(self, force=False):
        print(f'--- custom CronJobManager: {self}')
        return super(MyManager, self).should_run_now(force)
