from flask import Flask, request, jsonify
import xmltodict, json
import urllib.request
import threading
import time
import queue
import json
from operator import itemgetter
import re
from urlextract import URLExtract
extractor = URLExtract()

app = Flask(__name__)


def filter_props(prop):
    expandable_props = ['Structure','PHOTOs','TYPEs','MOBILEs','TELEPHONEs','LABELTHs','EMAILs', 'PHOTOSs']

    if prop in expandable_props:
        return True
    else:
        return False


def get_expandable_props(name, id, url):
    destination_url = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id;
    metadata = urllib.request.urlopen(url+"/$metadata").read()
    metadata = xmltodict.parse(metadata)
    schema = metadata["edmx:Edmx"]["edmx:DataServices"]["Schema"]
    # schema = json.loads(json.dumps(schema, default=str))
    entity_types = [item["EntityType"] for item in schema if "EntityType" in item.keys()][0]
    navigation_property = [properties["NavigationProperty"] for properties in entity_types if properties["@Name"] == "SyndicObject"][0]
    expandable_props = ",".join(filter(filter_props, [item["@Name"] for item in navigation_property]))
    return expandable_props


@app.route('/')
def index():
    return "Hello, I'm Genieouz!"


@app.route('/xml-to-json', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Ficher xml 'file' introuvable!"
    xml = request.files['file'].stream.read()
    return xmltodict.parse(xml)


@app.route('/tourinsoft/Syndication/old/<name>/<id>')
def get_tourinsoft_destination(name, id):
    destination_url = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id;
    expandable_props = get_expandable_props(name, id, destination_url)
    contents = urllib.request.urlopen(destination_url+"/Objects?$format=json&$expand="+expandable_props).read()
    return json.loads(contents)


def createField(entity, field):
    entity[field] = ""


def create_literal_dict(fields):
    literal = ""
    for field in fields:
        literal = literal + "['"+field+"']"
    return literal


@app.route('/tourinsoft/Syndication/<name>/<id>', methods=['GET', 'POST'])
def get_tourinsoft_syndication(name, id):
    data_form = request.get_json(force=True)
    destination_url = "http://wcf.tourinsoft.com/Syndication/3.0/"+name+"/"+id
    # print({'og': destination_url+"/Objects?$format=json&$expand="+expandable_props})
    print('request body', data_form)
    if 'api-v3.tourinsoft.com' in data_form['url']:
        req_url = data_form['url'] + '?format=json'
    else:
        req_url = data_form['url'] + '/Objects?$format=json'
    if 'expand' in data_form.keys() and data_form['expand'] is True:
        expandable_props = get_expandable_props(name, id, data_form['url'])
        req_url = req_url + "&$expand="+expandable_props
    print("req_url ",req_url)
    contents = urllib.request.urlopen(req_url).read()
    result = json.loads(contents)
    result.pop("odata.metadata", None)
    entries = []
    if "value" in result.keys():
        entries = result["value"]
    elif "d" in result.keys():
        entries = result["d"]
    mapping = []
    with open('mappings/mapping-type.json') as f:
        mapping = json.load(f)
    for entry in entries:
        if "contacts" not in entry.keys():
            entry["contacts"] = {'mail': "", 'phone': ""}
        if "mail" not in entry["contacts"].keys():
            entry["contacts"]["mail"] = ""
        if "phone" not in entry["contacts"].keys():
            entry["contacts"]["phone"] = ""
        if "address" not in entry.keys():
            entry["address"] = {"location": {'lat': "", 'lng': ""}, 'full_address': "", "locality": ""}
        if "location" not in entry["address"].keys():
            entry["address"]["location"] = {}
        if "informations" not in entry.keys():
            entry["informations"] = {'languages': ""}

        if "Structure" in entry.keys() and entry["Structure"] is not None and "Country" in entry["Structure"].keys():
            if entry["Structure"]["Country"] is not None:
                entry["country"] = entry["Structure"]["Country"]
        if "Adresses" in entry.keys() and isinstance(entry["Adresses"], list) and len(entry["Adresses"]) > 0:
            entry["Adresse"] = entry["Adresses"][0]["Adresse1"]
            entry["COMMUNE"] = entry["Adresses"][0]["Commune"]
            if "Adresse1Suite" in entry["Adresses"][0].keys() and entry["Adresses"][0]["Adresse1Suite"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["Adresses"][0]["Adresse1Suite"]
            if "CodePostal" in entry["Adresses"][0].keys() and entry["Adresses"][0]["CodePostal"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["Adresses"][0]["CodePostal"]
                entry["CodePostal"] = entry["Adresses"][0]["CodePostal"]
            if "Commune" in entry["Adresses"][0].keys() and entry["Adresses"][0]["Commune"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["Adresses"][0]["Commune"]

        if "ADRESSE1" in entry.keys() and entry["ADRESSE1"] is not None:
            entry["Adresse"] = entry["ADRESSE1"]
            if "ADRESSE1SUITE" in entry.keys() and entry["ADRESSE1SUITE"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["ADRESSE1SUITE"]
            if "CODEPOSTAL" in entry.keys() and entry["CODEPOSTAL"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["CODEPOSTAL"]
            if "COMMUNE" in entry.keys() and entry["COMMUNE"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["COMMUNE"]

        if "adresse1" in entry.keys() and entry["adresse1"] is not None:
            entry["Adresse"] = entry["adresse1"]
            if "adresse1Suite" in entry.keys() and entry["adresse1Suite"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["adresse1Suite"]
            if "codePostal" in entry.keys() and entry["codePostal"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["codePostal"]
            if "commune" in entry.keys() and entry["commune"] is not None:
                entry["Adresse"] = entry["Adresse"] + ", " + entry["commune"]

        if "photo" in entry.keys() and entry["photo"] is not None:
            entry["photo"] = entry["photo"].replace("|", " ")
            # entry["photo"] = re.sub(r'\|.*', '', entry["photo"])
            urls = extractor.find_urls(entry["photo"])
            entry["gallery"] = [x for x in urls]

        for field in mapping:
            for possibleName in field["fieldNames"]:
                if possibleName in entry.keys():
                    value = entry[possibleName]
                    if "newNameValueType" in field.keys() and field["newNameValueType"] == "Array" and entry[possibleName] is not None and isinstance(entry[possibleName], str):
                        value = entry[possibleName].split(field["createArrayWithSeparator"])
                    if field["newNameType"] == "text":
                        if isinstance(value, str):
                            if str(value).lower() == "non" or str(value).lower() == "oui":
                                value = True if value.lower() == "oui" else False
                            else:
                                value = str(value).replace("'", "\\'")
                        entry[field["fieldNewName"]] = value
                        if field["fieldNewName"] == 'title':
                            entry[field["fieldNewName"]] = value.capitalize()
                    else:
                        literal_dict = "entry"+create_literal_dict(field["fieldNewName"])
                        if value is not None:
                            eval_op = None
                            if isinstance(value, str) and field["newNameType"] != "ArrayExtracted":
                                if str(value).lower() == "non" or str(value).lower() == "oui":
                                    value = True if value.lower() == "oui" else False
                                else:
                                    value = str(value).replace("'", "\\'")
                                eval_op = literal_dict+"="+"'"+value+"'"
                            else:
                                if "levels" in field.keys():
                                    intermediateVal = None
                                    if isinstance(value, list):
                                        intermediateVal = []
                                        i = 0
                                        for val in value:
                                            for level1 in field["levels"]:
                                                subfields = [subfield for subfield in level1["fields"]]
                                                if len(level1["fields"]) == 0:
                                                    intermediateVal.append(val[level1["name"]])
                                                elif level1["name"] == "None":
                                                    intermediateVal.append({})
                                                    for subfield in level1["fields"]:
                                                        if subfield in val.keys():
                                                            intermediateVal[i][subfield] = itemgetter(subfield)(
                                                                val)
                                                else:
                                                    intermediateVal.append({})
                                                    for subfield in level1["fields"]:
                                                        intermediateVal[i][subfield] = itemgetter(subfield)(val[level1["name"]])
                                            i = i + 1
                                        value = intermediateVal
                                if field["newNameType"] == "ArrayExtracted":
                                    value = re.findall(field["regex"], value.replace("</span>", ""))
                                    if possibleName == 'Photo':
                                        value = [{'Url': v, "Credit": None, "Titre": None} for v in value]
                                if "changeArrayToOne" in field.keys() and field["changeArrayToOne"] == "true":
                                    value = value[0] if len(value) > 0 else None
                                if isinstance(value, str):
                                    value = str(value).replace("'", "\\'")
                                    eval_op = literal_dict + "=" + "'" + value + "'"
                                else:
                                    eval_op = literal_dict+"="+str(value)
                            exec(eval_op)
        if entry["address"]["locality"] is not None:
            entry["address"]["locality"] = entry["address"]["locality"].lower()
        if "scheduleText" in entry.keys() and entry["scheduleText"] is not None:
            entry["scheduleText"] = entry["scheduleText"].replace("\\", "");
            entry["scheduleText"] = entry["scheduleText"].replace("\n", " ")

    return result


if __name__ == "__main__":
    app.run()