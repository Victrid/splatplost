import unittest
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

from splatplost.generate_route import generate_route_file
from .pseudobackend import PseudoS2Wrapper, PseudoS3Wrapper


class TestDrawing(unittest.TestCase):
    __test__ = False
    backend = None
    splatoon3 = False

    def test_corner(self):
        backend = self.backend()
        with TemporaryDirectory(prefix="splatplost_test") as temp_dir:
            # generate the order file
            t = np.zeros((120, 320)).astype(np.uint8)
            t[0, 0] = 1
            t[119, 0] = 1
            t[0, 319] = 1
            t[119, 319] = 1
            t = 1 - t
            im = Image.fromarray(t * 255, mode="L").convert("1")
            im.save(f"{temp_dir}/test.png")
            generate_route_file(f"{temp_dir}/test.png", f"{temp_dir}/test.json")
            # plot the order file
            from splatplost.plot import plot
            first_run = False

            def input_mock(_):
                nonlocal first_run
                if first_run:
                    return "\n\n\n\n\n"
                else:
                    first_run = True
                    return "asdf\n\n\n\n\n"

            from unittest.mock import patch

            with patch("builtins.input", input_mock):
                # To test with PseudoS2Wrapper, we need to set the backend to a lambda function, and ignore the arguments
                # noinspection PyTypeChecker
                plot(order_file=f"{temp_dir}/test.json", backend=lambda *args, **kwargs: backend,
                     splatoon3=self.splatoon3
                     )
            result = backend.get_result()
        # check the result array matches the input array
        assert np.array_equal(result, t)

    def test_random(self):
        backend = self.backend()
        with TemporaryDirectory(prefix="splatplost_test") as temp_dir:
            # generate the order file
            t = np.random.randint(0, 2, (120, 320)).astype(np.uint8)
            t = 1 - t
            im = Image.fromarray(t * 255, mode="L").convert("1")
            im.save(f"{temp_dir}/test.png")
            generate_route_file(f"{temp_dir}/test.png", f"{temp_dir}/test.json")
            # plot the order file
            from splatplost.plot import plot
            first_run = False

            def input_mock(_):
                nonlocal first_run
                if first_run:
                    return "\n\n\n\n\n"
                else:
                    first_run = True
                    return "asdf\n\n\n\n\n"

            from unittest.mock import patch

            with patch("builtins.input", input_mock):
                # noinspection PyTypeChecker
                plot(order_file=f"{temp_dir}/test.json", backend=lambda *args, **kwargs: backend,
                     splatoon3=self.splatoon3
                     )
            result = backend.get_result()
        # check the result array matches the input array
        assert np.array_equal(result, t)


class TestSplatoon2Drawing(TestDrawing):
    __test__ = True
    backend = PseudoS2Wrapper
    splatoon3 = False


class TestSplatoon3Drawing(TestDrawing):
    __test__ = True
    backend = PseudoS3Wrapper
    splatoon3 = True
