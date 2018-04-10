# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

result = 0;
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("!!!Request:")
    print(json.dumps(req, indent=4))

    res = processRequest1(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest1(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        print("Failed!! Action is wrong");
        return {}
    print("Make Yahoo Query!!");
    result = makeYqlQuery1(req)
    data = json.loads(result)
    print("Sending:")
    print(data)
    res = makeWebhookResult(data)
    return res

def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    print("Final Sending:")
    res = makeWebhookResult(data)
    print(res)
    return res

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    number = parameters.get("number")
    number1 = parameters.get("number1")
    print("!!!number: " + str(number));
    print("!!!number1: " + str(number1));
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeYqlQuery1(req):
    result = req.get("result")
    parameters = result.get("parameters")
    print(parameters);
    number = parameters.get("number")
    number1 = parameters.get("number1")
    print("!!!number: " + str(number));
    print("!!!number1: " + str(number1));
    #return str(number + number1);
    return str(int(number) + int(number1));


def makeWebhookResult(data):
    print("Response:")
    print(data)

    return {
        "speech": data,
        "displayText": data,
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
