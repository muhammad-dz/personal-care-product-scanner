"""Ingredient rules used by the scorer.

Each rule has one or more regex patterns that are matched against a single
ingredient name (lower-cased). Patterns are anchored on letter boundaries by
the scorer, so "ethylparaben" will not match inside "methylparaben".

Set `whole=True` when the pattern should only match the entire ingredient
name. Plain "alcohol" on an INCI list means ethanol, but "cetearyl alcohol"
is a fatty alcohol that is fine for skin.

Concerns are checked before benefits and the first matching rule wins.

The concerns listed here are simplified and the points are my own judgement,
not medical advice.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    patterns: tuple
    reason: str
    level: str = ""  # "high" / "medium" / "low" for concerns
    points: int = 0  # positive for beneficial ingredients
    whole: bool = False


CONCERNS = [
    Rule("paraben", (r"(methyl|ethyl|propyl|butyl|isobutyl|isopropyl|benzyl)paraben",),
         "Preservative with possible endocrine effects", level="high"),
    Rule("formaldehyde releaser", (r"dmdm hydantoin", r"quaternium-15", r"diazolidinyl urea",
                                   r"imidazolidinyl urea", r"bronopol"),
         "Slowly releases formaldehyde, a known sensitiser", level="high"),
    Rule("phthalate", (r"[a-z]* ?phthalate",), "Plasticiser linked to hormone disruption", level="high"),
    Rule("triclosan", (r"triclosan",), "Antibacterial linked to hormone disruption", level="high"),
    Rule("hydroquinone", (r"hydroquinone",), "Skin lightener restricted in the UK and EU", level="high"),
    Rule("oxybenzone", (r"oxybenzone", r"benzophenone-3"), "UV filter that can cause allergic reactions",
         level="high"),

    Rule("sulfate", (r"sodium lauryl sulfate", r"sodium laureth sulfate", r"ammonium lauryl sulfate"),
         "Harsh surfactant that can strip and irritate skin", level="medium"),
    Rule("fragrance", (r"fragrance", r"parfum", r"perfume"),
         "Undisclosed mix and one of the most common allergens", level="medium"),
    Rule("drying alcohol", (r"alcohol denat\.?", r"denatured alcohol", r"sd alcohol",
                            r"isopropyl alcohol", r"ethanol"),
         "Can dry out and irritate skin", level="medium"),
    Rule("drying alcohol", (r"alcohol",), "Can dry out and irritate skin", level="medium", whole=True),
    Rule("peg compound", (r"peg-\d+",), "May carry traces of 1,4-dioxane from manufacturing", level="medium"),
    Rule("chemical uv filter", (r"octinoxate", r"ethylhexyl methoxycinnamate", r"homosalate"),
         "UV filter with hormone disruption concerns", level="medium"),

    Rule("silicone", (r"dimethicone", r"cyclomethicone", r"cyclopentasiloxane"),
         "Can feel heavy and clog pores for some people", level="low"),
    Rule("retinyl palmitate", (r"retinyl palmitate",), "May increase sun sensitivity", level="low"),
    Rule("octocrylene", (r"octocrylene",), "UV filter that can irritate sensitive skin", level="low"),
]

BENEFITS = [
    Rule("niacinamide", (r"niacinamide",), "Strengthens the skin barrier and evens tone", points=8),
    Rule("vitamin c", (r"ascorbic acid", r"vitamin c", r"ascorbyl glucoside",
                       r"sodium ascorbyl phosphate"), "Antioxidant and brightening", points=8),
    Rule("hyaluronic acid", (r"hyaluronic acid", r"sodium hyaluronate"), "Draws water into the skin", points=6),
    Rule("ceramide", (r"ceramides?",), "Repairs the skin barrier", points=6),
    Rule("retinol", (r"retinol",), "Well studied anti-ageing ingredient", points=6),
    Rule("azelaic acid", (r"azelaic acid",), "Helps with acne and redness", points=6),
    Rule("peptide", (r"[a-z-]*peptides?",), "Supports collagen", points=5),
    Rule("centella", (r"centella asiatica", r"madecassoside"), "Soothing", points=5),
    Rule("exfoliating acid", (r"salicylic acid", r"glycolic acid", r"lactic acid"), "Gentle exfoliation",
         points=4),
    Rule("squalane", (r"squalane",), "Lightweight moisturiser", points=4),
    Rule("antioxidant", (r"tocopherol", r"vitamin e", r"green tea", r"camellia sinensis",
                         r"resveratrol", r"ferulic acid"), "Antioxidant", points=3),
    Rule("soothing", (r"panthenol", r"allantoin", r"aloe barbadensis", r"aloe vera",
                      r"beta-glucan", r"bisabolol"), "Soothing and moisturising", points=3),
    Rule("humectant", (r"glycerin",), "Keeps skin hydrated", points=2),
    Rule("mineral sunscreen", (r"zinc oxide", r"titanium dioxide"), "Gentle mineral UV protection", points=4),
    Rule("butter", (r"shea butter", r"butyrospermum parkii", r"cocoa butter"), "Nourishing", points=2),
]
