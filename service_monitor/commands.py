"""
Command classes for usage with service-monitor.py.
"""

import abc
from time import sleep
import pickle

class Command(object):
    """ A Command class. Offers some common methods and variables for all
    commands. Any implementation of a command must implement the execute()
    method with the action that the command must perform.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, arguments, services_manager):
        """
        Args:
            arguments (dict): contains the arguments given in the command line.
            services_manager (ServicesManager): common interface for the
                supported commands.
        """
        self.arguments = arguments
        self.services_manager = services_manager
        self.excluded = self.excluded_services()

    def get_refresh_time(self):
        """ Gets the refresh time for the fetch command, from the arguments.

        Returns:
            Value of the argument (str)
        """
        return self.arguments.get("--refresh", None)

    def output_filename(self):
        """ Gets the output file filename, from the arguments.

        Returns:
            Filename (str)
        """
        return self.arguments.get("--filename", None)

    def format_output_file(self):
        """ Gets the format of the output file, from the arguments.

        Returns:
            Format (str)
        """
        return self.arguments.get("--format", None)

    def excluded_services(self):
        """ Based on the arguments, discovers which services will be excluded.
        If a user uses the flag --only, then all services will be excluded,
        except for the one after the flag.
        If a user uses the flag --except, then the specified services will be
        excluded.

        Returns:
            Excluded services (list)
        """
        if self.arguments.get("--only") is not None:
            supported = ["bitbucket", "gitlab"]
            wanted = self.arguments.get("--only")
            excluded = [x for x in supported if x not in wanted]

        else:
            excluded = self.arguments.get("--exclude", [])

        return excluded

    def get_merge(self):
        """ Used for the restore command. Gives info about what to do with the
        content of the input file: append (or merge) to the existing storage,
        or replace it.

        Returns:
            True if the file will be merged, False if not.
        """
        return self.arguments.get("--merge", False)

    @abc.abstractmethod
    def execute(self):
        """Executes the command. If the command is not implemented and a call
        to execute() was made, an info message is printed.
        """
        print("Command not implemented.")
        return

class PollCommand(Command):
    def execute(self):
        """ Polls implemented (and not excluded) services.

        Returns:
            The result of each service poll (str).
        """
        output = ""
        for service in self.services_manager.existing_services:
            if service.identifier not in self.excluded:
                output += service.poll() + "\n"

        self.services_manager.save()
        return output[:-1] # Remove extra \n

class ServicesCommand(Command):
    def __init__(self, arguments, services_manager, config_file):
        super().__init__(arguments, services_manager)
        self.config_file = config_file

    def execute(self):
        """ Lists the services at the config file.

        Returns:
            Config file services (str).
        """
        output = ""
        with open(self.config_file, "r") as conf:
            output += "Configured services:\n"
            for service_info in conf.readlines():
                output += "\n"
                elements = service_info.split("|")
                output += "Service ID: " + elements[0] + "\n"
                output += "Service Name: " + elements[1] + "\n"
                output += "URL: " + elements[2]

        return output

class BackupCommand(Command):
    def execute(self):
        """ Saves all the polls made to a given file."""

        format_chosen = self.format_output_file()

        if format_chosen == "txt":
            return self.save_as_txt()

        elif format_chosen == "csv":
            return self.save_as_csv()

        else:
            return self.save_as_binary()

    def save_as_txt(self):
        with open(self.output_filename(), "w") as out:
            for service in self.services_manager.get_services():
                for saved_poll in service.get_saved_polls():
                    out.write(saved_poll + "\n")
        return "Successfully wrote to " + self.output_filename() + " as a txt file."

    def save_as_csv(self):
        import csv
        with open(self.output_filename(), "w", newline='') as out:
            fieldnames = ["service_id", "date", "time", "status"]
            writer = csv.writer(out, delimiter=",")
            writer.writerow(fieldnames)
            for service in self.services_manager.get_services():
                for saved_poll in service.get_saved_polls():
                    split = saved_poll.split() # Split poll result at whitespace
                    info = split[1:4] # First character is a "-", ignore

                    # Last part of string should be one value but the sentence
                    # can be several words: join them into one string
                    status = ' '.join([c for c in split[4:]])
                    info.append(status)
                    writer.writerow(info)

            return "Successfully wrote to " + self.output_filename() + " as csv."

    def save_as_binary(self):
        with open(self.output_filename(), "wb") as out:
            pickle.dump(self.services_manager, out)
            return "Successfully wrote to " + self.output_filename() + " as binary file."

class HistoryCommand(Command):
    def execute(self):
        """ Lists all saved polls.

        Returns:
            Each poll logged (str).
        """
        output = ""
        for saved_poll in self.services_manager.get_saved_polls():
            output += saved_poll + "\n"

        return output[:-1] # Remove extra \n

class FetchCommand(Command):
    def execute(self):
        """ Polls services nonstop, with an optional refresh interval. Default is
        5 seconds.
        """
        while True:
            for service in self.services_manager.get_services():
                if service.identifier not in self.excluded:
                    print(service.poll())

            # After all services are polled, log that.
            self.services_manager.save()
            sleep(int(self.get_refresh_time()))

class RestoreCommand(Command):
    def execute(self):
        """ Restores the input file into storage. If it should be merged, simply
        append to storage; otherwise, replace the storage.

        Returns:
            Informative message (str).
        """
        with open(self.output_filename(), "rb") as storage:
            if self.get_merge():
                # Load the input storage into memory, to get the polls saved
                temp_manager = pickle.load(storage)
                polls_to_add = temp_manager.get_saved_polls()
                self.services_manager.add_polls(polls_to_add)
                self.services_manager.save()
                return "Successfully merged contents of file " + \
                    self.output_filename() + " to storage"

            else:
                # Simply replace the storage with the input.
                self.services_manager = pickle.load(storage)
                self.services_manager.save()
                return "Succesfully set storage to contents of file " + \
                    self.output_filename()
