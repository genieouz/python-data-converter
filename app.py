from flask import Flask, request
import xmltodict, json
import urllib.request
import threading
import time

app = Flask(__name__)

a = { "feed": { "entry": [] } }
thrs = [];
result = {}
def populateLink(objectLink, i, j, link): 
    populatedObject = urllib.request.urlopen(objectLink).read()
    # a.append(xmltodict.parse(populatedObject))
    # a["feed"]["entry"].append(result["feed"]["entry"][i])
    link["@linkValue"] = xmltodict.parse(populatedObject)
    # result["feed"]["entry"][i]["link"][j]["@linkValue"] = xmltodict.parse(populatedObject)

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
def getTourrinSoft(name, id):
    destinationUrl = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id;
    contents = urllib.request.urlopen(destinationUrl+"/Objects").read()
    result = xmltodict.parse(contents)
    i= 0 ;
    print("entress ", len(result["feed"]["entry"]))
    print("link ", len(result["feed"]["entry"][0]["link"]))
    for entry in result["feed"]["entry"]:
        global thrs
        if(i < 100):
            j = 0
            for link in entry["link"]: 
                if(j > 0): 
                    # populatedObject = urllib.request.urlopen(destinationUrl+"/"+link["@href"]).read()   
                    # link["@linkValue"] = xmltodict.parse(populatedObject)
                    t = threading.Thread(target=populateLink, args=(destinationUrl+"/"+link["@href"], i, j, link))
                    t.start();
                    thrs.append(t);
                j = j + 1
        i = i + 1
    if(i%50 == 0):
        for t in thrs:
            t.join()
        # time.sleep(1)
        thrs = [];
    return result

if __name__ == "__main__":
    app.run()