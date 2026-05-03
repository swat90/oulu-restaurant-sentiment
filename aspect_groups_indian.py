"""
aspect_groups_indian.py  —  Exhaustive EN + FI aspect keyword lists
for Indian restaurant sentiment analysis in Oulu, Finland.

Design principles:
  - Every aspect covers ALL natural ways a reviewer might mention it
  - Includes: formal words, casual/slang, pronouns-in-context, common misspellings,
    abbreviations, negative framings, Finnish words + common inflections
  - Finnish is agglutinative — we include common stem + frequent case endings
    (partitive, genitive, allative, etc.) because regex \b word boundary
    won't catch mid-word suffixes in Finnish
"""

ASPECT_GROUPS = {

    # ══════════════════════════════════════════════════════════════
    # SERVICE & STAFF  — most synonym-rich category in reviews
    # ══════════════════════════════════════════════════════════════
    "Service & Staff": {
        "en": [
            # Job titles / roles
            "staff", "waiter", "waitress", "server", "bartender", "host", "hostess",
            "manager", "owner", "chef", "cook", "cashier", "receptionist",
            "employee", "worker", "team", "crew", "personnel",
            # Informal / how reviewers actually write
            "guy", "girl", "boy", "lady", "man", "woman", "he", "she", "they",
            "the person", "the people", "everyone", "somebody", "no one",
            "the one who", "our server", "our waiter", "our waitress",
            # Service descriptors — positive
            "friendly", "helpful", "attentive", "polite", "courteous", "kind",
            "welcoming", "warm", "professional", "efficient", "prompt", "quick",
            "fast", "excellent service", "great service", "good service",
            "outstanding service", "wonderful", "amazing staff", "lovely staff",
            "nice staff", "sweet", "charming", "accommodating", "patient",
            "knowledgeable", "informative", "proactive", "went above and beyond",
            "came to check", "checked on us", "made us feel welcome",
            # Service descriptors — negative
            "rude", "unfriendly", "unhelpful", "impolite", "dismissive",
            "ignorant", "ignored", "ignored us", "ignored me", "ignored our table",
            "slow service", "bad service", "terrible service", "poor service",
            "awful service", "horrible service", "inattentive", "careless",
            "unprofessional", "arrogant", "condescending", "disinterested",
            "indifferent", "cold", "snobbish", "disrespectful", "abrupt",
            "we waited", "waited forever", "waited long", "long wait",
            "nobody came", "had to ask", "had to wave", "had to call",
            "took forever", "took too long", "never came back",
            # Communication / language
            "language barrier", "didn't understand", "couldn't communicate",
            "speaks english", "no english", "speaks finnish", "communication",
            # Reservation / booking
            "reservation", "booking", "booked", "table was ready", "table not ready",
            "they lost our reservation", "no record of booking",
            # Mistakes / errors
            "wrong order", "wrong dish", "made a mistake", "order was wrong",
            "mixed up", "forgot", "forgot our order", "forgot to bring",
        ],
        "fi": [
            # Job titles
            "henkilökunta", "tarjoilija", "omistaja", "kokki", "keittiömestari",
            "kassahenkilö", "vastaanottaja", "johtaja", "esimies", "tiimi",
            # Informal
            "tyttö", "poika", "nainen", "mies", "hän", "he", "ne",
            "henkilö", "ihmiset", "kaikki", "kukaan",
            # Positive descriptors + Finnish inflections
            "ystävällinen", "ystävällistä", "ystävällisesti", "ystävällisen",
            "auttavainen", "avulias", "avuliasta", "kohtelias", "kohteliasta",
            "ammattimainen", "ammattitaitoinen", "tehokas", "nopea", "ripeä",
            "palvelualtis", "iloinen", "miellyttävä", "mukava", "asiantunteva",
            "hyvä palvelu", "erinomainen palvelu", "loistava palvelu",
            "tervetullut", "vastaanotto", "hyvä vastaanotto",
            # Negative descriptors + inflections
            "epäystävällinen", "töykeä", "töykeää", "huono palvelu",
            "huonoa palvelua", "hidas palvelu", "hidasta palvelua",
            "ei kukaan tullut", "odotimme", "joutui odottamaan",
            "pitkä odotus", "ei välitetty", "ei huomioitu", "sivuuttivat",
            "epäammattimainen", "välinpitämätön",
            # Reservation
            "varaus", "pöytävaraus", "varasin", "pöytä ei ollut valmiina",
            # Order mistakes
            "väärä tilaus", "väärä annos", "unohtivat", "unohdettiin",
        ],
        "concepts": [
            "staff service waiter friendly rude helpful attentive slow",
            "henkilökunta palvelu tarjoilija ystävällinen töykeä",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # CHICKEN DISHES
    # ══════════════════════════════════════════════════════════════
    "Chicken Dishes": {
        "en": [
            # Dish names
            "chicken", "butter chicken", "chicken tikka masala", "chicken tikka",
            "tandoori chicken", "chicken korma", "chicken vindaloo", "chicken madras",
            "chicken saag", "chicken jalfrezi", "chicken balti", "chicken dopiaza",
            "chicken bhuna", "chicken biryani", "chicken curry", "chicken kebab",
            "chicken seekh kebab", "chicken shashlik", "chicken makhani",
            "chicken karahi", "chicken masala", "chicken pasanda",
            "half chicken", "quarter chicken", "whole chicken",
            # Informal / how people write it
            "chick", "chkn", "poultry",
            # Preparation style
            "grilled chicken", "roasted chicken", "fried chicken",
            "marinated chicken", "spiced chicken", "stuffed chicken",
            # Quality descriptors specific to chicken
            "juicy", "dry chicken", "overcooked chicken", "undercooked chicken",
            "raw chicken", "tender chicken", "tough chicken", "crispy chicken",
            "moist", "succulent", "rubbery", "chewy",
            # Specific parts
            "chicken breast", "chicken thigh", "chicken leg", "chicken wing",
            "chicken drumstick", "boneless", "bone-in", "on the bone",
        ],
        "fi": [
            "kana", "kanaa", "kanan", "kanalle", "kanasta",
            "kana tikka", "kanacurry", "kanabirijaani", "kanakebab",
            "grillattu kana", "tandoorikana", "butterkana",
            "mehevä", "kuiva kana", "ylikypsä kana",
        ],
        "concepts": [
            "chicken tikka masala butter chicken tandoori biryani curry",
            "kana kanaruoka kanacurry",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # LAMB & MUTTON
    # ══════════════════════════════════════════════════════════════
    "Lamb & Mutton Dishes": {
        "en": [
            "lamb", "mutton", "rogan josh", "lamb curry", "lamb biryani",
            "lamb chop", "lamb kebab", "lamb korma", "lamb vindaloo",
            "lamb saag", "lamb jalfrezi", "lamb madras", "lamb karahi",
            "lamb tikka", "lamb shank", "lamb mince",
            "seekh kebab", "gosht", "keema", "keema matar",
            "minced lamb", "ground lamb", "slow cooked lamb",
            "tender lamb", "tough lamb", "dry lamb", "juicy lamb",
            "rack of lamb", "shoulder of lamb", "leg of lamb",
        ],
        "fi": [
            "karitsa", "karitsaa", "karitsan", "karitsalle", "karitsasta",
            "lammas", "lammasta", "lampaan", "lampaalle", "lampaasta",
            "karitsacurry", "karitsabirijaani", "karitsapaisti",
        ],
        "concepts": [
            "lamb mutton rogan josh biryani kebab gosht keema",
            "karitsa lammas karitsacurry",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # VEGETARIAN & VEGAN OPTIONS
    # ══════════════════════════════════════════════════════════════
    "Vegetarian & Vegan Options": {
        "en": [
            # Labels
            "vegetarian", "vegan", "plant-based", "plant based", "meat-free",
            "meat free", "dairy-free", "dairy free", "egg-free", "gluten free",
            "v option", "veg option", "veggie", "veggie option",
            # Dishes
            "paneer", "palak paneer", "saag paneer", "paneer tikka",
            "paneer butter masala", "mutter paneer", "paneer biryani",
            "aloo", "aloo gobi", "aloo mutter", "aloo saag", "aloo jeera",
            "dal", "dahl", "daal", "dal makhani", "dal tadka", "dal fry",
            "chana", "chana masala", "chole", "chick pea", "chickpea",
            "lentil", "lentils", "red lentil", "yellow lentil",
            "gobi", "cauliflower", "spinach", "saag", "bhindi", "okra",
            "baingan", "aubergine", "eggplant", "courgette",
            "mixed vegetable", "vegetable curry", "vegetable biryani",
            "mushroom curry", "mushroom masala",
            "tofu", "jackfruit", "vegan cheese",
            # Inquiries / requests
            "is there a vegan option", "do you have vegetarian",
            "no meat", "without meat", "without dairy", "no dairy",
            "can be made vegan", "vegan friendly",
            # Negative — lack of options
            "no vegan", "no vegetarian", "limited vegan", "limited vegetarian",
            "not enough vegan", "not many vegetarian options",
        ],
        "fi": [
            "kasvisruoka", "kasvisruokaa", "kasvisvaihtoehto", "kasvikset",
            "vegaaninen", "vegaanista", "vegaaniruoka", "vegaanivaihtoehto",
            "kasvis", "kasvisannos", "vegaaniannos",
            "lihatonruoka", "lihaton", "maitoton",
            "linssit", "linssejä", "kikherneistä", "kikherne", "kikhernesoppa",
            "pinaatti", "pinaattia", "kukkakaali", "kukkakaalin",
            "kasviskarry", "kasvisbiryani", "paneer",
            "ei lihaa", "ilman lihaa", "vain kasvis",
            "ei vegaanisuutta", "vähän kasvisvaihtoehtoja",
        ],
        "concepts": [
            "vegetarian vegan paneer dal chana aloo saag plant-based",
            "kasvisruoka vegaaninen paneer dal linssit",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # BEEF DISHES
    # ══════════════════════════════════════════════════════════════
    "Beef Dishes": {
        "en": [
            "beef", "beef curry", "beef biryani", "beef kebab", "beef vindaloo",
            "beef madras", "beef karahi", "beef tikka", "beef masala",
            "beef steak", "beef keema", "minced beef", "ground beef",
            "slow cooked beef", "tender beef", "tough beef",
            "cow", "ox",
        ],
        "fi": [
            "nauta", "nautaa", "naudanliha", "naudanlihaa", "naudanlihas",
            "nautacurry", "nautabirijaani", "nautakebab",
            "lehmä", "härkä",
        ],
        "concepts": ["beef curry biryani vindaloo keema", "nauta naudanliha nautacurry"],
    },

    # ══════════════════════════════════════════════════════════════
    # SEAFOOD
    # ══════════════════════════════════════════════════════════════
    "Seafood": {
        "en": [
            "fish", "prawn", "prawns", "shrimp", "king prawn", "tiger prawn",
            "lobster", "crab", "mussels", "squid", "scallop", "cod",
            "salmon", "sea bass", "monkfish", "halibut",
            "fish curry", "prawn curry", "prawn masala", "prawn biryani",
            "fish tikka", "fish masala", "fish vindaloo", "fish biryani",
            "goan fish", "kerala fish", "malabar fish",
            "seafood", "sea food", "fruits de mer",
            "fresh fish", "frozen fish", "overcooked fish", "dry fish",
        ],
        "fi": [
            "kala", "kalaa", "kalan", "kalalle", "kalasta",
            "katkarapu", "katkarapua", "katkaravut", "katkarapuja",
            "meriruoka", "äyriäinen", "äyriäisiä",
            "lohta", "lohi", "turska", "sei",
            "kalacurry", "katkarapucurry", "kalamasala",
        ],
        "concepts": [
            "fish prawn shrimp seafood curry tikka biryani",
            "kala katkarapu meriruoka äyriäinen",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # BREAD & RICE
    # ══════════════════════════════════════════════════════════════
    "Bread & Rice": {
        "en": [
            # Breads
            "naan", "garlic naan", "cheese naan", "peshwari naan", "keema naan",
            "roti", "chapati", "chapatti", "paratha", "aloo paratha",
            "puri", "bhatura", "kulcha", "bread",
            "bread basket", "complimentary bread", "poppadom", "papadum",
            # Rice
            "rice", "basmati", "basmati rice", "plain rice", "boiled rice",
            "biryani", "chicken biryani", "lamb biryani", "vegetable biryani",
            "prawn biryani", "beef biryani", "egg biryani",
            "pilau", "pilaf", "jeera rice", "saffron rice", "fried rice",
            # Quality
            "fluffy naan", "dry naan", "burnt naan", "cold naan",
            "soft bread", "hard bread", "overcooked rice", "undercooked rice",
            "stodgy rice", "clumpy rice", "perfect rice",
        ],
        "fi": [
            "naan", "naania", "naanleipä", "valkosipulinaan", "juustonaan",
            "roti", "chapati", "paratha", "birijaani", "birijaania",
            "riisi", "riisiä", "basmati", "basmatiriisi", "keitetty riisi",
            "paahtoleipä", "focaccia", "papadum",
        ],
        "concepts": [
            "naan bread biryani rice roti paratha garlic",
            "naan birijaani riisi roti paratha",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # CURRY & SAUCE QUALITY
    # ══════════════════════════════════════════════════════════════
    "Curry & Sauce": {
        "en": [
            # Curry names
            "curry", "masala", "tikka masala", "korma", "vindaloo", "madras",
            "jalfrezi", "balti", "dopiaza", "bhuna", "pasanda", "saag",
            "rogan josh", "dhansak", "pathia", "phaal", "karahi",
            # Sauce descriptors
            "sauce", "gravy", "base", "tomato base", "creamy", "rich",
            "thick sauce", "thin sauce", "watery", "watery sauce",
            "coconut milk", "cream", "yoghurt", "butter",
            # Flavor
            "flavorful", "flavourful", "tasty", "bland", "tasteless",
            "delicious sauce", "amazing curry", "perfect curry",
            "too sour", "too sweet", "too salty", "not enough flavor",
            # Spice in sauce
            "well-spiced", "aromatic", "fragrant", "herby",
            "fresh spices", "stale spices", "old spices",
        ],
        "fi": [
            "curry", "currya", "curryn", "curryle", "currykastike",
            "kastike", "kastiketta", "kastikkeen", "kastikkeessa",
            "maustekastike", "kermainen", "kermaista", "tomaattipohja",
            "paksu", "ohut", "vetinen", "maukas", "mauton", "mautonta",
            "hyvä kastike", "upea curry", "täyteläinen",
        ],
        "concepts": [
            "curry sauce korma vindaloo masala tikka rich creamy",
            "curry kastike korma maukas kermainen",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # STARTERS & STREET FOOD
    # ══════════════════════════════════════════════════════════════
    "Starters & Street Food": {
        "en": [
            "starter", "starters", "appetizer", "appetisers", "side",
            "samosa", "samosas", "pakora", "pakoras", "bhaji", "bhajis",
            "onion bhaji", "spinach pakora", "vegetable pakora",
            "poppadom", "papadum", "poppadoms", "crispy",
            "chutney", "mango chutney", "mint chutney", "tamarind",
            "raita", "yoghurt dip",
            "kebab", "seekh kebab", "shish kebab", "kebab starter",
            "chicken tikka starter", "lamb tikka starter",
            "soup", "mulligatawny", "lentil soup",
            "chaat", "chat", "bhel puri", "pani puri", "gol gappa",
            "aloo tikki", "papdi chaat",
            "spring roll",
        ],
        "fi": [
            "alkuruoka", "alkuruokaa", "alkupala", "alkupaloja",
            "samosa", "pakora", "bhaji", "sivu-annos",
            "dippisoosi", "chutney", "raita", "jogurttidippi",
            "keitto", "linssisoppa", "alkukeitot",
        ],
        "concepts": [
            "starter samosa pakora bhaji poppadom chutney kebab",
            "alkuruoka samosa pakora chutney",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # SPICE LEVEL  —  critical for Finnish diners
    # ══════════════════════════════════════════════════════════════
    "Spice Level": {
        "en": [
            # General
            "spicy", "spice", "spice level", "spice tolerance",
            "mild", "medium", "hot", "very hot", "extra hot", "extra spicy",
            "too spicy", "too hot", "not spicy", "not spicy enough",
            "not hot enough", "could be spicier", "more spice",
            # Adjustment
            "can adjust spice", "customise spice", "adjust heat",
            "made it milder", "made it hotter",
            # Sensations
            "burn", "burning", "mouth on fire", "lips burning",
            "sweating", "eye watering",
            "heat", "warmth", "kick", "bite",
            "gentle heat", "subtle spice", "well-balanced spice",
            # Ingredients
            "chili", "chilli", "pepper", "cayenne", "paprika",
            "jalapeño", "green chili", "red chili", "black pepper",
            "cardamom", "cumin", "coriander", "turmeric", "garam masala",
            "fenugreek", "cinnamon", "clove", "star anise",
        ],
        "fi": [
            "tulinen", "tulista", "tulisen", "tuliselle",
            "mieto", "mietoa", "miedon",
            "mausteinen", "mausteista", "mausteisen",
            "liian tulinen", "liian mausteinen", "ei tarpeeksi tulinen",
            "ei tarpeeksi mausteinen", "voisi olla tulisempaa",
            "poltto", "poltteleva", "suu palaa",
            "chili", "pippuri", "chilikastike", "mausteet",
            "kumina", "korianteri", "kurkuma", "kardemumma",
        ],
        "concepts": [
            "spice level hot mild medium burn heat chili pepper",
            "mausteisuus tulinen mieto chili poltto",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # MENU VARIETY  — dietary labels, coverage
    # ══════════════════════════════════════════════════════════════
    "Menu Variety": {
        "en": [
            "menu", "menu variety", "menu selection", "selection",
            "choice", "choices", "options", "range",
            "extensive menu", "limited menu", "small menu", "large menu",
            "enough choices", "not enough choice",
            "seasonal menu", "daily specials", "set menu", "fixed menu",
            "buffet", "all you can eat", "lunch buffet", "dinner buffet",
            "kids menu", "children's menu", "kids options",
            "gluten free", "gluten-free", "coeliac", "celiac",
            "nut free", "nut allergy", "allergen", "allergy",
            "dairy free", "lactose free", "lactose intolerant",
            "halal", "halal certified", "kosher",
            "veg only restaurant", "separate veg menu",
        ],
        "fi": [
            "menu", "menun", "menulle", "lista", "ruokalista",
            "valikoima", "valikoimaa", "valinnanvara",
            "vaihtoehdot", "valinnat", "suppea valikoima",
            "laaja valikoima", "riittävästi vaihtoehtoja",
            "päivän menu", "lounaslista", "erikoisuudet",
            "buffet", "seisova pöytä", "lounasbuffet",
            "lastenannos", "lasten menu",
            "gluteeniton", "laktoositon", "allergia", "allergeeni",
            "halal", "pähkinätön",
        ],
        "concepts": [
            "menu variety selection options gluten-free halal buffet allergen",
            "menu valikoima vaihtoehdot gluteeniton halal allergia",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # AUTHENTICITY
    # ══════════════════════════════════════════════════════════════
    "Authenticity": {
        "en": [
            "authentic", "authenticity", "genuine", "real", "original",
            "traditional", "homestyle", "home-cooked", "home style",
            "just like india", "like in india", "real indian food",
            "true indian", "proper indian", "proper curry",
            "spices are fresh", "fresh spices", "real spices",
            "indian chef", "indian owner", "indian family",
            "not authentic", "inauthentic", "westernized", "adapted",
            "fusion", "too western", "watered down", "not the real thing",
            "tastes like a takeaway", "feels mass produced",
            "grandma's recipe", "family recipe", "secret recipe",
        ],
        "fi": [
            "aito", "aitoa", "aidon", "aidolle",
            "alkuperäinen", "alkuperäistä",
            "perinteinen", "perinteistä",
            "kotitekoinen", "kotitekoista",
            "oikea intialainen", "oikeaa intialaista",
            "ei aito", "ei ole aito",
            "länsimainen", "muokattu", "ei perinteinen",
        ],
        "concepts": [
            "authentic traditional genuine homestyle real indian spices",
            "aito perinteinen kotitekoinen oikea intialainen",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # CLEANLINESS & HYGIENE
    # ══════════════════════════════════════════════════════════════
    "Cleanliness & Hygiene": {
        "en": [
            # Clean
            "clean", "spotless", "immaculate", "pristine", "tidy", "neat",
            "clean table", "clean plates", "clean glasses", "clean cutlery",
            "clean kitchen", "clean toilet", "clean bathroom", "clean floor",
            "well maintained", "hygienic", "good hygiene",
            # Dirty
            "dirty", "filthy", "grimy", "unclean", "disgusting", "gross",
            "dirty table", "dirty plates", "dirty glasses", "dirty cutlery",
            "sticky table", "sticky menu", "greasy", "stained",
            "dirty floor", "dirty toilet", "dirty bathroom", "dirty kitchen",
            "not clean", "poorly maintained",
            # Specific issues
            "smell", "smells", "bad smell", "bad odor", "foul smell",
            "musty", "damp smell", "fried smell", "oil smell",
            "cockroach", "bug", "fly", "flies", "insect", "pest",
            "mouse", "rat", "rodent",
            "hair in food", "hair in my food", "found hair",
            "mold", "mould",
        ],
        "fi": [
            "puhdas", "puhdasta", "siisti", "siistiä", "siisteyden",
            "hygienia", "hygieeninen",
            "likainen", "likaista", "likaisen",
            "törky", "tuhruinen", "epäsiisti",
            "haju", "hajua", "pahanhajuinen", "paha haju",
            "kärpänen", "kärpäsiä", "hyönteinen", "tuholainen",
            "hius ruoassa", "hius", "sammal",
        ],
        "concepts": [
            "clean dirty hygiene spotless filthy smell cockroach",
            "puhdas likainen hygienia haju tuholainen",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # SEATING & SPACE
    # ══════════════════════════════════════════════════════════════
    "Seating & Space": {
        "en": [
            "seating", "seats", "table", "tables", "chairs", "booth",
            "space", "spacious", "cramped", "tight", "crowded",
            "comfortable", "uncomfortable", "comfortable chairs",
            "hard chairs", "soft chairs", "cushioned",
            "outdoor", "outdoor seating", "terrace", "patio", "balcony",
            "window seat", "corner table", "private table", "private booth",
            "high chair", "highchair", "baby chair", "wheelchair accessible",
            "wheelchair access", "disabled access", "step free",
            "layout", "interior design", "decor", "furnishings",
            "lighting", "ambient lighting", "dim", "bright",
            "air conditioning", "heating", "temperature", "ventilation",
            "too cold", "too hot", "stuffy", "well-ventilated",
            "large group", "big group", "group dining", "party dining",
            "cozy", "intimate", "romantic", "noisy", "quiet",
        ],
        "fi": [
            "istumapaikka", "istumapaikat", "istuimet", "pöytä", "tuoli",
            "tila", "tilaa", "ahdas", "ahdasta", "tilava", "tilavaa",
            "mukava", "epämukava", "pehmustettu",
            "terassi", "ulkoterassi", "parveke",
            "ikkunapaikka", "nurkkaistu", "yksityinen pöytä",
            "lastenistuin", "esteetön", "pyörätuolipääsy",
            "sisustus", "valaistus", "ilmastointi", "lämmitys",
            "kylmä", "kuuma", "tunkkainen", "ilmastoitu",
            "suuri ryhmä", "ryhmäruokailu",
            "kodikas", "romanttinen", "äänekäs", "hiljainen",
        ],
        "concepts": [
            "seating space comfortable cramped table chairs decor lighting",
            "istumapaikka tila mukava ahdas pöytä sisustus valaistus",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # PRICE & VALUE
    # ══════════════════════════════════════════════════════════════
    "Price & Value": {
        "en": [
            # General price
            "price", "prices", "pricing", "cost", "costs",
            "expensive", "pricey", "overpriced", "costly", "not worth",
            "cheap", "inexpensive", "affordable", "budget", "budget friendly",
            "reasonable", "fairly priced", "well priced", "great value",
            "good value", "value for money", "worth every penny",
            "worth the price", "not worth the price",
            # Portion
            "portion", "portion size", "serving size", "too small",
            "generous portion", "large portion", "small portion",
            "enough food", "not enough food", "could be bigger",
            # Specific costs
            "lunch price", "dinner price", "set menu price",
            "starter price", "drink price", "wine price",
            # Currency / specifics
            "euro", "euros", "€",
            # Deals / offers
            "deal", "lunch deal", "meal deal", "discount",
            "happy hour", "offer", "special offer", "promotion",
        ],
        "fi": [
            "hinta", "hintaa", "hinnan", "hinnalle", "hinnoittelu",
            "kallis", "kallista", "kalliin", "kalliille",
            "halpa", "halpaa", "edullinen", "edullista",
            "kohtuullinen", "hyvä hinta-laatu", "hintalaatu",
            "ylihintainen", "ei hinnan arvoinen",
            "annoskoko", "annos liian pieni", "reilu annos",
            "tarjous", "lounastarjous", "alennus",
            "euro", "euroa", "€",
        ],
        "concepts": [
            "price value expensive cheap affordable portion generous",
            "hinta arvo kallis halpa edullinen annoskoko",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # FOOD QUALITY (general)
    # ══════════════════════════════════════════════════════════════
    "Food Quality": {
        "en": [
            "quality", "fresh", "freshness", "not fresh", "stale",
            "frozen", "fresh ingredients", "seasonal ingredients",
            "local ingredients", "organic", "homemade",
            "presentation", "plating", "well presented", "nicely presented",
            "looks good", "looks bad", "looks appetising",
            "consistency", "inconsistent", "always the same quality",
            "varies every time", "better last time", "worse this time",
            "portion", "well cooked", "poorly cooked",
            "overcooked", "undercooked", "raw", "burnt", "charred",
            "well-done", "perfectly cooked",
        ],
        "fi": [
            "laatu", "laadun", "tuore", "tuoretta", "ei tuore",
            "pakastettu", "kotitekoinen", "luomu",
            "esittely", "asettelu", "näyttää hyvältä",
            "johdonmukaisuus", "epäjohdonmukainen",
            "ylikypsä", "raaka", "palanut", "täydellisesti kypsennetty",
        ],
        "concepts": [
            "quality fresh ingredients presentation overcooked stale",
            "laatu tuore raaka-aineet esittely ylikypsä",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # AMBIENCE & ATMOSPHERE
    # ══════════════════════════════════════════════════════════════
    "Ambience & Atmosphere": {
        "en": [
            "atmosphere", "ambience", "ambiance", "vibe", "feel",
            "cozy", "intimate", "romantic", "date night",
            "family friendly", "casual", "formal",
            "lighting", "dim lighting", "bright", "candlelit",
            "music", "background music", "bollywood music", "indian music",
            "too loud music", "no music", "nice music",
            "noise", "noisy", "quiet", "peaceful", "relaxing",
            "decor", "decoration", "indian decor", "colourful",
            "warm colours", "traditional decor", "modern decor",
            "pictures", "artwork", "tapestry", "elephant", "ganesh",
            "clean smell", "pleasant smell", "spice smell",
            "warm", "welcoming", "inviting",
        ],
        "fi": [
            "tunnelma", "tunnelmaa", "ilmapiiri",
            "kodikas", "romanttinen", "perheen yhteinen",
            "valaistus", "kynttilänvalo", "himmennys",
            "musiikki", "taustamusiikki", "liian kovaa musiikkia",
            "meteli", "äänekäs", "hiljainen", "rauhallinen",
            "sisustus", "värikäs", "lämmin", "kutsuva",
        ],
        "concepts": [
            "atmosphere ambience decor cozy romantic lighting music noise",
            "tunnelma sisustus kodikas romanttinen valaistus musiikki",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # DELIVERY & TAKEAWAY
    # ══════════════════════════════════════════════════════════════
    "Delivery & Takeaway": {
        "en": [
            "delivery", "home delivery", "deliver", "delivered",
            "takeaway", "take away", "take-away", "takeout", "take-out",
            "collection", "pick up", "click and collect",
            "wolt", "foodora", "uber eats", "just eat", "deliveroo",
            "order online", "online order", "app order",
            "delivery time", "fast delivery", "slow delivery",
            "late delivery", "on time", "cold on arrival", "arrived cold",
            "arrived hot", "packaging", "container", "bag",
            "leaked", "spilled", "packaging quality",
            "delivery fee", "delivery charge", "minimum order",
        ],
        "fi": [
            "toimitus", "toimitusta", "kotiinkuljetus", "kotiintoimitus",
            "nouto", "pikaruoka",
            "wolt", "foodora",
            "tilaus", "verkkotelaus", "sovellustilaus",
            "toimitusaika", "nopea toimitus", "hidas toimitus",
            "myöhässä", "kylmä saapuessa", "kuumana",
            "pakkaus", "pakkauksen laatu", "vuoti",
            "toimitusmaksu", "minimiostosraja",
        ],
        "concepts": [
            "delivery takeaway wolt foodora packaging cold arrived",
            "toimitus nouto wolt foodora pakkaus kylmä",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # LOCATION & ACCESSIBILITY
    # ══════════════════════════════════════════════════════════════
    "Location & Accessibility": {
        "en": [
            "location", "located", "situated", "address",
            "central", "city centre", "city center", "town centre",
            "oulu center", "oulu centre",
            "parking", "free parking", "paid parking", "parking lot",
            "street parking", "no parking",
            "bus", "bus stop", "bus route", "public transport",
            "tram", "train", "metro", "taxi",
            "walkable", "walking distance", "5 minute walk", "close by",
            "nearby", "next to", "opposite", "around the corner",
            "far", "far away", "out of the way", "off the beaten track",
            "easy to find", "hard to find", "couldn't find it",
            "google maps", "satnav", "directions",
            "wheelchair", "wheelchair accessible", "ramp", "step free",
            "disabled access", "accessible",
        ],
        "fi": [
            "sijainti", "sijainnissa", "sijaitsee",
            "keskusta", "kaupunkikeskus", "oulun keskusta",
            "pysäköinti", "ilmainen pysäköinti", "maksullinen pysäköinti",
            "bussi", "bussipysäkki", "julkinen liikenne",
            "kävelyetäisyys", "lähellä", "vieressä", "kaukana",
            "helppo löytää", "vaikea löytää", "ei löydy",
            "google maps", "kartta", "opasteet",
            "esteetön", "pyörätuoli", "pyörätuolipääsy", "ramppi",
        ],
        "concepts": [
            "location central parking bus walkable accessible",
            "sijainti keskusta pysäköinti bussi esteetön",
        ],
    },

    # ══════════════════════════════════════════════════════════════
    # OVERALL EXPERIENCE
    # ══════════════════════════════════════════════════════════════
    "Overall Experience": {
        "en": [
            # Positive overall
            "recommend", "highly recommend", "would recommend",
            "come again", "will come again", "would come back",
            "visit again", "will return", "definitely returning",
            "worth it", "worth a visit", "worth every penny",
            "hidden gem", "gem", "favourite", "favorite",
            "best indian", "best restaurant", "best meal",
            "loved it", "loved everything", "perfect experience",
            "amazing experience", "great experience", "brilliant",
            "exceeded expectations", "impressed",
            # Negative overall
            "disappointed", "disappointment", "not worth it",
            "wouldn't recommend", "would not recommend",
            "never again", "will not return", "won't go back",
            "waste of money", "waste of time", "below expectations",
            "left hungry", "left unsatisfied",
            # Neutral overall
            "overall", "overall impression", "in general",
            "all in all", "on the whole", "summing up",
            "mixed experience", "average", "ok", "okay", "decent",
            "nothing special", "mediocre",
        ],
        "fi": [
            "suositella", "suosittelisin", "suosittelen",
            "tulla uudelleen", "tulen uudelleen", "palaan",
            "ehdottomasti", "vierailun arvoinen",
            "paras intialainen", "paras ravintola", "suosikkini",
            "rakastin", "täydellinen kokemus", "upea kokemus",
            "ylitti odotukset", "yllätyin positiivisesti",
            "pettymys", "pettyin", "ei suosittele",
            "ei ikinä uudelleen", "en palaa", "ei kannata",
            "rahan hukkaa", "ajan hukkaa",
            "kaiken kaikkiaan", "yleisesti ottaen", "yhteenvetona",
            "sekalainen kokemus", "keskinkertainen", "ihan ok",
        ],
        "concepts": [
            "recommend return experience satisfied disappointed hidden gem",
            "suositella palata kokemus tyytyväinen pettymys",
        ],
    },
}

ALL_ASPECTS = list(ASPECT_GROUPS.keys())

ASPECT_DISPLAY = {
    "Service & Staff":           "👨‍🍳 Service & Staff",
    "Chicken Dishes":            "🍗 Chicken",
    "Lamb & Mutton Dishes":      "🥩 Lamb/Mutton",
    "Vegetarian & Vegan Options":"🥗 Veg/Vegan",
    "Beef Dishes":               "🥩 Beef",
    "Seafood":                   "🦐 Seafood",
    "Bread & Rice":              "🫓 Bread & Rice",
    "Curry & Sauce":             "🍛 Curry",
    "Starters & Street Food":    "🥙 Starters",
    "Spice Level":               "🌶️ Spice Level",
    "Menu Variety":              "📋 Menu Variety",
    "Authenticity":              "🏆 Authenticity",
    "Cleanliness & Hygiene":     "🧼 Cleanliness",
    "Seating & Space":           "🪑 Seating & Space",
    "Price & Value":             "💰 Price/Value",
    "Food Quality":              "✨ Food Quality",
    "Ambience & Atmosphere":     "🌿 Ambience",
    "Delivery & Takeaway":       "🛵 Delivery",
    "Location & Accessibility":  "📍 Location",
    "Overall Experience":        "⭐ Overall",
}
