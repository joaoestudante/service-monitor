import unittest
import sys
sys.path.append("../service_monitor")

import os
import service_monitor
import commands
import services
import custom_exceptions

class TestConfigs(unittest.TestCase):

    def test_one_service_normal(self):
        services_manager = services.ServiceManager("resources/one_service_normal.storage")
        result = services_manager.update_services("resources/config_one_normal.txt")
        self.assertIsNone(result)

    def test_two_services_normal(self):
        services_manager = services.ServiceManager("resources/two_services_normal.storage")
        result = services_manager.update_services("resources/config_two_normal.txt")
        self.assertIsNone(result)

    def test_one_unknown_service(self):
        services_manager = services.ServiceManager("resources/unknown_one_service.storage")
        try:
            result = services_manager.update_services("resources/config_one_unknown.txt")

        except custom_exceptions.UnrecognizedServiceException as e:
            self.assertEqual(str(e), "[ERROR] Service with identifier \"slack\" unrecognized. Supported services are: ['bitbucket', 'gitlab']")

    def test_two_unknown_service(self):
        services_manager = services.ServiceManager("resources/unknown_one_service.storage")
        try:
            result = services_manager.update_services("resources/config_two_unknown.txt")
        except custom_exceptions.UnrecognizedServiceException as e:
            self.assertEqual(str(e), "[ERROR] Service with identifier \"slack\" unrecognized. Supported services are: ['bitbucket', 'gitlab']")

    def test_bad_separators_line_1(self):
        services_manager = services.ServiceManager("resources/bad_separators_1.storage")
        try:
            result = services_manager.update_services("resources/config_bad_separators_line_1.txt")
        except custom_exceptions.BadConfigException as e:
            self.assertEqual(str(e), "[ERROR] Line 1 of config file does not have required format: identifier|name|url")

    def test_bad_separators_line_2(self):
        services_manager = services.ServiceManager("resources/bad_separators_2.storage")
        try:
            result = services_manager.update_services("resources/config_bad_separators_line_2.txt")
        except custom_exceptions.BadConfigException as e:
            self.assertEqual(str(e), "[ERROR] Line 2 of config file does not have required format: identifier|name|url")


