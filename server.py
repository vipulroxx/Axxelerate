from flask import Flask, request, Response, abort
from flask_cors import cross_origin
import json
import example_data
import pymysql
import credentials
app = Flask(__name__)

connection = pymysql.connect(host = credentials.host,
                             user = credentials.user,
                             password = credentials.password,
                             db = credentials.db,
                             cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def hello():
    return "Hello World"

@app.route("/results")
@cross_origin({"origins": "http://localhost:*"})
def getResults():
    queryString = request.args.get("query")
    f = request.args.get("from")

    sql_request = ""
    args = ()

    if (queryString == None):
        return "Bad stuff!"
    if (f == None):
        sql_request = "SELECT url, title, chipwords, pagerank FROM keywords LEFT JOIN pages ON pageID = pages.ID LEFT JOIN chipwords ON chipwords.ID = pages.ID WHERE word = %s ORDER BY pagerank DESC LIMIT 11"
        args = (queryString)
    else:
        sql_request = "SELECT url, title, chipwords, pagerank FROM keywords LEFT JOIN pages ON pageID = pages.ID LEFT JOIN chipwords ON chipwords.ID = pages.ID WHERE word = %s and pagerank <= %s ORDER BY pagerank DESC LIMIT 11";
        args = (queryString, f)

    result = None

    with connection.cursor() as cursor:
        cursor.execute(sql_request, args)
        raw_results = cursor.fetchmany(10)



        result = {
            "results" : []
        }

        last = cursor.fetchone()
        if (last != None):
            result["nextFrom"] = str(last['pagerank'])

        if (len(raw_results) > 0):
            currentStarter = raw_results[0]["pagerank"]
            sql_fetch_prev = "SELECT url, title, pagerank FROM keywords LEFT JOIN pages ON pageID = ID WHERE word = %s and pagerank >= %s ORDER BY pagerank LIMIT 12";
            cursor.execute(sql_fetch_prev, (queryString, currentStarter))
            results = cursor.fetchall()
            if (len(results) == 12 or len(results) == 11):
                result["prevFrom"] = str(results[10]["pagerank"])


        for page in raw_results:
            p = {
                "snippet" : "",
                "link" : page["url"].decode("latin1"),
                "title" : page["title"].decode("latin1"),
                "chipwords": page["chipwords"].decode("latin1").split(',')[:2]
            }
            result["results"].append(p)

    return Response(json.dumps(result), mimetype="application/json")

def getKeywords():
    queryString = request.args.get("query")
    sql_request = ""
    args = ()

    if (queryString == None):
        return "Bad stuff!"
    else:
        sql_request = "SELECT chipwords,title FROM chipwords,pages WHERE title  = %s and  <= %s ORDER BY pagerank DESC LIMIT 11";
        args = (queryString, f)

    result = None

    with connection.cursor() as cursor:
        cursor.execute(sql_request, args)

