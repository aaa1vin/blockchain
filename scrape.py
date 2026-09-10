import re
import requests
from datetime import datetime, timezone

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "fork-monitor/1.0"
}

PROJECTS = [
    {"component": "Bitcoin Core",          "repo": "bitcoin/bitcoin"},
    {"component": "Bitcoin Cash Node",     "repo": "bitcoin-cash-node/bitcoin-cash-node"},
    {"component": "Cardano",               "repo": "IntersectMBO/cardano-node"},
    {"component": "Cardano-Ogmios",        "repo": "CardanoSolutions/ogmios"},
    {"component": "Cardano-Wallet",        "repo": "cardano-foundation/cardano-wallet"},
    {"component": "Ethereum",              "repo": "ethereum/go-ethereum"},
    {"component": "Polkadot",              "repo": "paritytech/polkadot-sdk"},
    {"component": "Polkadot-Rest-API",     "repo": "paritytech/polkadot-rest-api"},
    {"component": "Ripple",                "repo": "XRPLF/rippled"},
    {"component": "Solana",                "repo": "anza-xyz/agave"}
]

KEYWORDS = [
    "hard fork",
    "network upgrade",
    "mandatory",
    "must upgrade",
    "activation",
    "runtime upgrade",
    "protocol upgrade",
    "fork",
    "amendment",
    "breaking"
]

DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def gh(repo):
    """Return GitHub stable releases only, newest first."""
    r = requests.get(
        f"https://api.github.com/repos/{repo}/releases",
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()

    releases = r.json()

    stable = [
        rel
        for rel in releases
        if not rel.get("prerelease", False)
        and not re.search(
            r"[-.]?(alpha|beta|rc)([-.]?\d+)?$",
            rel.get("tag_name", ""),
            re.IGNORECASE
        )
    ]

    if not stable:
        raise Exception("No stable release found")

    return stable


def infer(rel):
    """Infer upgrade information from release name and body."""
    name = rel.get("name", "")
    body = rel.get("body", "")

    txt = name + "\n" + body
    low = txt.lower()

    mandatory = any(k in low for k in KEYWORDS)

    upgrade = "-"
    for k in [
        "hard fork",
        "network upgrade",
        "runtime upgrade",
        "amendment"
    ]:
        if k in low:
            upgrade = k.title()
            break

    m = DATE_RE.search(txt)
    activation = m.group(1) if m else "-"

    return mandatory, upgrade, activation


def days(date):
    """Return number of days from today until activation date."""
    if date == "-":
        return "-"

    try:
        d = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
        return str((d - datetime.now(timezone.utc)).days)
    except ValueError:
        return "-"


# Table header
hdr = (
    f"{'Component':22} "
    f"{'Version':12} "
    f"{'Release':10} "
    # f"{'Activation':10} "
    f"{'Days':>6} "
    f"{'Mandatory':10} "
    # f"Source"
)

print(hdr)
print("-" * len(hdr))


# Process projects
for p in PROJECTS:
    try:
        # Get latest stable release only
        rel = gh(p["repo"])[0]

        version = rel.get("tag_name", "?")
        release = rel["published_at"][:10]

        mandatory, upgrade, activation = infer(rel)

        src = rel["html_url"]

        print(
            f"{p['component']:22} "
            f"{version:12} "
            f"{release:10} "
            # f"{activation:10} "
            f"{days(activation):>6} "
            f"{str(mandatory):10} "
            # f"{src}"
        )

    except Exception as e:
        print(
            f"{p['component']:22} "
            f"ERROR: {e}"
        )
