myTinyURl
=========

Experement project for Tornado features.

That service get request like: http://localhost:8888/get_tiny/http://localhost:8888/api/v1/resources/1/ and return tiny link
like http://localhost:8888/qA23Da
At follow tiny link service will redirect to full link: http://localhost:8888/get_tiny/http://localhost:8888/api/v1/resources/1/
and insert log entry to MongoDB.

Configuration
=============

Command-line parameters
-----------------------

--host - Application IP address for bind
--port - application port
--autoreload - Autoreload application after change files
--debug launch in Tornado Debug mode
--mongo_host - Mongo database host IP
--mongo_port - Mongo database port
--mongo_user - Mongo database user
--mongo_password - Mongo user password

All parameters can be written in config python file. Example You can find at /etc/tinyurld/settings.py.example. For use settings from config file you should launch tinyurld with --config parameter
 
 Command-line launch example:
 
    tinyurld --config=/etc/tinyurld/settings.py --autoreload --port=3334