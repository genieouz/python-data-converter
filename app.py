from flask import Flask, request
import xmltodict, json
import urllib.request

app = Flask(__name__)

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
    for entry in result["feed"]["entry"]:
        if(i < 10):
            j = 0
            for link in entry["link"]: 
                if(j > 0): 
                    populatedObject = urllib.request.urlopen(destinationUrl+"/"+link["@href"]).read()   
                    link["@linkValue"] = xmltodict.parse(populatedObject)
                j = j + 1
        i = i + 1
    return result

if __name__ == "__main__":
    app.run()