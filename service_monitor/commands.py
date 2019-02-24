"""
Command classes for usage with service-monitor.py.
"""

import abc
from time import sleep
import pickle

class Command(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, arguments, services_manager):
        self.arguments = arguments
        self.services_manager = services_manager
        self.excluded = self.excluded_services()

    def get_refresh_time(self):
        return self.arguments.get("--refresh", None)

    def output_filename(self):
        return self.arguments.get("--filename", None)

    def format_output_file(self):
        return self.arguments.get("--format", None)

    def excluded_services(self):
        if self.arguments.get("--only") is not None:
            supported = ["bitbucket", "gitlab"]
            wanted = self.arguments.get("--only")
            excluded = [x for x in supported if x not in wanted]

        else:
            excluded = self.arguments.get("--exclude", [])

        return excluded

    def get_merge(self):
        return self.arguments.get("--merge", False)

    @abc.abstractmethod
    def execute(self):
        """Executes the command."""
        print("Command not implemented.")
        return

class PollCommand(Command):
    def execute(self):
        output = ""
        for service in self.services_manager.existing_services:
            if service.identifier not in self.excluded:
                output += service.poll() + "\n"

        return output[:-2]

class ServicesCommand(Command):

    def __init__(self, arguments, services_manager, config_file):
        super().__init__(arguments, services_manager)
        self.config_file = config_file

    def execute(self):
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
                    split = saved_poll.split()
                    info = (split[1:4])
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
        output = ""
        for saved_poll in self.services_manager.get_saved_polls():
            output += saved_poll + "\n"

        return output[:-1]

class FetchCommand(Command):
    def execute(self):
        while True:
            for service in self.services_manager.get_services():
                if service.identifier not in self.excluded:
                    print(service.poll())

            self.services_manager.save()
            sleep(int(self.get_refresh_time()))

class RestoreCommand(Command):
    def execute(self):
        with open(self.output_filename(), "rb") as storage:
            if self.get_merge():
                temp_manager = pickle.load(storage)
                polls_to_add = temp_manager.get_saved_polls()
                self.services_manager.get_saved_polls().extend(polls_to_add)
                self.services_manager.save()
                return "Successfully merged contents of file " + self.output_filename() + " to storage"

            else:
                self.services_manager = pickle.load(storage)
                self.services_manager.save()
                return "Succesfully set storage to contents of file " + self.output_filename()







