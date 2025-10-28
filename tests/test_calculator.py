import importlib.util
import pathlib
import subprocess
import sys
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "test.py"
spec = importlib.util.spec_from_file_location("calculator_script", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
calculate = module.calculate


class CalculateTests(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculate(2, "+", 3), 5)

    def test_subtraction(self):
        self.assertEqual(calculate(10, "-", 4), 6)

    def test_multiplication(self):
        self.assertEqual(calculate(3, "*", 5), 15)

    def test_division(self):
        self.assertEqual(calculate(20, "/", 4), 5)

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            calculate(2, "%", 2)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculate(5, "/", 0)


class CLITests(unittest.TestCase):
    def test_cli_addition_and_exit(self):
        process = subprocess.Popen(
            [sys.executable, str(MODULE_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = process.communicate("2 + 2\nesci\n", timeout=5)
        finally:
            if process.poll() is None:
                process.kill()

        self.assertEqual(process.returncode, 0)
        self.assertEqual(stderr, "")
        self.assertIn("4", stdout)


if __name__ == "__main__":
    unittest.main()
