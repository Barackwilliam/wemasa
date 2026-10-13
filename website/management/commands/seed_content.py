"""
Load WEMASA's starting content (text, figures, team, partners, photos).

Safe to run on every deploy: it only fills in what is missing and never
overwrites edits made in the dashboard. Use --reset to wipe all website
content and start again from this file.
"""
import datetime
import sys
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from website import models as m

SEED_DIR = Path(settings.BASE_DIR) / "seed" / "images"
DOCS_DIR = Path(settings.BASE_DIR) / "seed" / "documents"


def photo(name, folder=SEED_DIR):
    path = folder / name
    if not path.exists():
        return None
    return File(path.open("rb"), name=path.name)


def upload(field_file, f):
    """Store a seed file. A file the storage refuses is skipped with a warning, so it cannot stop a deploy."""
    try:
        field_file.save(f.name, f, save=False)
        return True
    except Exception as exc:
        print(f"Warning: could not upload {f.name} ({exc}); skipped.", file=sys.stderr)
        return False
    finally:
        f.close()


def set_images(obj, **images):
    """Attach seed images to empty image fields only."""
    changed = False
    for field, name in images.items():
        if name and not getattr(obj, field):
            f = photo(name)
            if f and upload(getattr(obj, field), f):
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


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

SITE = {
    "org_name": "WEMASA Tanzania Organization",
    "short_name": "WEMASA",
    "tagline": "Weka Mazingira Safi — Keep the Environment Clean",
    "footer_about": (
        "WEMASA (Weka Mazingira Safi) is a Tanzanian non-governmental organisation raising community awareness "
        "on waste management, environmental conservation and natural resources management — through education, "
        "community action and innovation for a better planet."
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
    "newsletter_title": "Get stories of change in your inbox",
    "newsletter_text": "Field stories, project updates and opportunities to take part in WEMASA activities. No spam — unsubscribe any time.",
    "meta_description": (
        "WEMASA Tanzania Organization (Weka Mazingira Safi) empowers communities, schools, women and young people "
        "in Tanzania to manage waste, protect natural resources and act on climate change."
    ),
}

HOME = {
    "hero_eyebrow": "Weka Mazingira Safi · Registered NGO since 2021",
    "hero_title": "Cleaner communities, greener futures for Tanzania",
    "hero_highlight": "greener futures",
    "hero_subtitle": (
        "We equip communities, schools, women and young people with the knowledge and practical tools to manage "
        "waste, protect natural resources and lead the response to climate change — one neighbourhood at a time."
    ),
    "hero_primary_text": "Explore our work",
    "hero_primary_url": "/projects/",
    "hero_secondary_text": "Partner with us",
    "hero_secondary_url": "/get-involved/",
    "intro_eyebrow": "Who we are",
    "intro_title": "A grassroots movement for a cleaner, healthier Tanzania",
    "intro_text": (
        "<p>WEMASA — short for <strong>Weka Mazingira Safi</strong>, “Keep the Environment Clean” — began with a "
        "group of young neighbours who refused to accept littered streets as normal. Today we are a registered "
        "national NGO working alongside communities, schools, women farmers, journalists and local authorities to "
        "turn environmental awareness into everyday action.</p>"
        "<p>We believe lasting change happens when people understand why the environment matters and have the "
        "practical skills to protect it. That is why every programme we run combines education, community "
        "participation and locally led solutions.</p>"
    ),
    "intro_points": (
        "Community cleanups and household waste-management education\n"
        "Climate change awareness in secondary schools\n"
        "Organic farming training for women vegetable growers\n"
        "Evidence and mapping for smarter waste and energy decisions"
    ),
    "intro_badge_value": "2021",
    "intro_badge_label": "Registered as a national NGO",
    "focus_eyebrow": "What we do",
    "focus_title": "Six areas where we focus our energy",
    "focus_subtitle": (
        "Our programmes respond to the most pressing environmental challenges facing urban and peri-urban "
        "communities in Tanzania — from waste and climate to food, energy and information."
    ),
    "impact_eyebrow": "Our impact",
    "impact_title": "Real change, measured in people reached",
    "impact_subtitle": (
        "From classrooms in Temeke to vegetable plots in Kisewe and Kiburugwa, our programmes are changing how "
        "communities think about waste, energy and the natural world."
    ),
    "projects_eyebrow": "Featured projects",
    "projects_title": "Programmes making a difference on the ground",
    "projects_subtitle": "A selection of initiatives led by WEMASA with communities, schools and partners.",
    "story_eyebrow": "Our story",
    "story_title": "It all started on a football pitch",
    "story_text": (
        "One evening, while watching a local football match, a group of young neighbours noticed something "
        "everyone else seemed to ignore: rubbish piling up at the edges of the pitch, right beside people's homes.\n\n"
        "Instead of looking away, they went door to door — explaining how to store waste properly and why paying "
        "for collection mattered. Within months, the streets looked different. That simple act of community "
        "responsibility became WEMASA."
    ),
    "story_button_text": "Read our full story",
    "story_button_url": "/about/",
    "media_title": "As featured in",
    "news_eyebrow": "Latest from the field",
    "news_title": "News & stories",
    "testimonials_title": "What our community says",
    "partners_title": "Working together for a cleaner Tanzania",
    "partners_subtitle": (
        "We collaborate with funders, government, businesses and civil society to multiply our impact."
    ),
    "cta_title": "Be part of a cleaner, greener Tanzania",
    "cta_text": (
        "Partner with us, volunteer your time and skills, or support a programme. Together we can keep our "
        "communities clean, green and healthy for generations to come."
    ),
    "cta_primary_text": "Support our work",
    "cta_primary_url": "/donate/",
    "cta_secondary_text": "Get involved",
    "cta_secondary_url": "/get-involved/",
}
HOME_IMAGES = {
    "hero_image": "hero-hd.webp", "intro_image": "kisewe-06.webp", "intro_image_2": "trees-school-04.webp",
    "story_image": "kisewe-05.webp", "cta_image": "cleanup-02.webp",
}

ABOUT = {
    "story_eyebrow": "Our story",
    "story_title": "From one neighbourhood to a national mission",
    "story_text": (
        "<p>It was an ordinary evening at our local football ground. As we watched the match, we noticed that the "
        "edges of the pitch — right next to people’s homes — were covered in rubbish. Households near the ground "
        "had grown used to throwing waste just outside their doors. Local leaders turned a blind eye, and no one "
        "spoke up.</p>"
        "<p>A small group of young people who cared about the environment decided that silence was not an option. "
        "We began going from house to house, talking with families about how to store waste safely and why "
        "contributing to the waste-collection contractor mattered, so that rubbish could be collected on time. "
        "We also advised our ward to engage a dedicated waste-collection contractor.</p>"
        "<p>Slowly, attitudes changed. Residents began storing their waste in ways that made collection easier, and "
        "the cleanliness of our streets improved dramatically compared with how things had been before.</p>"
        "<p>That experience taught us a powerful lesson: when people understand the problem and are offered "
        "practical solutions, communities transform themselves. In 2021 we formalised our work by registering "
        "<strong>WEMASA — Weka Mazingira Safi</strong> as a non-governmental organisation, and we have been "
        "growing our reach ever since.</p>"
    ),
    "story_quote": "When people understand why the environment matters, they become its strongest protectors.",
    "vision": (
        "To see the whole community with enough awareness of waste management and everything about keeping our "
        "surroundings clean — a community that leads its own cleanup."
    ),
    "mission": (
        "To be a leading organisation providing education and raising community awareness on environmental and "
        "natural resources management."
    ),
    "objectives_title": "Our objectives",
    "objectives_intro": "As set out in our constitution, WEMASA exists to:",
    "values_title": "Our core values",
    "values_intro": "Four principles — in Kiswahili and English — guide every decision we make and every programme we run.",
    "approach_title": "Education, participation and innovation",
    "approach_text": (
        "<p>We do not believe in quick fixes. Environmental change sticks when communities own it, so our work "
        "follows a simple, proven approach:</p>"
        "<ul>"
        "<li><strong>Listen first.</strong> We start with the realities of each neighbourhood, school or market.</li>"
        "<li><strong>Educate practically.</strong> Training is hands-on — from making natural pesticides to sorting waste.</li>"
        "<li><strong>Act together.</strong> Cleanups, tree planting and awareness campaigns bring people and leaders together.</li>"
        "<li><strong>Measure and share.</strong> We collect data, map challenges and report openly on results.</li>"
        "</ul>"
    ),
    "timeline_title": "Our journey so far",
    "legal_title": "Registration & governance",
    "legal_text": (
        "WEMASA Tanzania Organization is registered under the Non-Governmental Organizations Act of the United "
        "Republic of Tanzania (Registration No. ooNGO/R/2395, 2021), with a national area of operation. We are "
        "governed by our constitution and committed to transparency and accountability in the use of every "
        "resource entrusted to us."
    ),
}
ABOUT_IMAGES = {"story_image": "kisewe-04.webp", "approach_image": "kisewe-07.webp"}

HEADERS = [
    ("about", "About us", "Weka Mazingira Safi — keep the environment clean",
     "A youth-led idea that grew into a registered national NGO, empowering communities to care for the environment they share.", "farming-05.webp"),
    ("focus", "What we do", "Our focus areas",
     "Six interconnected areas of work, from waste and climate education to organic farming, clean energy and environmental journalism.", "farming-08.webp"),
    ("projects", "Our work", "Projects & programmes",
     "Explore the initiatives through which WEMASA reaches communities, schools, markets, women farmers and journalists.", "kisewe-07.webp"),
    ("impact", "Results", "Our impact",
     "Measurable change in awareness, skills and behaviour — documented through figures, milestones and stories.", "trees-school-06.webp"),
    ("resources", "Library", "Reports & documents",
     "Project reports, publications and key organisational documents from WEMASA.", ""),
    ("media", "Press", "WEMASA in the media",
     "National television, newspapers and online outlets have covered our work across Tanzania.", "workshop-01.webp"),
    ("news", "Latest from the field", "News & stories",
     "Updates, events and stories of change from WEMASA programmes.", "kisewe-03.webp"),
    ("gallery", "Moments", "Photo gallery",
     "A visual journey through our trainings, cleanups, tree-planting days and community events.", "farming-04.webp"),
    ("videos", "Watch", "Videos",
     "See WEMASA’s cleanups, trainings and campaigns in motion, and hear from the people taking part.", "cover-waba-hd.webp"),
    ("team", "Our people", "Meet the team",
     "Dedicated founders, officers and community mobilisers who bring WEMASA’s mission to life every day.", "kiburugwa-02.webp"),
    ("partners", "Collaboration", "Our partners",
     "We achieve more together. Meet the organisations that support and work alongside WEMASA.", "trees-community-02.webp"),
    ("sdgs", "Global goals", "Contributing to the SDGs",
     "Our local action supports the United Nations Sustainable Development Goals for people and planet.", "trees-school-05.webp"),
    ("involved", "Join us", "Get involved",
     "Volunteer, partner, invite us to your school or share our work — there is a role for everyone.", "cleanup-02.webp"),
    ("donate", "Support WEMASA", "Your support keeps communities clean and green",
     "Every contribution funds training, cleanups, tree seedlings and school awareness sessions.", "schools-03.webp"),
    ("contact", "Contact", "Let’s talk",
     "Questions, partnership ideas or media requests — our team would love to hear from you.", "trees-community-02.webp"),
]

OBJECTIVES = [
    ("Promote environmental and natural resources management", "recycle",
     "Equip communities with the knowledge and practical skills to manage waste, conserve resources and keep their surroundings clean."),
    ("Raise awareness about the importance of biodiversity", "tree",
     "Help people understand how healthy ecosystems — trees, soils, water and wildlife — sustain livelihoods and wellbeing."),
    ("Promote peace in the community", "peace",
     "Foster cooperation and dialogue, recognising that shared responsibility for the environment brings neighbours together."),
    ("Promote democracy and children’s rights", "child",
     "Encourage inclusive participation in community decisions and protect every child’s right to grow up in a clean, safe environment."),
]

VALUES = [
    ("Equality", "Usawa", "scale",
     "We treat every person with fairness and respect, and make sure women, youth and marginalised groups have an equal voice in our work."),
    ("Transparency", "Uwazi", "eye",
     "We are open about our plans, finances and results, so partners and communities can see exactly how resources are used."),
    ("Accountability", "Uwajibikaji", "shield",
     "We take responsibility for our commitments and measure our results against the promises we make."),
    ("Diligence", "Bidii", "award",
     "We work hard and persistently, because protecting the environment takes consistent effort, not one-off events."),
]

MILESTONES = [
    ("The beginning", "Door to door for cleaner streets",
     "Young neighbours start educating households near a local football ground on waste storage and collection — and streets become visibly cleaner."),
    ("2021", "Registered as a national NGO",
     "WEMASA is formally registered under Tanzania’s NGO Act (Reg. No. ooNGO/R/2395), turning a neighbourhood initiative into a national organisation."),
    ("Growing reach", "Schools, markets and farms",
     "Programmes expand to climate awareness in 8 Temeke secondary schools, tree planting in schools, organic farming training and environmental data mapping."),
    ("2026", "First workshop for women environment journalists",
     "On 11 March 2026, as part of International Women’s Day, WEMASA hosts its first workshop for young girls and women environment journalists — covered by national TV, newspapers and online media."),
    ("2026", "World Cleanup Day with UNESCO",
     "On 21 September 2026, WEMASA and UNESCO Tanzania lead a cleanup and a waste and brand audit at Mbezi Beach, Dar es Salaam."),
]

FOCUS = [
    ("Waste Management & Community Cleanups", "recycle", "cleanup-01.webp",
     "Mobilising neighbourhoods, beaches and public spaces to clean up — and teaching households how to store and dispose of waste responsibly.",
     "<p>Uncollected waste is one of the most visible environmental challenges in Tanzania’s growing cities. It blocks drains, "
     "spreads disease and damages the places where people live, work and play.</p>"
     "<p>WEMASA organises beach and community cleanups with residents, local leaders and partners, and follows them with "
     "door-to-door education on storing waste properly and supporting reliable collection services. Our goal is not a single "
     "clean day, but lasting habits that keep neighbourhoods clean.</p>"),
    ("Environmental & Climate Education", "graduation", "trees-school-04.webp",
     "Bringing climate change and environmental awareness into secondary schools so young people grow up as champions for the planet.",
     "<p>Young people will live with the consequences of climate change the longest — and they are powerful messengers in their "
     "families and communities.</p>"
     "<p>Through interactive awareness sessions in secondary schools, WEMASA explains the causes and impacts of climate change, "
     "the link between waste and the environment, and the everyday actions students can take. In Temeke District alone, our "
     "sessions have reached 3,700 students across 8 secondary schools.</p>"),
    ("Sustainable & Organic Agriculture", "sprout", "farming-03.webp",
     "Training women vegetable farmers in organic methods, including natural pesticides, boosters and fungicides made from local plants.",
     "<p>Many small-scale vegetable farmers depend on costly chemical inputs that can harm soil, water and health.</p>"
     "<p>WEMASA trains women farmers in practical organic techniques — preparing natural pesticides, plant boosters and "
     "fungicides from locally available plants. The result is healthier crops, safer food and a farming model that protects the "
     "environment. Trainings have taken place with farmer groups in Kisewe and Kiburugwa, Dar es Salaam.</p>"),
    ("Tree Planting & Greening", "tree", "trees-school-06.webp",
     "Planting trees in schools and communities to restore green cover, provide shade and help fight climate change.",
     "<p>Trees cool our cities, protect soils, support biodiversity and absorb carbon. Every tree planted with a student or a "
     "community member is also a lesson in stewardship.</p>"
     "<p>WEMASA leads tree-planting days in schools — including Kibasila, Kongowe, Lionel and Vingunguti — and in public "
     "spaces, working with pupils, teachers, local leaders and partners to plant and care for seedlings.</p>"),
    ("Clean Energy & Environmental Data", "chart", "",
     "Generating evidence on cooking-fuel use and waste-collection points to guide cleaner energy choices and better waste services.",
     "<p>Good decisions need good data. WEMASA collects and maps information that helps communities, authorities and partners "
     "understand environmental challenges.</p>"
     "<p>We have mapped 78 food vendors across four major Temeke markets — Sterio, Kizuiani, Kampocheo and Mtongani — to "
     "understand their use of charcoal, gas and firewood, and mapped waste-collection points in the Dar es Salaam Region "
     "using a digital waste-mapping app.</p>"),
    ("Women & Media for the Environment", "mic", "workshop-01.webp",
     "Empowering young women journalists to report accurately and powerfully on environmental issues.",
     "<p>The media shapes how society understands environmental problems — and women’s voices are essential in that story.</p>"
     "<p>WEMASA builds the capacity of young girls and women journalists to investigate and report on waste, climate and "
     "natural resources. Our first workshop, held in March 2026 during International Women’s Day, was itself covered by "
     "national television, newspapers and online media.</p>"),
]

# Photos from the women journalists workshop, 11 March 2026 (name, caption).
WORKSHOP_PHOTOS = [
    ("workshop-10.webp", "A WEMASA session marking International Women’s Day 2026"),
    ("workshop-04.webp", "A session on why so few Tanzanian households cook with gas"),
    ("workshop-03.webp", "Women journalists during a session on clean cooking energy"),
    ("workshop-05.webp", "A session on saving and investing"),
    ("workshop-02.webp", "Participants and facilitators at the workshop"),
    ("workshop-06.webp", "Women journalists at the workshop"),
    ("workshop-07.webp", "Women journalists at the workshop"),
    ("workshop-08.webp", "Participants at the workshop"),
    ("workshop-09.webp", "Women journalists at the workshop"),
    ("workshop-11.webp", "Participants following a session"),
]

# Photos are (file name, caption). An empty caption shows the album name instead.
COMMUNITY_CLEANUP_PHOTOS = [
    ("community-01.webp", "Residents sweeping a market street during a community cleanup"),
    ("community-02.webp", "Clearing waste from a blocked drain"),
    ("community-03.webp", "Volunteers and residents at a market cleanup"),
    ("community-04.webp", "Community members joining the cleanup"),
    ("community-05.webp", "A drain choked with plastic waste"),
    ("community-06.webp", "Volunteers getting ready for a community cleanup"),
    ("community-07.webp", "“Weka taka hapa” (put waste here) bins for the community"),
    ("community-08.webp", "Bags of waste collected by volunteers"),
]

BEACH_CLEANUP_PHOTOS = [
    ("beach-01.webp", "Volunteers with the bags of waste they collected"),
    ("beach-02.webp", "Volunteers after a beach cleanup"),
    ("beach-03.webp", "Volunteers spread out along the beach"),
    ("beach-04.webp", "Picking up plastic from the shoreline"),
] + [("beach-%02d.webp" % i, "") for i in range(5, 17)]

WABA_PHOTOS = [
    ("waba-01.webp", "Sorting collected waste by type and brand"),
    ("waba-02.webp", "Syringes found during a waste audit"),
    ("waba-03.webp", "Volunteers recording the brands found in the waste"),
    ("waba-04.webp", "Checking a package to record its brand"),
    ("waba-05.webp", "Sorting beach waste for an audit"),
    ("waba-06.webp", "Auditing waste on the shore"),
    ("waba-07.webp", "Plastic containers sorted for counting"),
    ("waba-08.webp", "Waste laid out by category for the audit"),
]

WORLD_CLEANUP_DAY_PHOTOS = [
    ("wcd2026-01.webp", "Volunteers and UNESCO staff sorting a sample of the waste at Mbezi Beach"),
    ("wcd2026-02.webp", "Sorting waste for the waste and brand audit"),
    ("wcd2026-03.webp", "A sample of the waste collected on Mbezi Beach"),
    ("wcd2026-04.webp", "Clearing tangled waste from the beach"),
    ("wcd2026-05.webp", "Filling bags with waste on Mbezi Beach"),
]

WORKSHOP_PARTNERS = [
    "Lake Group", "Taifa Gas", "Nabaki Afrika", "Tanzania Coffee Board", "Kilimani Yetu Organization",
    "Tanga Women's Gala", "Mazingira Konekti", "Stara Fashion Week", "SB Plastics EPZ Ltd", "UTT AMIS",
    "Tanzania Human Rights Defenders Coalition (THRDC)",
]

WORKSHOP_REPORT = "1st Workshop for Young Girls and Women Environment Journalists: Report"
CLEANUP_DAY_REPORT = "World Cleanup Day 2026: Mbezi Beach Cleanup Report"

LEAD_PROJECTS = [
    "World Cleanup Day 2026: Mbezi Beach Cleanup", "Waste and Brand Audits (WABA)", "Beach & Community Cleanups",
]

PROJECTS = [
    {
        "title": "Organic Farming Training for Women Vegetable Farmers",
        "focus": "Sustainable & Organic Agriculture", "status": "completed", "cover": "kisewe-01.webp",
        "location": "Kisewe and Kiburugwa, Dar es Salaam", "beneficiaries": "Women vegetable farmers",
        "summary": "Hands-on training for women vegetable farmers in Kisewe and Kiburugwa to prepare natural pesticides, plant boosters and fungicides from local plants.",
        "description": (
            "<p>For many women vegetable growers around Dar es Salaam, pests and plant diseases mean buying expensive chemical "
            "products — costs that cut into household income and can harm soil, water and health.</p>"
            "<p>WEMASA organised practical, field-based training for women farmer groups in <strong>Kisewe</strong> and "
            "<strong>Kiburugwa</strong>. Working directly in the vegetable plots, participants learned step by step how to "
            "prepare:</p>"
            "<ul><li><strong>Natural pesticides</strong> from locally available plants and leaves;</li>"
            "<li><strong>Organic boosters</strong> to strengthen plant growth;</li>"
            "<li><strong>Natural fungicides</strong> to prevent fungal disease in vegetables.</li></ul>"
            "<p>Sessions combined demonstrations, group discussion and practice, so every participant left able to make the "
            "preparations herself — and to share the knowledge with neighbours.</p>"
        ),
        "outcomes": (
            "Women farmers practised preparing natural pesticides, boosters and fungicides themselves\n"
            "Training delivered in two farming communities: Kisewe and Kiburugwa\n"
            "Participants equipped to reduce reliance on costly chemical inputs"
        ),
        "stats": [("2", "Farming communities trained")],
        "photos": [("kisewe-0%d.webp" % i) for i in range(1, 8)] + [("kiburugwa-0%d.webp" % i) for i in range(2, 10)]
                  + [("farming-0%d.webp" % i) for i in range(1, 10)],
        "album": "Organic farming training",
    },
    {
        "title": "School Climate Change Awareness Programme",
        "focus": "Environmental & Climate Education", "status": "completed", "cover": "trees-school-04.webp",
        "location": "Temeke District, Dar es Salaam", "beneficiaries": "Secondary school students",
        "summary": "Interactive climate change awareness sessions that reached 3,700 students in 8 secondary schools across Temeke District.",
        "description": (
            "<p>Climate change can feel distant and abstract — until students connect it to the flooding, heat and waste they "
            "see in their own neighbourhoods.</p>"
            "<p>WEMASA delivered climate change awareness sessions in <strong>8 secondary schools in Temeke District</strong>, "
            "reaching <strong>3,700 students</strong>. Sessions explained the causes and impacts of climate change, the role "
            "of waste and deforestation, and the practical actions young people can lead at school and at home.</p>"
            "<p>Students are encouraged to become environmental ambassadors — carrying messages about waste management, tree "
            "planting and conservation back to their families and communities.</p>"
        ),
        "outcomes": (
            "3,700 students reached with climate change awareness sessions\n"
            "8 secondary schools in Temeke District engaged\n"
            "Students encouraged to act as environmental ambassadors at home and school"
        ),
        "stats": [("3,700", "Students reached"), ("8", "Secondary schools")],
        "photos": [],
    },
    {
        "title": "School Tree Planting Programme",
        "focus": "Tree Planting & Greening", "status": "ongoing", "cover": "schools-03.webp",
        "location": "Kibasila, Kongowe, Lionel and Vingunguti schools", "beneficiaries": "Pupils, students and teachers",
        "summary": "Greening school compounds with pupils and students at Kibasila, Kongowe, Lionel and Vingunguti — building a culture of environmental care from a young age.",
        "description": (
            "<p>Schools are where lifelong habits begin. Our School Tree Planting Programme brings learners, teachers, local "
            "leaders and partners together to plant and care for trees on school grounds.</p>"
            "<p>Tree-planting days have taken place at <strong>Kibasila, Kongowe, Lionel and Vingunguti</strong>. Each "
            "activity combines a short lesson on why trees matter — shade, clean air, soil protection and climate action — "
            "with hands-on planting, so every pupil helps a seedling take root.</p>"
        ),
        "outcomes": (
            "Tree planting carried out at four schools\n"
            "Pupils and students planted seedlings with their own hands\n"
            "School communities engaged in caring for newly planted trees"
        ),
        "stats": [("4", "Schools greened")],
        "photos": ["schools-0%d.webp" % i for i in range(1, 5)] + ["trees-school-0%d.webp" % i for i in range(1, 8)],
        "album": "School tree planting",
    },
    {
        "title": "Beach & Community Cleanups",
        "focus": "Waste Management & Community Cleanups", "status": "ongoing", "cover": "cover-beach-cleanup-hd.webp",
        "location": "Dar es Salaam", "beneficiaries": "Residents, youth and local leaders",
        "summary": "Mobilising volunteers, residents and partners to clear waste from beaches, streets and public spaces — and to keep them clean.",
        "description": (
            "<p>WEMASA cleanups bring together volunteers, women and youth groups, local leaders and partners to collect and "
            "remove waste from streets, beaches and public spaces.</p>"
            "<p>But a cleanup is only the beginning. Each event is paired with awareness on proper waste storage, the "
            "importance of paying for waste collection and the health risks of dumping — so that communities keep their "
            "surroundings clean long after the volunteers go home.</p>"
        ),
        "outcomes": (
            "Volunteers mobilised to collect waste from public spaces\n"
            "Collected waste bagged and handed over for proper disposal\n"
            "Residents engaged on proper waste storage and collection"
        ),
        "stats": [],
        "photos": ["cleanup-0%d.webp" % i for i in range(1, 4)],
        "album": "Community cleanups",
    },
    {
        "title": "World Cleanup Day 2026: Mbezi Beach Cleanup",
        "focus": "Waste Management & Community Cleanups", "status": "completed", "cover": "cover-world-cleanup-day-hd.webp",
        "location": "Rainbow Beach (Mbezi Beach), Dar es Salaam", "period": "21 September 2026",
        "beneficiaries": "Mbezi Beach community and volunteers",
        "summary": "With UNESCO Tanzania, more than 45 volunteers cleared 250 kg of waste from Mbezi Beach on World Cleanup Day 2026, then audited it to see what it was and where it came from.",
        "description": (
            "<p>On <strong>21 September 2026</strong>, for World Cleanup Day (theme: <em>“Strive for Five: From Clean "
            "Plates to Clean Cities”</em>), <strong>UNESCO Tanzania</strong> and WEMASA organised a cleanup at Rainbow "
            "Beach (Mbezi Beach) in Dar es Salaam.</p>"
            "<p>Over five hours, more than 45 volunteers, working with local community groups, filled "
            "<strong>50 bags with 250 kg of waste</strong>.</p>"
            "<p>A waste and brand audit of a 5% sample (5 full bags) found plastic bags were the most common item "
            "(150), followed by other plastic bottles (67) and baby diapers (35). MeTL, mainly through Mo Extra drinks, "
            "was the leading brand, followed by Mango Juice by U-Fresh Food Ltd and Tanga Fresh by Tanga Fresh Limited.</p>"
            "<p>A cleanup alone cannot fix the root causes of waste pollution. WEMASA is building on the day with "
            "year-round education, community mobilisation and data, so that beaches like Mbezi stay clean.</p>"
        ),
        "outcomes": (
            "50 bags of waste (250 kg) removed from Mbezi Beach\n"
            "Waste and brand audit carried out on a 5% sample of the waste\n"
            "Plastic bags identified as the most common item, and MeTL as the leading brand"
        ),
        "stats": [("45+", "Volunteers"), ("50", "Bags of waste"), ("250 kg", "Waste collected")],
        "photos": WORLD_CLEANUP_DAY_PHOTOS,
        "album": "World Cleanup Day 2026",
        "partners": ["UNESCO Tanzania"],
        "report": CLEANUP_DAY_REPORT,
    },
    {
        "title": "Waste and Brand Audits (WABA)",
        "focus": "Waste Management & Community Cleanups", "status": "ongoing", "cover": "cover-waba-hd.webp",
        "location": "Dar es Salaam", "beneficiaries": "Communities, local authorities and producers",
        "summary": "After a cleanup we sort and count the waste and record the brand on each item, to show what pollutes our streets and beaches and who produces it.",
        "description": (
            "<p>A cleanup removes waste; an audit explains it. In a Waste and Brand Audit (WABA), volunteers take a "
            "sample of the waste collected, sort it by type and record the brand on every item they can identify.</p>"
            "<p>The results show which kinds of waste are most common and whose products end up in the environment "
            "most often. WEMASA uses this evidence in awareness work, in discussions with local authorities and to "
            "call on producers to take responsibility for their packaging.</p>"
            "<p>At Mbezi Beach on World Cleanup Day 2026, an audit of 5 sample bags counted 150 plastic bags, 67 other "
            "plastic bottles and 35 baby diapers. The leading brands were MeTL (mainly Mo Extra drinks), U-Fresh Food Ltd "
            "(Mango Juice) and Tanga Fresh Limited.</p>"
        ),
        "outcomes": (
            "Collected waste sorted and counted by type\n"
            "Brands identified on the waste found\n"
            "Evidence for producers, local authorities and communities"
        ),
        "stats": [("150", "Plastic bags in a 5-bag sample at Mbezi Beach"), ("3", "Leading polluting brands named")],
        "photos": WABA_PHOTOS,
        "album": "Waste and brand audits",
    },
    {
        "title": "1st Workshop for Young Girls and Women Environment Journalists",
        "focus": "Women & Media for the Environment", "status": "completed", "cover": "workshop-01.webp",
        "location": "Dar es Salaam", "period": "11 March 2026", "beneficiaries": "Young women journalists",
        "summary": "A capacity-building workshop, held for International Women’s Day 2026, equipping women journalists to report on environmental challenges.",
        "description": (
            "<p>On <strong>11 March 2026</strong>, as part of International Women’s Day celebrations, WEMASA hosted the "
            "<strong>1st Workshop for Young Girls and Women Environment Journalists</strong> in Dar es Salaam.</p>"
            "<p>Women journalists had the opportunity to learn about and analyse environmental challenges — including the "
            "wide-ranging impacts of waste — and to explore how stronger reporting can drive public awareness and action. "
            "Discussions also addressed barriers to clean cooking energy for households.</p>"
            "<p>The workshop received wide coverage from national television, newspapers and online outlets, including "
            "Nipashe, Tanzania Leo, Mtanzania Leo, Star TV, SMTV, Tanganyika Television and Watetezi TV.</p>"
        ),
        "outcomes": (
            "Women journalists trained to report on environmental issues\n"
            "Environmental challenges and clean cooking energy discussed with experts and partners\n"
            "Coverage across national TV, newspapers and online media"
        ),
        "stats": [("1st", "Edition of the workshop"), ("10+", "Media outlets covered it")],
        "photos": ["workshop-01.webp"] + WORKSHOP_PHOTOS,
        "album": "Women journalists workshop",
        "partners": WORKSHOP_PARTNERS,
        "report": WORKSHOP_REPORT,
    },
    {
        "title": "Food Vendors Cooking Energy Mapping",
        "focus": "Clean Energy & Environmental Data", "status": "completed", "cover": "",
        "location": "Sterio, Kizuiani, Kampocheo and Mtongani markets, Temeke", "beneficiaries": "Market food vendors",
        "summary": "Mapping the cooking fuels used by 78 food vendors in four major Temeke markets — charcoal, gas and firewood — to inform cleaner energy solutions.",
        "description": (
            "<p>Food vendors in busy markets cook all day, and their choice of fuel affects their health, their costs and the "
            "surrounding environment.</p>"
            "<p>WEMASA visited <strong>78 food vendors</strong> in four of Temeke’s biggest markets — <strong>Sterio, "
            "Kizuiani, Kampocheo and Mtongani</strong> — to map who uses charcoal, gas and firewood. This evidence helps "
            "partners and authorities design practical solutions that make clean cooking energy accessible to small "
            "businesses.</p>"
        ),
        "outcomes": (
            "78 food vendors visited and their cooking fuels recorded\n"
            "Four major Temeke markets mapped\n"
            "Evidence generated to guide clean cooking energy interventions"
        ),
        "stats": [("78", "Food vendors mapped"), ("4", "Markets covered")],
        "photos": [],
    },
    {
        "title": "Waste Collection Points Mapping",
        "focus": "Clean Energy & Environmental Data", "status": "completed", "cover": "",
        "location": "Dar es Salaam Region", "beneficiaries": "Communities and local authorities",
        "summary": "Using a digital waste-mapping app to record waste-collection points across Dar es Salaam Region and support better waste services.",
        "description": (
            "<p>Knowing where waste is collected — and where it is not — is the first step to better services.</p>"
            "<p>WEMASA used a digital waste-mapping application to record waste-collection points across the "
            "<strong>Dar es Salaam Region</strong>. The resulting data helps identify gaps in collection coverage and "
            "supports conversations with communities and local authorities about improving waste management.</p>"
        ),
        "outcomes": (
            "Waste-collection points recorded digitally across Dar es Salaam Region\n"
            "Data available to support planning of waste services"
        ),
        "stats": [],
        "photos": [],
    },
]

# Albums added once, when no photo has that album name yet: (album, project title or "", photos).
EXTRA_ALBUMS = [
    ("Community tree planting", "", ["trees-community-0%d.webp" % i for i in range(1, 5)]),
    ("Community cleanup engagement", "Beach & Community Cleanups", COMMUNITY_CLEANUP_PHOTOS),
    ("Beach cleanups", "Beach & Community Cleanups", BEACH_CLEANUP_PHOTOS),
]

IMPACT = [
    (3700, "+", "Students reached", "Climate change awareness sessions in 8 secondary schools in Temeke", "graduation", True),
    (8, "", "Secondary schools", "Engaged in our school climate awareness programme", "school", True),
    (78, "", "Food vendors mapped", "Across 4 major Temeke markets to understand cooking-fuel use", "flame", True),
    (10, "+", "Media features", "TV, newspaper and online coverage of WEMASA’s work", "mic", True),
    (4, "", "Schools greened", "Tree planting at Kibasila, Kongowe, Lionel and Vingunguti", "tree", False),
    (2, "", "Farming communities trained", "Women vegetable farmers in Kisewe and Kiburugwa", "sprout", False),
]

SDGS = [
    (4, "Quality Education", "Climate change awareness in secondary schools and hands-on environmental learning for communities."),
    (5, "Gender Equality", "Training women farmers and building the skills and voice of young women environment journalists."),
    (7, "Affordable and Clean Energy", "Mapping cooking-fuel use among food vendors to support the shift to cleaner energy."),
    (11, "Sustainable Cities and Communities", "Cleanups, waste-collection mapping and better waste services for growing urban communities."),
    (12, "Responsible Consumption and Production", "Promoting responsible waste storage, disposal and organic farming practices."),
    (13, "Climate Action", "Raising awareness of climate change and mobilising young people to act."),
    (15, "Life on Land", "Tree planting in schools and communities to restore green cover and protect biodiversity."),
]

TEAM = [
    ("Ibrahim Haule", "Co-Founder & Executive Director", "founders", "team/ibrahim-haule.webp",
     "As Co-Founder and Executive Director, Ibrahim provides strategic leadership for WEMASA — guiding its programmes, "
     "partnerships and growth from a neighbourhood initiative into a registered national organisation."),
    ("Jackline Ndawila", "Co-Founder & Head of Women Projects", "founders", "team/jackline-ndawila.webp",
     "Jackline is a Co-Founder of WEMASA and leads its women-focused projects, ensuring that women and girls are at the "
     "centre of the organisation’s environmental work — from farming communities to the newsroom."),
    ("Carlos Mdemu", "Training Officer", "staff", "",
     "Carlos designs and facilitates WEMASA’s trainings and awareness sessions, translating environmental knowledge "
     "into practical learning for communities, students and journalists."),
    ("Frednand Nseso", "Chief Accountant", "staff", "team/frednand-nseso.jpg",
     "Frednand leads WEMASA’s financial management, safeguarding the transparency and accountability that partners "
     "and communities expect."),
    ("Hashim Mapengo", "Data Officer", "staff", "team/hashim-mapengo.webp",
     "Hashim manages WEMASA’s data and mapping work — including surveys of market food vendors and the mapping of "
     "waste-collection points — turning field information into evidence for action."),
    ("Jumanne Msumi", "Assistant Accountant", "staff", "team/jumanne-msumi.webp",
     "Jumanne supports WEMASA’s finance function, keeping accurate records and helping ensure every resource is "
     "properly accounted for."),
    ("Omary Mgomba", "Safeguarding Officer", "staff", "team/omary-mgomba.webp",
     "Omary oversees safeguarding across WEMASA’s activities, helping ensure that children, women and every "
     "participant are safe, respected and protected."),
    ("Lamlaty Omary", "Community Outreach Officer", "staff", "team/lamlaty-omary.webp",
     "Lamlaty connects WEMASA with the communities it serves — mobilising residents, groups and local leaders to take "
     "part in programmes and environmental action."),
]

# (name, category, logo in seed/images/partners/)
PARTNERS = [
    ("Global Fund for Women", "funding", "global-fund-for-women.png"),
    ("UNESCO Tanzania", "international", "unesco.png"),
    ("Government of the United Republic of Tanzania", "government", "tanzania-government.png"),
    ("National Environment Management Council (NEMC)", "government", "nemc.png"),
    ("Temeke Municipal Council", "government", ""),
    ("Tanzania Coffee Board", "government", ""),
    ("Taifa Gas", "corporate", "taifa-gas.png"),
    ("Lake Group", "corporate", "lake-group.png"),
    ("SB Plastics EPZ Ltd", "corporate", "sb-plastics.png"),
    ("UTT AMIS", "corporate", "utt-amis.png"),
    ("Stara Fashion Week", "corporate", ""),
    ("Nabaki Afrika", "ngo", "nabaki-afrika.png"),
    ("Tanzania Human Rights Defenders Coalition (THRDC)", "ngo", ""),
    ("Kilimani Yetu Organization", "ngo", ""),
    ("Mazingira Konekti", "ngo", "mazingira-konekti.png"),
    ("Tanga Women's Gala", "community", ""),
]

# (title, category, file in seed/documents/, cover, published on, description)
RESOURCES = [
    (WORKSHOP_REPORT, "project", "womens-journalists-workshop-report-2026.pdf",
     "womens-journalists-workshop-report-2026.webp", datetime.date(2026, 3, 11),
     "How WEMASA trained 30 young women journalists from more than 25 media houses to report on climate and the "
     "environment, for International Women’s Day 2026."),
    (CLEANUP_DAY_REPORT, "project", "world-cleanup-day-2026-report.pdf",
     "world-cleanup-day-2026-report.webp", datetime.date(2026, 9, 21),
     "The UNESCO Tanzania and WEMASA cleanup at Mbezi Beach: 45+ volunteers, 250 kg of waste, and what the waste "
     "and brand audit found."),
]

MEDIA = [
    ("Nipashe (IPP Media)", "newspaper", "Waandishi habari wanawake waimarishwa kuripoti mazingira", datetime.date(2026, 3, 11), "Pilly Kigome",
     "Nipashe reports on how WEMASA’s workshop strengthened the capacity of women journalists to report on environmental issues."),
    ("Tanzania Leo", "newspaper", "WEMASA watoa elimu ya mazingira wanahabari wanawake nchini", datetime.date(2026, 3, 12), "",
     "Front-page coverage of WEMASA’s environmental education workshop for women journalists."),
    ("Mtanzania Leo", "newspaper", "WEMASA yawanoa wanahabari wanawake utunzaji wa mazingira", datetime.date(2026, 3, 12), "",
     "Front-page story on WEMASA sharpening women journalists’ skills in environmental conservation reporting."),
    ("Watetezi TV", "tv", "THRDC yashiriki warsha ya kwanza ya wanawake na wasichana wanaoandika habari za mazingira", datetime.date(2026, 3, 14), "",
     "Coverage of the first workshop for women and girls who write about the environment, with THRDC’s participation."),
    ("Tanganyika Television", "tv", "WEMASA watoa kipaumbele kwa elimu ya mazingira kwa wanahabari wanawake", datetime.date(2026, 3, 11), "",
     "TTV highlights WEMASA’s focus on environmental education for women journalists during International Women’s Day."),
    ("SMTV", "tv", "WEMASA Tanzania yawajengea uwezo waandishi wa habari wanawake kuhusu masuala ya mazingira", datetime.date(2026, 3, 11), "",
     "SMTV reports on WEMASA building women journalists’ capacity on environmental matters."),
    ("Star TV", "tv", "Kipato kidogo tatizo matumizi ya gesi nchini", datetime.date(2026, 3, 11), "",
     "Discussion from the workshop on how low household income limits the use of cooking gas in Tanzania."),
    ("W-News", "online", "Changamoto ya matumizi nishati safi ya kupikia kutafutiwa suluhu", datetime.date(2026, 3, 11), "",
     "Coverage of the search for solutions to clean cooking energy challenges, discussed at the WEMASA workshop."),
    ("Tanzania Daima", "newspaper", "Coverage of WEMASA’s workshop for women environment journalists", datetime.date(2026, 3, 12), "",
     "Tanzania Daima covered WEMASA’s first workshop for young girls and women environment journalists."),
    ("Mwananchi", "newspaper", "Coverage of WEMASA’s workshop for women environment journalists", datetime.date(2026, 3, 12), "",
     "Mwananchi covered WEMASA’s first workshop for young girls and women environment journalists."),
]

NEWS = [
    {
        "title": "WEMASA and UNESCO clean up Mbezi Beach for World Cleanup Day 2026",
        "category": "event", "cover": "wcd2026-04.webp", "featured": False,
        "date": datetime.datetime(2026, 9, 21, 16, 0),
        "project": "World Cleanup Day 2026: Mbezi Beach Cleanup",
        "excerpt": "More than 45 volunteers collected 50 bags (250 kg) of waste from Mbezi Beach, then audited a sample to find out what it was and which brands it came from.",
        "body": (
            "<p>On 21 September 2026, UNESCO Tanzania and WEMASA marked World Cleanup Day with a cleanup at Rainbow Beach "
            "(Mbezi Beach) in Dar es Salaam. The theme this year was <em>“Strive for Five: From Clean Plates to Clean "
            "Cities”</em>.</p>"
            "<p>From 7 am to midday, more than 45 volunteers, UNESCO staff and local community groups combed the beach "
            "and filled 50 bags with 250 kg of waste.</p>"
            "<h2>What the audit found</h2>"
            "<p>Volunteers then carried out a waste and brand audit on a 5% sample of the waste (5 full bags). Plastic "
            "bags were by far the most common item, with 150 counted, followed by other plastic bottles (67) and baby "
            "diapers (35).</p>"
            "<p>The brand count put MeTL first, mainly because of Mo Extra drinks, followed by Mango Juice from U-Fresh "
            "Food Ltd and Tanga Fresh from Tanga Fresh Limited.</p>"
            "<h2>Beyond one day</h2>"
            "<p>Cleanups alone cannot solve waste pollution. Figures like these give communities, local authorities and "
            "producers evidence to act on, and WEMASA will keep up year-round education, community mobilisation and data "
            "collection so the movement lasts beyond World Cleanup Day.</p>"
            "<p>Thank you to UNESCO Tanzania, local government authorities, community leaders, volunteers, youth and media "
            "partners who made the day a success. Asante sana!</p>"
        ),
    },
    {
        "title": "WEMASA hosts first workshop for young girls and women environment journalists",
        "category": "event", "cover": "workshop-01.webp", "featured": True,
        "date": datetime.datetime(2026, 3, 11, 18, 0),
        "project": "1st Workshop for Young Girls and Women Environment Journalists",
        "excerpt": "As part of International Women’s Day 2026, WEMASA brought women journalists together in Dar es Salaam to learn about and analyse environmental challenges — and how to report on them.",
        "body": (
            "<p>On 11 March 2026, WEMASA Tanzania Organization hosted the <strong>1st Workshop for Young Girls and Women "
            "Environment Journalists</strong> in Dar es Salaam, as part of International Women’s Day celebrations.</p>"
            "<p>The workshop gave women journalists the opportunity to learn about and analyse the environmental challenges "
            "facing Tanzanian communities. A session on the impacts of waste, led by environmental conservation specialist "
            "Carlos Mdemu, explored how poorly managed waste affects health, livelihoods and the climate.</p>"
            "<h2>Why women journalists?</h2>"
            "<p>The media shapes how the public understands environmental problems. By strengthening the skills of women "
            "journalists, WEMASA aims to bring more accurate, more powerful and more diverse environmental stories to "
            "audiences across the country.</p>"
            "<p>Discussions also addressed household access to clean cooking energy, including the barriers that low incomes "
            "create for families who want to switch from charcoal and firewood to gas.</p>"
            "<h2>Wide media coverage</h2>"
            "<p>The workshop was covered by national newspapers including Nipashe, Tanzania Leo and Mtanzania Leo, and by "
            "television and online outlets including Star TV, SMTV, Tanganyika Television, Watetezi TV and W-News.</p>"
            "<blockquote>This was the first edition of the workshop — and the beginning of a growing network of women "
            "telling Tanzania’s environmental story.</blockquote>"
        ),
    },
    {
        "title": "Women farmers in Kisewe and Kiburugwa learn to make natural pesticides and fertilisers",
        "category": "story", "cover": "kisewe-06.webp", "featured": False,
        "date": None,
        "project": "Organic Farming Training for Women Vegetable Farmers",
        "excerpt": "In the vegetable plots of Kisewe and Kiburugwa, women farmers are learning to protect their crops with natural preparations made from local plants.",
        "body": (
            "<p>For women vegetable farmers on the outskirts of Dar es Salaam, every shilling spent on chemical pesticides "
            "is a shilling that does not reach the family. WEMASA’s organic farming training offers another way.</p>"
            "<p>Working directly in the fields of <strong>Kisewe</strong> and <strong>Kiburugwa</strong>, WEMASA trainers "
            "showed farmer groups how to prepare natural pesticides, plant boosters and fungicides using leaves and plants "
            "that grow locally. Participants chopped, mixed and prepared each recipe themselves, taking notes to share with "
            "others in their groups.</p>"
            "<h2>Healthier crops, healthier communities</h2>"
            "<p>Organic methods protect the soil and water that farming depends on, reduce exposure to harmful chemicals and "
            "lower production costs. Just as importantly, they put knowledge — and confidence — in the hands of women "
            "farmers.</p>"
        ),
    },
]

# (kind, title, account name, account number, branch, branch code, SWIFT, currency, instructions)
DONATION_METHODS = [
    ("bank", "Equity Bank", "WEMASA TANZANIA", "3010211798818", "Temeke Branch", "3010", "EQBLTZTZQ", "TZS",
     "After your transfer, please send the payment slip or confirmation to us on WhatsApp or by email, so that we can "
     "send you an official receipt."),
]

INVOLVEMENT = [
    ("Volunteer with us", "hand-heart", "Join cleanups, tree-planting days and community awareness campaigns. No environmental background needed — just energy and commitment.", "Become a volunteer", "/contact/?topic=volunteer"),
    ("Partner with WEMASA", "handshake", "Development partners, businesses and institutions can co-design, fund or scale programmes with measurable community impact.", "Discuss a partnership", "/contact/?topic=partnership"),
    ("Donate", "heart", "Your gift funds training materials, cleanup equipment, tree seedlings and school awareness sessions.", "Give today", "/donate/"),
    ("Invite us to your school", "school", "Bring climate change awareness and tree planting to your students. We work with primary and secondary schools.", "Request a visit", "/contact/?topic=general"),
    ("Media & storytelling", "megaphone", "Journalists and content creators can help amplify environmental stories and the voices of the communities we serve.", "Media enquiries", "/contact/?topic=media"),
    ("Spread the word", "send", "Follow WEMASA, share our stories and encourage your network to keep their surroundings clean.", "Subscribe to updates", "#newsletter"),
]

FAQS = [
    ("Is WEMASA a registered organisation?",
     "Yes. WEMASA Tanzania Organization is a non-governmental organisation registered in 2021 under Tanzania’s NGO Act, Registration No. ooNGO/R/2395, with a national area of operation."),
    ("Where does WEMASA work?",
     "We are registered to operate nationally. Most of our current programmes take place in Dar es Salaam, especially Temeke District, and we are expanding to new communities with our partners."),
    ("How are donations used?",
     "Donations fund programme activities such as training materials, cleanup equipment, tree seedlings, school awareness sessions and community mobilisation. We issue receipts and share reports on results."),
    ("Can I volunteer without an environmental background?",
     "Absolutely. Our volunteers include students, professionals and community members. We provide orientation, and there are roles in field activities, communications, data collection and more."),
    ("Can my school or community request a WEMASA programme?",
     "Yes. Contact us with your location and what you have in mind, and our team will discuss how we can work together."),
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

        for page, eyebrow, title, subtitle, image in HEADERS:
            header, created = m.PageHeader.objects.get_or_create(
                page=page, defaults={"eyebrow": eyebrow, "title": title, "subtitle": subtitle})
            if created and set_images(header, image=image):
                header.save()

        self.seed_simple(m.Objective, "title", [
            {"title": t, "icon": i, "description": d} for t, i, d in OBJECTIVES])
        self.seed_simple(m.CoreValue, "name", [
            {"name": n, "local_name": l, "icon": i, "description": d} for n, l, i, d in VALUES])
        self.seed_simple(m.Milestone, "title", [
            {"year": y, "title": t, "description": d} for y, t, d in MILESTONES])

        focus_by_title = {}
        for order, (title, icon, image, summary, description) in enumerate(FOCUS):
            area, created = m.FocusArea.objects.get_or_create(
                title=title, defaults={"icon": icon, "summary": summary, "description": description, "order": order})
            if created and set_images(area, image=image):
                area.save()
            focus_by_title[title] = area

        # The first version of this file misspelt SB Plastics.
        if not m.Partner.objects.filter(name="SB Plastics EPZ Ltd").exists():
            m.Partner.objects.filter(name="SP Plastics").update(name="SB Plastics EPZ Ltd")
        partners = {}
        for order, (name, category, logo) in enumerate(PARTNERS):
            partner, _ = m.Partner.objects.get_or_create(name=name, defaults={"category": category, "order": order})
            if set_images(partner, logo=f"partners/{logo}" if logo else ""):
                partner.save()
            partners[name] = partner

        resources = {}
        for title, category, filename, cover, date, description in RESOURCES:
            resource = m.Resource.objects.filter(title=title).first()
            if not resource:
                f = photo(filename, DOCS_DIR)
                if not f:
                    continue
                resource = m.Resource(title=title, category=category, published_on=date, description=description)
                if not upload(resource.file, f):
                    continue
                set_images(resource, cover=f"../documents/{cover}")
                resource.save()
            resources[title] = resource

        projects = {}
        # The latest work, with HD cover photos, comes first: the home page slider shows the first three.
        ordered = sorted(PROJECTS, key=lambda d: (d["title"] not in LEAD_PROJECTS, LEAD_PROJECTS.index(d["title"]) if d["title"] in LEAD_PROJECTS else 0))
        for order, data in enumerate(ordered):
            project, created = m.Project.objects.get_or_create(title=data["title"], defaults={
                "focus_area": focus_by_title.get(data["focus"]), "status": data["status"], "summary": data["summary"],
                "description": data["description"], "location": data["location"], "period": data.get("period", ""),
                "beneficiaries": data["beneficiaries"], "outcomes": data["outcomes"], "order": order,
            })
            projects[project.title] = project
            # Partners and the report are also filled in on projects that already exist, if still empty.
            if data.get("partners") and not project.partners.exists():
                project.partners.set([partners[name] for name in data["partners"]])
            if data.get("report") in resources and not project.report_id:
                project.report = resources[data["report"]]
                project.save(update_fields=["report"])
            if not created:
                continue
            if set_images(project, cover=data["cover"]):
                project.save()
            for i, (value, label) in enumerate(data["stats"]):
                m.ProjectStat.objects.create(project=project, value=value, label=label, order=i)
            for i, name in enumerate(data["photos"]):
                name, caption = name if isinstance(name, tuple) else (name, "")
                self.add_photo(name, project=project, album=data.get("album", ""), caption=caption, order=i)

        for album, project_title, names in EXTRA_ALBUMS:
            if not m.GalleryImage.objects.filter(album=album).exists():
                for i, name in enumerate(names):
                    name, caption = name if isinstance(name, tuple) else (name, "")
                    self.add_photo(name, album=album, caption=caption, project=projects.get(project_title), order=100 + i)

        for order, (value, suffix, label, desc, icon, home) in enumerate(IMPACT):
            m.ImpactStat.objects.get_or_create(label=label, defaults={
                "value": value, "suffix": suffix, "description": desc, "icon": icon, "show_on_home": home, "order": order})

        for order, (number, title, desc) in enumerate(SDGS):
            m.SDG.objects.get_or_create(number=number, defaults={"title": title, "description": desc, "order": order})

        for order, (name, role, group, image, bio) in enumerate(TEAM):
            member, created = m.TeamMember.objects.get_or_create(
                name=name, defaults={"role": role, "group": group, "bio": bio, "order": order})
            # A photo added here later also reaches members that already exist, if they still have none.
            if set_images(member, photo=image):
                member.save()

        for order, (outlet, kind, headline, date, reporter, excerpt) in enumerate(MEDIA):
            m.MediaCoverage.objects.get_or_create(outlet=outlet, headline=headline, defaults={
                "media_type": kind, "published_on": date, "reporter": reporter, "excerpt": excerpt, "order": order})

        for data in NEWS:
            if m.NewsPost.objects.filter(title=data["title"]).exists():
                continue
            date = timezone.make_aware(data["date"]) if data["date"] else timezone.now()
            post = m.NewsPost(title=data["title"], category=data["category"], excerpt=data["excerpt"], body=data["body"],
                              is_featured=data["featured"], published_at=date, project=projects.get(data["project"]))
            set_images(post, cover=data["cover"])
            post.save()

        self.seed_simple(m.DonationMethod, "title", [
            {"kind": k, "title": t, "account_name": n, "account_number": no, "branch": b, "branch_code": bc,
             "swift_code": sw, "currency": c, "instructions": i}
            for k, t, n, no, b, bc, sw, c, i in DONATION_METHODS])
        self.seed_simple(m.InvolvementOption, "title", [
            {"title": t, "icon": i, "description": d, "button_text": b, "button_url": u} for t, i, d, b, u in INVOLVEMENT])
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
        if upload(img.image, f):
            img.save()
