"""UK energy-industry domain knowledge used to focus queries and score relevance.

Kept separate from sources.py/pipeline.py so the vocabulary can be extended
(new regulators, companies, policy terms) without touching fetch logic.
"""
from __future__ import annotations

UK_ENERGY_SUBREDDITS = [
    "unitedkingdom",
    "CasualUK",
    "AskUK",
    "ukpolitics",
    "energy",
    "UKPersonalFinance",
    "solar",
    "electricvehicles",
]

REGULATORS_AND_BODIES = [
    "Ofgem",
    "NESO",
    "National Energy System Operator",
    "National Grid ESO",
    "DESNZ",
    "Department for Energy Security and Net Zero",
    "NSTA",
    "North Sea Transition Authority",
    "Crown Estate",
    "Climate Change Committee",
    "CCC",
]

MAJOR_COMPANIES = [
    "National Grid",
    "SSE",
    "Octopus Energy",
    "Centrica",
    "British Gas",
    "EDF Energy",
    "ScottishPower",
    "Iberdrola",
    "E.ON",
    "RWE",
    "Orsted",
    "Ørsted",
    "Rolls-Royce SMR",
    "Drax",
    "Shell",
    "BP",
    "Equinor",
    "Uniper",
    "OVO Energy",
]

POLICY_TERMS = [
    "Contracts for Difference",
    "CfD",
    "Capacity Market",
    "RIIO",
    "price cap",
    "standing charge",
    "net zero",
    "offshore wind",
    "small modular reactor",
    "SMR",
    "hydrogen strategy",
    "heat pump",
    "grid connection queue",
    "carbon capture",
    "CCUS",
    "REGO",
    "ROC",
    "interconnector",
    "gas storage",
    "North Sea",
    "warm home discount",
    "energy security",
]

RELEVANCE_VOCAB = sorted(
    {
        w.lower()
        for w in (
            REGULATORS_AND_BODIES
            + MAJOR_COMPANIES
            + POLICY_TERMS
            + ["energy", "electricity", "gas", "power", "grid", "renewable", "uk"]
        )
    }
)

# GOV.UK organisation slugs relevant to energy policy/regulation, kept for
# reference/future filtering (the current govuk source uses site-wide search).
GOVUK_ORGANISATIONS = [
    "department-for-energy-security-and-net-zero",
    "ofgem",
    "nstauthority",
    "office-for-nuclear-regulation",
]

# WordPress-style trade press feeds. These are recency feeds (not searchable),
# so fetch_trade_press() pulls recent entries and keyword-filters them locally.
TRADE_PRESS_RSS_FEEDS = {
    "Utility Week": "https://utilityweek.co.uk/feed/",
    "Current±": "https://www.current-news.co.uk/feed/",
    "edie": "https://www.edie.net/rss/",
    "Solar Power Portal": "https://www.solarpowerportal.co.uk/feed",
    "Smart Energy International": "https://www.smart-energy.com/feed/",
}

# London-listed tickers with meaningful UK energy exposure, used to scope the
# StockTwits symbol streams.
ENERGY_STOCK_TICKERS = ["NG", "SSE", "CNA", "DRX", "SHEL", "BP.", "UU"]
