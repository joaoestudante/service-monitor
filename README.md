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
beautifulsoup4==4.7.1
requests==2.21.0
docopt==0.6.2
```

### Design choices
There are 2 main entities in this project: a command, and a service. Since there are different types of services and commands, and they all share some (but not all) features, an OOP approach is desirable.

The `Command` class is inherited by each specific command. Every command must implement a method called `execute()`, responsible to do whatever the command must do.

The `Service` class is inherited by each type of service implemented. Similary to the `Command` class, each specific `Service` must implement some methods.

Finally, there is also a `ServiceManager` class, used to provide an interface for creation, storage, and access of all implemented `Service`s.
