# CloudComputing

This repository was created during Cloud Computing study @ Insper (www.insper.edu.br). It contains some of the APS (Practical Supervisionised Activities) and the main individual project of this module.

## APS 1: REST service using FastAPI

In this activity, I created a simple RESTful webserver with 6 endpoints:
- /task - *GET*: lists all tasks;
- /task - *POST*: adds a new tasks;
- /task/<id> - *GET*: lists task with certain id;
- /task/<id> - *PUT*: updates task with certain id;
- /task/<id> - *DELETE*: deletes task with certain id;
- /healthcheck: status 200 without text;
  
How to run:
```bash
 uvicorn main:app --reload
```
All tests were made with Postman and FastAPI's interface.

## APS 2: Creating a Client

Using the webserver created in APS1, created a python script for a client with the same endpoints as previously. The commands are the following:

```bash
  $ task list
  $ task search <id>
  $ task add <name> <description>
  $ task update <id> <name> <description>
  $ task delete <id>
```

## APS 3:


## Project:

