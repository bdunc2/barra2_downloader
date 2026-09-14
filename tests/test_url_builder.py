import unittest
from barra2_downloader import url_builder

class TestCoordinateBuilder(unittest.TestCase):
    def test_bbox_coordinate_builder(self):
        b = url_builder.BBox(-150, -152, 27, 26)
        self.assertEqual(
            url_builder._coordinate_builder(bbox=b),
            {"east": -150, "west": -152, "north": 27, "south": 26}
        )
    def test_latlon_coordinate_builder(self):
        self.assertEqual(
            url_builder._coordinate_builder(latitude=-152, longitude=27),
            {"latitude":-152, "longitude":27}
        )
    def test_blank_coordinate_builder(self):
        self.assertEqual(
            url_builder._coordinate_builder(),
            {}
        )

if __name__ == "__main__":
    unittest.main()