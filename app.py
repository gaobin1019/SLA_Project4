#!/usr/bin/env python

import urllib
import json
import os
import random

from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

# Flask app should start in global layout
app = Flask(__name__)

#config
app.config.from_object(os.environ['APP_SETTINGS'])

#create DB object
db = SQLAlchemy(app)

from model import *


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("request")
    print(json.dumps(req,indent=4))

    speech = processRequest(req)

    res = {
        "speech":speech,
        "displayText": speech,
        "source": "The Database of Tao"
    }
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#request as json object,return output as string,return error prompt if no action found.
#a lot of thing to factor and improve. todo
def processRequest(req):
    action = req.get("result").get("action")
    #data = ""
    #welcome to the jungle
    if action == "intro":
        tag = req.get("result").get("parameters").get("greeting")

        try:
            data = TaoQuotes.query.filter(TaoQuotes.tag == tag).first()
        except:
            db.session.rollback()
        taoquote = getattr(data,"quote")

        speech = taoquote

        return speech
    elif action == "general":
        rowList = []

        try:
            rowList = TaoQuotes.query.filter(TaoQuotes.tag == "general").all()
        except:
            db.session.rollback()

        taoquote = ""

        random.seed()
        whichRow = random.randint(1,len(rowList))

        taoquote += getattr(rowList[whichRow-1],"quote")

        speech = taoquote
        return speech

    else:
        keyword = req.get("result").get("parameters").get("keyword")

        rowList = []
        try:
            #fill the list with all matching quotes
            rowList = TaoQuotes.query.filter(TaoQuotes.tag == keyword).all()
        except:
            db.session.rollback()

        taoquote = ""

        #edge case of empty rowlist AKA no match for keyword
        if (len(rowList) == 0):
            try:
                #return a generic quote instead
                rowList = TaoQuotes.query.filter(TaoQuotes.tag == "general")
            except:
                db.session.rollback()
        
        #generate pseudorandom number between 1 and length of list
        #then pick that row from the list
        random.seed()
        whichRow = random.randint(1,len(rowList))

        taoquote += getattr(rowList[whichRow-1],"quote")

        speech = taoquote
        return speech


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
