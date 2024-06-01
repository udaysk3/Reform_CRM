from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .quickstart import main

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(main, 'interval', seconds=1)
	scheduler.start()