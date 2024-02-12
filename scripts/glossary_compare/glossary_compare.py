import argparse
from xml.etree import ElementTree as et

nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}


def extract_terms_smartling(file, locale):
    """Returns a set containing all terms extracted from the Smartling glossary export"""
    smartling_locale_map = {
        "bn": "bn-BD",
        "de": "de-DE",
        "fr": "fr-CA",
        "id": "id-ID",
        "is": "is-IS",
        "it": "it-IT",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "ms": "ms-MY",
        "nl": "nl-NL",
        "pl": "pl-PL",
        "ru": "ru-RU",
        "tr": "tr-TR",
        "vi": "vi-VN",
    }
    if locale in smartling_locale_map:
        locale = smartling_locale_map[locale]

    root = et.parse(file).getroot()
    term_list = []
    for termEntry in root.iter("termEntry"):
        term = termEntry.find(
            f"./langSet[@xml:lang='{locale}']/tig/term",
            nsmap,
        ).text
        term_list.append(term)
    return set(term_list)


def extract_terms_pontoon(file, locale):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smartling",
        required=True,
        dest="smartling_glossary",
        help="Path to .tbx file exported from Smartling",
    )
    parser.add_argument(
        "--pontoon",
        required=True,
        dest="pontoon_glossary",
        help="Path to .tbx file exported from Pontoon",
    )
    parser.add_argument(
        "--locale",
        default="en-US",
        required=False,
        dest="locale_code",
        help="Locale code for comparison",
    )
    parser.add_argument(
        "--csv",
        required=False,
        action="store_true",
        default=False,
        dest="csv_output",
        help="Store data as csv files",
    )

    args = parser.parse_args()

    smartling = extract_terms_smartling(args.smartling_glossary)
    pontoon = extract_terms_pontoon(args.pontoon_glossary)

    smartling_exclusive_terms = list(smartling.difference(pontoon), args.locale_code)
    smartling_exclusive_terms.sort()
    print(
        f"{args.locale_code} terminology exclusive to Smartling: {', '.join(smartling_exclusive_terms)}"
    )

    pontoon_exculsive_terms = list(pontoon.difference(smartling), args.locale_code)
    pontoon_exculsive_terms.sort()
    print(
        f"{args.locale_code} terminology exclusive to Pontoon: {', '.join(pontoon_exculsive_terms)}"
    )

    if args.csv_output:
        with open("smartling_exclusive_terms.csv", "w") as f:
            f.write("\n".join(smartling_exclusive_terms))
            print("Smartling exclusive terms saved to smartling_exclusive_terms.csv")

        with open("pontoon_exclusive_terms.csv", "w") as f:
            f.write("\n".join(pontoon_exculsive_terms))
            print("Pontoon exclusive terms saved to pontoon_exclusive_terms.csv")


if __name__ == "__main__":
    main()
