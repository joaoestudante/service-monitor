#! /usr/bin/env python3
"""
Service Monitor.

Usage:
    service-monitor poll [--exclude=<service>...|--only=<service>...]
    service-monitor fetch [--refresh=<time>] [--exclude=<service>...|--only=<service>...]
    service-monitor history [--only=<service>]
    service-monitor backup --filename=<filename> [--format=<filetype>]
    service-monitor restore --filename=<filename> [--merge=<merge>]
    service-monitor services
    service-monitor help
    service-monitor status

Options:
    --exclude=<service>   Excludes services from display.
    --only=<service>      Only shows info of the specified service.
    --filename=<filename> Saves to the argument file.
    --format=<filetype>   Format of the output file for backup (Supported: txt, csv).
    --merge=<merge>       True or False. Merges the content of the input file instead of replacing it.
    --refresh=<time>      Ammount of time, in seconds, that should pass between continuous polling [default: 5].
"""
from docopt import docopt
import datetime
import pickle
import abc
import os

import services as serv
import commands as cmd
import custom_exceptions


def load_service_manager(path):
    if os.path.isfile(path):
        with open(path, "rb") as sm:
            return pickle.load(sm)
    else:
        return serv.ServiceManager(path)

if __name__ == "__main__":
    arguments=docopt(__doc__, version='Service Monitor 1.0')

    used_args = {option:arguments[option] for option in arguments \
        if arguments[option] is not None and \
        not isinstance(arguments[option], bool) and \
        arguments[option] != []}

    services_manager = load_service_manager("service-monitor.storage")
    try:
        services_manager.update_services("config.txt")

    except (custom_exceptions.BadConfigException, custom_exceptions.UnrecognizedServiceException) as e:
        print(e)
        os.sys.exit(0)

    if arguments["poll"]:
        poll = cmd.PollCommand(used_args, services_manager)
        print(poll.execute())

    elif arguments["fetch"]:
        fetch = cmd.FetchCommand(used_args, services_manager)
        fetch.execute()

    elif arguments["history"]:
        history = cmd.HistoryCommand(used_args, services_manager)
        res = history.execute()
        print(res)

    elif arguments["backup"]:
        backup = cmd.BackupCommand(used_args, services_manager)
        print(backup.execute())

    elif arguments["restore"]:
        restore = cmd.RestoreCommand(used_args, services_manager)
        print(restore.execute())

    elif arguments["services"]:
        services = cmd.ServicesCommand(used_args, services_manager, "config.txt")
        print(services.execute())

    elif arguments["help"]:
        print(__doc__)

    elif arguments["status"]:
        status = cmd.StatusCommand(used_args, services_manager)
        status.execute()

