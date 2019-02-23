"""
Service Monitor.

Usage:
    service-monitor poll [--exclude=<service>...|--only=<service>...]
    service-monitor fetch [--refresh=<refresh_time>] [--exclude=<service>...|--only=<service>...]
    service-monitor history [--only=<service>]
    service-monitor backup [--format=<filetype>]
    service-monitor restore [--merge=<merge>]
    service-monitor services
    service-monitor help
    service-monitor status

Options:
    --exclude=<service>  Excludes services from display.
    --only=<service>     Only shows info of the specified service.
    --format=<filetype>  Format of the output file for backup (Supported: txt, csv)
    --merge=<merge>      True or False. Merges the content of the input file instead of replacing it.
"""
from docopt import docopt
import abc
import datetime
import requests
from bs4 import BeautifulSoup

class ServiceManager(object):
    """Stores all the created services."""
    def __init__(self):
        self.existing_services = []

    def create(self, service_str):
        values = service_str.split("|")
        if values[0] == "bitbucket":
            new_service = BitBucketService(identifier = values[0],
                name = values[1], link = values[2])
            self.existing_services.append(new_service)

        elif values[0] == "gitlab":
            new_service = GitLabService(identifier = values[0],
                name = values[1], link = values[2])
            self.existing_services.append(new_service)


class Service(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, identifier, name, link):
        self.identifier = identifier
        self.name = name
        self.link = link

    def get_content(self, url):
       """Attempts to get the content at `url`."""
       try:
           response = requests.get(url)
           content_type = response.headers["content-type"].lower()
           if "html" in content_type and response.status_code == 200:
               return response.content

       except requests.exceptions.RequestException:
           print("Error reading url: ", url)
           return False

       except requests.exceptions.MissingSchema:
           print("Missing schema (invalid url): ", url)
           return False

    @abc.abstractmethod
    def poll(self):
        """Polls the service page."""
        return

class BitBucketService(Service):
    def poll(self):
        status_string = "BitBucket: " + datetime.datetime.now().strftime("%Y-%m-%d, %H:%m:%S")
        content = self.get_content(self.link)
        if content:
            doc = BeautifulSoup(content, "html.parser")

            all_system_status = doc.find("span", class_="status font-large")
            status_string += " [" + all_system_status.getText().strip() + "]" + "\n"

            status_elements = doc.find_all("div", class_="component-container border-color")
            for div in status_elements:
                spans = div.findChildren("span")
                for span in spans:
                    if span.has_attr("class") and span["class"][0] == "name":
                        name_of_subservice = span.getText().strip()
                    if span.has_attr("class") and span["class"][0] == "component-status":
                        status = span.getText().strip()

                status_string += "* " + name_of_subservice + ": " + status + "\n"

        return status_string

class GitLabService(Service):
    def poll(self):
        status_string = "Gitlab: " + datetime.datetime.now().strftime("%Y-%m-%d, %H:%m:%S")
        content = self.get_content(self.link)
        if content:
            doc = BeautifulSoup(content, "html.parser")

            all_system_status = doc.find("div",class_="col-md-8 col-sm-6 col-xs-12")
            status_string += " [" + all_system_status.getText().strip() + "]\n"

            # First div of the status column
            first_status_div = doc.find("div", class_="component component_first status_td")
            first_name = first_status_div.find("p", class_="component_name").getText().strip()
            first_status = first_status_div.find("p", class_="pull-right component-status").getText().strip()
            status_string += "* " + first_name + ": " + first_status + "\n"

            # Middle divs of the status column
            for mid_div in doc.find_all("div", class_="component component_middle status_td"):
                mid_name = mid_div.find("p", class_="component_name").getText().strip()
                mid_status = mid_div.find("p", class_="pull-right component-status").getText().strip()
                status_string += "* " + mid_name + ": " + mid_status + "\n"

            # Last div of the status column
            last_div = doc.find("div", class_="component component_last status_td")
            last_name = last_div.find("p", class_="component_name").getText().strip()
            last_status = last_div.find("p", class_="pull-right component-status").getText().strip()
            status_string += "* " + last_name + ": " + last_status + "\n"

        return status_string


class Command(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, arguments, services_manager):
        self.arguments = arguments
        self.services_manager = services_manager
        self.excluded = self.excluded_services()

    def excluded_services(self):
        excluded = self.arguments.get("--exclude", [])
        return excluded

    @abc.abstractmethod
    def execute(self):
        """Executes the command."""
        return

class PollCommand(Command):
    def execute(self):
        for service in self.services_manager.existing_services:
            if service.identifier not in self.excluded:
                print(service.poll())
        return

def services_from_file(path):
    with open (path, "r") as services_config:
        all_services = services_config.readlines()
        return all_services

if __name__ == "__main__":
    arguments=docopt(__doc__, version='Service Monitor 1.0')

    used_args = {option:arguments[option] for option in arguments \
        if arguments[option] is not None and \
        not isinstance(arguments[option], bool) and \
        arguments[option] != []}

    services_manager = ServiceManager()
    for service in services_from_file("config.txt"):
        services_manager.create(service.replace("\n", ""))

    if arguments["poll"]:
        poll = PollCommand(used_args, services_manager)
        poll.execute()

    elif arguments["fetch"]:
        fetch = FetchCommand(used_args)
        fetch.execute()

    elif arguments["history"]:
        history = HistoryCommand(used_args)
        history.execute()

    elif arguments["backup"]:
        backup = BackupCommand(used_args)
        backup.execute()

    elif arguments["restore"]:
        restore = RestoreCommand(used_args)
        restore.execute()

    elif arguments["services"]:
        services = ServicesCommand(used_args)
        services.execute()

    elif arguments["help"]:
        help_command = HelpCommand(used_args)
        help_command.execute()

    elif arguments["status"]:
        status = StatusCommand(used_args)
        status.execute()

