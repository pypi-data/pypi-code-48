""" Tests for ComicInfo Tags """
import tempfile
from unittest import TestCase, main

from darkseid.comicinfoxml import ComicInfoXml
from darkseid.genericmetadata import GenericMetadata


class TestComicInfoXml(TestCase):
    """ Collection of tests for ComicInfo tags """

    def setUp(self):
        self.meta_data = GenericMetadata()
        self.meta_data.series = "Aquaman"
        self.meta_data.issue = "1"
        self.meta_data.year = "1993"
        self.meta_data.day = "15"
        self.meta_data.add_credit("Peter David", "Writer", primary=True)
        self.meta_data.add_credit("Martin Egeland", "Penciller")
        self.meta_data.add_credit("Martin Egeland", "Cover")
        self.meta_data.add_credit("Kevin Dooley", "Editor")
        self.meta_data.add_credit("Howard Shum", "Inker")
        self.meta_data.add_credit("Tom McCraw", "Colorist")
        self.meta_data.add_credit("Dan Nakrosis", "Letterer")

    def test_metadata_from_xml(self):
        """ Simple test of creating the ComicInfo """
        res = ComicInfoXml().string_from_metadata(self.meta_data)
        # TODO: add more asserts to verify data.
        self.assertIsNotNone(res)

    def test_meta_write_to_file(self):
        """ Test of writing the metadata to a file """
        tmp_file = tempfile.NamedTemporaryFile(suffix=".xml")
        ComicInfoXml().write_to_external_file(tmp_file.name, self.meta_data)
        # Read the contents of the file just written.
        # TODO: Verify the data.
        res = open(tmp_file.name).read()
        tmp_file.close()
        self.assertIsNotNone(res)

    def test_read_from_file(self):
        """ Test to read in the data from a file """
        tmp_file = tempfile.NamedTemporaryFile(suffix=".xml")
        # Write metadata to file
        ComicInfoXml().write_to_external_file(tmp_file.name, self.meta_data)
        # Read the metadat from the file
        new_md = ComicInfoXml().read_from_external_file(tmp_file.name)
        tmp_file.close()

        self.assertIsNotNone(new_md)
        self.assertEqual(new_md.series, self.meta_data.series)
        self.assertEqual(new_md.issue, self.meta_data.issue)
        self.assertEqual(new_md.year, self.meta_data.year)
        self.assertEqual(new_md.month, self.meta_data.month)
        self.assertEqual(new_md.day, self.meta_data.day)


if __name__ == "__main__":
    main()
