# Code Challenge for Mercedes-Benz.io, SINFO 2019

## Challenge
Building a CLI tool capable of monitoring given services. Services chosen are:
* https://status.bitbucket.org
* https://status.gitlab.com

## Info about me
João Pedro Lourenço \<estudante.lourenco@gmail.com\>

Instituto Superior Técnico, Engenharia Informática e de Computadores, 2nd year.

## Info about the tool
`status-monitor` was developed in Python, using the following libraries:

```
beautifulsoup4==4.7.1 # Webscraping
certifi==2018.11.29
chardet==3.0.4
docopt==0.6.2         # Parse CLI arguments
idna==2.8
requests==2.21.0      # Get web content
soupsieve==1.8
urllib3==1.24.1
```

### How to install and run
```
git clone https://github.com/joaoestudante/service-monitor
cd service-monitor
source venv/bin/activate
cd service_monitor
./service_monitor.py <command>
```

### Examples
```console
$ ./service_monitor poll
- BitBucket 2019-02-24 13:59:02 [All Systems Operational]
- Gitlab    2019-02-24 13:59:03 [All Systems Operational]

$ ./service_monitor services
Configured services:

Service ID: bitbucket
Service Name: BitBucket
URL: https://status.bitbucket.org

Service ID: gitlab
Service Name: GitLab
URL: https://status.gitlab.com

$ ./service_monitor poll --exclude=gitlab --exclude=bitbucket

$ ./service_monitor poll --only=gitlab
- Gitlab    2019-02-24 14:15:42 [All Systems Operational]
```

### Design choices
There are 2 main entities in this project: a command, and a service. Since there are different types of services and commands, and they all share some (but not all) features, an OOP approach is desirable.

The `Command` class is inherited by each specific command. Every command must implement a method called `execute()`, responsible to do whatever the command must do. The only exception to this is the `help` command: it isn't considered a command like the others because the user just has to see the `__doc__` property of the program - it is not necessary to actually create an object.

The `Service` class is inherited by each type of service implemented. Similary to the `Command` class, each specific `Service` must implement some methods.

Finally, there is also a `ServiceManager` class, used to provide an interface for creation, storage, and access of all implemented `Service`s.

### Implemented features
* _**poll**_
  - [x] Outputs results
  - [x] Saves to local storage
  - [x] Supports `--only` [BONUS]
  - [x] Supports `--exclude` [BONUS]

* _**fetch**_
  - [x] Outputs results
  - [x] Saves to local storage
  - [x] Supports `--only` [BONUS]
  - [x] Supports `--exclude` [BONUS]

* _**history**_
  - [x] Outputs data
  - [x] Supports `--only` [BONUS]

* _**backup**_
  - [x] Saves the storage
  - [x] Save to `--format=txt` [BONUS]
  - [x] Save to `--format=csv` [BONUS]

* _**restore**_
  - [x] Sets storage contents to argument file content
  - [x] Supports `--merge=True` [BONUS]

* _**services**_
  - [x] Outputs services in config file

* _**help**_
  - [x] Outputs available commands

* _**status**_ [BONUS]
  - Not implemented
