import json
import urllib.request
import urllib.error

from urllib.parse import quote
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion


PYTHON_VERSION = Version("3.11")
REQUIREMENTS_FILE = "requirements.txt"


def read_dependencies(filename):
    with open(filename, "r", encoding="utf-8") as file:
        dependencies = []

        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            name, separator, version = line.partition("==")

            if not separator or not name.strip() or not version.strip():
                continue

            dependencies.append((name.strip(), version.strip()))

    return dependencies


def get_pypi_release(package, version):

    package = quote(package, safe="")
    version = quote(version, safe="")

    url = f"https://pypi.org/pypi/{package}/{version}/json"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "dependency-checker/1.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise

    except urllib.error.URLError as error:
        print(f"Network error: {error}")
        return None


def check_python_compatibility(requires_python):

    if not requires_python:
        return True

    specifier = SpecifierSet(requires_python)

    return specifier.contains(PYTHON_VERSION)


def get_minimum_requirement(requires_python):

    if not requires_python:
        return None

    specifier = SpecifierSet(requires_python)

    candidates = []

    for item in specifier:
        if item.operator in (">=", ">", "=="):
            try:
                version = Version(item.version)

                candidates.append(
                    (version, item.operator, item.version)
                )

            except InvalidVersion:
                continue

    if not candidates:
        return None

    return max(candidates, key=lambda item: item[0])


def main():
    dependencies = read_dependencies(REQUIREMENTS_FILE)

    not_found = 0
    incompatible = 0

    highest_requirement = None

    for package, version in dependencies:

        release = get_pypi_release(package, version)

        if release is None:
            not_found += 1
            continue

        requires_python = release["info"].get("requires_python")

        if requires_python:
            compatible = check_python_compatibility(requires_python)

            if not compatible:
                incompatible += 1

            minimum = get_minimum_requirement(requires_python)

            if minimum is not None:
                if (
                    highest_requirement is None
                    or minimum[0] > highest_requirement[0]
                ):
                    highest_requirement = (
                        minimum[0],
                        package,
                        version,
                        minimum[1],
                        minimum[2]
                    )

    print(f"Dependencies checked: {len(dependencies)}")
    print(f"Not found on PyPI: {not_found}")
    print(f"Incompatible with Python 3.11: {incompatible}")

    if highest_requirement:
        _, package, version, operator, minimum = highest_requirement

        print(
            f"Highest requirement: "
            f"{package}=={version} ({operator}{minimum})"
        )
    else:
        print("Highest requirement: None")


if __name__ == "__main__":
    main()