import os
from unittest import TestCase

from bidsmanager.base.image import Image, FunctionalImage
from bidsmanager.read.image_reader import read_image_from_bids_path
from bidsmanager.write.dataset_writer import write_json


def touch(tmp_file):
    with open(tmp_file, "w") as opened_file:
        print("creating: " + tmp_file)
        return opened_file


class TestImage(TestCase):
    def test_change_acquisition(self):
        image = Image(modality="T1w", acquisition="contrast")
        basename = image.get_basename()
        image.set_acquisition("postcontrast")
        self.assertEqual(basename.replace("contrast", "postcontrast"), image.get_basename())

    def test_change_task_name(self):
        image = FunctionalImage(modality="bold", task_name="prediction", run_number=3)
        basename = image.get_basename()
        image.set_task_name("weatherprediction")
        self.assertEqual(basename.replace("prediction", "weatherprediction"), image.get_basename())

    def test_write_changed_acquisition(self):
        tmp_file = "run-05_FLAIR.nii.gz"
        self.touch(tmp_file)
        new_tmp_file = "acq-contrast_" + tmp_file
        self.assertTrue(os.path.exists(tmp_file))
        try:
            image = read_image_from_bids_path(tmp_file)
            image.set_acquisition("contrast")
            image.update(move=True)
            self.assertFalse(os.path.exists(tmp_file))
            self.assertTrue(os.path.exists(new_tmp_file))
            os.remove(new_tmp_file)
        except AssertionError as error:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            if os.path.exists(new_tmp_file):
                os.remove(new_tmp_file)
            raise error

    def test_write_metadata(self):
        tmp_file = "run-05_FLAIR.nii.gz"
        self.touch(tmp_file)
        tmp_json = "run-05_FLAIR.json"
        self._filenames_to_delete.add(tmp_json)
        json_data = {"the_answer": 42}
        write_json(json_data, tmp_json)
        image = read_image_from_bids_path(tmp_file)
        self.assertEqual(image.get_metadata(), json_data)

        image._run_number = 6
        image.update(move=False)
        self._filenames_to_delete.add(image.get_path())
        self._filenames_to_delete.add(image.sidecar_path)
        self.assertEqual(image.get_metadata(), json_data)
        self.assertTrue(os.path.exists(image.sidecar_path))

        prev_sidecar_path = image.sidecar_path
        image._run_number = 7
        image.update(move=True)
        self._filenames_to_delete.add(image.get_path())
        self._filenames_to_delete.add(image.sidecar_path)
        self.assertEqual(image.get_metadata(), json_data)
        self.assertFalse(os.path.exists(prev_sidecar_path))

    def test_add_sidecar_metadata(self):
        image_filename = "sub-9000_ses-gigawatts_angio.nii.gz"
        self.touch(image_filename)

    def touch(self, filename):
        touch(filename)
        self._filenames_to_delete.add(filename)

    def setUp(self):
        self._filenames_to_delete = set()

    def tearDown(self):
        for filename in self._filenames_to_delete:
            if os.path.exists(filename):
                os.remove(filename)
