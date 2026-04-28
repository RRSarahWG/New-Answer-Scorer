# ============================================================================
# අනුරාධපුර ඔන්ටොලොජිය — rdflib භාවිතයෙන් OWL ඔන්ටොලොජිය
# අනුරාධපුර යුගයේ සංකල්ප සඳහා පන්ති, පුද්ගලයින්, සහ ගුණාංග නිර්වචනය කරයි
# සියලු ප්‍රතිදානය සිංහලෙන්
# ============================================================================

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
import re


# Define namespace
ANR = Namespace("http://anuradhapura.ontology.org/")

# ============================================================================
# Sinhala display name mappings
# ============================================================================

# Class type labels in Sinhala
CLASS_LABELS_SI = {
    "Ruler": "රජතුමා",
    "BuddhistMonk": "බෞද්ධ භික්ෂුව",
    "IrrigationWork": "වාරිමාර්ග කටයුතු",
    "Stupa": "ස්තූප",
    "Temple": "විහාරය",
    "AdministrativeUnit": "පරිපාලන ඒකකය",
    "TradeRoute": "වෙළඳ මාර්ගය",
    "ArtWork": "කලා කෘතිය",
    "HistoricalEvent": "ඓතිහාසික සිදුවීම",
    "Religion": "ආගම",
}

# Property labels in Sinhala
PROPERTY_LABELS_SI = {
    "ruled_during": "රජකළ කාලය",
    "built_by": "ඉදිකළේ",
    "introduced_by": "හඳුන්වා දුන්නේ",
    "followed_by": "පසුව පැමිණියේ",
    "associated_with": "සම්බන්ධ",
    "located_in": "පිහිටා ඇත්තේ",
    "constructed_in_period": "ඉදිකළ කාලය",
}

# Individual labels in Sinhala
INDIVIDUAL_LABELS_SI = {
    "DevanampiyaTissa": "දේවානම්පියතිස්ස රජු",
    "Dutugamunu": "දුටුගැමුණු රජු",
    "Valagamba": "වළගම්බා රජු",
    "Mahasen": "මහසේන් රජු",
    "MahindaThero": "මිහිඳු මාහිමිපාණෝ",
    "SanghamittaThero": "සංඝමිත්තා තෙරණිය",
    "TissaWewa": "තිස්ස වැව",
    "NuwaraWewa": "නුවර වැව",
    "Minneriya": "මිනේරිය වැව",
    "KalaWewa": "කලා වැව",
    "BasawakkulamaWewa": "බසවක්කුලම වැව",
    "Ruwanwelisaya": "රුවන්වැලිසාය",
    "Jetavanaramaya": "ජේතවනාරාමය",
    "Abhayagiri": "අභයගිරිය",
    "Thuparamaya": "තූපාරාමය",
    "IntroductionOfBuddhism": "බුද්ධාගමය හඳුන්වාදීම",
    "UnificationBattle": "එක්සේසත් කිරීමේ සටන",
    "ConstructionOfRuwanwelisaya": "රුවන්වැලිසාය ඉදිකිරීම",
    "TheravadaBuddhism": "ථේරවාද බුද්ධාගම",
    "Tipitaka": "තිපිටකය",
    "BodhiTree": "බෝධි වෘක්ෂය",
}


def _si_label(uri_name):
    """Get Sinhala label for a URI name, fallback to original name."""
    return INDIVIDUAL_LABELS_SI.get(uri_name, uri_name)


def _si_class(class_name):
    """Get Sinhala class label."""
    return CLASS_LABELS_SI.get(class_name, class_name)


def _si_prop(prop_name):
    """Get Sinhala property label."""
    return PROPERTY_LABELS_SI.get(prop_name, prop_name)


def build_ontology():
    """Build and return the Anuradhapura Period OWL ontology."""
    g = Graph()
    g.bind("anr", ANR)
    g.bind("owl", OWL)

    # ========================================================================
    # CLASSES
    # ========================================================================
    classes = [
        "Ruler", "BuddhistMonk", "IrrigationWork", "Stupa", "Temple",
        "AdministrativeUnit", "TradeRoute", "ArtWork", "HistoricalEvent",
        "Religion"
    ]
    for cls in classes:
        g.add((ANR[cls], RDF.type, OWL.Class))
        g.add((ANR[cls], RDFS.label, Literal(_si_class(cls))))

    # ========================================================================
    # OBJECT PROPERTIES
    # ========================================================================
    properties = [
        ("ruled_during", "රජතුමා රජ කළ කාලය"),
        ("built_by", "ඉදිකිරීම සිදු කළ පුද්ගලයා"),
        ("introduced_by", "හඳුන්වා දුන් පුද්ගලයා"),
        ("followed_by", "පසුව පැමිණි අනුප්‍රාප්තිකයා"),
        ("associated_with", "සාමාන්‍ය සම්බන්ධතාවය"),
        ("located_in", "පිහිටි ස්ථානය"),
        ("constructed_in_period", "ඉදිකිරීමේ කාල සීමාව"),
    ]
    for prop_name, description in properties:
        g.add((ANR[prop_name], RDF.type, OWL.ObjectProperty))
        g.add((ANR[prop_name], RDFS.label, Literal(_si_prop(prop_name))))
        g.add((ANR[prop_name], RDFS.comment, Literal(description)))

    # ========================================================================
    # INDIVIDUALS — Rulers (Sinhala facts)
    # ========================================================================
    rulers = {
        "DevanampiyaTissa": {
            "ruled_during": "ක්‍රි.පූ. 307-267",
            "facts": [
                "ශ්‍රී ලංකාවේ ප්‍රථම බෞද්ධ රජතුමා",
                "අරහත් මිහිඳු මාහිමිපාණන් පිළිගත්තේය",
                "ශ්‍රී ලංකාවේ ප්‍රථම ස්තූපය වන තූපාරාමය ඉදිකළේය",
                "ශ්‍රී මහා බෝධිය රෝපණය කළේය",
                "භාරතයේ අශෝක අධිරාජාගේ සමකාලීන මිත්‍රයෙකි",
                "මහාවිහාර භික්ෂු සංකීර්ණය පිහිටුවන ලදී",
                "මහාමේඝ උද්‍යානය සංඝයාට පරිත්‍යාග කළේය"
            ]
        },
        "Dutugamunu": {
            "ruled_during": "ක්‍රි.පූ. 161-137",
            "facts": [
                "එළාර රජු පරාජය කර ශ්‍රී ලංකාව එක්සේසත් කළේය",
                "රුහුණේ කාවන්තිස්ස රජු සහ විහාරමහාදේවි මව්බිසවගේ පුත්‍රයාය",
                "රුවන්වැලිසාය (මහා ස්තූපය) ඉදිකළේය — උස මීටර් 103ක්",
                "ලෝහප්‍රාසාදය ඉදිකළේය — ගල් කුළුනු 1600ක්",
                "මිරිසවැටි ස්තූපය ඉදිකළේය",
                "ශ්‍රී ලංකාවේ ජාතික වීරයෙකි",
                "එළාර රජු සමග යුද ඇතුන් මත තනි සටනක් කළේය",
                "ඔහුගේ යුද ඇතා කන්දුල නම් වීය"
            ]
        },
        "Valagamba": {
            "ruled_during": "ක්‍රි.පූ. 1 වන සියවස",
            "facts": [
                "අභයගිරි විහාරය පිහිටුවන ලදී",
                "ඔහුගේ රජ සමයේ තිපිටකය අළුවිහාරයේදී ලියා තබන ලදී",
                "දකුණු ඉන්දියානු ආක්‍රමණ වලට මුහුණ දී සිංහාසනය නැවත අත්පත් කර ගත්තේය",
                "බෞද්ධ ශිෂ්‍යත්වයට අනුග්‍රහය දක්වන ලදී"
            ]
        },
        "Mahasen": {
            "ruled_during": "ක්‍රි.ව. 3 වන සියවස (274-301)",
            "facts": [
                "ජේතවනාරාමය ඉදිකළේය — පැරණි ලොව උසම ස්තූපය (මීටර් 122)",
                "මිනේරිය වැව ඉදිකළේය — දැවැන්ත වාරිමාර්ග ඉදිකිරීමක්",
                "ජේතවන විහාරයට අනුග්‍රහය දක්වන ලදී",
                "අනුරාධපුර යුගයේ ශ්‍රේෂ්ඨතම ඉදිකිරීම්කරුවන්ගෙන් කෙනෙකි"
            ]
        }
    }

    for name, info in rulers.items():
        g.add((ANR[name], RDF.type, ANR["Ruler"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        g.add((ANR[name], ANR["ruled_during"], Literal(info["ruled_during"])))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # INDIVIDUALS — Buddhist Monks (Sinhala facts)
    # ========================================================================
    monks = {
        "MahindaThero": {
            "facts": [
                "භාරතයේ අශෝක අධිරාජාගේ පුත්‍රයා (හෝ බෑනා)",
                "ක්‍රි.පූ. 247 දී ශ්‍රී ලංකාවට බුද්ධාගමය හඳුන්වා දුන්නේය",
                "මිහින්තලේට පැමිණ දේවානම්පියතිස්ස රජු හමුවිය",
                "චූලහත්ථිපදෝපම සූත්‍රය දේශනා කළේය",
                "ඉත්තිය, උත්තිය, සම්බල, භද්දසාල යන භික්ෂූන් සමඟ පැමිණියේය"
            ]
        },
        "SanghamittaThero": {
            "facts": [
                "අශෝක අධිරාජාගේ දියණිය",
                "මිහිඳු මාහිමිපාණන්ගේ සහෝදරිය",
                "ශ්‍රී මහා බෝධි වෘක්ෂ පැළය ශ්‍රී ලංකාවට ගෙන ආවාය",
                "භික්ෂුණී ශාසනය (බෞද්ධ භික්ෂුණී ගණය) පිහිටුවන ලදී",
                "ශ්‍රී ලංකාවේ ප්‍රථම කාන්තා පිරිස භික්ෂුණී ශාසනයට උපසම්පදා කළාය"
            ]
        }
    }

    for name, info in monks.items():
        g.add((ANR[name], RDF.type, ANR["BuddhistMonk"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # INDIVIDUALS — Irrigation Works (Sinhala facts)
    # ========================================================================
    irrigation = {
        "TissaWewa": {
            "built_by": "DevanampiyaTissa",
            "period": "ක්‍රි.පූ. 3 වන සියවස",
            "facts": [
                "දේවානම්පියතිස්ස රජු විසින් ඉදිකරන ලදී",
                "අක්කර 550ක් පමණ ආවරණය කළේය",
                "අනුරාධපුර නගරයට ජලය සපයා දුන්නේය",
                "අදටත් ක්‍රියාත්මකව පවතී"
            ]
        },
        "NuwaraWewa": {
            "built_by": None,
            "period": "ක්‍රි.පූ. 1 වන සියවස",
            "facts": [
                "අනුරාධපුර ප්‍රදේශයේ විශාලතම වැව්වලින් එකකි",
                "අක්කර 3200ක් පමණ ආවරණය කරයි",
                "නගර ජල සැපයුම හා කෘෂිකර්මය සඳහා ඉතා වැදගත් විය"
            ]
        },
        "Minneriya": {
            "built_by": "Mahasen",
            "period": "ක්‍රි.ව. 3 වන සියවස",
            "facts": [
                "මහසේන් රජු විසින් ඉදිකරන ලදී",
                "වේල්ල කිලෝමීටර් 3ක් දිගය",
                "පිරුණු විට අක්කර 4670ක් පමණ ආවරණය කරයි",
                "පැරණි වැව් අතරින් අතිශය විශිෂ්ට වැවකි"
            ]
        },
        "KalaWewa": {
            "built_by": None,
            "period": "ක්‍රි.ව. 5 වන සියවස",
            "facts": [
                "ධාතුසේන රජු විසින් ඉදිකරන ලදී",
                "යෝද ඇළ (ජය ගඟ) ඇළ පද්ධතියට සම්බන්ධයි — කිලෝමීටර් 87ක් දිගයි",
                "යෝද ඇළ සැතපුමකට අඟල් 6ක බෑවුමක් පමණි",
                "අතිවිශිෂ්ට ඉංජිනේරු ජයග්‍රහණයකි"
            ]
        },
        "BasawakkulamaWewa": {
            "built_by": None,
            "period": "ක්‍රි.පූ. 4 වන සියවස",
            "facts": [
                "ශ්‍රී ලංකාවේ පැරණිතම වැව් වලින් එකකි",
                "පණ්ඩුකාභය රජු විසින් ඉදිකරන ලදී",
                "අභය වැව ලෙසින්ද හැඳින්වේ"
            ]
        }
    }

    for name, info in irrigation.items():
        g.add((ANR[name], RDF.type, ANR["IrrigationWork"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        g.add((ANR[name], ANR["constructed_in_period"], Literal(info["period"])))
        if info["built_by"]:
            g.add((ANR[name], ANR["built_by"], ANR[info["built_by"]]))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # INDIVIDUALS — Stupas (Sinhala facts)
    # ========================================================================
    stupas = {
        "Ruwanwelisaya": {
            "built_by": "Dutugamunu",
            "period": "ක්‍රි.පූ. 2 වන සියවස",
            "facts": [
                "ශ්‍රී ලංකාවේ වඩාත්ම පූජනීය බෞද්ධ ස්මාරකවලින් එකකි",
                "උස මීටර් 103 (අඩි 338) පමණ වේ",
                "දුටුගැමුණු රජු විසින් ඉදිකරන ලදී",
                "ඇත් සිරුරු සිය ගණනකින් සැරසුණු බිත්තියකින් වට වී ඇත",
                "බෞද්ධ විශ්වවිද්‍යාලයේ මේරු පර්වතය නියෝජනය කරයි",
                "බුදුරදුන්ගේ ශාරීරික ධාතූන් නිධන් කර ඇත"
            ]
        },
        "Jetavanaramaya": {
            "built_by": "Mahasen",
            "period": "ක්‍රි.ව. 3 වන සියවස",
            "facts": [
                "මුලින් ඉදිකළ උසම ස්තූපය — මීටර් 122 (අඩි 400)",
                "පැරණි ලොව තුන්වන උසම ව්‍යුහය (ගීසා පිරමිඩ දෙකට පසුව)",
                "මහසේන් රජු විසින් ඉදිකරන ලදී",
                "පුළුස්සන ලද ගඩොල් මිලියන 93.3ක් පමණ භාවිතා කරන ලදී",
                "ජේතවන විහාර සංකීර්ණයේ මධ්‍යස්ථානය විය",
                "සංකීර්ණය හෙක්ටයාර් 5.6ක් පමණ ආවරණය කළේය"
            ]
        },
        "Abhayagiri": {
            "built_by": "Valagamba",
            "period": "ක්‍රි.පූ. 1 වන සියවස",
            "facts": [
                "වළගම්බා (වට්ටගාමණී අභය) රජු විසින් ඉදිකරන ලදී",
                "උස මීටර් 75ක් පමණ වේ",
                "පැරණි ලොව විශාලතම භික්ෂු සංකීර්ණවලින් එකක කොටසක් විය",
                "භික්ෂූන් 5000ක් පමණ නිවාස ගත කරන ලදී",
                "මහායාන සහ වජ්‍රයාන බලපෑම්වලට විවෘත විය",
                "චීන බෞද්ධ භික්ෂුව ෆාෂියන් ක්‍රි.ව. 5 වන සියවසේ සංචාරය කළේය"
            ]
        },
        "Thuparamaya": {
            "built_by": "DevanampiyaTissa",
            "period": "ක්‍රි.පූ. 3 වන සියවස",
            "facts": [
                "ශ්‍රී ලංකාවේ ඉදිකළ ප්‍රථම බෞද්ධ ස්තූපයය",
                "දේවානම්පියතිස්ස රජු විසින් ඉදිකරන ලදී",
                "බුදුරදුන්ගේ දකුණු අක්ෂිකටාහ ධාතුව නිධන් කර ඇත",
                "මුල් හැඩය ධාන්‍යාකාර (වී ගොඩක) ආකෘතියයි",
                "අරහත් මිහිඳු මාහිමිපාණන් භාරතයෙන් ගෙන එන ලදී"
            ]
        }
    }

    for name, info in stupas.items():
        g.add((ANR[name], RDF.type, ANR["Stupa"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        g.add((ANR[name], ANR["constructed_in_period"], Literal(info["period"])))
        g.add((ANR[name], ANR["built_by"], ANR[info["built_by"]]))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # INDIVIDUALS — Historical Events (Sinhala facts)
    # ========================================================================
    events = {
        "IntroductionOfBuddhism": {
            "facts": [
                "ක්‍රි.පූ. 247 දී දේවානම්පියතිස්ස රජුගේ රාජ්‍ය සමයේ සිදුවිය",
                "බුද්ධාගමය අරහත් මිහිඳු මාහිමිපාණන් විසින් භාරතයෙන් ගෙන එන ලදී",
                "මිහිඳු මාහිමිපාණෝ අශෝක අධිරාජාගේ පුත්‍රයා/බෑනාය",
                "මිහින්තලේ කන්දේ ප්‍රථම හමුවීම සිදුවිය",
                "ශ්‍රී ලංකා සමාජය, කලාව, සහ පාලනය පරිවර්තනය කළේය"
            ]
        },
        "UnificationBattle": {
            "facts": [
                "දුටුගැමුණු රජු ශ්‍රී ලංකාව එක්සේසත් කිරීම සඳහා සටන් කළේය",
                "වසර 44ක් අනුරාධපුරය පාලනය කළ චෝළ කුමාරයා එළාර පරාජය කළේය",
                "අනුරාධපුරයේ දකුණු දොරටුවේ අවසාන සටන පැවැත්විණි",
                "දෙදෙනාම යුද ඇතුන් මත තනි සටනක් කළහ",
                "දුටුගැමුණු රජු එළාර සඳහා අවමඟුල් ස්මාරකයක් ඉදිකළේය"
            ]
        },
        "ConstructionOfRuwanwelisaya": {
            "facts": [
                "ක්‍රි.පූ. 2 වන සියවසේ දුටුගැමුණු රජු විසින් ආරම්භ කරන ලදී",
                "පැරණි ලොව විශාලතම ස්තූපවලින් එකකි",
                "ඉදිකිරිම සඳහා මුළු රාජධානියම සම්බන්ධ විය",
                "උස මීටර් 103ක් පමණ වේ",
                "බුදුරදුන්ගේ ශාරීරික ධාතූන් නිධන් කර ඇත"
            ]
        }
    }

    for name, info in events.items():
        g.add((ANR[name], RDF.type, ANR["HistoricalEvent"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # INDIVIDUALS — Religion (Sinhala facts)
    # ========================================================================
    religion = {
        "TheravadaBuddhism": {
            "facts": [
                "ක්‍රි.පූ. 247 සිට ශ්‍රී ලංකාවේ ප්‍රධාන ආගමික සම්ප්‍රදායයයි",
                "මහාවිහාර භික්ෂු සම්ප්‍රදාය හරහා සංරක්ෂණය කරන ලදී",
                "පාලි ග්‍රන්ථමාලාව (තිපිටකය) මත පදනම් වේ",
                "ශ්‍රී ලංකාවේ සිට අග්නිදිග ආසියාවට ව්‍යාප්ත විය",
                "මහා ධර්ම විවරණකරු බුද්ධඝෝෂ හිමි මහාවිහාරයේ වැඩ කළේය"
            ]
        },
        "Tipitaka": {
            "facts": [
                "බුදු පිටක තුන: විනය පිටකය, සුත්ත පිටකය, අභිධම්ම පිටකය",
                "වළගම්බා රජුගේ රාජ්‍ය සමයේ අළුවිහාරයේදී ප්‍රථම වරට ලියා තබන ලදී",
                "ක්‍රි.පූ. 1 වන සියවසේ පුස්කොළ මත ලියන ලදී",
                "ශ්‍රී ලංකාව ලිඛිත පාලි ග්‍රන්ථමාලාවේ භාරකරු බවට පත්විය",
                "මුලින් සියවස් ගණනාවක් මුඛ පාඨ සම්ප්‍රදායෙන් සම්ප්‍රේෂණය කරන ලදී"
            ]
        },
        "BodhiTree": {
            "facts": [
                "සංඝමිත්තා තෙරණිය විසින් ශ්‍රී ලංකාවට ගෙන එන ලදී",
                "භාරතයේ බෝධ් ගයාවේ මුල් බෝධි වෘක්ෂයේ පැළයකි",
                "දේවානම්පියතිස්ස රජු විසින් අනුරාධපුරයේ රෝපණය කරන ලදී",
                "ලෝකයේ පැරණිතම ඓතිහාසික ලේඛනගත වෘක්ෂයයි — වසර 2300කට වඩා පැරණිය",
                "බුදුරදුන් බුද්ධත්වයට පත්වූ ගස"
            ]
        }
    }

    for name, info in religion.items():
        g.add((ANR[name], RDF.type, ANR["Religion"]))
        g.add((ANR[name], RDFS.label, Literal(_si_label(name))))
        for fact in info["facts"]:
            g.add((ANR[name], ANR["associated_with"], Literal(fact)))

    # ========================================================================
    # KEY RELATIONSHIPS
    # ========================================================================
    g.add((ANR["IntroductionOfBuddhism"], ANR["introduced_by"], ANR["MahindaThero"]))
    g.add((ANR["DevanampiyaTissa"], ANR["followed_by"], ANR["Dutugamunu"]))
    g.add((ANR["MahindaThero"], ANR["associated_with"], ANR["IntroductionOfBuddhism"]))
    g.add((ANR["SanghamittaThero"], ANR["associated_with"], ANR["BodhiTree"]))
    g.add((ANR["Ruwanwelisaya"], ANR["located_in"], Literal("අනුරාධපුරය")))
    g.add((ANR["Jetavanaramaya"], ANR["located_in"], Literal("අනුරාධපුරය")))
    g.add((ANR["Abhayagiri"], ANR["located_in"], Literal("අනුරාධපුරය")))
    g.add((ANR["Thuparamaya"], ANR["located_in"], Literal("අනුරාධපුරය")))
    g.add((ANR["TissaWewa"], ANR["located_in"], Literal("අනුරාධපුරය")))
    g.add((ANR["NuwaraWewa"], ANR["located_in"], Literal("අනුරාධපුරය")))

    return g


# ============================================================================
# QUERY FUNCTIONS — All output in Sinhala
# ============================================================================

def query_ontology(keywords, graph=None):
    """
    Query the ontology for concepts matching the given keywords.
    Returns a formatted Sinhala string of matching concepts and their facts.
    """
    if graph is None:
        graph = build_ontology()

    results = []
    keywords_lower = [kw.lower().strip() for kw in keywords if kw.strip()]

    seen_subjects = set()

    for subj in set(graph.subjects()):
        subj_str = str(subj)
        uri_name = subj_str.split("/")[-1]

        # Get the label
        label_list = list(graph.objects(subj, RDFS.label))
        label = str(label_list[0]) if label_list else uri_name
        label_lower = label.lower()
        uri_lower = uri_name.lower()

        # Check if any keyword matches
        matched = False
        for kw in keywords_lower:
            if kw in uri_lower or kw in label_lower:
                matched = True
                break

        if not matched or subj_str in seen_subjects:
            continue

        seen_subjects.add(subj_str)

        # Get class type in Sinhala
        types = list(graph.objects(subj, RDF.type))
        type_labels = []
        for t in types:
            t_name = str(t).split("/")[-1]
            if t_name not in ["Class", "ObjectProperty"]:
                type_labels.append(_si_class(t_name))

        # Get all associated facts (already in Sinhala)
        facts = [str(f) for f in graph.objects(subj, ANR["associated_with"])
                 if isinstance(f, Literal)]

        # Get built_by relationship
        builders = list(graph.objects(subj, ANR["built_by"]))
        builder_str = ""
        if builders:
            b_name = str(builders[0]).split("/")[-1]
            builder_str = f"  - ඉදිකළේ: {_si_label(b_name)}"

        # Get period
        periods = list(graph.objects(subj, ANR["constructed_in_period"]))
        period_str = ""
        if periods:
            period_str = f"  - ඉදිකළ කාලය: {str(periods[0])}"

        # Get ruled_during
        ruled = list(graph.objects(subj, ANR["ruled_during"]))
        ruled_str = ""
        if ruled:
            ruled_str = f"  - රජකළ කාලය: {str(ruled[0])}"

        # Build the Sinhala entry
        entry = f"**{label}** (වර්ගය: {', '.join(type_labels)})"
        if builder_str:
            entry += "\n" + builder_str
        if period_str:
            entry += "\n" + period_str
        if ruled_str:
            entry += "\n" + ruled_str
        if facts:
            entry += "\n" + "\n".join(f"  - {f}" for f in facts)

        results.append(entry)

    if not results:
        return "ගැලපෙන ඔන්ටොලොජි සංකල්ප හමු නොවීය."

    return "\n\n".join(results)


def get_ontology_context(question_topic, graph=None):
    """
    Get relevant ontology context for a question topic.
    Returns Sinhala formatted string.
    """
    if graph is None:
        graph = build_ontology()

    # Map topics to relevant keywords
    topic_keywords = {
        "Irrigation Systems": [
            "tissa", "wewa", "nuwara", "minneriya", "kala", "basawakkulama",
            "irrigation", "tank", "canal"
        ],
        "Introduction of Buddhism": [
            "mahinda", "sanghamitta", "buddhism", "bodhi", "devanampiya",
            "tipitaka", "theravada"
        ],
        "Notable Rulers": [
            "devanampiya", "dutugamunu", "valagamba", "mahasen", "ruler",
            "ruwanwelisaya", "thuparamaya"
        ],
        "Administrative Systems": [
            "ruler", "devanampiya", "dutugamunu", "administrative",
            "theravada", "buddhism"
        ],
        "Art and Architecture": [
            "ruwanwelisaya", "jetavanaramaya", "abhayagiri", "thuparamaya",
            "stupa", "art", "moonstone"
        ]
    }

    keywords = topic_keywords.get(question_topic, [question_topic.lower().split()])
    return query_ontology(keywords, graph)


def get_all_concepts(graph=None):
    """
    Return a list of all individuals and their relationships from the ontology.
    """
    if graph is None:
        graph = build_ontology()

    concepts = []
    seen = set()
    for subj, _, obj in graph.triples((None, RDF.type, None)):
        if str(obj) == str(OWL.Class) or str(obj) == str(OWL.ObjectProperty):
            continue
        subj_str = str(subj)
        if subj_str in seen:
            continue
        seen.add(subj_str)

        label_list = list(graph.objects(subj, RDFS.label))
        label = str(label_list[0]) if label_list else subj_str.split("/")[-1]
        type_name = str(obj).split("/")[-1]

        facts = [str(f) for f in graph.objects(subj, ANR["associated_with"])
                 if isinstance(f, Literal)]

        concepts.append({
            "name": label,
            "type": _si_class(type_name),
            "facts": facts
        })

    return concepts


# ============================================================================
# Module test
# ============================================================================
if __name__ == "__main__":
    print("ඔන්ටොලොජිය ගොඩනඟමින්...")
    g = build_ontology()
    print(f"ඔන්ටොලොජියේ ත්‍රිත්ව {len(g)}ක් ඇත.\n")

    print("=== විමසුම: 'dutugamunu' ===")
    print(query_ontology(["dutugamunu"], g))

    print("\n=== වාරිමාර්ග පද්ධති සන්දර්භය ===")
    print(get_ontology_context("Irrigation Systems", g))

    print(f"\n=== මුළු සංකල්ප: {len(get_all_concepts(g))} ===")
    for c in get_all_concepts(g):
        print(f"  {c['type']}: {c['name']}")
