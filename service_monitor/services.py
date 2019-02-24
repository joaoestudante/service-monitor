"""
Services classes, for usage with service-monitor.py
"""
import pickle
import abc
import datetime
import requests
from bs4 import BeautifulSoup

def services_from_file(path):
    with open (path, "r") as services_config:
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
            new_service = BitBucketService(identifier = service_str[0],
                name = service_str[1], link = service_str[2], manager=self)
            self.existing_services.append(new_service)

        elif service_str[0] == "gitlab":
            new_service = GitLabService(identifier = service_str[0],
                name = service_str[1], link = service_str[2], manager=self)
            self.existing_services.append(new_service)

    def existing_services_str(self):
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
        for service in services_from_file(config):
            service_str_clean = service.replace("\n", "")
            service_splitted = service_str_clean.split("|")
            if service_splitted[0] not in self.existing_services_str():
                self.create(service_splitted)

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

       except requests.exceptions.RequestException:
           print("Error reading url: ", url)
           return False

       except requests.exceptions.MissingSchema:
           print("Missing schema (invalid url): ", url)
           return False

    def save_poll(self, poll_result):
        self.stored_polls.append(poll_result)

    def get_saved_polls(self):
        return self.manager.get_saved_polls()

    @abc.abstractmethod
    def poll(self):
        """Polls the service page."""
        return

class BitBucketService(Service):
    def poll(self):
        status_string = "- BitBucket " + str(datetime.datetime.now())[:-7]
        content = self.get_content(self.link)
        if content:
            doc = BeautifulSoup(content, "html.parser")

            all_system_status = doc.find("span", class_="status font-large")
            #status_string += " [" + all_system_status.getText().strip() + "]" + "\n  "
            status_string += " [" + all_system_status.getText().strip() + "]"

            """
            Initially, polling returned all this info about sub-services,
            which was not that useful for a csv style logging, with a 1-liner
            with enough info. It is still kept here in case it is necessary in
            the future for some cases (or new commands).

            status_elements = doc.find_all("div", class_="component-container border-color")
            for div in status_elements:
                spans = div.findChildren("span")
                for span in spans:
                    if span.has_attr("class") and span["class"][0] == "name":
                        name_of_subservice = span.getText().strip()
                    if span.has_attr("class") and span["class"][0] == "component-status":
                        status = span.getText().strip()

                status_string += "* " + name_of_subservice + ": " + status + "\n  "
            """

        self.manager.add_to_saved_polls(status_string)
        return status_string

class GitLabService(Service):
    def poll(self):
        status_string = "- Gitlab    " + str(datetime.datetime.now())[:-7]
        content = self.get_content(self.link)
        if content:
            doc = BeautifulSoup(content, "html.parser")

            all_system_status = doc.find("div",class_="col-md-8 col-sm-6 col-xs-12")
            status_string += " [" + all_system_status.getText().strip() + "]"

            """
            Initially, polling returned all this info about sub-services,
            which was not that useful for a csv style logging, with a 1-liner
            with enough info. It is still kept here in case it is necessary in
            the future for some cases (or new commands).

            # First div of the status column
            first_status_div = doc.find("div", class_="component component_first status_td")
            first_name = first_status_div.find("p", class_="component_name").getText().strip()
            first_status = first_status_div.find("p", class_="pull-right component-status").getText().strip()
            status_string += "* " + first_name + ": " + first_status + "\n  "

            # Middle divs of the status column
            for mid_div in doc.find_all("div", class_="component component_middle status_td"):
                mid_name = mid_div.find("p", class_="component_name").getText().strip()
                mid_status = mid_div.find("p", class_="pull-right component-status").getText().strip()
                status_string += "* " + mid_name + ": " + mid_status + "\n  "

            # Last div of the status column
            last_div = doc.find("div", class_="component component_last status_td")
            last_name = last_div.find("p", class_="component_name").getText().strip()
            last_status = last_div.find("p", class_="pull-right component-status").getText().strip()
            status_string += "* " + last_name + ": " + last_status + "\n"
            """

        self.manager.add_to_saved_polls(status_string)
        return status_string
