# Va.Si.Li-Lab-backend
Monorepo for the various backend modules used by [Va.Si.Li-Lab](https://github.com/texttechnologylab/Va.Si.Li-Lab)

# Modules
## Database-API
Main api which is required for the use of Va.Si.Li-Lab. It allows to define scenes which in turn are stored in a MongoDB.
It also contains our logging api which allows all user data points to be logged and stored.

## Chatbot-API
The Chatbot-API defines an endpoint for which one can query spoken text as audio data and receive a response from a chatbot. One can dynamically add or remove chatbots as well as select the desired chatbot when making the query.

## Text2Speech-API
Takes written text and returns spoken text based on Googles Text to Speech library.