from flask import Flask, request
import xmltodict, json

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
    
if __name__ == "__main__":
    app.run()