"""Shared paths and address-normalization SQL for the geocoding study.

Street normalization is block-addresses' own (scripts/compact.py: USPS abbreviations for every
token, spelled and bare ordinals to "5TH"), imported rather than copied so voter streets and
source streets go through exactly the same rules. On top of that this module adds the few
NC-specific canonicalizations that the study measured as "cheap improvements" (highway names,
unit designators, house-number suffixes).
"""

import os
import sys

BLOCK_ADDRESSES = os.environ.get("BLOCK_ADDRESSES", os.path.expanduser("~/Programming/block-addresses"))
DATA = os.environ.get("DATA", os.path.expanduser("~/Programming/nc-voter-data"))
OA_DIR = os.path.join(BLOCK_ADDRESSES, "addresses", "us", "nc")
NAD_DIR = os.path.join(BLOCK_ADDRESSES, "overture", "by-state", "state=NC")
CENSUS = os.path.join(BLOCK_ADDRESSES, "census")

sys.path.insert(0, os.path.join(BLOCK_ADDRESSES, "scripts"))
import compact  # noqa: E402  (block-addresses/scripts/compact.py)

cleaned = compact.cleaned
city_cleaned = compact.city_cleaned


def street(col: str) -> str:
    """block-addresses' normalized street: '8th Avenue' and '8TH AVE' both become '8TH AVE'."""
    return compact.ordinalized(compact.street_tokens(col))


DIRS = ("N", "S", "E", "W", "NE", "NW", "SE", "SW")


# USPS Publication 28, Appendix C1 (street suffix abbreviations), for the suffixes that
# block-addresses' normalize.json leaves out. The voter file abbreviates these even inside
# street names ('JACK MOORE MTN RD', 'TURNPIKE PNES'), while AddressNC and NAD spell them
# out.
USPS_EXTRA = {
    "ALLEY": "ALY", "ANNEX": "ANX", "BEND": "BND", "BLUFF": "BLF", "BRANCH": "BR", "BRIDGE": "BRG",
    "BROOK": "BRK", "BYPASS": "BYP", "CANYON": "CYN", "CAUSEWAY": "CSWY", "CENTER": "CTR",
    "CLIFF": "CLF", "CLUB": "CLB", "COMMON": "CMN", "CORNER": "COR", "CREEK": "CRK",
    "CRESCENT": "CRES", "CREST": "CRST", "DALE": "DL", "ESTATE": "EST", "ESTATES": "ESTS",
    "EXTENSION": "EXT", "FALLS": "FLS", "FERRY": "FRY", "FIELD": "FLD", "FIELDS": "FLDS",
    "FLAT": "FLT", "FOREST": "FRST", "FORGE": "FRG", "FORK": "FRK", "FORKS": "FRKS", "FORT": "FT",
    "GARDEN": "GDN", "GARDENS": "GDNS", "GATEWAY": "GTWY", "GLEN": "GLN", "GREEN": "GRN",
    "GROVE": "GRV", "HARBOR": "HBR", "HAVEN": "HVN", "HEIGHTS": "HTS", "HILL": "HL", "HILLS": "HLS",
    "ISLAND": "IS", "JUNCTION": "JCT", "KNOLL": "KNL", "LAKE": "LK", "LAKES": "LKS",
    "LANDING": "LNDG", "MANOR": "MNR", "MEADOW": "MDW", "MEADOWS": "MDWS", "MILL": "ML",
    "MILLS": "MLS", "MOUNT": "MT", "MOUNTAIN": "MTN", "ORCHARD": "ORCH", "PINE": "PNE",
    "PINES": "PNES", "PLAZA": "PLZ", "PORT": "PRT", "RANCH": "RNCH", "RIDGE": "RDG", "RIVER": "RIV",
    "SHOAL": "SHL", "SHOALS": "SHLS", "SHORE": "SHR", "SHORES": "SHRS", "SPRING": "SPG",
    "SPRINGS": "SPGS", "STATION": "STA", "SUMMIT": "SMT", "TRACE": "TRCE", "TURNPIKE": "TPKE",
    "VALLEY": "VLY", "VIEW": "VW", "VILLAGE": "VLG", "VISTA": "VIS", "WELLS": "WLS",
    # Not Pub 28 suffixes, but spelled both ways between the voter file and the sources
    # (measured on the misses' closest source street, see 06_misses.py).
    "SAINT": "ST", "BUSINESS": "BUS", "CHURCH": "CH", "COUNTRY": "CTRY", "SCHOOL": "SCH",
    "POINTE": "PT", "CROSSROADS": "XRDS", "CROSSRDS": "XRDS", "CRSG": "XING", "JUNIOR": "JR",
    "CEMETARY": "CEMETERY", "&": "AND",
}
USPS_CASE = "CASE t " + " ".join(f"WHEN '{k}' THEN '{v}'" for k, v in USPS_EXTRA.items()) + " ELSE t END"


def highway(col: str) -> str:
    """Collapse the many spellings of a numbered highway to 'HWY <n>' (plus whatever follows).

    Seen in the data: voter 'NC HWY 62', 'NC HIGHWAY 150', 'S NC HWY 306 HWY', 'US HWY 70 W';
    AddressNC 'NORTH CAROLINA HIGHWAY 210', 'NC 55 HIGHWAY', 'UNITED STATES HIGHWAY 17',
    'W NC 55 HWY'; NAD 'State Highway HIGHWAY 62 North', 'OLD W UNITED STATES HWY 421'.
    Applied after street(), so HIGHWAY is already HWY and NORTH is N. A leading direction
    moves to the end ('S HWY 306' -> 'HWY 306 S'), and a repeated trailing HWY is dropped.
    It drops the NC/US distinction, which the ZIP and house number keep apart.
    """
    prefix = "(N CAROLINA|NC|N C|UNITED STATES|US|U S|STATE|ST|SR|STATE RD|STATE ROUTE)"
    d = "|".join(DIRS)
    s = f"regexp_replace({col}, '^(OLD )+', 'OLD ')"
    s = f"regexp_replace({s}, '(^| )(NC|US|SR)([0-9]+)( |$)', '\\1\\2 \\3\\4')"  # 'NC41 HWY S'
    # leading (OLD) direction before a highway -> direction at the end
    hw = f"(({prefix} )?(HWY|RTE|ROUTE) .*|{prefix} [0-9]+[A-Z]?( .*)?)"
    s = f"regexp_replace({s}, '^(OLD )?({d}) (OLD )?{hw}$', '\\1\\3\\4 \\2')"
    s = f"regexp_replace({s}, '^(OLD )?{prefix} (HWY |RTE |ROUTE |RT )*([0-9]+[A-Z]?)( HWY| RTE| ROUTE)?( |$)', '\\1HWY \\4\\6')"
    s = f"regexp_replace({s}, '^(OLD )?(HWY )+', '\\1HWY ')"
    s = f"regexp_replace({s}, '^((OLD )?HWY [0-9]+[A-Z]?( [A-Z]+)*) HWY( [A-Z]+)*$', '\\1\\4')"
    return f"trim({s})"


def canon(col: str) -> str:
    """The matching street: street() output with apostrophes dropped, hyphens/slashes as
    spaces, the extra USPS abbreviations applied and highways canonicalized
    ('GIBSONVILLE-OSSIPEE RD' -> 'GIBSONVILLE OSSIPEE RD', 'JACK MOORE MOUNTAIN RD' ->
    'JACK MOORE MTN RD', "RILEY'S RIDGE RD" -> 'RILEYS RDG RD')."""
    s = f"trim(regexp_replace(regexp_replace({col}, '[''`]', '', 'g'), '[-/ ]+', ' ', 'g'))"
    s = f"array_to_string(list_transform(string_split({s}, ' '), t -> {USPS_CASE}), ' ')"
    return highway(s)


def dirkey(col: str) -> str:
    """The street with its directional tokens moved to the end in sorted order, so that
    '2ND ST N' (voter file: suffix N) and 'N 2ND ST' (AddressNC: prefix N) share a key."""
    toks = f"string_split({col}, ' ')"
    dirs = ", ".join(f"'{x}'" for x in DIRS)
    rest = f"array_to_string(list_filter({toks}, t -> t not in ({dirs})), ' ')"
    ds = f"array_to_string(list_sort(list_filter({toks}, t -> t in ({dirs}))), ' ')"
    return f"trim({rest} || ' ' || {ds})"


def unit(col: str) -> str:
    """Unit without its designator or leading zeros: 'APT 101', '#101', 'UNIT 0101' -> '101'."""
    s = cleaned(col)
    s = f"regexp_replace({s}, '^(APT|APARTMENT|UNIT|STE|SUITE|LOT|RM|ROOM|NO|NUM|SPC|SPACE|TRLR|BLDG) ?', '')"
    s = f"regexp_replace({s}, '^0+([0-9])', '\\1')"
    return f"coalesce(trim({s}), '')"


def house_number(col: str) -> tuple[str, str]:
    """(numeric part, suffix) of a house number: '106 B' -> ('106', 'B'), '12 1/2' -> ('12', '1/2')."""
    c = f"upper(trim({col}))"
    num = f"regexp_extract({c}, '^0*([0-9]+)', 1)"
    sfx = f"trim(regexp_replace(regexp_replace({c}, '^[0-9]+', ''), '^[- ]+|½', '', 'g'))"
    sfx = f"case when {c} like '%½%' then '1/2' else {sfx} end"
    return num, sfx


def core(col: str) -> str:
    """The street with its type and directional tokens removed and spaces squeezed out.

    Used only as a last-resort key within a ZIP and house number, for type or direction
    disagreements ('MAIN ST' vs 'MAIN AVE', 'N MAIN ST' vs 'MAIN ST') and split words
    ('MC DONALD' vs 'MCDONALD').
    """
    types = "|".join(compact.RULES["streetTypes"] + ["HWY", "EXT", "CV", "PT", "BND", "RDG", "HL", "HLS", "LNDG"])
    # RE2 has no lookahead: each match eats its trailing space, so a second pass catches
    # the token after one it just removed.
    s = f"regexp_replace(' ' || {col} || ' ', ' (({types}|N|S|E|W|NE|NW|SE|SW) )+', ' ', 'g')"
    s = f"regexp_replace({s}, ' (({types}|N|S|E|W|NE|NW|SE|SW) )+', ' ', 'g')"
    s = f"replace({s}, ' ', '')"
    return f"case when {s} = '' then replace({col}, ' ', '') else {s} end"
