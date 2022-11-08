from copy import deepcopy
import os
import argparse
import requests
from pathlib import Path
from xml.etree import ElementTree as et

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class XMLCombiner(object):
    def __init__(self, filenames):
        if len(filenames) == 0:
            raise FileNotFoundError("Invalid path, or path contains no valid files.")

        try:
            self.roots = [et.parse(f).getroot() for f in filenames]
        except SyntaxError:
            print(
                "Invalid tbx file, possibly due to incorrect locale code. Check your locales file to ensure all locale codes are valid."
            )

    def combine(self):
        for r in self.roots[1:]:
            self.combine_element(self.roots[0], r)
        return et.ElementTree(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively combines text, attributes, and children of an xml element tree.
        It updates either the text/attributes/children of an element if another element is found in `one`,
        or adds it from `other` if not found.
        """
        mapping = {(el.tag, hashabledict(el.attrib)): el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    mapping[(el.tag, hashabledict(el.attrib))].text = el.text
                except KeyError:
                    # Element not found in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    one.append(el)
            else:
                # Nested
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[(el.tag, hashabledict(el.attrib))], el)
                except KeyError:
                    # Element not found in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    one.append(el)


def extract_smartling_id_term(f):
    """Creates a dictionary with (term, definition) as key, and the Smartling UID as value."""
    root = et.parse(f).getroot()
    smartling_map = {}
    for termEntry in root.iter("termEntry"):
        term = termEntry.find(
            "./langSet[@xml:lang='en-US']/tig/term",
            nsmap,
        ).text
        try:
            definition = termEntry.find(
                "./descrip[@type='definition']",
                nsmap,
            ).text
        except AttributeError:
            definition = None
        id = termEntry.attrib["id"]
        smartling_map[(term, definition)] = id

    return smartling_map


def replace_pontoon_ids(etree, smartling_map):
    """Replaces Pontoon IDs with Smartling IDs if the term and definition match exactly a term in Smartling glossary file."""
    root = etree.getroot()
    pontoon_term_map = {}
    for termEntry in root.iter("termEntry"):
        term = termEntry.find(
            "./langSet[@xml:lang='en-US']/ntig/termGrp/term",
            nsmap,
        ).text
        try:
            definition = termEntry.find(
                "./langSet[@xml:lang='en-US']/descripGrp/descrip[@type='definition']",
                nsmap,
            ).text
        except AttributeError:
            definition = None
        pontoon_term_map[(term, definition)] = termEntry

    for key in pontoon_term_map:
        if key in smartling_map:
            pontoon_term_map[key].attrib["id"] = smartling_map[key]
        else:
            pontoon_term_map[key].attrib.pop("id", None)


def remove_all_ids(etree):
    """Smartling system only accepts IDs it creates. This removes all IDs so all terms will be registered as new."""
    root = etree.getroot()

    for termEntry in root.iter("termEntry"):
        termEntry.attrib.pop("id", None)


def export_tbx(locale_list):
    root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

    locale_path = os.path.join(root_path, "pontoon_exports")
    if not os.path.isdir(locale_path):
        os.mkdir(locale_path)

    for locale in locale_list:
        try:
            response = requests.get(
                f"https://pontoon.mozilla.org/terminology/{locale}.v2.tbx"
            )

            with open(os.path.join(locale_path, f"{locale}_pontoon.tbx"), "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(e)

    return list(Path(locale_path).glob("*.tbx"))


def convert_locale_codes(etree):
    smartling_locale_map = {
        "de": ["de-DE"],
        "fr": ["fr-CA", "fr-FR"],
        "id": ["id-ID"],
        "it": ["it-IT"],
        "ja": ["ja-JP"],
        "ko": ["ko-KR"],
        "ms-MY": ["ms-MY"],
        "nl": ["nl-NL"],
        "pl": ["pl-PL"],
        "ru": ["ru-RU"],
        "tr": ["tr-TR"],
        "vi": ["vi-VN"],
    }
    root = etree.getroot()
    for mozilla_locale, smartling_locales in smartling_locale_map.items():
        for termEntry in root.iter("termEntry"):
            for langSet in termEntry.iter("langSet"):
                if langSet.attrib[f"{{{nsmap['xml']}}}lang"] == mozilla_locale:
                    langSet.attrib[f"{{{nsmap['xml']}}}lang"] = smartling_locales[0]
                    if len(smartling_locales) > 1:
                        for locale in smartling_locales[1:]:
                            langSetCopy = deepcopy(langSet)
                            langSetCopy.attrib[f"{{{nsmap['xml']}}}lang"] = locale
                            termEntry.append(langSetCopy)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--locales",
        required=True,
        dest="locale_list",
        help="Path to .txt file with each required locale code entered on a new line. The appropriate .tbx file will be exported from Pontoon.",
    )
    parser.add_argument(
        "--id-format",
        required=True,
        dest="ids",
        choices=["smartling", "new", "pontoon"],
        help="Define how to set IDs for termEntry. Select smartling for importing into an existing Smartling glossary, new for creating a new Smartling glossary, or pontoon to preserve Pontoon IDs.",
    )
    parser.add_argument(
        "--smartling",
        dest="smartling_export",
        help="Path to glossary tbx file exported from Smartling. Required when using --id-format smartling",
    )
    args = parser.parse_args()
    if args.ids == "smartling" and not args.smartling_export:
        parser.error(
            "Path to Smartling glossary tbx file not defined (--smartling argument required)."
        )

    with open(args.locale_list) as f:
        locale_list = [locale.strip() for locale in f]

    merge_files = export_tbx(locale_list)
    merged_tree = XMLCombiner(merge_files).combine()

    if args.ids == "pontoon":
        merged_tree.write(
            "pontoon_glossary_multilingual.tbx", encoding="UTF-8", xml_declaration=True
        )

    if args.ids == "smartling":
        smartling_map = extract_smartling_id_term(args.smartling_export)
        replace_pontoon_ids(merged_tree, smartling_map)
        convert_locale_codes(merged_tree)
        merged_tree.write(
            "smartling_merge_glossary.tbx", encoding="UTF-8", xml_declaration=True
        )

    if args.ids == "new":
        remove_all_ids(merged_tree)
        merged_tree.write(
            "smartling_new_glossary.tbx", encoding="UTF-8", xml_declaration=True
        )


if __name__ == "__main__":
    main()
