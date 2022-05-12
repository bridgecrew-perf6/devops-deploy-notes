from flask import Blueprint, jsonify, make_response
import requests
import time
import os
from app import redis_queue

view = Blueprint("view", __name__)

def get_current_weather(delay, API_KEY):
    time.sleep(delay)
    URL = f"https://api.openweathermap.org/data/2.5/onecall?lat=30.26&lon=97.74&exclude=minutely,hourly,daily,alerts&appid={API_KEY}"
    response = requests.get(URL)
    try:
        status_code, data = response.status_code, response.json()
        return status_code, data["current"]["weather"]
    except:
        return response.status_code, f"Weather API Call Failed: {response.text}"

# credit: https://blog.abbasmj.com/implementing-redis-task-queues-and-deploying-on-docker-compose
@view.route("/")
def index():
    num_jobs = len(redis_queue.jobs)
    html = '<center><br /><br />'
    for job in redis_queue.jobs:
        html += f'<a href="job/{job.id}">{job.id}</a><br /><br />'
    html += f'Total {num_jobs} Jobs in queue </center>'
    return f"{html}"

@view.route("/request_weather/")
def request_weather():
    # Note: this is a terrible solution, best to try and figure out how to access config variables from the app.config object in the future!
    API_KEY = os.environ.get("API_KEY", None)
    task = redis_queue.enqueue(get_current_weather, args=(2, API_KEY,))
    return make_response({"message": f"SUCCESS - enqueued job: {task.id}"}, 200)

@view.route("/weather/<job_id>/")
def view_weather(job_id):
    task = redis_queue.fetch_job(job_id)
    if not task.is_finished:
        return f'<center><br /><br /><h3>The job is still pending</h3><br /><br />ID:{job_id}<br />Queued at: {task.enqueued_at}<br />Status: {task._status}</center>' 
    return f'<center><p>Result of Job{job_id}</p><br /><p>{task.result}</p></center>'

@view.route("/ping")
def ping():
    return make_response(jsonify({"message":"SUCCESS"}), 200)
