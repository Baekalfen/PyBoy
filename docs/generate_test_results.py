"""Generate the Markdown test-results report and copy its image baselines."""

import json
import re
import shutil
from xml.etree import ElementTree
from pathlib import Path
from urllib.parse import quote


DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "tests" / "test_results"
OUTPUT = DOCS_DIR / "wiki" / "test-results.md"
IMAGE_OUTPUT = DOCS_DIR / "wiki" / "assets" / "test-results"
JUNIT_XML = RESULTS_DIR / "pytest.xml"
EXCLUDED_IMAGE_SUITES = {"Boot ROM modes", "Pokemon Blue", "Sound swoosh", "which", "whichboot"}
GITHUB_RESULTS_BASE = "https://github.com/Baekalfen/PyBoy/blob/master/"
GITHUB_RESULTS_TREE_BASE = "https://github.com/Baekalfen/PyBoy/tree/master/"
RESULT_COLORS = {"Passed": "#1a7f37", "Failed": "#cf222e"}


def github_result_url(path):
    relative = path.relative_to(PROJECT_ROOT).as_posix()
    return GITHUB_RESULTS_BASE + quote(relative, safe="/")


def github_results_directory_url(path):
    relative = path.relative_to(PROJECT_ROOT).as_posix()
    return GITHUB_RESULTS_TREE_BASE + quote(relative, safe="/")


def load_junit_statuses(path):
    if not path.exists():
        return {}

    statuses = {}
    root = ElementTree.parse(path).getroot()
    for testcase in root.iter("testcase"):
        if testcase.find("failure") is not None or testcase.find("error") is not None:
            status = "Failed"
        elif testcase.find("skipped") is not None:
            skipped = testcase.find("skipped")
            status = "Failed" if skipped.attrib.get("type") == "pytest.xfail" else "Skipped"
        else:
            status = "Passed"
        key = (testcase.attrib.get("classname", ""), testcase.attrib.get("name", ""))
        statuses[key] = status
    return statuses


def junit_status(statuses, classname, name):
    return statuses.get((classname, name), "Not run")


def junit_status_prefix(statuses, classname, prefix):
    matches = [
        status for (case_class, name), status in statuses.items() if case_class == classname and name.startswith(prefix)
    ]
    return matches[0] if len(matches) == 1 else "Not run"


def load_json_suite(name, path, statuses, test_name_for):
    data = json.loads(path.read_text())
    results = [(key, test_name_for(statuses, key)) for key in sorted(data)]
    return {"name": name, "results": results, "url": github_result_url(path)}


def blargg_test_status(statuses, case):
    return junit_status_prefix(statuses, "tests.test_blargg", f"test_blarggs[{case.removeprefix('blargg/')}-")


def samesuite_test_status(statuses, case):
    is_cgb = case.endswith(" [CGB]")
    rom = case.removesuffix(" [CGB]")
    mode = "CGB" if is_cgb else "DMG"
    return junit_status(statuses, "tests.test_samesuite", f"test_samesuite[{mode}-{rom}]")


def mooneye_test_status(statuses, case):
    is_cgb = case.endswith(" [CGB]")
    rom = case.removesuffix(" [CGB]")
    if is_cgb:
        mode = "CGB-False"
    elif rom.startswith("emulator-only/"):
        mode = "CGB-True"
    else:
        mode = "DMG-False"
    return junit_status(statuses, "tests.test_mooneye", f"test_mooneye[{mode}-{rom}]")


def rtc3test_status(statuses, case):
    return junit_status(statuses, "tests.test_rtc3test", f"test_rtc3test[{case}]")


def which_test_status(statuses, case):
    return junit_status(statuses, "tests.test_which", f"test_which[{case}]")


def image_suite_name(path):
    relative = path.relative_to(RESULTS_DIR)
    if len(relative.parts) > 1:
        return {
            "GB Tests": "GB Tests",
            "TurtleTest": "TurtleTest",
            "all_modes": "Boot ROM modes",
            "magen": "Magen",
            "mbc30": "MBC30",
            "mooneye": "Mooneye image results",
            "pokemon_blue": "Pokemon Blue",
            "which": "which",
            "whichboot": "whichboot",
        }.get(relative.parts[0], relative.parts[0])
    if "acid2" in path.name:
        return "Acid2"
    if path.name.startswith("sound_swoosh_"):
        return "Sound swoosh"
    return "Image results"


def safe_image_name(path):
    relative = path.relative_to(RESULTS_DIR).as_posix()
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", relative)


def image_test_status(path, suite_name, statuses):
    if suite_name == "GB Tests":
        return junit_status(statuses, "tests.test_shonumi", f"test_shonumi[{path.stem}]")
    if suite_name == "TurtleTest":
        return junit_status(statuses, "tests.test_turtle", f"test_turtletests[{path.stem}]")
    if suite_name == "Magen":
        return junit_status_prefix(statuses, "tests.test_magen", f"test_magen_test[{path.stem}-")
    if suite_name == "MBC30":
        return junit_status(statuses, "tests.test_mbc30", "test_mbc30_test_rom")
    if suite_name == "Mooneye image results":
        case = path.relative_to(RESULTS_DIR / "mooneye").with_suffix("").as_posix()
        is_cgb = case.endswith(" [CGB]")
        rom = case.removesuffix(" [CGB]")
        mode = "CGB-False" if is_cgb else "DMG-False"
        return junit_status(statuses, "tests.test_mooneye", f"test_mooneye[{mode}-{rom}]")
    if suite_name == "Acid2":
        if path.name == "cgb_acid2.gbc.png":
            return junit_status(statuses, "tests.test_acid_cgb", "test_cgb_acid")
        cgb = path.name.startswith("cgb_")
        return junit_status(statuses, "tests.test_acid_dmg", f"test_dmg_acid[{cgb}]")
    return "Not run"


def load_image_suites(statuses):
    suites = {}
    for path in sorted(RESULTS_DIR.rglob("*.png")):
        suite_name = image_suite_name(path)
        if suite_name in EXCLUDED_IMAGE_SUITES:
            continue
        relative = path.relative_to(RESULTS_DIR)
        if suite_name not in suites:
            result_location = path.parent if len(relative.parts) > 1 else RESULTS_DIR
            suites[suite_name] = {
                "results": [],
                "url": github_results_directory_url(result_location),
            }
        target = IMAGE_OUTPUT / safe_image_name(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        suites[suite_name]["results"].append(
            (relative.as_posix(), target.name, image_test_status(path, suite_name, statuses))
        )
    return [{"name": name, "results": suite["results"], "url": suite["url"]} for name, suite in sorted(suites.items())]


def suite_counts(suite):
    passed = sum(result[-1] == "Passed" for result in suite["results"])
    failed = sum(result[-1] == "Failed" for result in suite["results"])
    skipped = sum(result[-1] == "Skipped" for result in suite["results"])
    not_run = sum(result[-1] == "Not run" for result in suite["results"])
    return len(suite["results"]), passed, failed, skipped, not_run


def render_result(text, status):
    color = RESULT_COLORS.get(status)
    if color is None:
        return text
    return f'<span style="color: {color}; font-weight: bold">{text}</span>'


def render_json_suite(suite):
    lines = [
        "<details>",
        f"<summary>{suite['name']} cases</summary>",
        "",
        "| Case | Result |",
        "| --- | --- |",
    ]
    lines.extend(f"| `{case}` | {render_result(status, status)} |" for case, status in suite["results"])
    lines.extend(("</details>", ""))
    return lines


def render_image_suite(suite):
    lines = [f"## {suite['name']}", ""]
    for case, target, status in suite["results"]:
        lines.extend(
            (
                f"### `{case}`",
                "",
                f"**Result:** {render_result(status, status)}",
                "",
                f"```{{image}} assets/test-results/{target}",
                f":alt: Recorded result for {case}",
                ":width: 320px",
                "```",
                "",
            )
        )
    return lines


def main():
    statuses = load_junit_statuses(JUNIT_XML)
    json_suites = [
        load_json_suite("Blargg", RESULTS_DIR / "blargg.json", statuses, blargg_test_status),
        load_json_suite("SameSuite", RESULTS_DIR / "samesuite.json", statuses, samesuite_test_status),
        load_json_suite("Mooneye", RESULTS_DIR / "mooneye" / "results.json", statuses, mooneye_test_status),
        load_json_suite("RTC3Test", RESULTS_DIR / "rtc3test.json", statuses, rtc3test_status),
        load_json_suite("which", RESULTS_DIR / "which.json", statuses, which_test_status),
    ]
    image_suites = load_image_suites(statuses)
    suites = json_suites + image_suites

    lines = [
        "# Test results",
        "",
        "This page is generated from the recorded results in "
        "`tests/test_results/` and the latest pytest JUnit XML output. "
        "It is regenerated as part of `make docs`.",
        "",
        "Suite names in the overview table link to the corresponding result " "files or directories on GitHub.",
        "",
        "| Test suite | Cases | Passed | Failed |",
        "| --- | ---: | ---: | ---: |",
    ]
    for suite in suites:
        total, passed, failed, _, _ = suite_counts(suite)
        lines.append(
            f"| [{suite['name']}]({suite['url']}) | {total} | "
            f"{render_result(passed, 'Passed')} | {render_result(failed, 'Failed')} |"
        )
    lines.extend(
        (
            "",
            "Statuses come directly from the latest pytest JUnit XML. "
            "Expected failures are shown as failed, while skipped and missing "
            "cases remain distinguishable.",
            "",
        )
    )
    for suite in json_suites:
        lines.extend(render_json_suite(suite))
    for suite in image_suites:
        lines.extend(render_image_suite(suite))

    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
