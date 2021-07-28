from flask import Flask, request
from flask_sse import sse
import json
import accRandomizer as accR
from flask_cors import CORS, cross_origin
from flask import jsonify
from flask_ngrok import run_with_ngrok
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Timer
import time
import requests
from pyngrok import ngrok
from dotenv import dotenv_values
import datetime
import subprocess



config = dotenv_values(".env")

ngrok.set_auth_token(config['NGROK_AUTH_TOKEN'])

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/events')
run_with_ngrok(app)


ngrok_address = ''
def server_side_event(data, topicName):
    """ Function to publish server side event """
    with app.app_context():
        sse.publish(data, type=topicName)
        print("Event Scheduled at ",datetime.datetime.now())

@app.route('/', methods=['GET'])
def home():
    return "<h1>ACC randomize app Info Api</h1>"
# A route to return all data.
@app.route('/start_championnship', methods=['GET'])
@cross_origin()
def start_championnship():
    firstRoundSettings = accR.nextRound(True)
    return jsonify(firstRoundSettings)
@app.route('/display_result', methods=['GET'])
def display_result():
    fullResult = accR.checkResult()
    return fullResult

@app.route('/new_draw', methods=['GET'])
def new_draw():
    fullResult = accR.nextRound(False, True)
    return fullResult        
@app.route('/launch_server', methods=['GET'])
def launch_server():
    serverStatus = accR.launchServer()
    return jsonify(serverStatus)
@app.route('/shutdown_server', methods=['GET'])
def shutdown_server():
    serverStatus = accR.shutDownServer()
    return jsonify(serverStatus)
@app.route('/reset_championnship', methods=['GET'])
def reset_championnship():
    serverStatus = accR.resetChampionnship()
    return jsonify(serverStatus)
@app.route('/get_param_list', methods=['GET'])
def get_param_list():
    listParameters = accR.getParams()
    return jsonify(listParameters)
@app.route('/update_parameter', methods=['POST'])
def update_parameter():
    serverStatus = accR.updateParameters(request.json)
    return jsonify(serverStatus)
@app.route('/update_track_parameter', methods=['POST'])
def update_track_parameter():
    serverStatus = accR.updateTrackParameters(request.json)
    return jsonify(serverStatus)
@app.route('/update_car_parameter', methods=['POST'])
def update_car_parameter():
    serverStatus = accR.updateCarParameters(request.json)
    return jsonify(serverStatus)
@app.route('/update_user_parameter', methods=['POST'])
def update_user_parameter():
    serverStatus = accR.updateEntryParameters(request.json)
    return jsonify(serverStatus)
@app.route('/get_older_result', methods=['GET'])
def get_older_result():
    olderResult = accR.getOlderResult()
    return jsonify(olderResult)

@app.route('/api/v1/resources/books', methods=['GET'])
def schedule_check():
    # ADD CHECK RESULT EVERY 20 SEC
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(accR.checkResult,'interval',seconds=20)
    sched.start()
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

def ngrok_url():
    # ngrok_path = str(Path(tempfile.gettempdir(), "ngrok"))
    # executable = str(Path(ngrok_path, "ngrok.exe"))
    # ngrok = subprocess.Popen([executable, 'http', '5000'])
    # atexit.register(ngrok.terminate)
    localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
    time.sleep(1)
    tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
    j = json.loads(tunnel_url)
    
    tunnel_url = j['tunnels'][0]['public_url'] + "/" # Do the parsing of the get
    tunnel_url = tunnel_url.replace('http://', 'https://')
    API_ENDPOINT = "https://celtic-bromance-url.herokuapp.com/post_url"
    
    # data to be sent to api
    data = {'tunnel_url':tunnel_url}
    
    # sending post request and saving response as response object
    r = requests.post(url = API_ENDPOINT, data = data)
    pastebin_url = r.text
    schedule_check()

def startRedis():
    #Lunch redis server
    subprocess.call("Redis-x64-3.0.504\\redis-server.exe", shell=True)

if __name__ == "__main__":
    thread = Timer(5, ngrok_url)
    thread.setDaemon(True)
    thread.start()
    threadTwo = Timer(1, startRedis)
    threadTwo.setDaemon(True)
    threadTwo.start()
    app.run()