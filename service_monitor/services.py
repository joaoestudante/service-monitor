"""
Services classes, for usage with service_monitor.py
"""
import pickle
import abc
import datetime
import requests
from bs4 import BeautifulSoup
import custom_exceptions


def services_from_file(path):
    with open(path, "r") as services_config:
        all_services = services_config.readlines()
        return all_services


class ServiceManager(object):
    """Stores all the created services."""

    def __init__(self, path):
        self.existing_services = []
        self.storage_location = path
        self.stored_polls = []

    def create(self, service_str):
        if service_str[0] == "bitbucket":
            new_service = BitBucketService(
                identifier=service_str[0],
                name=service_str[1],
                link=service_str[2],
                manager=self,
            )
            self.existing_services.append(new_service)

        elif service_str[0] == "gitlab":
            new_service = GitLabService(
                identifier=service_str[0],
                name=service_str[1],
                link=service_str[2],
                manager=self,
            )
            self.existing_services.append(new_service)

        else:
            raise custom_exceptions.UnrecognizedServiceException(
                "[ERROR] "
                'Service with identifier "' + service_str[0] + '" unrecognized. '
                "Supported services are: " + self.existing_services_lst)
            )

    def existing_services_lst(self):
        """Returns existing services as list."""
        services = []
        for service in self.existing_services:
            services.append(service.identifier)

        return services

    def get_services(self):
        return self.existing_services

    def get_saved_polls(self):
        return self.stored_polls

    def add_polls(self, polls):
        self.get_saved_polls().extend(polls)

    def update_services(self, config):
        """Given a config file, updates the services stored. Will delete any
        service no longer in the config file, and update any
        information (like name, link, etc)
        """
        services = services_from_file(config)
        config_services_names = []
        line_n = 1

        for service in services:
            service_str_clean = service.replace("\n", "")
            service_splitted = service_str_clean.split("|")

            if len(service_splitted) != 3: # Config line should only have 3 elements
                raise custom_exceptions.BadConfigException(
                    "[ERROR] Line " + str(line_n) + " of config file "
                    "does not have required format: identifier|name|url"
                )

            config_services_names.append(service_splitted[0])

            if service_splitted[0] not in self.existing_services_lst():
                self.create(service_splitted)
            elif service_splitted[0] in self.existing_services_lst():
                for service in self.existing_services:
                    if service.identifier == service_splitted[0]:
                        service.name = service_splitted[1]
                        service.link = service_splitted[2]
            line_n += 1

        for service in self.existing_services:
            if service.identifier not in config_services_names:
                self.existing_services.remove(service)

    def add_to_saved_polls(self, line):
        self.stored_polls.append(line)

    def save(self):
        with open(self.storage_location, "wb") as sl:
            pickle.dump(self, sl)


class Service(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, identifier, name, link, manager):
        self.identifier = identifier
        self.name = name
        self.link = link
        self.manager = manager

    def get_content(self, url):
        """Attempts to get the content at `url`."""
        try:
            response = requests.get(url)
            content_type = response.headers["content-type"].lower()
            if "html" in content_type and response.status_code == 200:
                return response.content

        except requests.exceptions.ConnectionError:
            raise custom_exceptions.ConnectionException(
                "[ERROR] Couldn't connect to: " + url + ". Check if your internet "
                "connection is working."
            )

        except requests.exceptions.Timeout:
            raise custom_exceptions.TimoutException(
                "[ERROR] Connection timed out when connecting to " + url
            )

        except requests.exceptions.URLRequired:
            raise custom_exceptions.InvalidUrlException(
                "[ERROR] This url is not valid: " + url
            )

        except requests.exceptions.MissingSchema:
            raise custom_exceptions.InvalidUrlException(
                "[ERROR] Missing schema (did your forget http or https?): ", url
            )

    def save_poll(self, poll_result):
        """ Saves the poll_result in the manager."""
        self.stored_polls.append(poll_result)

    def get_saved_polls(self):
        """Gets all the saved polls in the manager."""
        return self.manager.get_saved_polls()

    def get_basic_status_line(self):
        """Builds a common status line for every service."""
        status_string = "- {} {}".format(self.name, str(datetime.datetime.now())[:-7])
        return status_string

    @abc.abstractmethod
    def poll(self):
        """Polls the service page."""
        return


class BitBucketService(Service):
    def poll(self):
        try:
            content = self.get_content(self.link)
            status_string = self.get_basic_status_line()

            doc = BeautifulSoup(content, "html.parser")
            all_system_status = doc.find("span", class_="status font-large")
            status_string += " [" + all_system_status.getText().strip() + "]"

        except custom_exceptions.CustomRequestsException as e:
            status_string = str(e)

        self.manager.add_to_saved_polls(status_string)
        return status_string


class GitLabService(Service):
    def poll(self):
        try:
            content = self.get_content(self.link)
            status_string = self.get_basic_status_line()

            doc = BeautifulSoup(content, "html.parser")
            all_system_status = doc.find("div", class_="col-md-8 col-sm-6 col-xs-12")
            status_string += " [" + all_system_status.getText().strip() + "]"

        except custom_exceptions.CustomRequestsException as e:
            status_string = str(e)

        self.manager.add_to_saved_polls(status_string)
        return status_string
