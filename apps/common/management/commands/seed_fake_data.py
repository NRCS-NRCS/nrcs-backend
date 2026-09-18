"""Wipe the local database and repopulate it with realistic fake content.

Meant for local development and demos only -- the command refuses to run
outside DEBUG unless ``--force`` is passed.

Files (cover images, attachments, audio) come from an assets directory laid
out as::

    <assets-dir>/images/   jpg/png for cover images and markdown inline images
    <assets-dir>/logos/    jpg/png for partner logos
    <assets-dir>/docs/     pdf/docx/xlsx/csv for every FileField
    <assets-dir>/audio/    mp3 for radio programs

A missing directory is simply skipped: the matching field is left empty, or the
object is skipped when the field is required.
"""

from __future__ import annotations

import random
import shutil
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.core.management.sql import emit_post_migrate_signal
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.utils import timezone

from apps.blog.models import Blog
from apps.common.models import StatusEnum
from apps.department.models import Department
from apps.faq.models import Faq
from apps.news.models import ActionLink, KeyStat, News, NewsAttachment
from apps.partner.models import Partner, PartnerScopeEnum
from apps.procurement.models import Procurement
from apps.project.models import Project
from apps.radio_program.models import RadioProgram, RadioProgramTypeEnum
from apps.resources.models import Resource, ResourceTypeEnum
from apps.strategic.models import MajorResponsibilities, StrategicDirectives
from apps.vacancy.models import JobVacancy

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
DOC_SUFFIXES = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt"}
AUDIO_SUFFIXES = {".mp3", ".wav", ".ogg", ".flac", ".aac"}


class AssetPool:
    """Cycles through the files in a directory so every object gets one."""

    def __init__(self, directory: Path, suffixes: set[str]):
        self.directory = directory
        self.paths: list[Path] = []
        if directory.is_dir():
            self.paths = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in suffixes)
        self._cursor = 0

    def __bool__(self) -> bool:
        return bool(self.paths)

    def next_path(self) -> Path | None:
        if not self.paths:
            return None
        path = self.paths[self._cursor % len(self.paths)]
        self._cursor += 1
        return path

    def next_file(self) -> ContentFile | None:
        """Next asset as an in-memory file, ready to assign to a File/ImageField."""
        path = self.next_path()
        if path is None:
            return None
        return ContentFile(path.read_bytes(), name=path.name)


# -- Content ---------------------------------------------------------------

DIRECTIVES = [
    (
        "Health and Care in the Community",
        (
            "Improve the health status of vulnerable communities through community based health promotion, "
            "first aid training, epidemic preparedness and better access to essential services."
        ),
    ),
    (
        "Disaster Risk Management",
        (
            "Strengthen the resilience of at-risk communities by reducing disaster risk, preparing for "
            "effective response and supporting recovery that builds back safer."
        ),
    ),
    (
        "Blood Service",
        (
            "Ensure a safe, adequate and sustainable supply of blood and blood components through a "
            "nationwide network of voluntary non-remunerated donors."
        ),
    ),
    (
        "Water, Sanitation and Hygiene Promotion",
        (
            "Increase sustainable access to safe drinking water, improved sanitation and better hygiene "
            "practices in underserved rural and peri-urban communities."
        ),
    ),
    (
        "Organisational Development and Volunteer Management",
        (
            "Build a well governed, financially sustainable National Society with a motivated, well "
            "trained and protected volunteer base at district and sub-chapter level."
        ),
    ),
    (
        "Humanitarian Principles, Values and Advocacy",
        (
            "Promote the Fundamental Principles, humanitarian diplomacy, social inclusion and protection, "
            "gender and diversity across all programmes and partnerships."
        ),
    ),
]

RESPONSIBILITIES = [
    (
        "Community Mobilisation",
        (
            "Mobilise district chapters and sub-chapters to plan, deliver and monitor activities with "
            "the communities they serve."
        ),
    ),
    (
        "Capacity Building",
        ("Deliver standardised training packages to staff and volunteers and maintain a roster of trained responders."),
    ),
    (
        "Quality and Accountability",
        ("Apply the humanitarian standards, run community feedback mechanisms and act on the complaints received."),
    ),
    (
        "Resource Mobilisation",
        "Develop proposals, manage partner agreements and diversify the domestic income base.",
    ),
    (
        "Monitoring and Reporting",
        "Track indicators against the operational plan and publish periodic progress reports.",
    ),
]

DEPARTMENTS = [
    (
        "Disaster Management Department",
        "Coordinates preparedness, emergency response and recovery operations across all district chapters.",
        "dm@nrcs.example.org",
    ),
    (
        "Health Services Department",
        "Runs community health, first aid, ambulance and psychosocial support programmes nationwide.",
        "health@nrcs.example.org",
    ),
    (
        "Blood Transfusion Service",
        "Operates the central and regional blood transfusion centres and the voluntary donor programme.",
        "bts@nrcs.example.org",
    ),
    (
        "Water, Sanitation and Hygiene",
        "Delivers water supply schemes, sanitation facilities and hygiene promotion campaigns.",
        "wash@nrcs.example.org",
    ),
    (
        "Organisational Development",
        "Supports governance, branch development, volunteer management and youth engagement.",
        "od@nrcs.example.org",
    ),
    (
        "Planning, Monitoring and Evaluation",
        "Leads planning cycles, data quality assurance, evaluations and institutional learning.",
        "pmer@nrcs.example.org",
    ),
    (
        "Communication and Advocacy",
        "Manages public communication, media relations, campaigns and humanitarian diplomacy.",
        "comms@nrcs.example.org",
    ),
    (
        "Finance and Administration",
        "Oversees financial management, audit compliance, administration and asset management.",
        "finance@nrcs.example.org",
    ),
    (
        "Logistics and Procurement",
        "Manages warehousing, fleet, supply chain and the procurement of relief items.",
        "logistics@nrcs.example.org",
    ),
    (
        "Human Resources Department",
        "Handles recruitment, staff welfare, learning and development and HR policy.",
        "hr@nrcs.example.org",
    ),
]

CONTACT_NAMES = [
    "Anjana Shrestha",
    "Bikash Thapa",
    "Chandra Gurung",
    "Deepa Maharjan",
    "Elina Rai",
    "Gopal Adhikari",
    "Hari Bahadur Karki",
    "Ishwor Tamang",
    "Jyoti Bhandari",
    "Kiran Lama",
]

NEWS_ITEMS = [
    "Nepal Red Cross reaches 12,000 flood affected households in Rasuwa",
    "Emergency blood collection drive launched after Kathmandu valley shortage",
    "New early warning system installed along the Koshi river basin",
    "Volunteers complete community based first aid training in Sindhupalchok",
    "Winterisation support distributed to families in Humla and Mugu",
    "Cholera outbreak response scales up in Birgunj",
    "National Society opens new blood transfusion centre in Pokhara",
    "Landslide response operation concludes in Myagdi district",
    "Nepal Red Cross marks World Red Cross and Red Crescent Day",
    "Cash based assistance delivered to 3,500 earthquake affected families",
    "Youth volunteers lead road safety campaign in Lalitpur",
    "Mobile health camp treats 1,200 patients in Karnali province",
    "Water supply scheme handed over to community in Dhanusha",
    "Ambulance fleet expanded with ten new vehicles",
    "Psychosocial support teams deployed after Jajarkot earthquake",
    "Annual general assembly endorses new five year strategic plan",
    "First aid training rolled out for public transport drivers",
    "Emergency stock prepositioned ahead of the monsoon season",
    "School safety programme launched in 45 public schools",
    "Community disaster preparedness plans updated in 20 municipalities",
]

BLOG_POSTS = [
    ("What a district chapter does when the water rises", "Sunita Basnet"),
    ("Twenty years of voluntary blood donation in Nepal", "Rajendra Shakya"),
    ("Notes from a mobile health camp in Humla", "Dr. Prakash Rana"),
    ("Why community first aid saves the first hour", "Manju Tamang"),
    ("Building back safer after the Jajarkot earthquake", "Ramesh Bhattarai"),
    ("The volunteers behind the ambulance siren", "Kabita Shrestha"),
    ("How cash assistance restores dignity in recovery", "Nirajan Poudel"),
    ("Preparing for the monsoon before the first rain", "Sarita Chaudhary"),
    ("A day at the central blood transfusion centre", "Ashok Maharjan"),
    ("Hygiene promotion that communities actually keep", "Pramila Yadav"),
    ("Mapping risk with the people who live with it", "Dipesh Karki"),
    ("Youth circles and the next generation of volunteers", "Anuja Gurung"),
    ("Restoring family links across borders", "Tek Bahadur Rai"),
    ("What we learned from the Melamchi flood response", "Bishal Adhikari"),
    ("Snakebite prevention in the Terai belt", "Dr. Sabina Thapa"),
]

PROJECTS = [
    (
        "Community Resilience Programme",
        (
            "A multi-year programme strengthening disaster preparedness in 120 flood and landslide "
            "prone communities across Koshi and Madhesh provinces."
        ),
    ),
    (
        "Safe Blood for All",
        "Modernising blood collection, testing and cold chain across seven regional transfusion centres.",
    ),
    (
        "Urban Risk Reduction Initiative",
        (
            "Working with municipalities in the Kathmandu valley on seismic risk, open space protection "
            "and urban search and rescue."
        ),
    ),
    (
        "Rural Water Supply and Sanitation",
        "Constructing gravity water schemes and household toilets in Karnali and Sudurpashchim provinces.",
    ),
    (
        "Forecast based Financing",
        (
            "Releasing anticipatory cash and preparedness support before predicted flood peaks in the "
            "Koshi and Karnali basins."
        ),
    ),
    (
        "Climate Smart Livelihoods",
        "Supporting climate resilient agriculture and income diversification for 4,000 households.",
    ),
    (
        "First Aid for Every Household",
        "Scaling community based first aid training so that every ward has trained responders.",
    ),
    (
        "Psychosocial Support Network",
        "Establishing district level psychosocial teams and a national referral pathway.",
    ),
    (
        "School Safety Programme",
        "Retrofitting assessments, drills and student led preparedness clubs in public schools.",
    ),
    (
        "Volunteer Management System",
        "Digitising volunteer registration, deployment, insurance and recognition nationwide.",
    ),
]

RESOURCES = [
    ("Annual Report 2024", ResourceTypeEnum.REPORT),
    ("Rasuwa Flood Situation Update No. 3", ResourceTypeEnum.REPORT),
    ("Cholera Outbreak Response Factsheet", ResourceTypeEnum.REPORT),
    ("Monsoon Preparedness and Response Plan", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Volunteer Management Policy", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Child Protection Policy", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Blood Transfusion Service Standard Operating Procedures", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Rapid Needs Assessment Factsheet", ResourceTypeEnum.REPORT),
    ("Cash and Voucher Assistance Guidelines", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Population Movement Assessment", ResourceTypeEnum.REPORT),
    ("Early Action Protocol Summary", ResourceTypeEnum.POLICY_AND_GUIDELINES),
    ("Mid Term Review of the Strategic Plan", ResourceTypeEnum.REPORT),
]

PROCUREMENTS = [
    (
        "Supply of non-food relief items",
        (
            "Sealed bids are invited from registered suppliers for the supply and delivery of tarpaulins, "
            "blankets and kitchen sets to the central warehouse."
        ),
    ),
    (
        "Construction of district chapter building",
        (
            "Invitation for bids for the construction of a two storey district chapter office including "
            "boundary wall and water supply."
        ),
    ),
    (
        "Procurement of ambulance vehicles",
        "Tender for the supply of five fully equipped type B ambulances with after sales service and warranty.",
    ),
    (
        "Annual audit services",
        "Request for proposals from registered audit firms for the statutory audit of the fiscal year accounts.",
    ),
    (
        "Supply of medical consumables",
        "Bids invited for blood bags, reagents and laboratory consumables for regional transfusion centres.",
    ),
    (
        "Hire of transport services",
        "Framework agreement for the hire of trucks for relief distribution across the eastern corridor.",
    ),
    (
        "Printing of information materials",
        "Quotations invited for the design and printing of hygiene promotion materials in Nepali and Maithili.",
    ),
    (
        "Supply of water treatment units",
        "Tender for portable water treatment units with training and one year of maintenance support.",
    ),
    (
        "Consultancy for programme evaluation",
        ("Request for proposals for an external end of programme evaluation with field data collection in four districts."),
    ),
    (
        "Supply of information technology equipment",
        "Bids invited for laptops, printers and networking equipment for headquarters and provincial offices.",
    ),
]

VACANCIES = [
    ("Programme Officer", "Disaster Management Department", 2),
    ("Field Coordinator", "Disaster Management Department", 5),
    ("Public Health Officer", "Health Services Department", 1),
    ("Laboratory Technician", "Blood Transfusion Service", 3),
    ("WASH Engineer", "Water, Sanitation and Hygiene", 2),
    ("Monitoring and Evaluation Officer", "Planning, Monitoring and Evaluation", 1),
    ("Communication Officer", "Communication and Advocacy", 1),
    ("Finance Assistant", "Finance and Administration", 2),
    ("Logistics Officer", "Logistics and Procurement", 1),
    ("Human Resources Officer", "Human Resources Department", 1),
]

PARTNERS = [
    ("International Federation of Red Cross and Red Crescent Societies", PartnerScopeEnum.GLOBAL),
    ("International Committee of the Red Cross", PartnerScopeEnum.GLOBAL),
    ("British Red Cross", PartnerScopeEnum.GLOBAL),
    ("Danish Red Cross", PartnerScopeEnum.GLOBAL),
    ("American Red Cross", PartnerScopeEnum.GLOBAL),
    ("Japanese Red Cross Society", PartnerScopeEnum.GLOBAL),
    ("Canadian Red Cross", PartnerScopeEnum.GLOBAL),
    ("Finnish Red Cross", PartnerScopeEnum.GLOBAL),
    ("Ministry of Health and Population", PartnerScopeEnum.LOCAL),
    ("National Disaster Risk Reduction and Management Authority", PartnerScopeEnum.LOCAL),
    ("Nepal Scouts", PartnerScopeEnum.LOCAL),
    ("Disaster Preparedness Network Nepal", PartnerScopeEnum.LOCAL),
]

RADIO_PROGRAMS = [
    ("Together for Humanity: Fire safety during Tihar", RadioProgramTypeEnum.TOGETHER_FOR_HUMANITY),
    ("Together for Humanity: Preparing your household for the monsoon", RadioProgramTypeEnum.TOGETHER_FOR_HUMANITY),
    ("Together for Humanity: Voices from the blood donor camp", RadioProgramTypeEnum.TOGETHER_FOR_HUMANITY),
    ("Together for Humanity: Living with landslide risk", RadioProgramTypeEnum.TOGETHER_FOR_HUMANITY),
    ("Radio Red Cross: What to do in the first hour", RadioProgramTypeEnum.RADIO_RED_CROSS),
    ("Radio Red Cross: Clean water, healthy village", RadioProgramTypeEnum.RADIO_RED_CROSS),
    ("Radio Red Cross: Stories from the district chapters", RadioProgramTypeEnum.RADIO_RED_CROSS),
    ("Radio Red Cross: Snakebite, myths and first aid", RadioProgramTypeEnum.RADIO_RED_CROSS),
]

FAQS = [
    (
        "Who can donate blood?",
        (
            "Any healthy person between 18 and 60 years of age weighing at least 45 kg can donate blood "
            "every three months. A short health screening is carried out at the donation site."
        ),
    ),
    (
        "How do I become a volunteer?",
        (
            "Visit your nearest district chapter with a copy of your citizenship certificate and a "
            "passport size photograph. Orientation and basic training are provided free of charge."
        ),
    ),
    (
        "How can I request an ambulance?",
        (
            "Call the ambulance service number of your district chapter. Services run around the clock "
            "and charges follow the published district rate."
        ),
    ),
    (
        "How do I become a life member?",
        (
            "Complete the life member application form, submit it at your district chapter with the "
            "prescribed fee and attach a copy of your citizenship certificate."
        ),
    ),
    (
        "Where does my donation go?",
        (
            "Donations are allocated to the programme or emergency appeal you select. Audited accounts "
            "and programme reports are published in the resources section."
        ),
    ),
    (
        "Does Nepal Red Cross provide first aid training?",
        (
            "Yes. Community based first aid, workplace first aid and specialised courses for drivers "
            "and teachers are offered through district chapters."
        ),
    ),
    (
        "How can my organisation partner with Nepal Red Cross?",
        (
            "Send a letter of interest to the Communication and Advocacy Department. Partnerships are "
            "formalised through a memorandum of understanding."
        ),
    ),
    (
        "How do I report a complaint about a programme?",
        (
            "Use the community feedback desk at the activity site, call the toll free line or write to "
            "the Planning, Monitoring and Evaluation Department."
        ),
    ),
    (
        "What should be in a household emergency kit?",
        (
            "Drinking water, dry food, a torch, a whistle, essential medicines, copies of important "
            "documents, cash and a basic first aid box."
        ),
    ),
    (
        "Can I request a copy of an old report?",
        (
            "Published reports are available in the resources section. For older documents, contact the "
            "department that produced them."
        ),
    ),
    (
        "Does Nepal Red Cross help trace missing family members?",
        (
            "Yes. Restoring family links services are provided in cooperation with the International "
            "Committee of the Red Cross."
        ),
    ),
    (
        "How is a district chapter governed?",
        (
            "Each district chapter is governed by an elected executive committee accountable to its "
            "general assembly and to the central governing board."
        ),
    ),
]

PARAGRAPHS = [
    (
        "District chapter teams reached the affected wards within twelve hours of the alert, working "
        "alongside local government and the security forces to move families to higher ground."
    ),
    (
        "Trained volunteers carried out a rapid needs assessment, registered the affected households "
        "and set up a community feedback desk at the temporary shelter."
    ),
    (
        "Relief items were released from the prepositioned stock at the regional warehouse, keeping "
        "the delivery within the first seventy two hours of the emergency."
    ),
    (
        "The response was designed with the community from the start: ward representatives helped "
        "define the selection criteria and verified the list in a public meeting."
    ),
    (
        "Health teams screened for waterborne disease, distributed water purification supplies and "
        "referred severe cases to the district hospital."
    ),
    (
        "Psychosocial first aid was provided to families who lost their homes, and follow up visits "
        "were scheduled for the most affected households."
    ),
    (
        "Support continues through the recovery phase, with cash grants for shelter repair and "
        "technical guidance on building back safer."
    ),
    (
        "Lessons from the operation are being folded into the updated preparedness plan so that the "
        "next response starts faster and reaches further."
    ),
]

EMBEDS = [
    "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
]


class Command(BaseCommand):
    help = "Wipe the database and populate it with fake content for local development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--assets-dir",
            default=str(Path(settings.BASE_DIR) / "data" / "seed_assets"),
            help="Directory holding images/, logos/, docs/ and audio/ sub-directories.",
        )
        parser.add_argument("--keep-data", action="store_true", help="Do not flush the database first.")
        parser.add_argument("--keep-media", action="store_true", help="Do not delete previously uploaded media.")
        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-password", default="admin123")
        parser.add_argument("--admin-email", default="admin@example.com")
        parser.add_argument("--seed", type=int, default=20240501, help="Random seed, for reproducible runs.")
        parser.add_argument("--force", action="store_true", help="Allow the run outside DEBUG.")

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError("Refusing to run with DEBUG=False. Pass --force if this is a throwaway database.")

        self.rng = random.Random(options["seed"])
        assets_dir = Path(options["assets_dir"])
        self.images = AssetPool(assets_dir / "images", IMAGE_SUFFIXES)
        self.logos = AssetPool(assets_dir / "logos", IMAGE_SUFFIXES) or self.images
        self.docs = AssetPool(assets_dir / "docs", DOC_SUFFIXES)
        self.audio = AssetPool(assets_dir / "audio", AUDIO_SUFFIXES)

        self.stdout.write(
            f"Assets from {assets_dir}: {len(self.images.paths)} images, {len(self.logos.paths)} logos, "
            f"{len(self.docs.paths)} documents, {len(self.audio.paths)} audio files",
        )
        for label, pool in (("images", self.images), ("documents", self.docs), ("audio files", self.audio)):
            if not pool:
                self.stdout.write(self.style.WARNING(f"No {label} found -- related fields will be left empty."))

        if not options["keep_data"]:
            self.stdout.write("Flushing the database ...")
            self._flush_database()
        if not options["keep_media"]:
            self._clear_media()

        self.today = timezone.localdate()
        with transaction.atomic():
            self.users = self._create_users(options)
            directives = self._create_directives()
            departments = self._create_departments(directives)
            self._create_blogs(departments, directives)
            self._create_news(directives)
            self._create_projects(departments)
            self._create_resources(directives)
            self._create_procurements()
            self._create_vacancies(departments)
            self._create_partners()
            self._create_radio_programs()
            self._create_faqs()

        self._report(options)

    # -- helpers ----------------------------------------------------------

    def _flush_database(self):
        """Truncate every application table, the way ``manage.py flush`` does.

        ``flush`` itself is not used because it truncates without CASCADE: a
        stale table left behind by a removed app still holds a foreign key into
        the app tables and makes the whole command fail. CASCADE empties those
        leftovers too, which is what a "clear the database" run wants anyway.
        """
        connection = connections[DEFAULT_DB_ALIAS]
        table_names = connection.introspection.django_table_names(only_existing=True, include_views=False)
        statements = connection.ops.sql_flush(no_style(), table_names, reset_sequences=True, allow_cascade=True)
        with (
            transaction.atomic(using=DEFAULT_DB_ALIAS, savepoint=connection.features.can_rollback_ddl),
            connection.cursor() as cursor,
        ):
            for statement in statements:
                cursor.execute(statement)
        # Recreates content types and permissions, exactly like flush does.
        emit_post_migrate_signal(verbosity=0, interactive=False, db=DEFAULT_DB_ALIAS)

    def _clear_media(self):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            self.stdout.write(self.style.WARNING("Remote storage in use -- skipping media cleanup."))
            return
        root = Path(media_root)
        if not root.is_dir():
            return
        self.stdout.write(f"Clearing media files under {root} ...")
        for entry in root.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=True)
            else:
                entry.unlink(missing_ok=True)

    def _stamp(self) -> dict:
        """created_by / modified_by for a UserResource."""
        user = self.rng.choice(self.users)
        return {"created_by": user, "modified_by": user}

    def _days_ago(self, low: int, high: int) -> date:
        return self.today - timedelta(days=self.rng.randint(low, high))

    def _inline_image_url(self) -> str | None:
        """Store an image where the markdown editor would put it and return its URL."""
        image = self.images.next_file()
        if image is None:
            return None
        saved_path = default_storage.save(f"editor/{image.name}", image)
        return default_storage.url(saved_path)

    def _markdown(self, title: str, *, with_embed: bool = False, with_image: bool = True) -> str:
        paragraphs = self.rng.sample(PARAGRAPHS, k=4)
        parts = [f"## {title}", "", paragraphs[0], ""]
        if with_image:
            url = self._inline_image_url()
            if url:
                parts += [f"![{title}]({url})", ""]
        parts += [
            "### What was done",
            "",
            f"- {paragraphs[1]}",
            f"- {paragraphs[2]}",
            "- Coordination meetings were held daily with the district disaster management committee.",
            "",
            "> Working with the community, not for the community, is what makes a response stick.",
            "",
            paragraphs[3],
            "",
        ]
        if with_embed:
            parts += [
                "```embed",
                f"url: {self.rng.choice(EMBEDS)}",
                "orientation: horizontal",
                "caption: Field footage from the operation",
                "```",
                "",
            ]
        return "\n".join(parts)

    # -- creators ---------------------------------------------------------

    def _create_users(self, options) -> list[User]:
        admin = User.objects.create_superuser(
            username=options["admin_username"],
            email=options["admin_email"],
            password=options["admin_password"],
            first_name="Site",
            last_name="Administrator",
        )
        users = [admin]
        for username, first_name, last_name in (
            ("editor", "Editor", "One"),
            ("reviewer", "Review", "Desk"),
            ("comms", "Comms", "Team"),
            ("guest", "Guest", "Viewer"),
        ):
            users.append(
                User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password=options["admin_password"],
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=username != "guest",
                ),
            )
        return users

    def _create_directives(self) -> list[StrategicDirectives]:
        directives = []
        for title, description in DIRECTIVES:
            directive = StrategicDirectives.objects.create(
                title=title,
                description=description,
                cover_image=self.images.next_file(),
                **self._stamp(),
            )
            for responsibility_title, responsibility_description in self.rng.sample(RESPONSIBILITIES, k=3):
                MajorResponsibilities.objects.create(
                    title=f"{responsibility_title} -- {title.split()[0]}",
                    description=responsibility_description,
                    directive=directive,
                    **self._stamp(),
                )
            directives.append(directive)
        return directives

    def _create_departments(self, directives) -> list[Department]:
        departments = []
        for index, (title, description, email) in enumerate(DEPARTMENTS):
            departments.append(
                Department.objects.create(
                    title=title,
                    description=description,
                    strategic_directive=directives[index % len(directives)],
                    contact_person_name=CONTACT_NAMES[index % len(CONTACT_NAMES)],
                    contact_person_email=email,
                    **self._stamp(),
                ),
            )
        return departments

    def _create_blogs(self, departments, directives):
        for index, (title, author) in enumerate(BLOG_POSTS):
            Blog.objects.create(
                title=title,
                author=author,
                published_date=self._days_ago(1, 500),
                content=self._markdown(title, with_embed=index % 5 == 0),
                cover_image=self.images.next_file(),
                featured=index < 4,
                # Featured posts come first, so keep the drafts to the tail end.
                status=StatusEnum.DRAFT if index % 6 == 5 else StatusEnum.PUBLISHED,
                department=self.rng.choice(departments),
                directive=self.rng.choice(directives),
                **self._stamp(),
            )

    def _news_status(self, index: int) -> StatusEnum:
        # Highlighted items are the first six, so they stay published.
        if index % 7 == 6:
            return StatusEnum.DRAFT
        if index % 9 == 8:
            return StatusEnum.ARCHIVED
        return StatusEnum.PUBLISHED

    def _create_news(self, directives):
        for index, title in enumerate(NEWS_ITEMS):
            news = News.objects.create(
                title=title,
                content=self._markdown(title, with_embed=index % 4 == 0),
                published_date=self._days_ago(1, 400),
                directive=self.rng.choice(directives),
                cover_image=self.images.next_file(),
                status=self._news_status(index),
                is_highlighted=index < 6,
                show_in_popup=index == 0,
                **self._stamp(),
            )

            ActionLink.objects.create(url="https://nrcs.org/donate", label="Support this operation", news=news)
            if index % 3 == 0:
                ActionLink.objects.create(url="https://nrcs.org/volunteer", label="Become a volunteer", news=news)

            if index % 2 == 0:
                stats = [
                    ("People reached", self.rng.randrange(2_000, 90_000)),
                    ("Households supported", self.rng.randrange(500, 15_000)),
                    ("Volunteers mobilised", self.rng.randrange(40, 900)),
                    ("Districts covered", self.rng.randrange(2, 30)),
                ]
                for order, (stat_title, value) in enumerate(stats[: self.rng.randint(2, 4)], start=1):
                    KeyStat.objects.create(
                        order=order,
                        title=stat_title,
                        stat=value,
                        featured=order <= KeyStat.MAX_FEATURED_PER_NEWS,
                        news=news,
                    )

            if self.docs and index % 2 == 1:
                for order in range(1, self.rng.randint(1, 3) + 1):
                    attachment = self.docs.next_file()
                    if attachment is None:
                        break
                    NewsAttachment.objects.create(
                        file=attachment,
                        order=order,
                        label=Path(attachment.name or "attachment").stem.replace("-", " ").replace("_", " ").title(),
                        news=news,
                    )

    def _create_projects(self, departments):
        if not self.images:
            self.stdout.write(self.style.WARNING("No images available -- skipping projects (cover image required)."))
            return
        for title, description in PROJECTS:
            Project.objects.create(
                title=title,
                description=description,
                cover_image=self.images.next_file(),
                department=self.rng.choice(departments),
                **self._stamp(),
            )

    def _create_resources(self, directives):
        for title, resource_type in RESOURCES:
            Resource.objects.create(
                title=title,
                content=self._markdown(title, with_image=False),
                file=self.docs.next_file(),
                published_date=self._days_ago(10, 900),
                directive=self.rng.choice(directives),
                cover_image=self.images.next_file(),
                type=resource_type,
                **self._stamp(),
            )

    def _create_procurements(self):
        for title, description in PROCUREMENTS:
            published_date = self._days_ago(1, 120)
            Procurement.objects.create(
                title=title,
                description=description,
                file=self.docs.next_file(),
                published_date=published_date,
                expiry_date=published_date + timedelta(days=self.rng.randint(15, 60)),
                **self._stamp(),
            )

    def _create_vacancies(self, departments):
        if not self.docs:
            self.stdout.write(self.style.WARNING("No documents available -- skipping vacancies (file required)."))
            return
        departments_by_title = {department.title: department for department in departments}
        for position, department_title, count in VACANCIES:
            published_at = self._days_ago(1, 90)
            expiry_date = published_at + timedelta(days=self.rng.randint(10, 45))
            JobVacancy.objects.create(
                title=f"Vacancy announcement for {position}",
                file=self.docs.next_file(),
                position=position,
                description=(
                    f"Nepal Red Cross Society invites applications for the post of {position} under the "
                    f"{department_title}. The position is based at headquarters with frequent field travel. "
                    "Interested candidates should submit a cover letter and curriculum vitae before the closing date."
                ),
                number_of_vacancies=count,
                expiry_date=expiry_date,
                department=departments_by_title.get(department_title),
                is_archived=expiry_date < self.today,
                published_at=published_at,
                **self._stamp(),
            )

    def _create_partners(self):
        for title, scope in PARTNERS:
            Partner.objects.create(
                title=title,
                image=self.logos.next_file(),
                scope=scope,
                **self._stamp(),
            )

    def _create_radio_programs(self):
        if not self.audio:
            self.stdout.write(self.style.WARNING("No audio files available -- skipping radio programs."))
            return
        for title, program_type in RADIO_PROGRAMS:
            RadioProgram.objects.create(
                title=title,
                audio_file=self.audio.next_file(),
                published_date=self._days_ago(7, 700),
                type=program_type,
                **self._stamp(),
            )

    def _create_faqs(self):
        for order, (question, answer) in enumerate(FAQS, start=1):
            Faq.objects.create(question=question, answer=answer, order_index=order, **self._stamp())

    # -- output -----------------------------------------------------------

    def _report(self, options):
        rows = [
            ("Users", User.objects.count()),
            ("Strategic directives", StrategicDirectives.objects.count()),
            ("Major responsibilities", MajorResponsibilities.objects.count()),
            ("Departments", Department.objects.count()),
            ("Blogs", Blog.objects.count()),
            ("News", News.objects.count()),
            ("News action links", ActionLink.objects.count()),
            ("News key stats", KeyStat.objects.count()),
            ("News attachments", NewsAttachment.objects.count()),
            ("Projects", Project.objects.count()),
            ("Resources", Resource.objects.count()),
            ("Procurements", Procurement.objects.count()),
            ("Job vacancies", JobVacancy.objects.count()),
            ("Partners", Partner.objects.count()),
            ("Radio programs", RadioProgram.objects.count()),
            ("FAQs", Faq.objects.count()),
        ]
        width = max(len(label) for label, _ in rows)
        self.stdout.write("")
        for label, count in rows:
            self.stdout.write(f"  {label.ljust(width)}  {count}")
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded. Log in as '{options['admin_username']}' / '{options['admin_password']}' "
                "-- editor, reviewer, comms and guest share the same password.",
            ),
        )
