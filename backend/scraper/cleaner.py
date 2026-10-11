import argparse
import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_FILE = CLEANED_DIR / "scraped_destinations.json"


BOILERPLATE_PATTERNS = [
    "related links",
    "contact us",
    "where to go",
    "plan your trip",
    "what's new",
    "business & partnership",
    "business and partnership",
    "subscribe",
    "privacy policy",
    "terms and conditions",
    "copyright",
]


GENERIC_HEADINGS = [
    "quick info box",
    "things to do",
    "things to do in",
    "things to do / experiences",
    "experiences",
    "activities",
    "attractions",
    "food",
    "food &",
    "food –",
    "food -",
    "culinary",
    "best time to visit",
    "best time",
    "when to visit",
    "where to stay",
    "where to eat",
    "travel tips",
    "nearby",
    "nearby destinations",
    "nearby places",
    "places near",
    "places to visit",
    "places to see",
    "top places to visit",
    "gallery",
    "reviews",
    "contact",
    "conclusion",
    "accommodation",
    "faqs",
    "faq",
]


QUESTION_STARTS = (
    "what ",
    "what is ",
    "what are ",
    "where ",
    "where is ",
    "where are ",
    "when ",
    "when is ",
    "how ",
    "how can ",
    "how do ",
    "can i ",
    "can we ",
    "why ",
    "which ",
)


BEST_TIME_PATTERNS = [
    "best time to visit",
    "best time",
    "when to visit",
    "ideal time",
    "best month",
]


ACTIVITY_PATTERNS = [
    "trek",
    "trekking",
    "rafting",
    "camping",
    "boating",
    "water sports",
    "watersports",
    "safari",
    "cycling",
    "kayaking",
    "bird watching",
    "jeep ride",
    "river rafting",
    "forest safari",
    "backwater safari",
    "walk through",
    "walking through",
    "ride to",
    "waterfall viewing",
    "viewing & photography",
    "photography",
    "light and sound show",
]


FOOD_PATTERNS = [
    "pandi curry",
    "coorg pork",
    "akki roti",
    "kadumbuttu",
    "bamboo shoot curry",
    "coorg filter coffee",
    "noolputtu",
    "mysore pak",
    "mysuru pak",
    "ragi mudde",
    "bisi bele bath",
]


ATTRACTION_PATTERNS = [
    "temple",
    "palace",
    "fort",
    "falls",
    "waterfall",
    "beach",
    "sanctuary",
    "national park",
    "museum",
    "monument",
    "dam",
    "lake",
    "cave",
    "viewpoint",
    "plantation",
    "church",
    "mosque",
    "monastery",
    "park",
]


INFORMATIONAL_PATTERNS = [
    "history",
    "significance",
    "introduction",
    "overview",
    "how to reach",
    "how to get",
    "by road",
    "by train",
    "by air",
    "location",
    "altitude",
    "distance",
    "timings",
    "entry fee",
    "weather",
    "nearby",
    "places near",
    "nearby places",
    "nearby destinations",
    "accommodation",
    "where to stay",
    "where to eat",
    "travel tips",
    "quick info",
    "festivals",
    "festival",
    "events",
    "event",
    "conclusion",
    "faq",
    "faqs",
]


NON_ATTRACTION_PATTERNS = [
    "hotel",
    "resort",
    "homestay",
    "hostel",
    "accommodation",
    "light and sound show",
    "nearby places",
    "nearby destinations",
    "places near",
    "history",
    "significance",
    "viewing & photography",
    "waterfall viewing",
]


# Known unrelated destination names that can appear
# inside another destination's page.
UNRELATED_DESTINATION_NAMES = [
    "badami cave temples",
]


def normalize_text(text):
    if not text:
        return ""

    text = str(text)

    # Common missing-space cases.
    text = re.sub(
        r"(?<=[a-z])(?=[A-Z])",
        " ",
        text,
    )

    text = re.sub(
        r"(?<=[A-Za-z])(?=\d)",
        " ",
        text,
    )

    text = re.sub(
        r"(?<=\d)(?=[A-Za-z])",
        " ",
        text,
    )

    # Normalize common HTML extraction artifacts.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def normalize_name(text):
    text = normalize_text(text)

    replacements = {
        "GoldenTemple": "Golden Temple",
        "GRSFantasy": "GRS Fantasy",
        "GRS FantasyPark": "GRS Fantasy Park",
        "RiverRafting": "River Rafting",
        "WaterSports": "Water Sports",
        "Watersports": "Water Sports",
        "Water Sports onVaruna": "Water Sports on Varuna",
        "River Rafting & Water Sports": "River Rafting & Water Sports",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def canonical_entity_name(name):
    """
    Normalize known duplicate naming variations.
    """

    name = normalize_name(name)

    aliases = {
        "Virupaksha Temple": "Virupaksha Temple, Hampi",
        "Virupaksha Temple, Hampi": "Virupaksha Temple, Hampi",
        "GoldenTemple (Namdroling Monastery)": (
            "Golden Temple (Namdroling Monastery)"
        ),
        "Trekking to the Base": "Trek to the Base",
        "RiverRafting & Water Sports": (
            "River Rafting & Water Sports"
        ),
    }

    return aliases.get(
        name,
        name,
    )


def is_boilerplate(text):
    lower = normalize_text(text).lower()

    return any(
        pattern in lower
        for pattern in BOILERPLATE_PATTERNS
    )


def deduplicate(items):
    result = []
    seen = set()

    for item in items:

        normalized = canonical_entity_name(item)

        if not normalized:
            continue

        key = normalized.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result


def clean_headings(headings):
    result = []

    for heading in headings or []:

        heading = normalize_name(heading)

        if not heading:
            continue

        if len(heading) < 3:
            continue

        if is_boilerplate(heading):
            continue

        result.append(heading)

    return deduplicate(result)


def clean_paragraphs(paragraphs):
    result = []

    for paragraph in paragraphs or []:

        paragraph = normalize_text(paragraph)

        if not paragraph:
            continue

        if len(paragraph) < 20:
            continue

        if is_boilerplate(paragraph):
            continue

        result.append(paragraph)

    return deduplicate(result)


def clean_images(images):
    result = []
    seen = set()

    for image in images or []:

        if isinstance(image, str):

            url = normalize_text(image)
            alt = ""
            title = ""

        elif isinstance(image, dict):

            url = normalize_text(
                image.get("url", "")
            )

            alt = normalize_text(
                image.get("alt", "")
            )

            title = normalize_text(
                image.get("title", "")
            )

        else:
            continue

        if not url:
            continue

        if url.startswith("data:"):
            continue

        if url in seen:
            continue

        seen.add(url)

        result.append(
            {
                "url": url,
                "alt": alt,
                "title": title,
            }
        )

    return result


def clean_links(links):
    result = []
    seen = set()

    for link in links or []:

        if isinstance(link, str):

            url = normalize_text(link)
            text = ""

        elif isinstance(link, dict):

            url = normalize_text(
                link.get("url", "")
            )

            text = normalize_text(
                link.get("text", "")
            )

        else:
            continue

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)

        result.append(
            {
                "url": url,
                "text": text,
            }
        )

    return result


def is_question_heading(text):
    lower = normalize_text(text).lower()

    if "?" in text:
        return True

    return lower.startswith(
        QUESTION_STARTS
    )


def is_generic_heading(text):
    lower = normalize_text(text).lower()

    if not lower:
        return True

    if is_question_heading(text):
        return True

    for pattern in GENERIC_HEADINGS:

        if lower == pattern:
            return True

        if lower.startswith(
            pattern + " "
        ):
            return True

        if lower.startswith(
            pattern + ":"
        ):
            return True

    return False


def is_informational_heading(text):
    lower = normalize_text(text).lower()

    return any(
        pattern in lower
        for pattern in INFORMATIONAL_PATTERNS
    )


def is_non_attraction_heading(text):
    lower = normalize_text(text).lower()

    return any(
        pattern in lower
        for pattern in NON_ATTRACTION_PATTERNS
    )


def is_unrelated_destination(text):
    lower = normalize_text(text).lower()

    return any(
        name in lower
        for name in UNRELATED_DESTINATION_NAMES
    )


def classify_heading(heading):
    """
    High-confidence classification.

    The heading is the primary signal.
    Section text is intentionally NOT used to turn
    arbitrary headings into entities.
    """

    heading = canonical_entity_name(
        heading
    )

    lower = heading.lower()

    if not heading:
        return None

    # ---------------------------------------------------------
    # BEST TIME
    # ---------------------------------------------------------

    if any(
        pattern in lower
        for pattern in BEST_TIME_PATTERNS
    ):
        return "best_time"

    # ---------------------------------------------------------
    # Generic / informational
    # ---------------------------------------------------------

    if is_generic_heading(heading):
        return None

    if is_informational_heading(heading):
        return None

    # ---------------------------------------------------------
    # Explicit exclusions
    # ---------------------------------------------------------

    if is_unrelated_destination(heading):
        return None

    if is_non_attraction_heading(heading):
        return None

    # ---------------------------------------------------------
    # FOOD
    # ---------------------------------------------------------

    if any(
        pattern in lower
        for pattern in FOOD_PATTERNS
    ):
        return "food"

    food_words = [
        "cuisine",
        "dish",
        "food",
        "culinary",
        "recipe",
    ]

    if any(
        word in lower
        for word in food_words
    ):
        return None

    # ---------------------------------------------------------
    # ACTIVITIES
    # ---------------------------------------------------------

    if any(
        pattern in lower
        for pattern in ACTIVITY_PATTERNS
    ):
        return "activities"

    # ---------------------------------------------------------
    # ATTRACTIONS
    # ---------------------------------------------------------

    if any(
        pattern in lower
        for pattern in ATTRACTION_PATTERNS
    ):
        return "attractions"

    return None


def clean_sections(raw_sections):
    sections = []

    classified = {
        "attractions": [],
        "activities": [],
        "food": [],
        "best_time": [],
        "content_sections": [],
    }

    for raw_section in raw_sections or []:

        if not isinstance(raw_section, dict):
            continue

        heading = normalize_name(
            raw_section.get(
                "heading",
                ""
            )
        )

        text = normalize_text(
            raw_section.get(
                "text",
                ""
            )
        )

        if not heading:
            continue

        if is_boilerplate(heading):
            continue

        section = dict(raw_section)

        section["heading"] = heading
        section["text"] = text

        if "categories" in section:

            section["categories"] = deduplicate(
                section.get(
                    "categories",
                    []
                )
            )

        sections.append(section)

        field = classify_heading(
            heading
        )

        if field == "attractions":

            classified[
                "attractions"
            ].append(heading)

        elif field == "activities":

            classified[
                "activities"
            ].append(heading)

        elif field == "food":

            classified[
                "food"
            ].append(heading)

        elif field == "best_time":

            classified[
                "best_time"
            ].append(heading)

        else:

            classified[
                "content_sections"
            ].append(heading)

    for key in classified:

        classified[key] = deduplicate(
            classified[key]
        )

    return sections, classified


def build_content_blocks(sections):
    blocks = []

    for section in sections:

        heading = section.get(
            "heading",
            ""
        )

        text = section.get(
            "text",
            ""
        )

        if heading:

            blocks.append(
                {
                    "type": "heading",
                    "text": heading,
                }
            )

        if text:

            blocks.append(
                {
                    "type": "paragraph",
                    "text": text,
                }
            )

    return blocks


def get_description(data, paragraphs):
    """
    Description priority:

    1. Scraper description if present.
    2. Meta description.
    3. First meaningful paragraph.
    """

    description = normalize_text(
        data.get(
            "description",
            ""
        )
    )

    if description:
        return description

    meta = normalize_text(
        data.get(
            "meta_description",
            ""
        )
    )

    if meta:
        return meta

    for paragraph in paragraphs:

        if len(paragraph) >= 60:
            return paragraph

    return ""


def get_primary_image(data, images):
    primary = normalize_text(
        data.get(
            "primary_image",
            ""
        )
    )

    if primary:
        return primary

    if images:
        return images[0]["url"]

    return ""


def clean_record(raw_record):

    data = raw_record.get(
        "data",
        {}
    )

    headings = clean_headings(
        data.get(
            "headings",
            []
        )
    )

    paragraphs = clean_paragraphs(
        data.get(
            "paragraphs",
            []
        )
    )

    sections, classified = clean_sections(
        data.get(
            "sections",
            []
        )
    )

    images = clean_images(
        data.get(
            "images",
            []
        )
    )

    internal_links = clean_links(
        data.get(
            "internal_links",
            []
        )
    )

    description = get_description(
        data,
        paragraphs,
    )

    primary_image = get_primary_image(
        data,
        images,
    )

    raw_text = normalize_text(
        data.get(
            "raw_text",
            ""
        )
    )

    content_blocks = build_content_blocks(
        sections
    )

    return {
        "destination_id": raw_record.get(
            "destination_id"
        ),

        "slug": raw_record.get(
            "slug"
        ),

        "source_url": (
            raw_record.get("url")
            or data.get("source_url")
        ),

        "page_title": normalize_text(
            data.get(
                "page_title",
                ""
            )
        ),

        "description": description,

        "meta_desc": normalize_text(
            data.get(
                "meta_description",
                ""
            )
        ),

        "primary_image": primary_image,

        "images": images,

        "headings": headings,

        "paragraphs": paragraphs,

        "sections": sections,

        "content_blocks": content_blocks,

        "attractions_sections": (
            classified["attractions"]
        ),

        "activities_sections": (
            classified["activities"]
        ),

        "food_sections": (
            classified["food"]
        ),

        "best_time_sections": (
            classified["best_time"]
        ),

        "content_sections": (
            classified["content_sections"]
        ),

        "internal_links": internal_links,

        "raw_text_cleaned": raw_text,
    }


def clean_all(slug_filter=None):

    CLEANED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    raw_files = sorted(
        RAW_DIR.glob("*.json")
    )

    if slug_filter:

        raw_files = [
            file
            for file in raw_files
            if file.stem == slug_filter
        ]

    print(
        "HiddenGem – Data Cleaner"
    )

    print(
        "========================================"
    )

    print(
        f"Raw files to clean: "
        f"{len(raw_files)}"
    )

    print()

    if not raw_files:

        print(
            f"No raw JSON files found in "
            f"{RAW_DIR}"
        )

        return

    cleaned_records = []

    for raw_file in raw_files:

        print(
            f"Cleaning: {raw_file.name}"
        )

        try:

            with raw_file.open(
                "r",
                encoding="utf-8"
            ) as file:

                raw_record = json.load(
                    file
                )

            cleaned = clean_record(
                raw_record
            )

            print(
                f"  Headings: "
                f"{len(cleaned['headings'])}"
            )

            print(
                f"  Paragraphs: "
                f"{len(cleaned['paragraphs'])}"
            )

            print(
                f"  Sections: "
                f"{len(cleaned['sections'])}"
            )

            print(
                f"  Images: "
                f"{len(cleaned['images'])}"
            )

            print(
                f"  Attraction entities: "
                f"{len(cleaned['attractions_sections'])}"
            )

            print(
                f"  Activity entities: "
                f"{len(cleaned['activities_sections'])}"
            )

            print(
                f"  Food entities: "
                f"{len(cleaned['food_sections'])}"
            )

            print(
                "  Description: "
                + (
                    "YES"
                    if cleaned["description"]
                    else "NO"
                )
            )

            cleaned_records.append(
                cleaned
            )

        except json.JSONDecodeError as exc:

            print(
                f"  [ERROR] Invalid JSON: "
                f"{exc}"
            )

        except Exception as exc:

            print(
                f"  [ERROR] {exc}"
            )

        print()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cleaned_records,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Saved {len(cleaned_records)} "
        f"record(s) to:"
    )

    print(
        OUTPUT_FILE
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Clean scraped Karnataka "
            "Tourism data."
        )
    )

    parser.add_argument(
        "--slug",
        help=(
            "Clean only one destination, "
            "e.g. mysuru"
        ),
    )

    args = parser.parse_args()

    clean_all(
        slug_filter=args.slug
    )


if __name__ == "__main__":
    main()