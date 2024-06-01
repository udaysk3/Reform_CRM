from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .quickstart import main

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(main, 'interval', days=1)
	scheduler.start()