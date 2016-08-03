# myTinyURl

Experement project for Tornado features.

That service get request like: http://localhost:8888/get_tiny/http://localhost:8888/api/v1/resources/1/ and return tiny link
like http://localhost:8888/qA23Da
At follow tiny link service will redirect to full link: http://localhost:8888/get_tiny/http://localhost:8888/api/v1/resources/1/
and insert log entry to MongoDB.