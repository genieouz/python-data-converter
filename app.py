from flask import Flask, request
import xmltodict, json
import urllib.request
import threading
import time
import queue

app = Flask(__name__)

a = { "feed": { "entry": [] } }
thrs = [];
result = {}
temoin = { "c": 0, "len": 0 }
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
    links = 0
    print("entress ", len(result["feed"]["entry"]))
    print("link ", len(result["feed"]["entry"][0]["link"]))
    q = queue.Queue()
    for entry in result["feed"]["entry"]:
        # print("nb links ",len(entry["link"]) - 1)
        global thrs
        # if(i < 200):
        links = links + len(entry["link"]) - 1
        j = 0
        for link in entry["link"]: 
            if(j > 0): 
                # populatedObject = urllib.request.urlopen(destinationUrl+"/"+link["@href"]).read()   
                # link["@linkValue"] = xmltodict.parse(populatedObject)
                t = threading.Thread(target=populateLink, args=(destinationUrl+"/"+link["@href"], i, j, link))
                # t.start();
                q.put(t)
            j = j + 1
        i = i + 1
    thrs = []
    print("queue size ", q.qsize())
    step = 1
    while(not q.empty()):
        t = q.get()
        t.start()
        thrs.append(t)
        if len(thrs) == 200 or q.empty():
            print("step ", step)
            step = step + 1
            for i in range(len(thrs)):
                thrs[i].join()
            thrs = []

    # for t in thrs:
    #     t.join()
    # thrs = [];
    print("linksValues ", links)
    return result

if __name__ == "__main__":
    app.run()