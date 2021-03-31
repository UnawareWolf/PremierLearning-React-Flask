# Premier Learning

## 1 The Project

### 1.1 [`api`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api)

The [`api`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api) directory contains python backend code and player data.

#### 1.1.1 [`flasktools`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/flasktools)

This python module creates the flask app and attaches blueprints for url routes. The routes give access to [`squadtools`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/squadtools) to get transfer suggestions and [`premierlearning`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/premierlearning) for admin to re-learn the model.

#### 1.1.2 [`persistence`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/persistence)

This python module handles interactions with the database; it inserts players created from [`premierlearning`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/premierlearning) and also extracts players for squad optimising.

#### 1.1.3 [`premierlearning`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/premierlearning)

This python module updates player data in [`data`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/data) with calls to the fantasy premier league api. It uses this data to initialise player objects which are inputs to the tensor flow machine learning model that predicts future player scores. These predictions are attached to the original player objects and saved to the database via [`persistence`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/persistence).

#### 1.1.4 [`squadtools`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/squadtools)

This python module selects learnt players from the database via [`persistence`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/persistence), logs in to a user's fantasy team with a call to the fantasy premier league api and uses a pulp linear-optimisation model to offer transfer suggestions.

#### 1.1.5 [`data`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/api/data)

This directory holds player data from the fantasy premier league api in csv and json files.

## 1.2 [`src`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/src)

The [`src`](https://github.com/UnawareWolf/PremierLearning-React-Flask/tree/main/src) directory contains front end react code which calls the python api and renders results.

## 2 Tutorials

### Machine Learning

[3Blue1Brown YouTube series on neural networks and deep learning](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)

[Tutorial on keras (python, uses tensorflow)](https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/)

[Installing tensorflow no cache](https://stackoverflow.com/questions/44335087/unable-to-install-tensorflow-memoryerror)

### React

[Noughts and Crosses](https://reactjs.org/tutorial/tutorial.html)

[Async, Await Fireship YouTube video](https://www.youtube.com/watch?v=vn3tm0quoqE)

[Sending Requests DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-call-web-apis-with-the-useeffect-hook-in-react)

### TypeScript

[TypeScript React Ben Awad YouTube video](https://www.youtube.com/watch?v=Z5iWr6Srsj8)

### Flask

[Blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints/)

[SQLite3](https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/)

[Application Context](https://flask.palletsprojects.com/en/1.1.x/appcontext/)

[Flask CORS](https://flask-cors.readthedocs.io/en/latest/)

[Receiving Requests](https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask)

### SQLite

[SQLite3 Python DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-use-the-sqlite3-module-in-python-3)

### Server

[Miguel Grinberg blog: react and flask on localhost](https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project)

[NGINX Fireship YouTube video](https://www.youtube.com/watch?v=JKxlsvZXG7c)

[Miguel Grinberg blog: react and flask on server using NGINX](https://blog.miguelgrinberg.com/post/how-to-deploy-a-react--flask-project)

[Linode: securing your server](https://www.linode.com/docs/guides/securing-your-server/)

[HTTPS setup with Let's Encrypt/Certbot](https://letsencrypt.org/getting-started/)

[HTTPS more detailed instructions with DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04)
