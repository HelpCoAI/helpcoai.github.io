#!/usr/bin/env python3
"""
Named regions for the BMF extraction, so a pilot can be moved without editing code.

Adding a region is a dict entry: county -> set of city names as they appear in the
IRS Business Master File (uppercase, no punctuation normalisation needed beyond
what the extractor already does).
"""

TAMPA_BAY = {
    "Sarasota": {"SARASOTA", "VENICE", "NORTH PORT", "OSPREY", "NOKOMIS",
                 "LONGBOAT KEY", "ENGLEWOOD", "LAUREL", "SIESTA KEY", "VAMO"},
    "Manatee": {"BRADENTON", "BRADENTON BEACH", "PALMETTO", "ANNA MARIA",
                "HOLMES BEACH", "ELLENTON", "PARRISH", "MYAKKA CITY",
                "LAKEWOOD RANCH", "CORTEZ", "TERRA CEIA", "DUETTE", "ONECO"},
    "Hillsborough": {"TAMPA", "PLANT CITY", "TEMPLE TERRACE", "BRANDON", "RIVERVIEW",
                     "VALRICO", "LUTZ", "RUSKIN", "SUN CITY CENTER", "APOLLO BEACH",
                     "SEFFNER", "WIMAUMA", "GIBSONTON", "DOVER", "THONOTOSASSA",
                     "LITHIA", "ODESSA"},
    "Pinellas": {"ST PETERSBURG", "SAINT PETERSBURG", "CLEARWATER", "LARGO",
                 "PINELLAS PARK", "DUNEDIN", "TARPON SPRINGS", "PALM HARBOR",
                 "SEMINOLE", "SAFETY HARBOR", "OLDSMAR", "GULFPORT",
                 "TREASURE ISLAND", "ST PETE BEACH", "SAINT PETE BEACH",
                 "MADEIRA BEACH", "INDIAN ROCKS BEACH", "BELLEAIR", "KENNETH CITY",
                 "CLEARWATER BEACH"},
    "Pasco": {"NEW PORT RICHEY", "PORT RICHEY", "DADE CITY", "ZEPHYRHILLS",
              "LAND O LAKES", "WESLEY CHAPEL", "HUDSON", "HOLIDAY", "TRINITY",
              "SAN ANTONIO", "SPRING HILL"},
}

SOUTH_FLORIDA = {
    "Miami-Dade": {
        "MIAMI", "MIAMI BEACH", "HIALEAH", "CORAL GABLES", "HOMESTEAD",
        "MIAMI GARDENS", "NORTH MIAMI", "NORTH MIAMI BEACH", "MIAMI LAKES",
        "DORAL", "AVENTURA", "KENDALL", "CUTLER BAY", "PALMETTO BAY", "PINECREST",
        "SOUTH MIAMI", "SWEETWATER", "HIALEAH GARDENS", "OPA LOCKA", "OPA-LOCKA",
        "MIAMI SPRINGS", "KEY BISCAYNE", "SUNNY ISLES BEACH", "BAL HARBOUR",
        "SURFSIDE", "MIAMI SHORES", "FLORIDA CITY", "MEDLEY", "VIRGINIA GARDENS",
        "EL PORTAL", "BISCAYNE PARK", "GOLDEN BEACH", "WEST MIAMI",
        "COCONUT GROVE", "MIAMI GARDEN", "NORTH BAY VILLAGE",
    },
    "Broward": {
        "FORT LAUDERDALE", "FT LAUDERDALE", "HOLLYWOOD", "PEMBROKE PINES",
        "CORAL SPRINGS", "MIRAMAR", "POMPANO BEACH", "DAVIE", "PLANTATION",
        "SUNRISE", "WESTON", "DEERFIELD BEACH", "LAUDERHILL", "TAMARAC",
        "MARGATE", "COCONUT CREEK", "OAKLAND PARK", "NORTH LAUDERDALE",
        "HALLANDALE BEACH", "HALLANDALE", "LAUDERDALE LAKES", "PARKLAND",
        "COOPER CITY", "DANIA BEACH", "DANIA", "WILTON MANORS",
        "LIGHTHOUSE POINT", "HILLSBORO BEACH", "PEMBROKE PARK", "WEST PARK",
        "SOUTHWEST RANCHES", "LAUDERDALE BY THE SEA", "SEA RANCH LAKES",
    },
    "Palm Beach": {
        "WEST PALM BEACH", "BOCA RATON", "BOYNTON BEACH", "DELRAY BEACH",
        "JUPITER", "PALM BEACH GARDENS", "WELLINGTON", "LAKE WORTH",
        "RIVIERA BEACH", "GREENACRES", "ROYAL PALM BEACH", "PALM BEACH",
        "JUNO BEACH", "TEQUESTA", "NORTH PALM BEACH", "PALM SPRINGS",
        "LANTANA", "BELLE GLADE", "PAHOKEE", "SOUTH BAY", "LOXAHATCHEE",
        "ATLANTIS", "MANALAPAN", "GULF STREAM", "HIGHLAND BEACH",
        "OCEAN RIDGE", "HYPOLUXO", "BRINY BREEZES", "GLEN RIDGE", "HAVERHILL",
        "LAKE PARK", "MANGONIA PARK", "WESTLAKE", "PALM BEACH SHORES",
        "SOUTH PALM BEACH", "LAKE CLARKE SHORES", "JUPITER INLET COLONY",
    },
}

REGIONS = {
    "tampa-bay": {"state": "FL", "counties": TAMPA_BAY},
    "south-florida": {"state": "FL", "counties": SOUTH_FLORIDA},
}


def cities(region: str) -> set:
    return set().union(*REGIONS[region]["counties"].values())


def county_for(region: str, city: str) -> str:
    for county, names in REGIONS[region]["counties"].items():
        if city in names:
            return county
    return "Unknown"


if __name__ == "__main__":
    for name, cfg in REGIONS.items():
        n = sum(len(v) for v in cfg["counties"].values())
        print(f"{name:<16} {cfg['state']}  {len(cfg['counties'])} counties, {n} cities")
