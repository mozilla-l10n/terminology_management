import argparse
import sys
import os
import requests
from xml.etree import ElementTree as et

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}


def extract_terms(file, locale):
    """Returns a set containing all terms extracted from the Pontoon terminology export"""
    root = et.parse(file).getroot()
    term_list = []
    for termEntry in root.iter("termEntry"):
        term = termEntry.find(
            f"./langSet[@xml:lang='{locale}']/ntig/termGrp/term",
            nsmap,
        ).text
        term_list.append(term)
    return set(term_list)


def retrieve_remote_tbx(locale):
    root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

    locale_path = os.path.join(root_path, "pontoon_exports")
    if not os.path.isdir(locale_path):
        os.mkdir(locale_path)

    try:
        response = requests.get(
            f"https://pontoon.mozilla.org/terminology/{locale}.v2.tbx"
        )
        file = os.path.join(locale_path, f"{locale}.tbx")
        with open(file, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(e)

    return file


def retrieve_repo_tbx(repository_path, locale):
    file = os.path.join(repository_path, f"{locale}.tbx")
    return file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--locales",
        required=True,
        dest="locale_list",
        help="Path to .txt file with each required locale code entered on a new line. The appropriate .tbx file will be exported from Pontoon.",
    )
    parser.add_argument(
        "--repo",
        required=True,
        dest="repo_path",
        help="Path to .tbx file exported from Pontoon",
    )

    args = parser.parse_args()

    updates = {}

    with open(args.locale_list) as f:
        locale_list = [locale.strip() for locale in f]

    for locale in locale_list:
        repo_terms = extract_terms(retrieve_repo_tbx(args.repo_path, locale), locale)
        remote_terms = extract_terms(retrieve_remote_tbx(locale), locale)

        remote_updated_terms = [f"+{term}" for term in list(remote_terms.difference(repo_terms))]
        remote_removed_terms = [f"-{term}" for term in list(repo_terms.difference(remote_terms))]
        remote_updated_terms.extend(remote_removed_terms)

        if remote_updated_terms:
            updates[locale] = remote_updated_terms
    
    if updates:
        locales = list(updates.keys())
        locales.sort()

        output = []
        locales_updated = len(locales)
        output.append(f"\nTotal locales updated: {locales_updated}")
        for locale in locales:
            output.append(f"\nLocale: {locale}")

            terms = updates[locale]
            terms.sort()
            total_terms = len(terms)
            output.append(f"Changed terms: {total_terms}")
            for term in terms:
                output.append(
                    f"{term}"
                )

        sys.exit("\n".join(output))
    else:
        print("No updated locales found.")


if __name__ == "__main__":
    main()
