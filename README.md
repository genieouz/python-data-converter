## Présentation
Ce projet est un convertisseur de format de données.

## Lancement de l'application

pour lancer l'application, exécutez les commandes suivantes:

`export FLASK_APP=app`

`export FLASK_ENV=development`

`flask run`

## Utilisation
Conversion XML to JSON

Une fois le projet lancé, vous pouvez uploader un fichier('file' etant le nom du champ du formulaire) vers [http://localhost:5000/xml-to-json](http://localhost:5000/xml-to-json). 
Ce endpoint retournera le contenu du fichier xml en json

Vous pouvez utilisez le fichier data.xml qui se trouve dans le dossier seeds pour tester.

Vous pouvez aussi utiliser l'api en Ligne: [https://py-data-converter.herokuapp.com/xml-to-json](https://py-data-converter.herokuapp.com/xml-to-json)