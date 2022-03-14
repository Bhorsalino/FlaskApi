docker-compose up -d

--REQUEST para app_1.py (Es necesario borrar la imagen flask-mongo_web, modificar Dockerfile para que lea app_1.py)

curl -L \
--request POST \
--url http://localhost:5000/add \
--header 'Content-Type: application/json' \
--data '
{
    "x": 4,
    "y": 8
}'

curl -L \
--request GET \
--url http://localhost:5000/hello


--REQUEST para app.py
wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz

curl -L \
--request POST \
--url http://localhost:5000/register \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "password": "Futurama80"
}'

curl -L \
--request POST \
--url http://localhost:5000/store \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "password": "Futurama80",
    "sentence": "Super ultra secret sentence"
}'

curl -L \
--request POST \
--url http://localhost:5000/get \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "password": "Futurama80"
}'

curl -L \
--request POST \
--url http://localhost:5000/detect \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "password": "Futurama80",
    "text1": "This is a cute dog",
    "text2": "Wow, the dog is so cute!"
}'

curl -L \
--request POST \
--url http://localhost:5000/refill \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "admin_pwd": "abc123",
    "refill": 4 
}'

curl -L \
--request POST \
--url http://localhost:5000/classify \
--header 'Content-Type: application/json' \
--data '
{
    "username": "Giorgio",
    "password": "Futurama80",
    "url": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Plains_Zebra_Equus_quagga.jpg"
}'

--Logeo en EC2
Cuando se descargan las llaves la primera vez es necesarion hacer chmod 400 al archivo .pem
ssh -i <key.pem> ubuntu@<DNS public>

ssh -i PythonApi.pem ubuntu@ec2-54-185-118-239.us-west-2.compute.amazonaws.com