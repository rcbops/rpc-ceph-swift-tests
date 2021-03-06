import json

from snappy.swift_constants import Constants
from snappy.swift_fixtures import ObjectStorageFixture

CONTENT_TYPE_TEXT = "text/plain; charset=UTF-8"
CONTAINER_NAME = 'list_delimiter_test_container'


class DelimiterTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(DelimiterTest, cls).setUpClass()

        cls.container_name = CONTAINER_NAME
        cls.client.create_container(cls.container_name)

        cls.object_data = Constants.VALID_OBJECT_DATA
        cls.content_length = str(len(cls.object_data))
        cls.headers = {"Content-Length": cls.content_length,
                       "Content-Type": CONTENT_TYPE_TEXT}

    @classmethod
    def tearDownClass(cls):
        super(DelimiterTest, cls).setUpClass()
        cls.behaviors.force_delete_containers([cls.container_name])

    def test_delimeter(self):
        """
        Scenario: create three objs and perform a container list using
        the 'delimiter' query string parameter

        Expected Results: return all of the top level psuedo directories
        and objects in a container. if the object name is 'foo/bar'
        then the top level psuedo dir name would be 'foo/'
        """
        obj_names = ["asteroid_photo",
                     "music_collection0/grok_n_roll/grok_against_the_machine",
                     "music_to_sling_code_to",
                     "music_collection2/maximum_drok",
                     "transparent_aluminum_doc"]

        for obj_name in obj_names:
            self.client.create_object(
                self.container_name,
                obj_name,
                headers=self.headers,
                data=self.object_data)

        params = {"delimiter": "/", "format": "json"}
        response = self.client.list_objects(self.container_name, params=params)

        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        parsed_content = []
        for member in content:
            if "subdir" in member.keys():
                parsed_content.append(member["subdir"])
            elif "name" in member.keys():
                parsed_content.append(member["name"])
            else:
                continue

        expected = len(obj_names)
        received = len(parsed_content)

        self.assertEqual(
            expected,
            received,
            msg="expected {0} objects in the response body, received"
                " {1}".format(expected, received))

        for obj_name in obj_names:
            tokens = obj_name.split('/')
            if len(tokens) > 1:
                # top level psuedo dir
                current_name = "{0}/".format(tokens[0])
            else:
                # object name
                current_name = tokens[0]

            self.assertIn(current_name, parsed_content)
