from flask import Flask, request, jsonify
import xmltodict, json
import urllib.request
import threading
import time
import queue
import json

app = Flask(__name__)

def getExpandableProps(name, id):
    destinationUrl = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id;
    metadata = urllib.request.urlopen(destinationUrl+"/$metadata").read()
    metadata = xmltodict.parse(metadata)
    schema = metadata["edmx:Edmx"]["edmx:DataServices"]["Schema"]
    # schema = json.loads(json.dumps(schema, default=str))
    entityTypes = [item["EntityType"] for item in schema if "EntityType" in item.keys()][0]
    navigationProperty = [properties["NavigationProperty"] for properties in entityTypes if properties["@Name"] == "SyndicObject"][0]
    expandableProps = ",".join([item["@Name"] for item in navigationProperty])
    return expandableProps

@app.route('/')
def index():
    return "Hello, I'm Genieouz!"

@app.route('/xml-to-json', methods=['POST'])
def uploadFile():
    if 'file' not in request.files:
        return "Ficher xml 'file' introuvable!"
    xml = request.files['file'].stream.read()
    return xmltodict.parse(xml)

@app.route('/tourinsoft/Syndication/<name>/<id>')
def getTourrinSoftDestination(name, id):
    destinationUrl = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id;
    expandableProps = getExpandableProps(name, id)
    contents = urllib.request.urlopen(destinationUrl+"/Objects?$format=json&$expand="+expandableProps).read()
    return json.loads(contents)

if __name__ == "__main__":
    app.run()