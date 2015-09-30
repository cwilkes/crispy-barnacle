# What is this project?

At the [2015 AEC Hackathon in Seattle](http://aechackathon.com/aec-hackathon-seattle) a team formed ([see CREDITS](./CREDITS.md)) 
around frustration having to deal with [NavisWorks](http://www.autodesk.com/products/navisworks/overview)'s lack of triage ability
with thousands of clashes in a typical building.

A "clash" is when two items occupy the same space that aren't allowed to -- for example a pipe running into a duct.  Pipes
running into walls may or may not be clashes.  NavisWorks offers some functionality to write rules to group things together
however it is very time consuming.  Also it does not have reporting capabilities for questions as easy as "how many clashes
does this group have today versus yesterday?"

This is the backend side of the project that ingests the clash XML from NavisWorks, pulls out the relevant clashes, stores them,
and has basic charting capabilities.  To get data into this system do an HTTP POST with a NavisWorks file or use
[Mark Kinsman's send clash xml plugin](https://github.com/MarkKinsman/NavisworksExtensions) on github.


# Using the project

This was a weekend hack project so there's a definate lack of some niceties -- for example you have to upload an undocumented
JSON file that describes the levels in a building [Here's a demo file](web/static/clash_util.json) to the `/projects/<projectname>`
endpoint even before you upload data.

After that all you need to do is upload a file to the `/xml/<projectname>/<date>` endpoint.  The field name for the file is
"file" and the date is in YYYY-MM-DD format.  Omitting the <date> will either give it today's date or one higher than the
highest date for that project.

Finally going to `/time` will show you charts for your projects.



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

Commands to run:
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

and now you can go to [http://docker]
