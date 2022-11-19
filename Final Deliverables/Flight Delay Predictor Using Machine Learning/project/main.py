
from flask import Blueprint, render_template,request,redirect,url_for
from flask_login import login_required, current_user
from . import db
import requests
import flask
from flask_cors import CORS
from datetime import datetime

API_KEY = "b1papptuFebhE9mB86BRaPcjkCS3jwsVV_69I5w3os7E"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

main = Blueprint('main', __name__)
@main.route('/')
def index():
    return render_template('index.html')


    

@main.route('/profile')
@login_required
def profile():  
    return render_template('profile.html', name=current_user.name) 

@main.route('/prediction')
@login_required
def prediction():
    return render_template('prediction.html')

@main.route('/prediction',methods=['POST'])
@login_required
def prediction_post():
    departure_date=request.form['date_flight'] 
    departure_time=request.form['time_flight']
    departure_date_lis=departure_date.split('-') 
    departure_date_str=departure_date_lis[2]+"/"+departure_date_lis[1]+"/"+departure_date_lis[0]
    origin=request.form['source']
    destination=request.form['destination'] 
    departure_date_time=departure_date_str+" "+departure_time
    try:
        departure_date_time_parsed = datetime.strptime(departure_date_time, '%d/%m/%Y %H:%M:%S')
    except ValueError as e:
        return 'Error parsing date/time - {}'.format(e)

    month = departure_date_time_parsed.month
    day = departure_date_time_parsed.day
    day_of_week = departure_date_time_parsed.isoweekday()
    hour = departure_date_time_parsed.hour

    origin = origin.upper()
    destination = destination.upper()
    X= [[month, day, day_of_week, hour, 1 if origin == 'ATL' else 0, 1 if origin == 'DTW' else 0, 
    1 if origin == 'JFK' else 0, 1 if origin == 'MSP' else 0, 1 if origin == 'SEA' else 0,
    1 if destination == 'ATL' else 0, 1 if destination == 'DTW' else 0, 1 if destination == 'JFK' else 0,
    1 if destination == 'MSP' else 0, 1 if destination == 'SEA' else 0 ]]
    print(X)
    
    
    #predict= model.predict(X)[0]
    #print(predict) 
    pred=['Flight is on Time','Flight is Delayed']
    payload_scoring = {"input_data": [{"field": [['MONTH','DAY','DAY_OF_WEEK','CRS_DEP_TIME','ORIGIN_ATL',
    'ORIGIN_DTW','ORIGIN_JFK','ORIGIN_MSP','ORIGIN_SEA','DEST_ATL','DEST_DTW','DEST_JFK','DEST_MSP','DEST_SEA']], "values": X}]}
    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/82a07ea5-a22b-4882-acc3-7edb67a61b88/predictions?version=2022-11-15', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + mltoken})
    print(response_scoring)
    predictions = response_scoring.json()
    print(predictions)
    predict = int(predictions['predictions'][0]['values'][0][0]) 
    predict_str=pred[predict]
    print("Final prediction :",predict_str)
    
    # showing the prediction results in a UI# showing the prediction results in a UI
    return render_template('output.html', predict_str=predict_str)

@main.route('/output')
@login_required 
def predict_again():
    return render_template('prediction.html')





  



