import argparse
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ===============================================================
# CONFIGURATION
# ===============================================================

REQUEST_DELAY_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 15

USER_AGENT = (
    "HiddenGem-Scraper/1.0 "
    "(Karnataka Tourism research project)"
)

BASE_DIR = Path(__file__).parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ===============================================================
# APPROVED KARNATAKA TOURISM SOURCES
# ===============================================================
#
# This is configuration, not destination-specific scraping logic.
#
# The scraper itself is generic and can process any approved
# Karnataka Tourism URL added here.
#
# destination_id can be None for a general/thematic page.
# ===============================================================

APPROVED_URLS = [
    {
        "destination_id": "DEST_001",
        "slug": "mysuru",
        "url": "https://karnatakatourism.org/en/destinations/mysuru",
    },
    {
        "destination_id": "DEST_002",
        "slug": "coorg",
        "url": "https://karnatakatourism.org/en/destinations/coorg",
    },
    {
        "destination_id": "DEST_003",
        "slug": "hampi",
        "url": "https://karnatakatourism.org/en/destinations/hampi",
    },
    {
        "destination_id": "DEST_004",
        "slug": "jog-falls",
        "url": "https://karnatakatourism.org/en/attractions/jog-falls",
    },
    {
        "destination_id": "DEST_005",
        "slug": "dandeli",
        "url": "https://karnatakatourism.org/en/experiences/dandeli-wildlife-sanctuary",
    },
]


# ===============================================================
# CATEGORY KEYWORDS
# ===============================================================
#
# These are only used for broad page-level discovery.
# They are NOT treated as final entity classifications.
#
# The cleaner performs the more conservative classification.
# ===============================================================

CONTENT_CATEGORY_KEYWORDS = {
    "food": [
        "food",
        "cuisine",
        "culinary",
        "dish",
        "dishes",
        "curry",
        "coffee",
        "roti",
        "rice",
        "sweet",
        "snack",
        "recipe",
        "local cuisine",
    ],

    "activities": [
        "things to do",
        "activity",
        "activities",
        "trek",
        "trekking",
        "rafting",
        "camping",
        "boating",
        "cycling",
        "kayaking",
        "safari",
        "jeep ride",
        "adventure",
        "bird watching",
        "wildlife safari",
    ],

    "attractions": [
        "attraction",
        "temple",
        "palace",
        "fort",
        "falls",
        "waterfall",
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
        "sanctuary",
    ],

    "heritage": [
        "heritage",
        "historical",
        "history",
        "ancient",
        "architecture",
        "monument",
        "temple",
        "palace",
        "fort",
        "dynasty",
        "kingdom",
        "unesco",
    ],

    "nature": [
        "nature",
        "forest",
        "hill",
        "hills",
        "mountain",
        "valley",
        "river",
        "lake",
        "waterfall",
        "landscape",
        "scenic",
        "greenery",
    ],

    "wildlife": [
        "wildlife",
        "sanctuary",
        "national park",
        "forest",
        "tiger",
        "elephant",
        "leopard",
        "bird",
        "birds",
        "safari",
        "biodiversity",
    ],

    "best_time": [
        "best time",
        "when to visit",
        "ideal time",
        "best season",
        "season",
        "october",
        "november",
        "december",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
    ],

    "travel_tips": [
        "how to reach",
        "how to get",
        "travel",
        "by road",
        "by train",
        "by air",
        "airport",
        "railway",
        "bus",
        "distance",
        "accommodation",
        "stay",
        "tips",
        "travel tips",
    ],
}


# ===============================================================
# ROBOTS
# ===============================================================

def robots_allowed(url: str) -> bool:
    """
    Check robots.txt before scraping.

    If robots.txt cannot be verified, return True so the
    explicitly approved URL can still be requested.
    """

    robots_url = "https://karnatakatourism.org/robots.txt"

    print("    Checking robots.txt...")

    try:
        response = requests.get(
            robots_url,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        # If robots.txt itself is unavailable, don't block the
        # explicitly approved source URL.
        if response.status_code >= 400:
            print(
                "    [ROBOTS] Could not verify robots.txt. "
                "Continuing with approved URL."
            )
            return True

        robots_text = response.text.casefold()

        # Explicit disallow for all user agents.
        if (
            "user-agent: *" in robots_text
            and "disallow: /" in robots_text
        ):
            print(
                "    [ROBOTS] Site-wide disallow detected."
            )
            return False

        print(
            "    [ROBOTS] Verification completed."
        )

        return True

    except requests.RequestException as exc:

        print(
            "    [ROBOTS] Could not verify robots.txt: "
            f"{exc}"
        )

        print(
            "    [ROBOTS] Continuing with explicitly "
            "approved URL."
        )

        return True


def fetch_page(url: str):
    """
    Fetch an explicitly approved public Karnataka Tourism page.
    """

    if not robots_allowed(url):

        print(
            f"    [ROBOTS] Access blocked: {url}"
        )

        return None

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,"
            "application/xhtml+xml"
        ),
        "Accept-Language": (
            "en-IN,en;q=0.9"
        ),
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        print(
            f"    [HTTP {response.status_code}] "
            "Page fetched successfully."
        )

        return response.text

    except requests.HTTPError as exc:

        print(
            f"    [HTTP ERROR] {exc}"
        )

    except requests.ConnectionError as exc:

        print(
            f"    [CONNECTION ERROR] {exc}"
        )

    except requests.Timeout:

        print(
            "    [TIMEOUT] Request timed out."
        )

    except requests.RequestException as exc:

        print(
            f"    [REQUEST ERROR] {exc}"
        )

    return None
# ===============================================================
# TEXT CLEANING
# ===============================================================

def clean_text(text):
    """
    Normalize visible text while preserving its meaning.
    """

    if not text:
        return ""

    text = str(text)

    # Normalize whitespace.
    text = " ".join(text.split())

    return text.strip()


def normalize_name(text):
    """
    Normalize heading/entity text.
    """

    text = clean_text(text)

    if not text:
        return ""

    return text


# ===============================================================
# BOILERPLATE DETECTION
# ===============================================================

def is_boilerplate_text(text):
    """
    Detect obvious website navigation/footer text.
    """

    if not text:
        return False

    lower = clean_text(text).lower()

    patterns = [
        "related links",
        "contact us",
        "privacy policy",
        "terms and conditions",
        "copyright",
        "subscribe",
        "business & partnership",
        "business and partnership",
        "where to go",
        "plan your trip",
        "what's new",
        "all rights reserved",
    ]

    return any(
        pattern in lower
        for pattern in patterns
    )


def remove_boilerplate(soup):
    """
    Remove elements that are not useful tourism content.
    """

    selectors = [
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "nav",
        "footer",
        "form",
    ]

    for selector in selectors:
        for element in soup.select(selector):
            element.decompose()

    return soup


# ===============================================================
# CONTENT ROOT
# ===============================================================

def find_content_root(soup):
    """
    Find the most likely main content container.

    Falls back to <body> if no common article/content container
    is found.
    """

    selectors = [
        "main",
        "article",
        "[role='main']",
        ".entry-content",
        ".post-content",
        ".page-content",
        ".single-content",
        ".content-area",
        ".site-main",
    ]

    for selector in selectors:

        element = soup.select_one(selector)

        if element:
            return element

    if soup.body:
        return soup.body

    return soup


# ===============================================================
# CATEGORY DETECTION
# ===============================================================

def detect_categories(text):
    """
    Detect broad tourism themes from text.

    This is intentionally broad.

    It is NOT used to decide whether an individual heading is
    actually an attraction/activity/food item.
    """

    lower = clean_text(text).lower()

    categories = []

    for category, keywords in CONTENT_CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            if keyword in lower:
                categories.append(category)
                break

    return categories


# ===============================================================
# SECTION EXTRACTION
# ===============================================================

def extract_sections(content):
    """
    Extract heading + following content blocks.

    Each section keeps its original heading and text.
    """

    sections = []

    headings = content.find_all(
        ["h2", "h3"]
    )

    for heading in headings:

        heading_text = normalize_name(
            heading.get_text(" ", strip=True)
        )

        if not heading_text:
            continue

        if is_boilerplate_text(
            heading_text
        ):
            continue

        section_parts = []

        current = heading.find_next_sibling()

        while current:

            if current.name in ["h2", "h3"]:
                break

            if current.name in ["p", "li"]:

                text = clean_text(
                    current.get_text(
                        " ",
                        strip=True,
                    )
                )

                if len(text) >= 20:
                    if not is_boilerplate_text(text):
                        section_parts.append(text)

            current = current.find_next_sibling()

        section_text = clean_text(
            " ".join(section_parts)
        )

        categories = detect_categories(
            heading_text + " " + section_text
        )

        sections.append({
            "heading": heading_text,
            "categories": categories,
            "text": section_text,
        })

    return sections


# ===============================================================
# LINK EXTRACTION
# ===============================================================

def extract_links(content, base_url):
    """
    Extract internal Karnataka Tourism links.
    """

    links = []
    seen = set()

    base_domain = urlparse(
        base_url
    ).netloc.lower()

    for anchor in content.find_all("a"):

        href = anchor.get("href")

        if not href:
            continue

        href = urljoin(
            base_url,
            href,
        ).strip()

        if not href:
            continue

        parsed = urlparse(href)

        if parsed.scheme not in [
            "http",
            "https",
        ]:
            continue

        domain = parsed.netloc.lower()

        # Keep links belonging to Karnataka Tourism.
        if "karnatakatourism.org" not in domain:
            continue

        # Remove fragment.
        clean_url = href.split("#")[0]

        if clean_url.lower() in seen:
            continue

        seen.add(
            clean_url.lower()
        )

        label = clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        links.append({
            "url": clean_url,
            "label": label,
        })

    return links


# ===============================================================
# IMAGE EXTRACTION
# ===============================================================

def extract_images(content, base_url):
    """
    Extract images actually present on the approved page.

    Supports common lazy-loading attributes as well as normal src.
    """

    images = []
    seen = set()

    for img in content.find_all("img"):

        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("data-original")
        )

        if not src:
            continue

        src = urljoin(
            base_url,
            src,
        ).strip()

        if not src:
            continue

        # Ignore inline data images.
        if src.startswith("data:"):
            continue

        key = src.lower()

        if key in seen:
            continue

        seen.add(key)

        alt = clean_text(
            img.get("alt", "")
        )

        title = clean_text(
            img.get("title", "")
        )

        images.append({
            "url": src,
            "alt": alt,
            "title": title,
        })

    return images


# ===============================================================
# COMPLETE HTML EXTRACTION
# ===============================================================

def extract_from_html(
    html: str,
    url: str,
) -> dict:
    """
    Generic extraction from any approved Karnataka Tourism page.

    The scraper preserves rich source content instead of reducing
    the page to only categories.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    remove_boilerplate(soup)

    content = find_content_root(soup)

    # ---------------------------------------------------------------
    # Page title
    # ---------------------------------------------------------------

    title = ""

    og_title = soup.find(
        "meta",
        property="og:title",
    )

    if og_title and og_title.get("content"):

        title = clean_text(
            og_title["content"]
        )

    elif soup.title:

        title = clean_text(
            soup.title.get_text()
        )

    else:

        h1 = content.find("h1")

        if h1:

            title = clean_text(
                h1.get_text()
            )

    # ---------------------------------------------------------------
    # Meta description
    # ---------------------------------------------------------------

    meta_desc = ""

    og_desc = soup.find(
        "meta",
        property="og:description",
    )

    if og_desc and og_desc.get("content"):

        meta_desc = clean_text(
            og_desc["content"]
        )

    else:

        description = soup.find(
            "meta",
            attrs={
                "name": "description"
            },
        )

        if (
            description
            and description.get("content")
        ):

            meta_desc = clean_text(
                description["content"]
            )

    # ---------------------------------------------------------------
    # Headings
    # ---------------------------------------------------------------

    headings = []

    for tag in content.find_all(
        ["h1", "h2", "h3"]
    ):

        text = normalize_name(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        if is_boilerplate_text(text):
            continue

        if text not in headings:
            headings.append(text)

    # ---------------------------------------------------------------
    # Paragraphs
    # ---------------------------------------------------------------

    paragraphs = []

    for tag in content.find_all(
        ["p", "li"]
    ):

        text = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if len(text) < 30:
            continue

        if is_boilerplate_text(text):
            continue

        if text not in paragraphs:
            paragraphs.append(text)

    # ---------------------------------------------------------------
    # Section-level tourism information
    # ---------------------------------------------------------------

    sections = extract_sections(
        content
    )

    # ---------------------------------------------------------------
    # Images
    # ---------------------------------------------------------------

    images = extract_images(
        content,
        url,
    )

    # ---------------------------------------------------------------
    # Detected categories for whole page
    # ---------------------------------------------------------------

    category_text = " ".join(
        headings + paragraphs
    )

    detected_categories = detect_categories(
        category_text
    )

    # ---------------------------------------------------------------
    # Internal links
    # ---------------------------------------------------------------

    internal_links = extract_links(
        content,
        url,
    )

    # ---------------------------------------------------------------
    # Visible content
    # ---------------------------------------------------------------

    visible_parts = []

    for element in content.find_all(
        ["h1", "h2", "h3", "p", "li"]
    ):

        text = clean_text(
            element.get_text(
                " ",
                strip=True,
            )
        )

        if len(text) < 20:
            continue

        if is_boilerplate_text(text):
            continue

        if text not in visible_parts:
            visible_parts.append(text)

    raw_text = clean_text(
        " ".join(visible_parts)
    )

    # ---------------------------------------------------------------
    # Final structured source record
    # ---------------------------------------------------------------

    return {
        "source_url": url,

        "page_title": title,

        "meta_description": meta_desc,

        "detected_categories": detected_categories,

        "headings": headings,

        "paragraphs": paragraphs,

        "sections": sections,

        "images": images,

        "internal_links": internal_links,

        "raw_text": raw_text,
    }


# ===============================================================
# OUTPUT FILE NAME
# ===============================================================

def output_slug(source):
    """
    Generate a safe output filename.
    """

    slug = source.get("slug")

    if slug:
        return slug

    parsed = urlparse(
        source["url"]
    )

    path = parsed.path.strip("/")

    if not path:
        return "page"

    last_part = path.split("/")[-1]

    return last_part or "page"


# ===============================================================
# SAVE RAW DATA
# ===============================================================

def save_raw(
    source,
    extracted,
):
    """
    Save the complete scraped source record.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        output_slug(source)
        + ".json"
    )

    output_path = (
        RAW_DATA_DIR
        / filename
    )

    record = {
        "destination_id": source.get(
            "destination_id"
        ),

        "slug": source.get(
            "slug"
        ),

        "url": source["url"],

        "data": extracted,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            record,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path


# ===============================================================
# SCRAPE ALL APPROVED SOURCES
# ===============================================================

def scrape_all(
    dry_run=False,
):
    """
    Scrape all approved Karnataka Tourism URLs.
    """

    print()
    print(
        "HiddenGem – Generic Karnataka Tourism Scraper"
    )
    print(
        "============================================="
    )

    print(
        f"Approved URLs : {len(APPROVED_URLS)}"
    )

    print(
        f"Delay         : {REQUEST_DELAY_SECONDS}s"
    )

    print(
        f"Output        : {RAW_DATA_DIR}"
    )

    print(
        f"Dry run       : {dry_run}"
    )

    print()

    success_count = 0

    for index, source in enumerate(
        APPROVED_URLS,
        start=1,
    ):

        url = source["url"]

        print(
            f"[{index}/{len(APPROVED_URLS)}]"
        )

        print(
            f"    URL: {url}"
        )

        print(
            f"    Destination: "
            f"{source.get('destination_id')}"
        )

        # -----------------------------------------------------------
        # Robots check
        # -----------------------------------------------------------

        print(
            "    Checking robots.txt..."
        )

        if not robots_allowed(url):

            print(
                "    [SKIPPED] robots.txt does not allow scraping "
                "or could not be verified."
            )

            print()

            continue

        if dry_run:

            print(
                "    [DRY RUN] Page was not fetched."
            )

            print()

            continue

        # -----------------------------------------------------------
        # Fetch
        # -----------------------------------------------------------

        try:

            html = fetch_page(
                url
            )

            print(
                "    [HTTP 200] "
                "Page fetched successfully."
            )

        except Exception as exc:

            print(
                f"    [ERROR] Could not fetch page: {exc}"
            )

            print()

            continue

        # -----------------------------------------------------------
        # Extract
        # -----------------------------------------------------------

        try:

            extracted = extract_from_html(
                html,
                url,
            )

        except Exception as exc:

            print(
                f"    [ERROR] Extraction failed: {exc}"
            )

            print()

            continue

        print(
            f"    Extracted: "
            f"{len(extracted['headings'])} headings, "
            f"{len(extracted['paragraphs'])} paragraphs"
        )

        print(
            f"    Categories: "
            f"{', '.join(extracted['detected_categories'])}"
        )

        print(
            f"    Sections: "
            f"{len(extracted['sections'])}"
        )

        print(
            f"    Images: "
            f"{len(extracted['images'])}"
        )

        print(
            f"    Links: "
            f"{len(extracted['internal_links'])}"
        )

        # -----------------------------------------------------------
        # Save
        # -----------------------------------------------------------

        try:

            output_path = save_raw(
                source,
                extracted,
            )

            print(
                f"    [SAVED] {output_path}"
            )

            success_count += 1

        except Exception as exc:

            print(
                f"    [ERROR] Could not save data: {exc}"
            )

        print()

        # -----------------------------------------------------------
        # Delay
        # -----------------------------------------------------------

        if index < len(APPROVED_URLS):

            time.sleep(
                REQUEST_DELAY_SECONDS
            )

    print(
        f"Done. "
        f"{success_count}/{len(APPROVED_URLS)} "
        f"pages scraped successfully."
    )


# ===============================================================
# COMMAND LINE INTERFACE
# ===============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generic Karnataka Tourism scraper "
            "for HiddenGem."
        )
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show approved URLs without "
            "fetching pages."
        ),
    )

    args = parser.parse_args()

    scrape_all(
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()