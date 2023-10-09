# Chatbot Module
This module allows for various chatbots to be dynamically loaded which will then be queryable from the chatbot-host.
This is achieved by automatically establishing a socket connection between the host and the various chatbot clients.

In the `./chatbots` directory you can find various chatbots with dockerfiles available.

# Running
To run this service simply run the `./chatbot-host.py` file as well as a selection of chatbots that you want to use.


Available environment variables for the chatbot-host script are:

|Value| Description| Default|
| ---| ---| ---|
|MAX_HTTP_BUFFER_SIZE | The maximum size of requests socket io allows in bytes|2,000,0000|
|PORT| The port this service uses| 5000|
|SOCKET_SECRET| The socket secret to be used| reallyGoodSecret!|
|DEBUG| Wether debugging is enabled or not| False|
|HOST| The host the service is running on | 0.0.0.0|