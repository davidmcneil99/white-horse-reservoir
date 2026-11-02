"""Download EN0110044 boundary GeoJSON and overlay on ONS civil parish boundaries.

If the PINS download is blocked or the boundary format is unexpected, falls back
to a manually-populated list of the five known scheme parishes.
"""
import json
import pathlib
import datetime
import sys

try:
    import requests
except ImportError:
    requests = None  # type: ignore

PINS_URL = (
    "https://national-infrastructure-consenting.planninginspectorate.gov.uk"
    "/projects/EN0110044/download-boundary"
)
ONS_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "Parishes_and_Non_Civil_Parished_Areas_December_2023_EW_BGC_2022/FeatureServer/0/query"
    "?where=1%3D1&outFields=PARNM23&outSR=4326&f=json"
    "&resultOffset={offset}&resultRecordCount=1000"
)
USER_AGENT = (
    "WHReservoir/1.0 (+https://github.com/davidmcneil99/white-horse-reservoir)"
)

# Five parishes confirmed from EN0110044 application documents
KNOWN_SCHEME_PARISHES = [
    "Baulking",
    "Charney Bassett",
    "Garford",
    "Goosey",
    "West Hanney",
]

OUT_PATH = pathlib.Path("data/cearn/boundary-parishes.json")


def fetch_json(url: str) -> dict:
    if requests is None:
        raise RuntimeError("requests not installed")
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all_parishes() -> list:
    """Fetch all ONS parish features (paginated ArcGIS JSON)."""
    features, offset = [], 0
    while True:
        data = fetch_json(ONS_URL.format(offset=offset))
        batch = data.get("features", [])
        if not batch:
            break
        features.extend(batch)
        offset += len(batch)
        if len(batch) < 1000:
            break
    return features


def try_automated(verbose: bool = True) -> list | None:
    """Attempt to derive scheme parishes via PINS + ONS spatial overlay.

    Returns a sorted list of parish name strings, or None on failure.
    Requires: shapely>=2.0
    """
    try:
        from shapely.geometry import shape  # type: ignore
    except ImportError:
        if verbose:
            print("  shapely not installed; skipping automated overlay.")
        return None

    # --- Fetch PINS boundary ---
    if verbose:
        print("Fetching EN0110044 boundary from PINS...")
    try:
        boundary_data = fetch_json(PINS_URL)
    except Exception as exc:
        if verbose:
            print(f"  PINS fetch failed: {exc}")
        return None

    try:
        features = boundary_data.get("features") or []
        if features:
            raw_geom = features[0]["geometry"]
        else:
            raw_geom = boundary_data.get("geometry") or boundary_data
        boundary_geom = shape(raw_geom)
    except Exception as exc:
        if verbose:
            print(f"  Could not parse PINS boundary geometry: {exc}")
        return None

    # --- Fetch ONS parishes ---
    if verbose:
        print("Fetching ONS civil parish boundaries (paginated)...")
    try:
        parish_features = fetch_all_parishes()
    except Exception as exc:
        if verbose:
            print(f"  ONS fetch failed: {exc}")
        return None

    if verbose:
        print(f"  {len(parish_features)} parish features loaded")

    # --- Spatial intersection ---
    scheme_parishes = []
    for feat in parish_features:
        try:
            geom = shape(feat["geometry"])
            if boundary_geom.intersects(geom):
                name = (feat.get("properties") or {}).get("PARNM23", "")
                if name:
                    scheme_parishes.append(name)
        except Exception:
            pass  # skip malformed geometries

    if verbose:
        print(f"  {len(scheme_parishes)} intersecting parishes found")
    return sorted(scheme_parishes) if scheme_parishes else None


def main(verbose: bool = True) -> None:
    automated = try_automated(verbose=verbose)

    if automated:
        scheme_parishes = automated
        source = PINS_URL
        notes = (
            "Cable corridor parishes not yet determinable; cable route "
            "published at Stage 2 consultation (Feb-Mar 2027)."
        )
    else:
        if verbose:
            print(
                "Automated overlay unavailable; using manually verified parish list."
            )
        scheme_parishes = list(KNOWN_SCHEME_PARISHES)
        source = PINS_URL
        notes = (
            "Manually populated; automated download blocked or shapely unavailable. "
            "Parishes confirmed from EN0110044 application documents. "
            "Cable corridor parishes not yet determinable."
        )

    result = {
        "scheme_parishes": scheme_parishes,
        "corridor_parishes": [],
        "source": source,
        "ons_source": (
            "ONS Open Geography Portal: "
            "Parishes and Non Civil Parished Areas Dec 2023"
        ),
        "checked_date": datetime.date.today().isoformat(),
        "notes": notes,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if verbose:
        print(f"Written {OUT_PATH}: {len(scheme_parishes)} scheme parishes")
        print("Parishes:", ", ".join(scheme_parishes))


if __name__ == "__main__":
    main()
