import sys
from importlib.metadata import version


def test_python_version():
    assert sys.version_info[:2] == (3, 11)


def test_required_packages():
    expected = {
        "ibm-watsonx-orchestrate": "2.13.0",
        "ibm-watsonx-ai": "1.6.0",
        "pydantic": "2.13.4",
        "pytest": "9.1.1",
        "python-dotenv": "1.2.2",
    }

    for package, expected_version in expected.items():
        assert version(package) == expected_version
