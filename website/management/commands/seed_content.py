"""
Load WEMASA's starting content (text, team, partners, press, photos).

Safe to run on every deploy: it only fills in what is missing and never
overwrites edits made in the dashboard. Use --reset to wipe all website
content and start again from this file.
"""
import datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from website import models as m

SEED_DIR = Path(settings.BASE_DIR) / "seed" / "images"


def photo(name):
    path = SEED_DIR / name
    if not name or not path.exists():
        return None
    return File(path.open("rb"), name=path.name)


def set_images(obj, **images):
    """Attach seed images to empty image fields only."""
    changed = False
    for field, name in images.items():
        if name and not getattr(obj, field):
            f = photo(name)
            if f:
                getattr(obj, field).save(f.name, f, save=False)
                f.close()
                changed = True
    return changed


def fill_singleton(model, values, images=None):
    obj = model.load()
    changed = False
    for key, value in values.items():
        if not getattr(obj, key):
            setattr(obj, key, value)
            changed = True
    changed = set_images(obj, **(images or {})) or changed
    if changed:
        obj.save()
    return obj


# Captions used for photos, written so they are true for every photo in the group.
FARMING = "Organic farming training with women vegetable farmers, Dar es Salaam."
SCHOOL_TREES = "Tree planting at a school in Dar es Salaam."
CLEANUP = "Community cleanup, Dar es Salaam."
WORKSHOP = "Workshop for young women environment journalists, Dar es Salaam, March 2026."
ROADSIDE = "Tree planting along a road, Dar es Salaam."

# ---------------------------------------------------------------------------
# Site-wide details
# ---------------------------------------------------------------------------

SITE = {
    "org_name": "WEMASA Tanzania Organization",
    "short_name": "WEMASA",
    "tagline": "Weka Mazingira Safi. Keep the environment clean.",
    "footer_about": (
        "WEMASA (Weka Mazingira Safi) is a Tanzanian NGO working with neighbourhoods, schools, markets and "
        "women farmers on waste, trees, clean cooking and organic farming."
    ),
    "registration_number": "ooNGO/R/2395",
    "registration_year": "2021",
    "registration_note": "Registered under the NGO Act, Tanzania",
    "email": "wemasatanzania@gmail.com",
    "phone": "+255 787 618 186",
    "whatsapp": "255787618186",
    "location": "Temeke, Dar es Salaam, Tanzania",
    "address": "P.O. Box 42017, Dar es Salaam",
    "donate_button_text": "Donate",
    "newsletter_title": "Letters from the field",
    "newsletter_text": "A short note when we have something worth telling you: a new project, a cleanup day, a report.",
    "meta_description": (
        "WEMASA Tanzania Organization (Weka Mazingira Safi) works with communities, schools and women farmers "
        "in Dar es Salaam on waste, tree planting, clean cooking and organic farming."
    ),
}

HOME = {
    "hero_kicker": "Weka Mazingira Safi · Keep the environment clean",
    "hero_title": "It started with rubbish at the edge of a football pitch.",
    "hero_text": (
        "A few young neighbours in Dar es Salaam got tired of looking at it, so they knocked on doors and "
        "talked to the families living nearby. The street got cleaner. That was the beginning of WEMASA. "
        "Today we work with neighbourhoods, schools, market vendors, women farmers and journalists on the "
        "everyday business of keeping the places we live clean and green."
    ),
    "hero_caption": "A participant in our organic farming training holds freshly harvested greens. Dar es Salaam.",
    "hero_primary_text": "Read our story",
    "hero_primary_url": "/about/",
    "hero_secondary_text": "See the projects",
    "hero_secondary_url": "/projects/",
    "focus_title": "What we do",
    "focus_intro": (
        "Most of our work happens in Temeke and the surrounding wards of Dar es Salaam. "
        "It falls into six areas, and they overlap more than this list suggests."
    ),
    "projects_title": "From the field",
    "projects_intro": "Recent projects, in the words and pictures of the people who ran them.",
    "story_quote": (
        "Households near the ground had got used to throwing waste just outside their doors. "
        "Nobody said anything. So we did."
    ),
    "story_attribution": "From the WEMASA founding story",
    "story_text": (
        "We went house to house, explaining how to store rubbish so the collector could take it, and why the "
        "small collection fee mattered. We asked our ward to bring in a proper waste contractor. Within a few "
        "months the difference was obvious. In 2021 we registered as an NGO so we could do the same thing in "
        "more places."
    ),
    "story_caption": "Women farmers and WEMASA staff after a training session.",
    "story_link_text": "The full story",
    "photos_title": "Photographs",
    "press_title": "In the press",
    "press_intro": (
        "Our first workshop for women environment journalists, in March 2026, was picked up by newspapers, "
        "television and online outlets across the country. These are their headlines, as published."
    ),
    "stories_title": "Stories",
    "partners_title": "We work with",
    "cta_title": "Help us keep Dar es Salaam clean.",
    "cta_text": (
        "Come to a cleanup. Bring us to your school. Fund a training for a farmers' group. "
        "If you have an idea for working together, we would like to hear it."
    ),
    "cta_caption": "Volunteers with brooms and reflector vests before a cleanup.",
    "cta_primary_text": "Get involved",
    "cta_primary_url": "/get-involved/",
    "cta_secondary_text": "Donate",
    "cta_secondary_url": "/donate/",
}
HOME_IMAGES = {"hero_image": "kisewe-06.webp", "story_image": "kisewe-05.webp", "cta_image": "cleanup-02.webp"}

ABOUT = {
    "story_eyebrow": "Our story",
    "story_title": "How a neighbourhood clean-up became an NGO",
    "story_text": (
        "<p>It was an ordinary evening at our local football ground. While we watched the match, we noticed the "
        "edges of the pitch, right next to people’s houses, were covered in rubbish. The families living there "
        "had got used to throwing waste just outside their doors. Local leaders looked the other way, and nobody "
        "complained.</p>"
        "<p>A handful of us who cared about the environment decided not to look the other way. We started going "
        "from house to house. We talked to families about storing their rubbish so it could be collected, and "
        "about paying the waste contractor so collection would happen on time. We also asked our ward to bring "
        "in a contractor of its own.</p>"
        "<p>People changed how they kept their waste, collection became easier, and within months the street "
        "looked nothing like it had before.</p>"
        "<p>We learned something from that. When people understand a problem and are given a practical way to "
        "fix it, they usually do. In 2021 we registered <strong>WEMASA, Weka Mazingira Safi</strong>, as a "
        "non-governmental organisation so we could take the same approach to other neighbourhoods, schools and "
        "markets.</p>"
    ),
    "story_caption": "Farmers and WEMASA staff in Dar es Salaam.",
    "story_quote": "When people understand a problem and are given a practical way to fix it, they usually do.",
    "vision": (
        "A community where everyone understands how to manage waste and takes part in keeping their "
        "surroundings clean."
    ),
    "mission": (
        "To educate and raise awareness in communities on managing the environment and natural resources."
    ),
    "objectives_title": "Objectives",
    "objectives_intro": "Our constitution sets out four objectives.",
    "values_title": "Values",
    "values_intro": "We hold ourselves to four values. We name them in Kiswahili first, because that is how we use them.",
    "approach_title": "How we work",
    "approach_text": (
        "<p>We start where people are. Before a training or a cleanup, we talk to the residents, teachers or "
        "farmers involved and find out what they already do and what gets in their way.</p>"
        "<p>Our trainings are practical. Farmers make the pesticide themselves. Students plant the tree "
        "themselves. Households are shown where the rubbish goes, not just told.</p>"
        "<p>We work alongside local leaders and the municipal council, so that changes last after we leave. "
        "And we write things down: we map markets and waste collection points, and we report back to the "
        "people who funded the work.</p>"
    ),
    "approach_caption": "A training session held outdoors, between the vegetable beds.",
    "timeline_title": "Milestones",
    "legal_title": "Registration",
    "legal_text": (
        "WEMASA Tanzania Organization is registered under the Non-Governmental Organizations Act of the United "
        "Republic of Tanzania, registration number ooNGO/R/2395 (2021). Our area of operation is national. "
        "We are governed by our constitution."
    ),
}
ABOUT_IMAGES = {"story_image": "kisewe-04.webp", "approach_image": "kisewe-07.webp"}

HEADERS = [
    ("about", "About", "About WEMASA",
     "A small group of neighbours started cleaning up their street. In 2021 they registered as an NGO.",
     "farming-05.webp", FARMING),
    ("focus", "Our work", "What we do",
     "Waste, schools, organic farming, trees, clean cooking and the people who report on all of it.",
     "farming-08.webp", FARMING),
    ("projects", "Our work", "Projects",
     "Everything we have run so far, from school tree planting to a survey of market food vendors.",
     "kisewe-07.webp", FARMING),
    ("impact", "Our work", "Results",
     "What our projects have reached, written down plainly so you can check it.",
     "", ""),
    ("resources", "Library", "Reports and documents",
     "Project reports and organisational documents. More will be added as they are published.",
     "", ""),
    ("media", "Press", "In the press",
     "Headlines from newspapers, television and online outlets that have covered our work.",
     "workshop-01.webp", "A WEMASA facilitator interviewed by Star TV at the women journalists’ workshop, March 2026."),
    ("news", "Stories", "Stories from the field",
     "Notes and news from our projects.",
     "", ""),
    ("gallery", "Photographs", "Photographs",
     "Trainings, cleanups and tree planting days, as they happened.",
     "", ""),
    ("team", "People", "The people behind WEMASA",
     "Founders, officers and mobilisers. Most of us live in the communities we work in.",
     "", ""),
    ("partners", "Partners", "Who we work with",
     "Funders, local government, businesses and community groups.",
     "trees-community-02.webp", "WEMASA staff and community members at a tree planting day."),
    ("sdgs", "Our work", "The Sustainable Development Goals",
     "How our local work lines up with the global goals.",
     "", ""),
    ("involved", "Join us", "Get involved",
     "Volunteer, invite us to your school, partner with us or tell our stories.",
     "cleanup-01.webp", "Bags of rubbish collected by volunteers during a cleanup."),
    ("donate", "Support", "Support our work",
     "Money we receive pays for training materials, seedlings, cleanup equipment and transport to schools.",
     "schools-03.webp", "Pupils hold up seedlings at a school tree planting day."),
    ("contact", "Contact", "Get in touch",
     "Call, write, or send a message using the form below.",
     "", ""),
]

OBJECTIVES = [
    ("Promote environmental and natural resources management",
     "Help households, schools and businesses manage waste and use natural resources carefully."),
    ("Raise awareness about the importance of biodiversity",
     "Explain why trees, soil, water and wildlife matter to the people who depend on them."),
    ("Promote peace in the community",
     "Bring neighbours together around a shared responsibility for the places they live."),
    ("Promote democracy and children’s rights",
     "Make sure community decisions include everyone, and that children can grow up in a clean, safe environment."),
]

VALUES = [
    ("Equality", "Usawa",
     "Women, young people and the poorest households get the same voice and the same attention in our work."),
    ("Transparency", "Uwazi",
     "We are open about our plans, our money and our results."),
    ("Accountability", "Uwajibikaji",
     "We answer for what we promise to communities and to the people who fund us."),
    ("Diligence", "Bidii",
     "Clean streets need steady work, week after week, not a single event."),
]

MILESTONES = [
    ("Before 2021", "The football pitch",
     "Young neighbours start visiting households near a local football ground to talk about waste storage and collection."),
    ("2021", "Registered as an NGO",
     "WEMASA is registered under Tanzania’s NGO Act, registration number ooNGO/R/2395."),
    ("2021 onwards", "Schools, markets and farms",
     "Climate change sessions in eight Temeke secondary schools, school tree planting, organic farming training and market surveys."),
    ("March 2026", "First workshop for women environment journalists",
     "Held in Dar es Salaam for International Women’s Day and covered by national newspapers and television."),
]

FOCUS = [
    ("Waste and community cleanups", "cleanup-01.webp", CLEANUP,
     "Cleanups in streets, markets and on the beach, followed by door-to-door visits on how to store and hand over rubbish.",
     "<p>Uncollected rubbish blocks drains, spreads disease and makes neighbourhoods miserable to live in. We "
     "organise cleanups with residents, youth groups and local leaders, and we follow them up.</p>"
     "<p>After each cleanup we visit households to talk about storing waste so the collector can take it, "
     "paying the collection fee, and what happens when rubbish is dumped instead. A clean street for a day is "
     "easy. Keeping it clean is the real work.</p>"),
    ("Climate change in schools", "trees-school-04.webp", SCHOOL_TREES,
     "Sessions in secondary schools on what climate change is, why it matters in Dar es Salaam, and what students can do about it.",
     "<p>Students live with the effects of climate change longest, and they take what they learn home. We run "
     "sessions in secondary schools that connect climate change to things students already see: flooding, "
     "heat, rubbish in the drains.</p>"
     "<p>So far we have held these sessions in eight secondary schools in Temeke District, with about 3,700 "
     "students taking part.</p>"),
    ("Organic farming", "farming-03.webp", FARMING,
     "Training women vegetable farmers to make their own pesticides, plant boosters and fungicides from local plants.",
     "<p>Small vegetable farmers spend a lot on chemical sprays that are bad for the soil, the water and the "
     "people handling them. We train women farmers to make natural alternatives from plants that grow nearby.</p>"
     "<p>The trainings happen in the field, between the vegetable beds. Each farmer prepares the mixtures "
     "herself. We have trained farmers’ groups in Kisewe and Kiburugwa.</p>"),
    ("Tree planting", "trees-school-06.webp", SCHOOL_TREES,
     "Planting trees with pupils and students in school grounds, and with residents in public spaces.",
     "<p>Trees give shade, hold the soil together and make a school compound a better place to learn. Every "
     "tree planted by a pupil is also a small lesson in looking after something.</p>"
     "<p>We have planted trees at Kibasila, Kongowe, Lionel and Vingunguti, working with pupils, teachers, "
     "local leaders and partners.</p>"),
    ("Clean cooking and environmental data", "", "",
     "Surveys and maps that show how food vendors cook and where rubbish is collected, so decisions can be based on facts.",
     "<p>It is hard to fix a problem nobody has measured. We collect and map information that communities and "
     "local authorities can use.</p>"
     "<p>We surveyed 78 food vendors in four large Temeke markets, Sterio, Kizuiani, Kampocheo and Mtongani, "
     "to find out who cooks with charcoal, gas or firewood. We have also mapped waste collection points in the "
     "Dar es Salaam Region using a waste-mapping app.</p>"),
    ("Women journalists and the environment", "workshop-01.webp", WORKSHOP,
     "Training young women journalists to report on waste, climate and natural resources.",
     "<p>How the press covers the environment shapes what the public thinks about it, and women reporters are "
     "under-represented on the environment beat.</p>"
     "<p>In March 2026 we held our first workshop for young girls and women environment journalists. The "
     "workshop itself was covered by newspapers, television and online outlets.</p>"),
]

PROJECTS = [
    {
        "title": "Organic farming training for women vegetable farmers",
        "focus": "Organic farming", "status": "completed",
        "cover": "kisewe-01.webp", "cover_caption": "Farmers mixing a natural pesticide from chopped leaves.",
        "location": "Kisewe and Kiburugwa, Dar es Salaam", "beneficiaries": "Women vegetable farmers",
        "summary": "Field trainings where women farmers learned to make natural pesticides, plant boosters and fungicides from plants growing around them.",
        "description": (
            "<p>Most of the women who grow vegetables around Kisewe and Kiburugwa had been buying chemical "
            "sprays to deal with pests and plant disease. The sprays are expensive, and nobody was sure what "
            "they were doing to the soil or to the people using them.</p>"
            "<p>We held the trainings in the farms themselves. Working between the vegetable beds, the farmers "
            "learned to prepare three things from local plants and leaves:</p>"
            "<ul><li>a natural pesticide,</li><li>a booster to help plants grow,</li>"
            "<li>a natural fungicide against fungal disease.</li></ul>"
            "<p>Each farmer chopped, mixed and prepared the recipes herself and took notes to share with the "
            "rest of her group.</p>"
        ),
        "outcomes": (
            "Farmers prepared each natural mixture themselves during the sessions\n"
            "Trainings held with groups in two communities, Kisewe and Kiburugwa"
        ),
        "stats": [("Communities", "Kisewe, Kiburugwa")],
        "photos": ["kisewe-0%d.webp" % i for i in range(1, 8)] + ["kiburugwa-0%d.webp" % i for i in range(2, 10)]
                  + ["farming-0%d.webp" % i for i in range(1, 10)],
        "caption": FARMING, "album": "Organic farming training",
    },
    {
        "title": "Climate change sessions in Temeke secondary schools",
        "focus": "Climate change in schools", "status": "completed",
        "cover": "trees-school-04.webp", "cover_caption": "Students and teachers at a WEMASA school activity.",
        "location": "Temeke District, Dar es Salaam", "beneficiaries": "Secondary school students",
        "summary": "Sessions on climate change in eight secondary schools in Temeke District, with about 3,700 students taking part.",
        "description": (
            "<p>Climate change can sound abstract to a fifteen-year-old until it is connected to the flooding, "
            "heat and blocked drains in their own neighbourhood. That is where our sessions start.</p>"
            "<p>We ran them in eight secondary schools across Temeke District, reaching about 3,700 students. "
            "We covered what causes climate change, how waste and cutting down trees make it worse, and what "
            "students can actually do at school and at home.</p>"
        ),
        "outcomes": "Sessions held in eight secondary schools\nAbout 3,700 students took part",
        "stats": [("Schools", "8 secondary schools"), ("Students", "About 3,700")],
        "photos": [],
    },
    {
        "title": "Tree planting in schools",
        "focus": "Tree planting", "status": "ongoing",
        "cover": "schools-03.webp", "cover_caption": "Pupils hold up seedlings before planting.",
        "location": "Kibasila, Kongowe, Lionel and Vingunguti", "beneficiaries": "Pupils, students and teachers",
        "summary": "Pupils and students planting trees in their own school grounds at Kibasila, Kongowe, Lionel and Vingunguti.",
        "description": (
            "<p>A school compound with trees is cooler, greener and a better place to learn. Our tree planting "
            "days bring pupils, teachers, local leaders and partners together to plant seedlings and look after "
            "them.</p>"
            "<p>We have planted at Kibasila, Kongowe, Lionel and Vingunguti. Each day starts with a short talk "
            "about why trees matter, then every pupil gets their hands in the soil.</p>"
        ),
        "outcomes": "Trees planted at four schools\nPupils planted the seedlings themselves",
        "stats": [("Schools", "Kibasila, Kongowe, Lionel, Vingunguti")],
        "photos": ["schools-0%d.webp" % i for i in range(1, 5)] + ["trees-school-0%d.webp" % i for i in range(1, 8)],
        "caption": SCHOOL_TREES, "album": "Tree planting in schools",
    },
    {
        "title": "Community and beach cleanups",
        "focus": "Waste and community cleanups", "status": "ongoing",
        "cover": "cleanup-02.webp", "cover_caption": "Volunteers ready with brooms before a cleanup.",
        "location": "Dar es Salaam", "beneficiaries": "Residents, youth groups and local leaders",
        "summary": "Volunteers, residents and partners clearing rubbish from streets, markets and beaches, with follow-up visits to households.",
        "description": (
            "<p>Our cleanups bring together volunteers, women’s and youth groups, local leaders and partners. "
            "Rubbish is collected, bagged and handed over for proper disposal.</p>"
            "<p>The follow-up matters as much as the day itself. We talk to households about storing waste, "
            "paying for collection and the health risks of dumping, so the area stays clean afterwards.</p>"
        ),
        "outcomes": "Rubbish collected, bagged and handed over for disposal\nHouseholds visited after cleanups",
        "stats": [],
        "photos": ["cleanup-0%d.webp" % i for i in range(1, 4)],
        "caption": CLEANUP, "album": "Cleanups",
    },
    {
        "title": "First workshop for young women environment journalists",
        "focus": "Women journalists and the environment", "status": "completed",
        "cover": "workshop-01.webp", "cover_caption": "A facilitator speaks to Star TV at the workshop.",
        "location": "Dar es Salaam", "period": "11 March 2026", "beneficiaries": "Young women journalists",
        "summary": "A one-day workshop for International Women’s Day 2026 on reporting about waste, climate and clean cooking.",
        "description": (
            "<p>On 11 March 2026, for International Women’s Day, we held our first workshop for young girls and "
            "women environment journalists in Dar es Salaam.</p>"
            "<p>The participants looked at the environmental problems facing Tanzanian communities, including "
            "the many ways badly managed waste affects health and livelihoods, and talked through how to report "
            "on them. There was also a long discussion about clean cooking, and why many households still cannot "
            "afford to switch from charcoal to gas.</p>"
            "<p>Nipashe, Tanzania Leo, Mtanzania Leo, Star TV, SMTV, Tanganyika Television and Watetezi TV "
            "were among the outlets that covered it.</p>"
        ),
        "outcomes": "Women journalists trained on environmental reporting\nCovered by national newspapers, TV and online media",
        "stats": [("Date", "11 March 2026")],
        "photos": ["workshop-01.webp"],
        "caption": WORKSHOP, "album": "Women journalists workshop",
    },
    {
        "title": "Cooking fuel survey of market food vendors",
        "focus": "Clean cooking and environmental data", "status": "completed",
        "cover": "", "cover_caption": "",
        "location": "Sterio, Kizuiani, Kampocheo and Mtongani markets, Temeke", "beneficiaries": "Market food vendors",
        "summary": "We visited 78 food vendors in four Temeke markets to find out who cooks with charcoal, gas or firewood.",
        "description": (
            "<p>Food vendors cook all day, and the fuel they use affects their health, their costs and the air "
            "around the market.</p>"
            "<p>We visited 78 vendors in four of Temeke’s largest markets, Sterio, Kizuiani, Kampocheo and "
            "Mtongani, and recorded whether they cook with charcoal, gas or firewood. The results give partners "
            "and the authorities a starting point for helping small businesses move to cleaner fuel.</p>"
        ),
        "outcomes": "78 food vendors visited\nFour markets covered",
        "stats": [("Vendors visited", "78"), ("Markets", "Sterio, Kizuiani, Kampocheo, Mtongani")],
        "photos": [],
    },
    {
        "title": "Mapping waste collection points",
        "focus": "Clean cooking and environmental data", "status": "completed",
        "cover": "", "cover_caption": "",
        "location": "Dar es Salaam Region", "beneficiaries": "Residents and local authorities",
        "summary": "Recording waste collection points across the Dar es Salaam Region with a waste-mapping app.",
        "description": (
            "<p>Before you can improve waste collection, you need to know where it happens and where it does not.</p>"
            "<p>We used a waste-mapping app to record collection points across the Dar es Salaam Region. The map "
            "shows the gaps and gives communities and local authorities something concrete to plan around.</p>"
        ),
        "outcomes": "Collection points recorded across the Dar es Salaam Region",
        "stats": [],
        "photos": [],
    },
]

EXTRA_ALBUMS = [("Tree planting in the community", ["trees-community-0%d.webp" % i for i in range(1, 5)], ROADSIDE)]

IMPACT = [
    (3700, "", "students took part in climate change sessions", "Eight secondary schools, Temeke District"),
    (8, "", "secondary schools held climate change sessions", "Temeke District"),
    (78, "", "food vendors surveyed on cooking fuel", "Sterio, Kizuiani, Kampocheo and Mtongani markets"),
    (4, "", "schools planted trees with us", "Kibasila, Kongowe, Lionel and Vingunguti"),
    (2, "", "farming communities trained in organic methods", "Kisewe and Kiburugwa"),
    (10, "", "media outlets covered the women journalists’ workshop", "Newspapers, television and online, March 2026"),
]

SDGS = [
    (4, "Quality Education", "Climate change sessions in secondary schools and practical training in communities."),
    (5, "Gender Equality", "Training for women farmers and for young women environment journalists."),
    (7, "Affordable and Clean Energy", "Our survey of cooking fuel among market food vendors."),
    (11, "Sustainable Cities and Communities", "Cleanups and the mapping of waste collection points in Dar es Salaam."),
    (12, "Responsible Consumption and Production", "Better waste storage and disposal, and organic farming."),
    (13, "Climate Action", "Climate change awareness with students."),
    (15, "Life on Land", "Tree planting in schools and public spaces."),
]

TEAM = [
    ("Ibrahim Haule", "Co-Founder & Executive Director", "founders", "team/ibrahim-haule.webp",
     "Ibrahim co-founded WEMASA and leads the organisation day to day: its projects, its partnerships and its staff."),
    ("Jackline Ndawila", "Co-Founder & Head of Women Projects", "founders", "team/jackline-ndawila.webp",
     "Jackline co-founded WEMASA and runs its projects with women, from the farmers’ groups to the journalists’ workshop."),
    ("Carlos Mdemu", "Training Officer", "staff", "team/carlos-mdemu.webp",
     "Carlos plans and leads WEMASA’s trainings and awareness sessions in communities, schools and workshops."),
    ("Frednand Nseso", "Chief Accountant", "staff", "",
     "Frednand is responsible for WEMASA’s finances and financial reporting."),
    ("Hashim Mapengo", "Data Officer", "staff", "team/hashim-mapengo.webp",
     "Hashim manages WEMASA’s data work, including the market vendor survey and the mapping of waste collection points."),
    ("Jumanne Msumi", "Assistant Accountant", "staff", "team/jumanne-msumi.webp",
     "Jumanne supports the finance team and keeps WEMASA’s accounts in order."),
    ("Omary Mgomba", "Safeguarding Officer", "staff", "team/omary-mgomba.webp",
     "Omary makes sure that children, women and everyone else taking part in our activities are safe and treated with respect."),
    ("Lamlaty Omary", "Community Outreach Officer", "staff", "team/lamlaty-omary.webp",
     "Lamlaty is our link to the communities we work in. She mobilises residents, groups and local leaders to take part."),
]

PARTNERS = [
    ("Global Fund for Women", "funding"),
    ("Temeke Municipal Council", "government"),
    ("Taifa Gas", "corporate"),
    ("Lake Group", "corporate"),
    ("SP Plastics", "corporate"),
    ("Nabaki Afrika", "ngo"),
    ("Tanga Women's Gala", "community"),
]

MEDIA = [
    ("Nipashe", "newspaper", "Waandishi habari wanawake waimarishwa kuripoti mazingira", datetime.date(2026, 3, 11), "Pilly Kigome",
     "Women journalists strengthened to report on the environment."),
    ("Tanzania Leo", "newspaper", "WEMASA watoa elimu ya mazingira wanahabari wanawake nchini", datetime.date(2026, 3, 12), "",
     "WEMASA gives environmental education to women journalists. Front page."),
    ("Mtanzania Leo", "newspaper", "WEMASA yawanoa wanahabari wanawake utunzaji wa mazingira", datetime.date(2026, 3, 12), "",
     "WEMASA sharpens women journalists on environmental conservation. Front page."),
    ("Watetezi TV", "tv", "THRDC yashiriki warsha ya kwanza ya wanawake na wasichana wanaoandika habari za mazingira", datetime.date(2026, 3, 14), "",
     "THRDC takes part in the first workshop for women and girls who write about the environment."),
    ("Tanganyika Television", "tv", "WEMASA watoa kipaumbele kwa elimu ya mazingira kwa wanahabari wanawake", datetime.date(2026, 3, 11), "",
     "WEMASA prioritises environmental education for women journalists on International Women’s Day."),
    ("SMTV", "tv", "WEMASA Tanzania yawajengea uwezo waandishi wa habari wanawake kuhusu masuala ya mazingira", datetime.date(2026, 3, 11), "",
     "WEMASA builds women journalists’ capacity on environmental issues."),
    ("Star TV", "tv", "Kipato kidogo tatizo matumizi ya gesi nchini", datetime.date(2026, 3, 11), "",
     "Low income holds back the use of cooking gas in Tanzania."),
    ("W-News", "online", "Changamoto ya matumizi nishati safi ya kupikia kutafutiwa suluhu", datetime.date(2026, 3, 11), "",
     "Solutions sought for the clean cooking energy challenge."),
    ("Tanzania Daima", "newspaper", "Coverage of the women environment journalists’ workshop", datetime.date(2026, 3, 12), "",
     ""),
    ("Mwananchi", "newspaper", "Coverage of the women environment journalists’ workshop", datetime.date(2026, 3, 12), "",
     ""),
]

NEWS = [
    {
        "title": "Our first workshop for women environment journalists",
        "category": "event", "cover": "workshop-01.webp", "cover_caption": WORKSHOP, "featured": True,
        "date": datetime.datetime(2026, 3, 11, 18, 0),
        "project": "First workshop for young women environment journalists",
        "excerpt": "For International Women’s Day 2026 we brought young women journalists together in Dar es Salaam to talk about how to report on the environment.",
        "body": (
            "<p>On 11 March 2026 we held our first workshop for young girls and women environment journalists, "
            "in Dar es Salaam, as part of International Women’s Day.</p>"
            "<p>The day was about the environmental problems Tanzanian communities live with and how to report on "
            "them well. Carlos Mdemu led a session on the impacts of waste, from blocked drains and disease to "
            "lost income.</p>"
            "<h2>Why journalists</h2>"
            "<p>What the public knows about the environment mostly comes from the press. Women reporters are "
            "still a minority on the environment beat, and we think the coverage is poorer for it.</p>"
            "<p>A good part of the afternoon went on clean cooking. Several participants pointed out that many "
            "families know charcoal is harmful but cannot afford gas, a point Star TV later ran as its headline.</p>"
            "<h2>Coverage</h2>"
            "<p>The workshop was reported by Nipashe, Tanzania Leo and Mtanzania Leo, and by Star TV, SMTV, "
            "Tanganyika Television, Watetezi TV and W-News. We plan to make this an annual event.</p>"
        ),
    },
    {
        "title": "Making pesticide from leaves in Kisewe and Kiburugwa",
        "category": "story", "cover": "kisewe-06.webp", "cover_caption": FARMING, "featured": False,
        "date": None,
        "project": "Organic farming training for women vegetable farmers",
        "excerpt": "Women vegetable farmers spent a morning between their beds learning to make natural sprays from plants that grow nearby.",
        "body": (
            "<p>For a woman growing vegetables on the edge of Dar es Salaam, every shilling spent on chemical "
            "sprays is a shilling that does not go home. Our organic farming trainings offer another option.</p>"
            "<p>In Kisewe and Kiburugwa we worked with farmers’ groups right in their fields. Our trainers showed "
            "them how to make a natural pesticide, a plant booster and a fungicide from leaves and plants that "
            "grow locally. The farmers chopped, mixed and prepared each recipe themselves and wrote the steps down "
            "to share with others.</p>"
            "<p>Organic methods are kinder to the soil and the water, and cheaper. They also leave the knowledge "
            "with the farmers, which is the point.</p>"
        ),
    },
]

INVOLVEMENT = [
    ("Volunteer", "Join a cleanup, a tree planting day or a community visit. You do not need any background in the environment.", "Sign up to volunteer", "/contact/?topic=volunteer"),
    ("Partner with us", "Funders, businesses and institutions can support a project or design one with us.", "Talk about a partnership", "/contact/?topic=partnership"),
    ("Invite us to your school", "We run climate change sessions and tree planting days for primary and secondary schools.", "Request a school visit", "/contact/?topic=general"),
    ("Report on the environment", "Journalists and content creators can help us tell these stories and reach more people.", "Media enquiries", "/contact/?topic=media"),
    ("Donate", "Money pays for training materials, seedlings, cleanup equipment and transport.", "How to give", "/donate/"),
]

FAQS = [
    ("Is WEMASA a registered organisation?",
     "Yes. WEMASA Tanzania Organization was registered in 2021 under Tanzania’s NGO Act, registration number ooNGO/R/2395."),
    ("Where do you work?",
     "We are registered to work anywhere in Tanzania. Most of our projects so far have been in Dar es Salaam, especially Temeke District."),
    ("What does a donation pay for?",
     "Training materials, seedlings, cleanup equipment, transport to schools and communities, and the time of the people running the activities. We give receipts and report back on what the money did."),
    ("Do I need experience to volunteer?",
     "No. We will show you what to do. We also need help with photography, writing and data collection."),
    ("Can my school or community ask for a project?",
     "Yes. Send us a message with your location and what you have in mind."),
]


class Command(BaseCommand):
    help = "Load WEMASA's starting website content (only fills what is missing)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete all website content first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            for model in (m.GalleryImage, m.ProjectStat, m.Project, m.FocusArea, m.NewsPost, m.MediaCoverage, m.Resource,
                          m.TeamMember, m.Partner, m.Testimonial, m.ImpactStat, m.SDG, m.Objective, m.CoreValue,
                          m.Milestone, m.PageHeader, m.InvolvementOption, m.FAQ, m.DonationMethod,
                          m.SiteSettings, m.HomePage, m.AboutPage):
                model.objects.all().delete()
            self.stdout.write("Existing content removed.")

        fill_singleton(m.SiteSettings, SITE)
        fill_singleton(m.HomePage, HOME, HOME_IMAGES)
        fill_singleton(m.AboutPage, ABOUT, ABOUT_IMAGES)

        for page, eyebrow, title, subtitle, image, caption in HEADERS:
            header, created = m.PageHeader.objects.get_or_create(
                page=page, defaults={"eyebrow": eyebrow, "title": title, "subtitle": subtitle, "caption": caption})
            if created and set_images(header, image=image):
                header.save()

        self.seed_simple(m.Objective, "title", [{"title": t, "description": d} for t, d in OBJECTIVES])
        self.seed_simple(m.CoreValue, "name", [{"name": n, "local_name": l, "description": d} for n, l, d in VALUES])
        self.seed_simple(m.Milestone, "title", [{"year": y, "title": t, "description": d} for y, t, d in MILESTONES])

        focus_by_title = {}
        for order, (title, image, caption, summary, description) in enumerate(FOCUS):
            area, created = m.FocusArea.objects.get_or_create(title=title, defaults={
                "summary": summary, "description": description, "image_caption": caption, "order": order})
            if created and set_images(area, image=image):
                area.save()
            focus_by_title[title] = area

        for order, (name, category) in enumerate(PARTNERS):
            m.Partner.objects.get_or_create(name=name, defaults={"category": category, "order": order})

        projects = {}
        for order, data in enumerate(PROJECTS):
            project, created = m.Project.objects.get_or_create(title=data["title"], defaults={
                "focus_area": focus_by_title.get(data["focus"]), "status": data["status"], "summary": data["summary"],
                "description": data["description"], "location": data["location"], "period": data.get("period", ""),
                "beneficiaries": data["beneficiaries"], "outcomes": data["outcomes"], "order": order,
                "cover_caption": data["cover_caption"],
            })
            projects[project.title] = project
            if not created:
                continue
            if set_images(project, cover=data["cover"]):
                project.save()
            for i, (label, value) in enumerate(data["stats"]):
                m.ProjectStat.objects.create(project=project, label=label, value=value, order=i)
            for i, name in enumerate(data["photos"]):
                self.add_photo(name, project=project, album=data.get("album", ""), caption=data.get("caption", ""), order=i)

        for album, names, caption in EXTRA_ALBUMS:
            if not m.GalleryImage.objects.filter(album=album).exists():
                for i, name in enumerate(names):
                    self.add_photo(name, album=album, caption=caption, order=100 + i)

        for order, (value, suffix, label, desc) in enumerate(IMPACT):
            m.ImpactStat.objects.get_or_create(label=label, defaults={
                "value": value, "suffix": suffix, "description": desc, "show_on_home": False, "order": order})

        for order, (number, title, desc) in enumerate(SDGS):
            m.SDG.objects.get_or_create(number=number, defaults={"title": title, "description": desc, "order": order})

        for order, (name, role, group, image, bio) in enumerate(TEAM):
            member, created = m.TeamMember.objects.get_or_create(
                name=name, defaults={"role": role, "group": group, "bio": bio, "order": order})
            if created and set_images(member, photo=image):
                member.save()

        for order, (outlet, kind, headline, date, reporter, excerpt) in enumerate(MEDIA):
            m.MediaCoverage.objects.get_or_create(outlet=outlet, headline=headline, defaults={
                "media_type": kind, "published_on": date, "reporter": reporter, "excerpt": excerpt, "order": order})

        for data in NEWS:
            if m.NewsPost.objects.filter(title=data["title"]).exists():
                continue
            date = timezone.make_aware(data["date"]) if data["date"] else timezone.now()
            post = m.NewsPost(title=data["title"], category=data["category"], excerpt=data["excerpt"], body=data["body"],
                              cover_caption=data["cover_caption"], is_featured=data["featured"], published_at=date,
                              project=projects.get(data["project"]))
            set_images(post, cover=data["cover"])
            post.save()

        self.seed_simple(m.InvolvementOption, "title", [
            {"title": t, "description": d, "button_text": b, "button_url": u} for t, d, b, u in INVOLVEMENT])
        self.seed_simple(m.FAQ, "question", [{"question": q, "answer": a} for q, a in FAQS])

        self.stdout.write(self.style.SUCCESS("WEMASA content is ready."))

    def seed_simple(self, model, key, rows):
        for order, row in enumerate(rows):
            lookup = {key: row.pop(key)}
            model.objects.get_or_create(**lookup, defaults={**row, "order": order})

    def add_photo(self, name, order=0, **fields):
        f = photo(name)
        if not f:
            return
        img = m.GalleryImage(order=order, **fields)
        img.image.save(f.name, f, save=False)
        f.close()
        img.save()
