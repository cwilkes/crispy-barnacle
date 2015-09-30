# Running locally


1. setup python virtual env
```
  virtualenv-2.7 venv 
	. venv/bin/activate
```

2. setup http://redis.io locally (for mac type "brew install redis")
3. export two environment variables:
```
  export PYTHONPATH=.
  export REDISCLOUD_URL=redis://localhost
```
4. Run the server
```
  gunicorn --log-level DEBUG --logger-class=simple --pythonpath web --access-logfile - --error-logfile - --log-file - url:app
```

# Heroku instructions

1. Get account on https://www.heroku.com
2. Create an application (first one is free)
3. Logon locally: `heroku login`
3. Install the rediscloud application `heroku addons:create rediscloud:30`
4. edit your file .env with:
```
  PYTHONPATH=.
  REDISCLOUD_URL=redis://localhost
```
 5. Finally run it locally: `heroku local`
 
If that works then setup a remote branch with the endpoint being your heroku instance,
`git config --local --edit` should have this in it:
```
  [remote "herokuprod"]
  url = git@heroku.com:your-heroku-project.git
  fetch = +refs/heads/*:refs/remotes/herokuprod/*
```


# Docker instructions

This is easiest if you use (for local development):
1. Docker toolbox https://www.docker.com/toolbox
2. Virtualbox https://www.virtualbox.org

```
  docker-machine create -d virtualbox dev
  docker-machine ls
  eval $(docker-machine env dev)
  docker-compose build
  docker-compose up -d
```

To connect to the server use the IP address that's in the environment variable $DOCKER_HOST, or:
```
  echo $(echo $DOCKER_HOST | cut -d\/ -f3 | cut -d\:  -f1) docker | sudo tee -a /etc/hosts
```

and now you can go to http://docker
