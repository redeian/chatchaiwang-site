#!/usr/bin/env python3
"""Static build for chatchaiwang.com — online resume and portfolio.

No framework, no runtime, no external requests. Every page is one HTML file
with the CSS inlined, so the first paint costs one round trip.
Run: env -u PYTHONPATH /opt/homebrew/anaconda3/bin/python3 build.py
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import subprocess
import sys

SITE = pathlib.Path(__file__).resolve().parent
BASE = "https://www.chatchaiwang.com"
EMAIL = "chatchai_wan@utcc.ac.th"
LINKEDIN = "https://linkedin.com/in/chatchai-mark-wangwiwattana-ph-d-8659b230"
YOUTUBE = "https://www.youtube.com/@markdigitalacademy"
ACADEMY = "https://markdigitalacademy.com/"
ORCID = "https://orcid.org/0000-0002-2922-6498"
ORCID_ID = "0000-0002-2922-6498"
# The identity hub. markdigitalacademy.com/about declares the single Person
# entity; this site declares the same entity from the other end, which is what
# lets a search engine or a model merge the two into one person.
HUB = "https://markdigitalacademy.com/about"
ORG_ID = "https://markdigitalacademy.com/#organization"
GITHUB = "https://github.com/redeian"
KAGGLE = "https://www.kaggle.com/redeian"
XTW = "https://x.com/redeian"
SCHOLAR = "https://scholar.google.com/citations?user=jJaSRS4AAAAJ&hl=en"
FACEBOOK = "https://web.facebook.com/prodgamers"
ACM = "https://dl.acm.org/profile/99658754368"

# Every name this person answers to, in the spellings people actually type.
ALIASES = ["หมาก ดิจิทัล", "Mark Digital", "อ.หมาก", "ชัชชัย หวังวิวัฒนา",
           "redeian", "Chatchai Mark Wangwiwattana"]

# Must stay in step with markdigitalacademy.com/about; drift here is what breaks
# entity merging, so this list is the single copy the whole build reads.
SAME_AS = [HUB, YOUTUBE, GITHUB, "https://www.linkedin.com/in/chatchai-mark-wangwiwattana-ph-d-8659b230",
           KAGGLE, ORCID, SCHOLAR, FACEBOOK, XTW, ACM, ACADEMY]
# Set once the exact profile URL is known. ResearchGate answers every guess with
# 403, and a wrong profile URL is worse than none, so this stays empty until
# Mark pastes his own.
RESEARCHGATE = ""
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

NAME = "Chatchai Wangwiwattana"
NAME_FULL = "Chatchai Wangwiwattana, Ph.D."
NAME_TH = "ชัชชัย หวังวิวัฒนา"

# --------------------------------------------------------------------- data
STATS = [
    ("18", "peer-reviewed publications", "2015 to 2026"),
    ("76", "training and speaking programmes", "since 2018"),
    ("20+", "software systems built in house", "at the university, running today"),
    ("80%", "below the vendor quote", "in-house build at the university"),
]

FOCUS = [
    (
        "Applied AI",
        "Language models that hold up outside a demo: assessment, service agents, manpower planning.",
    ),
    (
        "Data governance",
        "Privacy programmes people can follow. Master planning for the national regulator.",
    ),
    (
        "Capability building",
        "Seventy-six programmes since 2018. It counts only if they can run it without me.",
    ),
]

PROJECTS = [
    (
        "Agentic AI Driven Programming Assistant for Teachers: Teacher-in-the-Loop Adaptive Learning and Real-Time Feedback",
        "Principal Investigator",
        "University research grant, University of the Thai Chamber of Commerce",
        "2025",
    ),
    (
        "Large Language Model Chatbot Question and Answer System for Higher Education",
        "Principal Investigator",
        "University research grant, University of the Thai Chamber of Commerce",
        "2024",
    ),
    (
        "Applying Digital and AI Technology to the Operational Efficiency of the Senate",
        "Principal Investigator",
        "Senate of Thailand",
        "2025 to 2026",
    ),
    (
        "Digital Trade Ecosystem to Support Sustainable Trade Transactions",
        "Co-Investigator",
        "ETDA under the CPTA programme",
        "2025 to 2026",
    ),
    (
        "Data Governance Framework for Mineral and Mining Data",
        "Co-Investigator",
        "Department of Primary Industries and Mines",
        "2025 to 2026",
    ),
    (
        "Marketing Strategies and Game Consumption across the Game Life Cycle",
        "Principal Investigator",
        "True Corporation",
        "2023",
    ),
    (
        "Procedural Map Generation for Game Development",
        "Principal Investigator",
        "True Corporation",
        "2023",
    ),
]

EXPERIENCE = [
    (
        "Leadership and academic appointments",
        [
            ("Vice President of Information Technology", "University of the Thai Chamber of Commerce", "2025 to present"),
            ("Member, Business and Service Standards Certification Committee", "Thai Chamber of Commerce", "2023 to present"),
            ("Head, Bachelor's Degree Program in Gaming and Esports Business", "University of the Thai Chamber of Commerce", "2023 to 2026"),
            ("Assistant to the President for Information Technology", "University of the Thai Chamber of Commerce", "2018 to 2025"),
            ("Lecturer, Faculty of Science and Technology", "University of the Thai Chamber of Commerce", "2018 to present"),
            ("Assistant Professor", "University of the Thai Chamber of Commerce", "2023 to present"),
            ("Special Lecturer, Information Technology", "Mahidol University", "2017 to 2019"),
        ],
    ),
    (
        "Industry and advisory",
        [
            ("Founder and Executive", "Mark Digital Academy", "2023 to present"),
            ("AI Transformation Consultant, cross-functional initiative", "Generali Life Assurance (Thailand)", "2026"),
            ("AI Transformation Consultant, AI champion projects, training and design thinking", "B.Grimm Power", "2024 to 2026"),
            ("AI Transformation Consultant", "Srithai Superware", "2025 to present"),
            ("Founder and Chief Technology Officer", "Demon Wagon Game Studio, with earlier software and CIO roles at Profitarrowmarketing, Southern Methodist University and CPF IT Center", "2008 to 2018"),
            ("Consultant, Master Plan for Personal Data Protection", "Office of the Personal Data Protection Committee", "2021"),
            ("Expert in Artificial Intelligence and Cloud Architecture", "AiTi, University of the Thai Chamber of Commerce", "2017 to 2020"),
            ("Special Specialist, Information and Digital Transformation", "Department of Primary Industries and Mines, Ministry of Industry", "2019 to 2020"),
            ("Digital Transformation Consultant", "SME Next Normal Project, Thai Chamber of Commerce", "2022"),
        ],
    ),
]

JOURNALS = [
    dict(
        authors="Nilyaporn, N., & Wangwiwattana, C.",
        year="2026",
        title="Generative AI-based smart manpower planning and career development system for civil servants",
        venue="Procedia of Multidisciplinary Research, 4(10), 26",
        url="https://so09.tci-thaijo.org/index.php/PMR/article/view/10867",
    ),
    dict(
        authors="Wangwiwattana, C.",
        year="2019",
        title="Fall detection with a single commodity RGB camera based-on 2D pose estimation",
        venue="International Journal of Development Administration Research, 2(2), 12-22",
        url="https://so02.tci-thaijo.org/index.php/ijdar/article/view/247218",
    ),
    dict(
        authors="Wangwiwattana, C., Ding, X., & Larson, E. C.",
        year="2018",
        title="PupilNet: measuring task evoked pupillary response using commodity RGB tablet cameras",
        venue="Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies, 1(4), Article 171",
        url="https://doi.org/10.1145/3161164",
    ),
]

CONFERENCES = [
    dict(
        authors="Wangwiwattana, C., & Meeyen, A.",
        year="2024",
        title="Design through AI eyes: automating aesthetic assessments for learning graphic design concepts",
        venue="MIWAI 2024, Lecture Notes in Computer Science, pp. 336-347. Springer",
        url="https://doi.org/10.1007/978-981-96-0695-5_27",
    ),
    dict(
        authors="Wangwiwattana, C., & Jantarick, W.",
        year="2024",
        title="Building intelligent academic service agents: FAQ extraction and chatbots with large language models",
        venue="InCIT 2024, pp. 370-375. IEEE",
        url="https://doi.org/10.1109/InCIT63192.2024.10810553",
    ),
    dict(
        authors="Wangwiwattana, C., & Tongvivat, Y.",
        year="2023",
        title="Automating academic assessment: a large language model approach",
        venue="InCIT 2023, pp. 330-334. IEEE",
        url="https://doi.org/10.1109/InCIT60207.2023.10412991",
    ),
    dict(
        authors="Wangwiwattana, C., & Tongvivat, Y.",
        year="2022",
        title="Semi-automatic short-answer grading tools for Thai language using natural language processing",
        venue="ICETM 2022, pp. 123-128. ACM",
        url="https://doi.org/10.1145/3582580.3582600",
    ),
    dict(
        authors="Wangwiwattana, C., & Tongvivat, Y.",
        year="2022",
        title="Semi-automatic short answers clustering and grading with K-means and keyword matching algorithms",
        venue="InCIT 2022, pp. 280-284. IEEE",
        url="https://doi.org/10.1109/InCIT56086.2022.10067412",
    ),
    dict(
        authors="Tribuppachatsakul, W., & Wangwiwattana, C.",
        year="2022",
        title="Brand personality analysis in social media network with topic modelling and word embedding",
        venue="Proceedings of the 7th International Sripatum University Conference",
        url="",
    ),
    dict(
        authors="Wangwiwattana, C., Sathienpaisal, E., Chaiwattanaphong, T., Singhapong, P., Janrathitikarn, O., & Akrawutpornpat, S.",
        year="2019",
        title="Fall detection with a single RGB camera based on 2D pose estimation",
        venue="International Multidisciplinary Academic Conference, Bangkok",
        url="",
    ),
    dict(
        authors="Wangwiwattana, C.",
        year="2018",
        title="Photoplethysmogram extraction with a mobile phone for meditation practices",
        venue="Proceedings of the 6th Academic Science and Technology Conference (ASTC 2018)",
        url="",
    ),
    dict(
        authors="Wangwiwattana, C., Rafiqi, S., Fernandez, E., Nair, S., & Larson, E.",
        year="2015",
        title="PupilWare-M: cognitive load estimation using unmodified smartphone cameras",
        venue="IEEE MASS 2015, pp. 645-650",
        url="https://doi.org/10.1109/MASS.2015.31",
    ),
    dict(
        authors="Rafiqi, S., Wangwiwattana, C., Fernandez, E., Nair, S., Kim, J., & Larson, E. C.",
        year="2015",
        title="PupilWare: towards pervasive cognitive load measurement using commodity devices",
        venue="ACM PETRA 2015, pp. 1-8",
        url="https://doi.org/10.1145/2769493.2769506",
    ),
]

THAI = [
    dict(
        authors="นิรันดร์ ผลมูล และ ชัชชัย หวังวิวัฒนา",
        year="2024",
        title="การใช้การเรียนรู้ของเครื่องเพื่อเพิ่มความรวดเร็วของการวิเคราะห์อนุมัติสินเชื่อส่วนบุคคลและลดปัญหาหนี้เสีย",
        venue="การประชุมวิชาการเสนอผลงานวิจัยระดับชาติและนานาชาติ ครั้งที่ 16, 16(2), 405-412",
        url="http://www.journalgrad.ssru.ac.th/index.php/8thconference/article/view/4615",
    ),
    dict(
        authors="วิชชา ณัฐญานธร และ ชัชชัย หวังวิวัฒนา",
        year="2024",
        title="การศึกษาการพัฒนาระบบรวบรวมและกระจายข่าวสารด้านการเงิน และความปลอดภัยทางไซเบอร์ด้วย RPA",
        venue="การประชุมวิชาการเสนอผลงานวิจัยระดับชาติและนานาชาติ ครั้งที่ 16, 16(2), 431-438",
        url="http://journalgrad.ssru.ac.th/index.php/8thconference/article/view/4618",
    ),
    dict(
        authors="รจิต รามสูตร และ ชัชชัย หวังวิวัฒนา",
        year="2023",
        title="การศึกษาออกแบบระบบเพื่อจัดการข้อมูลลูกค้าสินเชื่อเคหะของกลุ่มลูกค้าบุคคล",
        venue="รายงานการประชุม Graduate School Conference, 6(1), 344",
        url="http://journalgrad.ssru.ac.th/index.php/miniconference/article/view/4435",
    ),
    dict(
        authors="ศุภณัฐ นิยมค้า และ ชัชชัย หวังวิวัฒนา",
        year="2022",
        title="การประยุกต์เหมืองข้อมูลในการศึกษาลักษณะของผู้ใช้บริการที่บัญชีไม่เคลื่อนไหวผ่านการทำแบบจำลอง Clustering",
        venue="DPU International Conference on Business Innovation and Social Sciences 2022, pp. 908-918",
        url="https://www.airitilibrary.com/Article/Detail/P20220628001-202205-202206280001-202206280001-908-918",
    ),
]

PREPRINTS = [
    dict(
        authors="Wangwiwattana, C., Aggarwal, S., & Larson, E. C.",
        year="2021",
        title="Writers gonna wait: the effectiveness of notifications to initiate aversive action in writing procrastination",
        venue="arXiv preprint arXiv:2101.10191",
        url="https://arxiv.org/abs/2101.10191",
    ),
]

SPEAKING = {
    "2026": [
        ("Workshop, Design Thinking", "The Cloud Space, Nonthaburi", "Apr 2026"),
        ("Speaker, AI Agents, Robotics and Intelligent Digital Twins", "Harbour.Space@UTCC", "Apr 2026"),
        ("Speaker, Generative AI for Military Work", "National Defence Studies Institute", "Mar 2026"),
        ("Instructor, Agentic AI for Health Professionals", "Kluaynamthai Hospital", "Feb 2026"),
        ("Instructor, AI Training Day 3", "Generali Life Assurance (Thailand)", "Feb 2026"),
        ("Instructor, AI Training", "Generali Life Assurance (Thailand)", "Jan 2026"),
    ],
    "2025": [
        ("Speaker, Apple Distinguished Educator South East Asia", "Apple Inc.", "Nov 2025"),
        ("Instructor, AI Champion Support Practitioner (Round 2)", "University of the Thai Chamber of Commerce", "Oct 2025"),
        ("Instructor, AI Champion Support Practitioner (Round 1)", "University of the Thai Chamber of Commerce", "Oct 2025"),
        ("Instructor, AI Practitioner (Round 2)", "University of the Thai Chamber of Commerce", "Oct 2025"),
        ("Instructor, AI Practitioner 1 (Round 1)", "University of the Thai Chamber of Commerce", "Sep 2025"),
        ("Advisor and Instructor, Deep Tech 2025", "National Innovation Agency", "Aug 2025"),
        ("Instructor, AI Transformation for Executives", "Srithai Superware", "Aug 2025"),
        ("Instructor, AI in Workplace (Round 2)", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, AI in Workplace (Round 1)", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, AI Training for Staff (Round 3)", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Speaker, AI Explorer, English session", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, AI Onsite Training (Round 2)", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, AI Training for Staff (Round 1)", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, CWIE Faculty Supervision Program", "Office of the Higher Education Commission", "Jul 2025"),
        ("Speaker and Judge, Make it Happen Hackathon", "University of the Thai Chamber of Commerce", "Jul 2025"),
        ("Speaker and Judge, YPC Hackathon", "Thai Chamber of Commerce", "Jul 2025"),
        ("Instructor, AI and Data Driven Organization for Executives", "Office of the PDPC", "Jul 2025"),
    ],
    "2024": [
        ("Speaker, Generative AI for the Modern Workplace", "University of the Thai Chamber of Commerce", "Jun 2024"),
        ("Instructor, Creating Effective Digital Media with Canva", "Thai Chamber of Commerce", "Jun 2024"),
        ("Instructor, Generative AI for Business", "Krungthai Bank", "May 2024"),
        ("Speaker, Generative AI for Professional", "University of the Thai Chamber of Commerce", "Apr 2024"),
        ("Instructor, Train the Trainer, Generative AI for Education", "University of the Thai Chamber of Commerce", "Mar 2024"),
        ("Speaker, eSports Business in Thailand", "University of the Thai Chamber of Commerce", "Mar 2024"),
        ("Speaker, Introduction to Generative AI for Business", "IMC", "Mar 2024"),
        ("Speaker, Generative AI for Content Creation for Educators", "Srinakharinwirot University", "Mar 2024"),
        ("Speaker, Design Thinking", "Tourism Authority of Thailand", "Mar 2024"),
        ("Speaker, Generative AI for Teaching and Learning", "School of Humanities, UTCC", "Jan 2024"),
        ("Speaker, Design Thinking Workshop", "B. Grimm Power", "2024"),
        ("Speaker, Design Thinking Workshop", "State Enterprise Policy Office", "2024"),
    ],
    "2023": [
        ("Speaker, Design Thinking Workshop", "Excise Department", "2023"),
        ("Speaker, Big Data to Reduce Socio-economic Inequality", "National Digital Economy and Society Commission", "2023"),
        ("Speaker, Digital Skills for Digital Transformation", "National Digital Economy and Society Commission", "2023"),
        ("Consultant and Lecturer, Digital Technology for Business", "ASEAN Mentorship for Entrepreneurs Network, Philippines", "2023"),
        ("Moderator, Cryptocurrency for Creative Economy", "Education Next 2023, Ministry of Higher Education, Science, Research and Innovation", "2023"),
        ("Lecturer, ChatGPT for Business", "University of the Thai Chamber of Commerce", "2023"),
        ("Lecturer, Active Learning with the DISCO Framework", "University of the Thai Chamber of Commerce", "2023"),
        ("Lecturer, Digital Content Creation in Video Format", "Khon Kaen University", "Mar 2023"),
        ("Lecturer, JavaScript Workshop", "King Mongkut's University of Technology Ladkrabang", "Feb 2023"),
    ],
    "2022": [
        ("Lecturer, Digital Literacy for Work", "Thai Chamber of Commerce", "2022"),
        ("Lecturer, Digital Trust and Society", "Government Savings Bank", "2022"),
        ("Lecturer, Developing Bangkok with Modern Digital Technology", "Bangkok Metropolitan Administration", "2022"),
        ("Lecturer, Digital Transformation Topics for SMEs", "SME Next Normal Project", "2022"),
        ("Lecturer, Video Editing Content Creation for Mobile", "Quart Association", "2022"),
        ("Lecturer, Digital Transformation for Education", "Senior Vocational Education Training Program", "2022"),
        ("Lecturer, 7-day Master PDPA for IT", "Open programme", "2022"),
        ("Speaker, Infographics and Video with Mobile Phones", "Ministry of Culture", "2022"),
        ("Lecturer, Design Thinking", "Food Passion", "2022"),
        ("Speaker, Editing Videos on a Single Phone", "Government Savings Bank", "2022"),
        ("Speaker, Metaverse for SMEs", "Singha People Development", "2022"),
        ("Co-speaker, Metaverse in Fintech", "Harbour.Space University at UTCC", "2022"),
        ("Co-speaker, Future Technology: Quantum Computing, Space Technology and the Metaverse", "University of the Thai Chamber of Commerce", "2022"),
        ("Lecturer, Mindfulness", "21 Days Transform You, UTCC", "2022"),
        ("Lecturer, Crypto and Blockchain 101", "21 Days Transform You, UTCC", "2022"),
        ("Speaker, Editing Videos on a Single Mobile Phone", "Ministry of Culture", "2022"),
    ],
    "2021": [
        ("Lecturer, Digital Transformation", "V-Surf Logistics", "2021"),
        ("Business Pitching, IDE Competition", "IDE Center at UTCC", "2021"),
        ("Lecturer, Zoom, WebEx and Microsoft Teams for Work and Online Teaching", "University of the Thai Chamber of Commerce", "2021"),
        ("Lecturer, Redesign Your Life for SMEs", "Business Boost Up, UTCC", "2021"),
    ],
    "2020": [
        ("Lecturer, Digital E-commerce on a Single Mobile Phone", "Business Boost Up, UTCC", "2020"),
        ("Lecturer, WebEx Meeting for Online Teaching", "Quart Association", "2020"),
        ("Lecturer, Microsoft Teams for Online Teaching", "University of the Thai Chamber of Commerce", "2020"),
        ("Lecturer, Online Meetings in the New Normal", "Department of Health, Ministry of Public Health", "2020"),
        ("Lecturer, Big Data Fundamentals", "Food Innovation Warrior Project, Food Institute", "2020"),
        ("Coach, Digital Transformative Leader", "Thai Chamber of Commerce", "2020"),
        ("Lecturer, Digital Enablement for Executives", "Krungthai Bank", "2020"),
        ("Coach, ToPCATS", "University of the Thai Chamber of Commerce", "2020"),
    ],
    "2019": [
        ("Lecturer, 2nd Digital Trend in FinTech for Executives", "Krungthai Bank", "2019"),
        ("Lecturer, 1st Digital Trend in FinTech for Executives", "Krungthai Bank", "2019"),
    ],
    "2018": [
        ("Speaker, Child Online Protection in the US", "Office of the National Digital Economy and Society Commission", "2018"),
        ("Lecturer, eSports as a New Children's Activity", "International Institute of Communications", "2018"),
    ],
}

EDUCATION = [
    ("Ph.D. in Computer Science (Ubiquitous Computing)", "Southern Methodist University, USA"),
    ("Master of Interactive Technology", "Southern Methodist University, USA"),
    ("Master of Business Administration (Marketing)", "University of the Thai Chamber of Commerce"),
    ("Bachelor of Science in Computer Science, First Class Honours", "University of the Thai Chamber of Commerce"),
]

EXEC_PROGRAMMES = [
    ("TepDE Senior Executive Program in Digital Technology, Martech and AI", "2024"),
    ("TopCATs Senior Executive Program in Service Innovation, 3rd generation", "2022"),
    ("Senior Executive Program, Ministry of Higher Education, Science, Research and Innovation (WiNSX)", "2022"),
]

CERTIFICATIONS = [
    ("Certified Digital Transformation Trainer", "Digital Economy Promotion Agency, Thailand"),
    ("Certified Proficiency in Data Protection and GRC", "OCEG, Singapore"),
    ("Certified Video Game Developer", "The Guildhall at SMU, USA"),
    ("Certified Design Your Life Trainer", "Stanford University"),
    ("Certified IoT with NetPie Trainer", "NECTEC, Thailand"),
]

# Selected engagements: what was actually delivered, not just the title held.
ENGAGEMENTS = [
    dict(
        org="University of the Thai Chamber of Commerce",
        meta="Vice President of Information Technology &middot; 2025 to present",
        body=[
            "Initiated the AI UTCC programme that turned the university into an AI-first "
            "institution: a fifty-person IT organisation, 2,000 computers and 20,000 iPads, and a "
            "rebuilt digital backbone of data warehouse, cybersecurity, paperless workflow, "
            "API-first, data governance and martech.",
            "Data protection officer under PDPA. More than twenty systems built in house; the eight "
            "AI ones at about a fifth of what outside vendors quoted. No AI servers bought, compute "
            "paid for as tokens.",
            "First education institution in Asia-Pacific on Wi-Fi 7. The work led to two ACES "
            "Awards in 2026, including Premier Educational Institutions in Asia.",
        ],
    ),
    dict(
        org="Srithai Superware",
        meta="AI transformation consultant &middot; 2025 to present",
        body=[
            "Set up their AI champion programme and the transformation that followed.",
            "Executives trained first, then champion cohorts who went on to train the whole "
            "factory themselves.",
            "Projects now running across digital, data and AI, digital twin work included, after a "
            "hackathon and a pitch round. Their programmers upskilled on using AI safely and under "
            "governance.",
        ],
    ),
    dict(
        org="Generali Life Assurance Thailand",
        meta="AI transformation consultant, cross-functional initiative &middot; 2026, completed",
        body=[
            "Design thinking with the executive team, then four rounds with their AI champions "
            "from idea to working product, closing in a pitch to sponsors.",
            "The projects that won funding are in use across sales, customer service, digital "
            "marketing and data.",
        ],
    ),
    dict(
        org="B.Grimm Power",
        meta="AI champion programme &middot; 2024 to 2026",
        body=(
            "Training, capacity building and pitching for their AI champions, with projects "
            "reaching production each year."
        ),
    ),
]

CLIENTS = (
    "Krungthai Bank, Generali Life Assurance, Srithai Superware, B. Grimm Power, Singha, "
    "Government Savings Bank, Thai Chamber of Commerce, PDPC, NDSI, Excise Department, NESDC, "
    "Ministry of Culture, Tourism Authority of Thailand, NIA"
)

# Organisation marks: nominative use only. Each band names what the organisation
# actually vouches for, never "clients" or "trusted by", and a mark never appears
# without the text that says what the relationship was.
LOGO_BANDS = [
    (
        "Research grants and advisory work for the public sector",
        "Commissioned and funded, 2019 to 2026.",
        [
            ("senate", "Senate of Thailand", 96),
            ("etda", "Electronic Transactions Development Agency", 314),
            ("pdpc", "Office of the Personal Data Protection Committee", 172),
            ("dpim", "Department of Primary Industries and Mines", 86),
            ("tcc", "Thai Chamber of Commerce", 331),
        ],
    ),
    (
        "AI transformation and applied research for companies",
        "Consulting and research, 2023 to present.",
        [
            ("true", "True Corporation", 233),
            ("srithai", "Srithai Superware", 304),
            ("generali", "Generali Life Assurance Thailand", 465),
            ("bgrimm", "B.Grimm Power", 288),
        ],
    ),
    (
        "Certified by",
        "Thailand, Singapore, the United States.",
        [
            ("depa", "Digital Economy Promotion Agency", 154),
            ("oceg", "OCEG, Singapore", 252),
        ],
    ),
    (
        "Degrees from the United States and Thailand",
        "Ph.D. and Master of Interactive Technology, Dallas. First class honours, Bangkok.",
        [
            ("smu-lockup", "Southern Methodist University, USA", 253),
            ("utcc", "University of the Thai Chamber of Commerce", 215),
        ],
    ),
]

LOGO_NOTE = (
    "Organisation marks identify the institutions and companies I have worked for or studied "
    "at. All marks remain the property of their owners. Their appearance here does not imply "
    "endorsement, partnership or certification."
)


def logo_bands(bands=None) -> str:
    # Emblems read smaller than wordmarks at the same cap height, so the two
    # seal-shaped marks get a few extra pixels to hold their optical weight.
    emblems = {"senate", "dpim", "smu-seal"}
    out = []
    for heading, sub, items in (bands or LOGO_BANDS):
        imgs = "".join(
            f'<img src="assets/logos/{key}.png" alt="{e(name)}" width="{w}" height="96" '
            f'class="{"emblem" if key in emblems else "wordmark"}" '
            f'loading="lazy" decoding="async">'
            for key, name, w in items
        )
        line = (f'<p style="margin:-10px 0 20px;font-size:14px;color:var(--muted)">{e(sub)}</p>'
                if sub else "")
        out.append(f'<div class="band"><h3>{e(heading)}</h3>{line}'
                   f'<div class="logos">{imgs}</div></div>')
    return "".join(out)

# ---------------------------------------------------------------------- css
CSS = """
:root{
  --paper:#F5F2EA; --ink:#0B0B0C; --muted:#6B675E; --line:rgba(11,11,12,.13);
  --line-strong:rgba(11,11,12,.28); --tile:#0B0B0C; --tile-ink:#F5F2EA;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
/* one theme only: paper and ink. A dark variant was tried and dropped — the
   colour organisation marks need a light plate, and two surfaces doubled the
   work for no reader benefit. */
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line-strong)}
a:hover{border-bottom-color:var(--ink)}
a:focus-visible,button:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:2px}
img{max-width:100%;height:auto;display:block}
.wrap{max-width:1120px;margin:0 auto;padding:0 28px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:28px;top:14px;background:var(--paper);padding:10px 16px;border:1px solid var(--ink);z-index:9}
h1,h2,h3,h4{font-family:var(--serif);font-weight:400;letter-spacing:-.01em;margin:0}
p{margin:0 0 1em}

/* header */
.masthead{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line)}
.masthead .wrap{display:flex;align-items:center;justify-content:space-between;height:72px;gap:24px}
.brand{display:inline-flex;align-items:center;gap:12px;border:0}
.brand svg{width:30px;height:30px;flex:none}
.brand span{font-family:var(--serif);font-size:17px;letter-spacing:.04em;line-height:1.1}
.nav{display:flex;gap:26px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.nav a{border:0}
.nav a[aria-current]{color:var(--ink)}
@media (max-width:720px){
  .masthead .wrap{height:auto;flex-wrap:wrap;padding:14px 0 6px;row-gap:6px}
  .nav{display:flex;width:100%;justify-content:flex-start;gap:22px;font-size:12px}
  .nav a{padding:11px 0;display:inline-block}
}

/* hero */
.hero{padding:84px 0 64px;border-bottom:1px solid var(--line)}
.hero-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:64px;align-items:start}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:0 0 26px}
.hero h1{font-size:clamp(38px,5.4vw,64px);line-height:1.04;letter-spacing:-.02em;margin:0 0 24px}
.lede{font-size:19px;line-height:1.55;max-width:34em;color:var(--ink);margin:0 0 30px}
.now{font-size:14px;line-height:1.7;color:var(--muted);max-width:34em;margin:0 0 34px}
.actions{display:flex;flex-wrap:wrap;gap:12px}
.btn{display:inline-block;border:1px solid var(--ink);background:var(--ink);color:var(--paper);
  padding:13px 24px;font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;border-radius:0}
.btn:hover{background:transparent;color:var(--ink)}
.btn.ghost{background:transparent;border-color:var(--line-strong);color:var(--muted)}
.btn.ghost:hover{color:var(--ink);border-color:var(--ink)}
.portrait{margin:0}
.portrait img{border:1px solid var(--line);width:100%}
.portrait figcaption{font-size:12px;color:var(--muted);letter-spacing:.06em;margin-top:12px}
@media (max-width:860px){
  .hero{padding:52px 0 46px}
  .hero-grid{grid-template-columns:1fr;gap:36px}
  .portrait{max-width:320px}
  .lede{font-size:17.5px}
}

/* stats */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-bottom:1px solid var(--line)}
.stat{padding:26px 0;border-right:1px solid var(--line)}
.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:34px;line-height:1;font-weight:400}
.stat span{display:block;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:8px}
.stat i{display:block;font-style:normal;font-size:12px;color:var(--muted);margin-top:2px;opacity:.8}
@media (max-width:720px){
  .stats{grid-template-columns:1fr 1fr}
  .stat{border-bottom:1px solid var(--line);padding:20px 0}
  .stat:nth-child(2n){border-right:0}
  .stat b{font-size:26px}
}

/* sections */
section{padding:72px 0;border-bottom:1px solid var(--line)}
.section-grid{display:grid;grid-template-columns:190px 1fr;gap:40px}
.label{font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink);
  margin:0;padding-top:13px;border-top:1px solid var(--ink)}
@media (max-width:800px){ section{padding:48px 0} .section-grid{grid-template-columns:1fr;gap:18px} }

.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--line)}
.card{padding:30px 32px 34px 0;border-right:1px solid var(--line)}
.card:last-child{border-right:0;padding-right:0}
.card h3{font-size:22px;margin:0 0 12px}
.card p{font-size:14.5px;line-height:1.6;color:var(--muted);margin:0;max-width:34ch}
@media (max-width:800px){
  .cards{grid-template-columns:1fr}
  .card{border-right:0;border-bottom:1px solid var(--line);padding:22px 0}
  .card:last-child{border-bottom:0}
}

.rows{border-top:1px solid var(--line)}
.row{display:grid;grid-template-columns:1fr auto;gap:16px;padding:18px 0;border-bottom:1px solid var(--line);align-items:baseline}
.row:last-child{border-bottom:0}
.row .t{font-size:16px;line-height:1.4;max-width:64ch}
.row .t small{display:block;font-size:13.5px;color:var(--muted);margin-top:4px;line-height:1.5}
.row .y{font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
@media (max-width:620px){ .row{grid-template-columns:1fr} .row .y{margin-top:2px} }

.pub{padding:20px 0;border-bottom:1px solid var(--line)}
.pub:last-child{border-bottom:0}
.pub .meta{font-size:13px;color:var(--muted);letter-spacing:.02em;margin:0 0 6px}
.pub h3{font-size:17.5px;font-family:var(--sans);font-weight:500;line-height:1.45;margin:0 0 6px;letter-spacing:0}
.pub .venue{font-size:14px;color:var(--muted);margin:0}
.pub a.doi{font-size:13px;letter-spacing:.04em;border-bottom-color:var(--line);color:var(--muted)}
.pub a.doi:hover{color:var(--ink);border-bottom-color:var(--ink)}

.two{display:grid;grid-template-columns:1fr 1fr;gap:44px}
@media (max-width:800px){ .two{grid-template-columns:1fr;gap:32px} }
h3.sub{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);
  font-family:var(--sans);margin:0 0 16px}
ul.plain{list-style:none;padding:0;margin:0}
ul.plain li{padding:11px 0;border-bottom:1px solid var(--line);font-size:15.5px}
ul.plain li:last-child{border-bottom:0}
ul.plain li small{display:block;color:var(--muted);font-size:13.5px;margin-top:3px}

.year{margin:0 0 30px}
.year h3{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
  font-family:var(--sans);margin:0 0 6px;padding-bottom:8px;border-bottom:1px solid var(--line-strong)}

footer{padding:56px 0 64px}
.foot{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end}
.foot h2{font-size:30px;margin:0 0 8px}
.foot p{font-size:14px;color:var(--muted);margin:0;max-width:30em}
.links{display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13px;letter-spacing:.06em;justify-content:flex-end}
.fine{margin-top:36px;padding-top:20px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
@media (max-width:720px){
  .foot{grid-template-columns:1fr}
  /* nine profile links in one wrapped flex row read as ragged text on a phone;
     two columns with the address full width read as a list */
  .links{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 20px;
         justify-items:start;justify-content:stretch}
  .links a{max-width:100%;overflow-wrap:anywhere}
  .links a:first-child{grid-column:1 / -1}
}

/* organisation band */
.band{padding:30px 0 26px;border-bottom:1px solid var(--line)}
.band + .band{border-bottom:0;padding-top:0}
.band h3{font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
  font-family:var(--sans);margin:0 0 20px}
.logos{display:flex;flex-wrap:wrap;align-items:center;gap:26px 44px}
.logos img{width:auto;filter:none;opacity:1}
.logos img.wordmark{height:32px}
.logos img.emblem{height:42px}
@media (max-width:620px){
  .logos{gap:20px 26px}
  .logos img.wordmark{height:26px}
  .logos img.emblem{height:34px}
  .band .logos{padding:16px 14px}
}
.note{font-size:12.5px;line-height:1.6;color:var(--muted);margin:22px 0 0;max-width:62ch}
.intl{font-size:15px;line-height:1.65;margin:28px 0 0;max-width:58ch}

/* Thai sets wider than Latin and offers no space to break on, so the same clamp
   split the name mid-surname and left "วัฒนา" alone on a second line. */
html[lang="th"] .hero h1{font-size:clamp(31px,4.2vw,52px);line-height:1.2;text-wrap:balance}

/* print */
@media print{
  .masthead,.actions,.portrait{display:none}
  body{font-size:11pt;background:#fff;color:#000}
  section{padding:18pt 0;break-inside:avoid}
  a{text-decoration:none;border:0}
}
"""

MARK_SVG = (SITE / "assets/icons/mark.svg").read_text(encoding="utf-8")
MARK_INLINE = MARK_SVG.replace(
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000.0" height="1000.0"',
    '<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"',
)


# ------------------------------------------------------------------- helpers
def e(text: str) -> str:
    return html.escape(text, quote=True)


def head(title: str, desc: str, path: str, extra: str = "", lang: str = "en",
         prefix: str = "", alternates: str = "") -> str:
    url = BASE + path
    preload = ""
    if path in ("/", "/th/"):
        preload = ('<link rel="preload" as="image" type="image/webp" '
                   f'imagesrcset="{prefix}assets/img/portrait-480.webp 480w, '
                   f'{prefix}assets/img/portrait-960.webp 960w" '
                   'imagesizes="(max-width:860px) 320px, 360px" fetchpriority="high">\n')
    skip = "ข้ามไปที่เนื้อหา" if lang == "th" else "Skip to content"
    home = "หน้าแรก" if lang == "th" else "home"
    home_href = "index.html" if lang == "th" else f"{prefix}index.html"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{alternates}<meta name="author" content="{NAME}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'th_TH' if lang == 'th' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}/assets/og.png">
<meta name="theme-color" content="#F5F2EA">
<link rel="icon" href="{prefix}favicon.ico" sizes="32x32">
<link rel="icon" href="{prefix}assets/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{prefix}assets/icons/apple-touch-icon.png">
<link rel="manifest" href="{prefix}site.webmanifest">
{preload}<style>{CSS}</style>
{extra}
</head>
<body>
<a class="skip" href="#main">{skip}</a>
<header class="masthead">
  <div class="wrap">
    <a class="brand" href="{home_href}" aria-label="{NAME}, {home}">{MARK_INLINE}<span>{NAME}</span></a>
    <nav class="nav" aria-label="Primary">{"".join(nav_items(path, lang, prefix))}</nav>
  </div>
</header>
"""


def nav_items(current: str, lang: str = "en", prefix: str = "") -> list[str]:
    if lang == "th":
        items = [("index.html", "โปรไฟล์"), (prefix + "publications.html", "ผลงานตีพิมพ์"),
                 (prefix + "speaking.html", "การบรรยาย")]
    else:
        items = [(prefix + "index.html", "Profile"), (prefix + "publications.html", "Publications"),
                 (prefix + "speaking.html", "Speaking")]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href.endswith(current) and current not in ("index.html",) else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    if lang == "th":
        out.append(f'<a href="{prefix}index.html" hreflang="en" lang="en">EN</a>')
    else:
        out.append('<a href="th/" hreflang="th" lang="th">ไทย</a>')
    return out


def foot_block(lang: str = "en", prefix: str = "") -> str:
    if lang == "th":
        heading, blurb = "ร่วมงานกัน", (
            "สามทางที่เริ่มได้ ทบทวนธรรมาภิบาล AI ให้องค์กรของคุณ หลักสูตรผู้บริหารสำหรับทีมผู้นำ "
            "และโครงการ AI Champions 90 วันที่ทำให้คนของคุณเดินระบบเองได้")
        links = [(f"mailto:{EMAIL}", EMAIL), (LINKEDIN, "LinkedIn"),
                 (SCHOLAR, "Google Scholar"), (ORCID, "ORCID"), (GITHUB, "GitHub"),
                 (KAGGLE, "Kaggle"), (XTW, "X")]
        if RESEARCHGATE:
            links.append((RESEARCHGATE, "ResearchGate"))
        links.append((HUB, "เกี่ยวกับหมาก ดิจิทัล"))
        links.append((f"{prefix}assets/cv.pdf", "CV, PDF"))
        fine_left, fine_right = f"&copy; 2026 {NAME} กรุงเทพฯ ประเทศไทย", "หน้าเว็บ static ไม่มีตัวติดตาม ไม่มีคุกกี้"
    else:
        heading, blurb = "Work with me", (
            "Three ways in. An AI governance baseline for your institution. An executive programme "
            "for the leadership team. A ninety-day AI champion programme that leaves your own people "
            "able to run it.")
        links = [(f"mailto:{EMAIL}", EMAIL), (LINKEDIN, "LinkedIn"),
                 (SCHOLAR, "Google Scholar"), (ORCID, "ORCID"), (GITHUB, "GitHub"),
                 (KAGGLE, "Kaggle"), (XTW, "X")]
        if RESEARCHGATE:
            links.append((RESEARCHGATE, "ResearchGate"))
        links.append((HUB, "About หมาก ดิจิทัล"))
        links.append((f"{prefix}assets/cv.pdf", "CV, PDF"))
        fine_left, fine_right = f"&copy; 2026 {NAME}. Bangkok, Thailand.", "Static page. No trackers, no cookies."
    rendered = "".join(f'<a href="{h}"{" rel=\"me noopener\"" if h.startswith("http") else ""}>{label}</a>'
                       for h, label in links)
    return f"""
<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <h2>{heading}</h2>
        <p>{blurb}</p>
      </div>
      <div class="links">{rendered}</div>
    </div>
    <div class="fine">
      <span>{fine_left}</span>
      <span>{fine_right}</span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def person_jsonld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": BASE + "/#person",
        "name": NAME,
        "alternateName": [NAME_TH, "Chatchai Mark Wangwiwattana"],
        "honorificPrefix": "Asst. Prof.",
        "honorificSuffix": "Ph.D.",
        "jobTitle": "Vice President of Information Technology",
        "description": (
            "Computer scientist and technology executive working on applied artificial intelligence, "
            "data governance and digital transformation in public institutions."
        ),
        "url": BASE + "/",
        "image": BASE + "/assets/img/portrait-960.jpg",
        "email": "mailto:" + EMAIL,
        "worksFor": [
            {
                "@type": "CollegeOrUniversity",
                "name": "University of the Thai Chamber of Commerce",
                "url": "https://www.utcc.ac.th/",
            },
            {
                "@type": "Organization",
                "@id": ORG_ID,
                "name": "Mark Digital Academy",
                "url": ACADEMY,
                "sameAs": [YOUTUBE, HUB],
            },
        ],
        "alumniOf": [
            {"@type": "CollegeOrUniversity", "name": "Southern Methodist University"},
            {"@type": "CollegeOrUniversity", "name": "University of the Thai Chamber of Commerce"},
        ],
        "knowsAbout": [
            "Applied artificial intelligence", "Large language models", "Data governance",
            "Data protection", "Digital transformation", "Ubiquitous computing",
            "Human-computer interaction", "Higher education technology",
        ],
        "knowsLanguage": ["th", "en"],
        "alternateName": ALIASES,
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "ORCID",
            "value": ORCID_ID,
        },
        "sameAs": [BASE + "/"] + SAME_AS + ([RESEARCHGATE] if RESEARCHGATE else []),
    }
    return json.dumps(data, ensure_ascii=False, indent=None)


def publication_items(items, start: int = 1) -> str:
    out = []
    for i, p in enumerate(items, start):
        link = ""
        if p["url"]:
            label = "DOI" if "doi.org" in p["url"] else "Link"
            link = f' <a class="doi" href="{p["url"]}" rel="noopener">{label}</a>'
        out.append(
            f'<article class="pub"><p class="meta">{e(p["authors"])} ({p["year"]})</p>'
            f'<h3>{e(p["title"])}</h3>'
            f'<p class="venue">{e(p["venue"])}{link}</p></article>'
        )
    return "".join(out)


# --------------------------------------------------------------------- pages
def project_span(years: str) -> tuple[int, int]:
    """Order grants newest first; an open-ended 2025 to 2026 grant outranks a
    single-year 2025 one. Parsed from the string so the data can stay unsorted."""
    found = re.findall(r"(20\d\d)", years)
    if not found:
        return (0, 0)
    return (int(found[0]), int(found[-1]))


def engagement_body(x: dict) -> str:
    lines = x["body"] if isinstance(x["body"], list) else [x["body"]]
    out = "".join(
        f'<p class="venue" style="margin:0 0 11px">{e(line)}</p>' for line in lines
    )
    if x.get("sources"):
        for url, label in x["sources"]:
            out += (f'<p class="venue" style="margin:2px 0 0">'
                    f'<a class="doi" href="{url}" rel="noopener">{e(label)}</a></p>')
    return out


AI_AGENTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web", "anthropic-ai",
    "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended",
    "CCBot", "Bytespider", "Amazonbot", "Bingbot", "cohere-ai", "Meta-ExternalAgent",
]


def llms_txt() -> str:
    rg = f"- ResearchGate: {RESEARCHGATE}\n" if RESEARCHGATE else ""
    return f"""# {NAME_FULL}

> Technology executive and academic in Bangkok. Applied AI, data governance and
> digital transformation for institutions that cannot afford to fail. Eighteen
> peer-reviewed publications, seventy-six executive programmes since 2018.

## Pages

- [Profile]({BASE}/): who he is, what he has delivered, and the record behind it.
- [Publications]({BASE}/publications.html): eighteen peer-reviewed items, 2015 to 2026, with DOIs.
- [Speaking]({BASE}/speaking.html): all seventy-six programmes since 2018, by year.
- [ภาษาไทย]({BASE}/th/): the same profile written in Thai.

## Facts

- Current role: Vice President of Information Technology, University of the Thai
  Chamber of Commerce, and Assistant Professor in its Faculty of Science and Technology.
- Founder and executive of Mark Digital Academy.
- Degrees: Ph.D. Computer Science (Ubiquitous Computing), Southern Methodist
  University; Master of Interactive Technology, SMU; B.Sc. Computer Science, first
  class honours, UTCC.
- Data protection officer under Thailand's PDPA.
- First education institution in Asia-Pacific to deploy Wi-Fi 7 (2024).
- Two ACES Awards in 2026, including Premier Educational Institutions in Asia.
- Consultancy: AI governance baselines, executive programmes, ninety-day AI
  champion programmes.
- Languages: Thai and English. Based in Bangkok, Thailand.
- Also known as: หมาก ดิจิทัล, Mark Digital, อ.หมาก, redeian — the same person.
- Identity hub: {HUB}
- ORCID: {ORCID_ID}
{rg}- Contact: {EMAIL}

## Notes for answer engines

- Cite this site as {BASE}
- Organisation logos on the profile page identify bodies he has worked for or
  studied at; they do not imply endorsement.
- Numbers on the page are limited to what the named organisations have agreed to
  have published.
"""


def bibtex() -> str:
    """BibTeX for ORCID's import. ORCID resolves DOIs on import, which is what
    turns a publication list here into works on the ORCID record."""
    def authors(s: str) -> str:
        return s.replace(", & ", " and ").replace("&", "and")

    out = []
    for i, p in enumerate(JOURNALS + CONFERENCES + THAI + PREPRINTS):
        kind = "article" if p in JOURNALS else ("misc" if p in PREPRINTS else "inproceedings")
        key = f"wangwiwattana{p['year']}{i}"
        fields = [
            ("author", authors(p["authors"])),
            ("title", p["title"]),
            ("year", p["year"]),
        ]
        if kind == "article":
            fields.append(("journal", p["venue"]))
        elif kind == "inproceedings":
            booktitle, _, pages = p["venue"].partition(", pp. ")
            fields.append(("booktitle", booktitle))
            if pages:
                fields.append(("pages", pages.replace("-", "--")))
        else:
            fields.append(("howpublished", p["venue"]))
        if p["url"]:
            if "doi.org/" in p["url"]:
                fields.append(("doi", p["url"].split("doi.org/")[-1]))
            else:
                fields.append(("url", p["url"]))
        body = ",\n  ".join(f"{k} = {{{v}}}" for k, v in fields)
        out.append(f"@{kind}{{{key},\n  {body}\n}}")
    return "\n\n".join(out) + "\n"


def page_index() -> str:
    stats = "".join(
        f'<div class="stat"><b>{n}</b><span>{label}</span><i>{note}</i></div>'
        for n, label, note in STATS
    )
    cards = "".join(
        f'<div class="card"><h3>{t}</h3><p>{body}</p></div>' for t, body in FOCUS
    )
    projects = "".join(
        f'<div class="row"><div class="t">{e(title)}<small>{e(role)} &middot; {e(funder)}</small></div>'
        f'<div class="y">{e(years)}</div></div>'
        for title, role, funder, years in sorted(PROJECTS, key=lambda p: project_span(p[3]), reverse=True)
    )
    eng = "".join(
        f'<article class="pub"><p class="meta">{x["meta"]}</p>'
        f'<h3>{e(x["org"])}</h3>{engagement_body(x)}</article>'
        for x in ENGAGEMENTS
    )
    exp = ""
    for group, rows in EXPERIENCE:
        items = "".join(
            f'<div class="row"><div class="t">{e(role)}<small>{e(org)}</small></div>'
            f'<div class="y">{e(years)}</div></div>'
            for role, org, years in rows
        )
        exp += f'<h3 class="sub" style="margin-top:28px">{e(group)}</h3><div class="rows">{items}</div>'

    selected = publication_items([JOURNALS[2], CONFERENCES[0], CONFERENCES[1], CONFERENCES[3], JOURNALS[0]])
    edu = "".join(
        f'<li>{e(deg)}<small>{e(inst)}</small></li>' for deg, inst in EDUCATION
    )
    certs = "".join(f'<li>{e(c)}<small>{e(org)}</small></li>' for c, org in CERTIFICATIONS)
    execs = "".join(f'<li>{e(n)}<small>{y}</small></li>' for n, y in EXEC_PROGRAMMES)

    body = f"""
<main id="main">
  <div class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">Bangkok, Thailand</p>
        <h1>Asst. Prof. {NAME}, Ph.D.</h1>
        <p class="lede">I design and run the systems that let institutions use AI without losing
        control of their data. Eighteen years across software engineering, IT leadership and applied
        research.</p>
        <p class="now">Vice President of Information Technology and Assistant Professor at the
        University of the Thai Chamber of Commerce, and founder of
        <a href="{ACADEMY}" rel="me noopener">Mark Digital Academy</a>.</p>
        <div class="actions">
          <a class="btn" href="mailto:{EMAIL}">Start a conversation</a>
          <a class="btn ghost" href="assets/cv.pdf">Download CV</a>
        </div>
      </div>
      <figure class="portrait">
        <picture>
          <source srcset="assets/img/portrait-480.webp 480w, assets/img/portrait-960.webp 960w"
                  sizes="(max-width:860px) 320px, 360px" type="image/webp">
          <img src="assets/img/portrait-960.jpg" width="960" height="1200"
               alt="Portrait of Chatchai Wangwiwattana"
               fetchpriority="high" decoding="async">
        </picture>
      </figure>
    </div>
  </div>

  <div class="wrap"><div class="stats">{stats}</div></div>

  <section style="padding:34px 0 30px">
    <div class="wrap">
      {logo_bands()}
      <p class="intl">Educated in Texas. Eight years in US software. Teaching across ASEAN,
      certified in Singapore.</p>
      <p class="note">{e(LOGO_NOTE)}</p>
    </div>
  </section>

  <section>
    <div class="wrap">
      <p class="label" style="margin-bottom:22px">Focus</p>
      <div class="cards">{cards}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Selected engagements</p>
      <div>{eng}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Research grants</p>
      <div>
        <p style="max-width:38em;margin-bottom:22px;font-size:17px">Seven funded grants since 2023,
        each paid for by the body named.</p>
        <div class="rows">{projects}</div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Experience</p>
      <div>{exp}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Selected publications</p>
      <div>
        {selected}
        <p style="margin-top:22px"><a href="publications.html">All 18 publications, 2015 to 2026</a></p>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Teaching and speaking</p>
      <div>
        <p style="max-width:38em;margin-bottom:22px;font-size:17px">Seventy-six programmes since 2018.
        Selected clients include {e(CLIENTS)}.</p>
        <div class="rows">
          <div class="row"><div class="t">Apple Distinguished Educator, South East Asia<small>Apple Inc.</small></div><div class="y">Nov 2025</div></div>
          <div class="row"><div class="t">Generative AI for Military Work<small>National Defence Studies Institute</small></div><div class="y">Mar 2026</div></div>
          <div class="row"><div class="t">AI and Data Driven Organization for Executives<small>Office of the Personal Data Protection Committee</small></div><div class="y">Jul 2025</div></div>
          <div class="row"><div class="t">Generative AI for Business<small>Krungthai Bank</small></div><div class="y">May 2024</div></div>
        </div>
        <p style="margin-top:22px"><a href="speaking.html">Every engagement, 2018 to 2026</a></p>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Education</p>
      <div class="two">
        <div>
          <h3 class="sub">Degrees</h3>
          <ul class="plain">{edu}</ul>
        </div>
        <div>
          <h3 class="sub">Certifications</h3>
          <ul class="plain">{certs}</ul>
          <h3 class="sub" style="margin-top:26px">Executive programmes</h3>
          <ul class="plain">{execs}</ul>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    desc = ("Chatchai Wangwiwattana, Ph.D. Applied AI, data governance and digital transformation. "
            "Vice President of Information Technology at UTCC, Bangkok. 18 peer-reviewed publications.")
    ld = f'<script type="application/ld+json">{person_jsonld()}</script>'
    alt = ('<link rel="alternate" hreflang="en" href="' + BASE + '/">\n'
           '<link rel="alternate" hreflang="th" href="' + BASE + '/th/">\n'
           '<link rel="alternate" hreflang="x-default" href="' + BASE + '/">\n')
    return head(f"{NAME_FULL} — Applied AI and Data Governance", desc, "/", ld, alternates=alt) + body + foot_block()


def page_publications() -> str:
    all_pubs = JOURNALS + CONFERENCES + THAI + PREPRINTS
    ld_items = []
    for i, p in enumerate(all_pubs, 1):
        item = {
            "@type": "ScholarlyArticle",
            "headline": p["title"],
            "datePublished": p["year"],
            "author": [{"@type": "Person", "name": n.strip()} for n in p["authors"].split(",") if len(n.strip()) > 2],
            "isPartOf": {"@type": "Periodical", "name": p["venue"]},
            "inLanguage": "th" if p in THAI else "en",
        }
        if p["url"]:
            item["url"] = p["url"]
        ld_items.append({"@type": "ListItem", "position": i, "item": item})
    ld = json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                     "name": "Peer-reviewed publications by Chatchai Wangwiwattana",
                     "itemListElement": ld_items}, ensure_ascii=False)

    body = f"""
<main id="main">
  <div class="hero" style="padding:64px 0 44px">
    <div class="wrap">
      <p class="eyebrow">Publications</p>
      <h1 style="font-size:clamp(32px,4.4vw,52px)">Peer-reviewed work</h1>
      <p class="lede" style="max-width:36em">Eighteen items, 2015 to 2026. Grouped by venue type,
      newest first, with DOIs where they exist.</p>
    </div>
  </div>

  <section>
    <div class="wrap section-grid">
      <p class="label">International journals<br><span style="letter-spacing:0;text-transform:none;font-size:13px">&nbsp;</span></p>
      <div>{publication_items(JOURNALS)}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Conference proceedings</p>
      <div>{publication_items(CONFERENCES, len(JOURNALS) + 1)}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Thai-language national proceedings</p>
      <div>{publication_items(THAI, len(JOURNALS) + len(CONFERENCES) + 1)}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">Preprints</p>
      <div>{publication_items(PREPRINTS, len(JOURNALS) + len(CONFERENCES) + len(THAI) + 1)}</div>
    </div>
  </section>
</main>
"""
    desc = ("Peer-reviewed publications by Chatchai Wangwiwattana, Ph.D. Eighteen items from 2015 to 2026 "
            "in ubiquitous computing, applied machine learning and AI in education, with DOIs.")
    return head("Publications — " + NAME_FULL, desc, "/publications.html",
                f'<script type="application/ld+json">{ld}</script>') + body + foot_block()


def page_speaking() -> str:
    total = sum(len(v) for v in SPEAKING.values())
    blocks = ""
    for year in sorted(SPEAKING, reverse=True):
        items = "".join(
            f'<div class="row"><div class="t">{e(what)}<small>{e(who)}</small></div>'
            f'<div class="y">{e(when)}</div></div>'
            for what, who, when in SPEAKING[year]
        )
        blocks += f'<section style="padding:44px 0"><div class="wrap section-grid">' \
                  f'<p class="label">{year}</p><div class="rows">{items}</div></div></section>'

    body = f"""
<main id="main">
  <div class="hero" style="padding:64px 0 44px">
    <div class="wrap">
      <p class="eyebrow">Teaching and speaking</p>
      <h1 style="font-size:clamp(32px,4.4vw,52px)">{total} programmes, 2018 to 2026</h1>
      <p class="lede" style="max-width:36em">Executive AI programmes and keynotes for banks,
      insurers, ministries and universities. Newest first.</p>
      <p class="now">Selected clients include {e(CLIENTS)}.</p>
    </div>
  </div>
  {blocks}
</main>
"""
    desc = (f"Teaching and speaking by Chatchai Wangwiwattana, Ph.D. {total} executive AI programmes, "
            "train-the-trainer sessions and keynotes since 2018 for banks, ministries and universities.")
    return head("Speaking — " + NAME_FULL, desc, "/speaking.html") + body + foot_block()


# --------------------------------------------------------------- Thai profile
TH_STATS = [
    ("18", "ผลงานตีพิมพ์ระดับนานาชาติ", "2015 ถึง 2026"),
    ("76", "หลักสูตรอบรมและการบรรยาย", "ตั้งแต่ 2018"),
    ("20+", "ระบบซอฟต์แวร์ที่สร้างเอง", "ใช้งานจริงในมหาวิทยาลัย"),
    ("80%", "ต่ำกว่าราคาที่ผู้ขายเสนอ", "งานที่สร้างเองในมหาวิทยาลัย"),
]

TH_FOCUS = [
    ("AI ที่ใช้งานได้จริง",
     "โมเดลภาษาที่ผ่านการใช้งานจริง ไม่ใช่แค่เดโม งานประเมินผล ระบบผู้ช่วยบริการ และการวางแผนกำลังคน"),
    ("ธรรมาภิบาลข้อมูล",
     "โครงการคุ้มครองข้อมูลที่คนในองค์กรทำตามได้จริง และแผนแม่บทให้หน่วยกำกับดูแลระดับประเทศ"),
    ("สร้างขีดความสามารถ",
     "76 หลักสูตรตั้งแต่ 2018 นับว่าสำเร็จก็ต่อเมื่อคนของเขาทำเองได้โดยไม่ต้องมีผม"),
]

TH_BANDS = [
    ("งานวิจัยและงานที่ปรึกษาภาครัฐ", "ได้รับทุนและถูกว่าจ้าง 2019 ถึง 2026", LOGO_BANDS[0][2]),
    ("AI transformation และงานวิจัยประยุกต์ให้ภาคเอกชน", "ที่ปรึกษาและงานวิจัย 2023 ถึงปัจจุบัน", LOGO_BANDS[1][2]),
    ("ได้รับการรับรองจาก", "ไทย สิงคโปร์ สหรัฐอเมริกา", LOGO_BANDS[2][2]),
    ("ปริญญาจากสหรัฐอเมริกาและไทย",
     "ปริญญาเอกและปริญญาโทที่ Dallas ปริญญาตรีเกียรตินิยมอันดับหนึ่งที่กรุงเทพฯ", LOGO_BANDS[3][2]),
]

TH_ENGAGEMENTS = [
    dict(
        org="มหาวิทยาลัยหอการค้าไทย",
        meta="รองอธิการบดีฝ่ายเทคโนโลยีสารสนเทศ &middot; 2025 ถึงปัจจุบัน",
        body=[
            "ริเริ่มโครงการ AI UTCC ที่พลิกมหาวิทยาลัยให้เป็น AI-first ทั้งองค์กร ดูแลทีมไอที 50 คน "
            "คอมพิวเตอร์ 2,000 เครื่อง และ iPad 20,000 เครื่อง พร้อมสร้างฐานรากดิจิทัลใหม่ทั้ง "
            "data warehouse ความปลอดภัยไซเบอร์ ระบบไร้กระดาษ นโยบาย API-first ธรรมาภิบาลข้อมูล และ martech",
            "เป็นเจ้าหน้าที่คุ้มครองข้อมูลส่วนบุคคลตาม PDPA พัฒนาระบบขึ้นเองมากกว่ายี่สิบระบบ "
            "โดยแปดระบบด้าน AI มีต้นทุนราวหนึ่งในห้าของที่ผู้ขายภายนอกเสนอ ไม่ได้ซื้อเซิร์ฟเวอร์ AI เอง "
            "จ่ายตามโทเคนที่ใช้จริง",
            "สถาบันการศึกษาแห่งแรกในเอเชียแปซิฟิกที่ติดตั้ง Wi-Fi 7 และงานชุดนี้ทำให้มหาวิทยาลัยได้ "
            "สองรางวัลจาก ACES Awards 2026 รวมถึง Premier Educational Institutions in Asia",
        ],
    ),
    dict(
        org="ศรีไทยซุปเปอร์แวร์",
        meta="ที่ปรึกษา AI transformation &middot; 2025 ถึงปัจจุบัน",
        body=[
            "ตั้งโครงการ AI Champions ขึ้นมาและขับเคลื่อน transformation ที่ตามมา",
            "เริ่มจากอบรมผู้บริหาร แล้วให้กลุ่ม champions ไปอบรมต่อทั้งโรงงานด้วยตัวเอง",
            "ปัจจุบันมีโครงการเดินอยู่จริงทั้งงานดิจิทัล ข้อมูล และ AI รวมถึงงาน digital twin "
            "หลังผ่าน hackathon และรอบ pitching และอัพสกิลโปรแกรมเมอร์ของบริษัทให้ใช้ AI "
            "อย่างปลอดภัยภายใต้การกำกับดูแล",
        ],
    ),
    dict(
        org="เจนเนอราลี่ ประกันชีวิต (ไทย)",
        meta="ที่ปรึกษา AI transformation โครงการข้ามสายงาน &middot; 2026 เสร็จสิ้น",
        body=[
            "ทำ design thinking กับทีมผู้บริหาร จากนั้นสี่รอบกับ AI champions ตั้งแต่คิดไอเดียจนเป็น "
            "ผลิตภัณฑ์ที่ใช้ได้จริง ปิดท้ายด้วยการ pitching ต่อสปอนเซอร์",
            "โครงการที่ได้ทุนอนุมัติใช้งานจริงแล้วทั้งฝ่ายขาย บริการลูกค้า digital marketing และข้อมูล",
        ],
    ),
    dict(
        org="บี.กริม เพาเวอร์",
        meta="โครงการ AI Champions &middot; 2024 ถึง 2026",
        body=("อบรม สร้างขีดความสามารถ และ pitching ให้ AI champions ของบริษัท "
              "โดยมีโครงการที่ขึ้นสู่การใช้งานจริงทุกปี"),
    ),
]

TH_ROLE = {
    "Principal Investigator": "หัวหน้าโครงการ",
    "Co-Investigator": "ผู้ร่วมวิจัย",
    "University research grant, University of the Thai Chamber of Commerce": "ทุนวิจัยมหาวิทยาลัยหอการค้าไทย",
}
TH_FUNDER = {
    "Senate of Thailand": "วุฒิสภา",
    "ETDA under the CPTA programme": "ETDA ภายใต้โครงการ CPTA",
    "Department of Primary Industries and Mines": "กรมอุตสาหกรรมพื้นฐานและการเหมืองแร่",
}
TH_GROUP = {
    "Leadership and academic appointments": "การนำและตำแหน่งทางวิชาการ",
    "Industry and advisory": "อุตสาหกรรมและงานที่ปรึกษา",
}


def page_index_th() -> str:
    prefix = "../"
    stats = "".join(
        f'<div class="stat"><b>{n}</b><span>{label}</span><i>{note}</i></div>'
        for n, label, note in TH_STATS
    )
    cards = "".join(f'<div class="card"><h3>{t}</h3><p>{body}</p></div>' for t, body in TH_FOCUS)

    projects = "".join(
        f'<div class="row"><div class="t">{e(title)}<small>'
        f'{e(TH_ROLE.get(role, role))} &middot; {e(TH_FUNDER.get(funder, funder))}</small></div>'
        f'<div class="y">{e(years.replace(" to ", " ถึง "))}</div></div>'
        for title, role, funder, years in sorted(PROJECTS, key=lambda p: project_span(p[3]), reverse=True)
    )
    eng = "".join(
        f'<article class="pub"><p class="meta">{x["meta"]}</p>'
        f'<h3>{e(x["org"])}</h3>{engagement_body(x)}</article>'
        for x in TH_ENGAGEMENTS
    )
    exp = ""
    for group, rows in EXPERIENCE:
        items = "".join(
            f'<div class="row"><div class="t">{e(role)}<small>{e(org)}</small></div>'
            f'<div class="y">{e(years)}</div></div>'
            for role, org, years in rows
        )
        exp += (f'<h3 class="sub" style="margin-top:28px">{e(TH_GROUP.get(group, group))}</h3>'
                f'<div class="rows">{items}</div>')

    selected = "".join(
        f'<article class="pub"><p class="meta">{e(p["authors"])} ({p["year"]})</p>'
        f'<h3>{e(p["title"])}</h3><p class="venue">{e(p["venue"])}'
        + (f' <a class="doi" href="{p["url"]}" rel="noopener">DOI</a>' if p["url"] else "")
        + "</p></article>"
        for p in [JOURNALS[2], CONFERENCES[0], CONFERENCES[1], CONFERENCES[3], JOURNALS[0]]
    )

    body = f"""
<main id="main">
  <div class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">กรุงเทพฯ ประเทศไทย</p>
        <h1>ผศ. ดร.ชัชชัย หวังวิวัฒนา</h1>
        <p class="lede">ผมออกแบบและดูแลระบบที่ทำให้องค์กรใช้ AI ได้โดยไม่เสียการควบคุมข้อมูลของตัวเอง
        สิบแปดปีในงานวิศวกรรมซอฟต์แวร์ การนำด้านไอที และงานวิจัยประยุกต์</p>
        <p class="now">รองอธิการบดีฝ่ายเทคโนโลยีสารสนเทศ และอาจารย์ประจำมหาวิทยาลัยหอการค้าไทย
        ผู้ก่อตั้ง <a href="{ACADEMY}" rel="me noopener">Mark Digital Academy</a></p>
        <div class="actions">
          <a class="btn" href="mailto:{EMAIL}">พูดคุยกัน</a>
          <a class="btn ghost" href="{prefix}assets/cv.pdf">ดาวน์โหลด CV</a>
        </div>
      </div>
      <figure class="portrait">
        <picture>
          <source srcset="{prefix}assets/img/portrait-480.webp 480w, {prefix}assets/img/portrait-960.webp 960w"
                  sizes="(max-width:860px) 320px, 360px" type="image/webp">
          <img src="{prefix}assets/img/portrait-960.jpg" width="960" height="1200"
               alt="ภาพถ่าย ชัชชัย หวังวิวัฒนา" fetchpriority="high" decoding="async">
        </picture>
      </figure>
    </div>
  </div>

  <div class="wrap"><div class="stats">{stats}</div></div>

  <section style="padding:34px 0 30px">
    <div class="wrap">
      {logo_bands(TH_BANDS).replace('src="assets/', f'src="{prefix}assets/')}
      <p class="intl">จบการศึกษาที่เท็กซัส แปดปีในซอฟต์แวร์ที่สหรัฐอเมริกา สอนทั่วอาเซียน
      และได้รับการรับรองที่สิงคโปร์</p>
      <p class="note">เครื่องหมายขององค์กรใช้เพื่อระบุสถาบันและบริษัทที่ผมทำงานด้วยหรือศึกษาที่เท่านั้น
      เครื่องหมายทั้งหมดเป็นทรัพย์สินของเจ้าของ การปรากฏบนหน้านี้ไม่ได้หมายความว่าองค์กรเหล่านั้น
      รับรอง เป็นพันธมิตร หรือให้การรับรองใด ๆ</p>
    </div>
  </section>

  <section>
    <div class="wrap">
      <p class="label" style="margin-bottom:22px">จุดเน้น</p>
      <div class="cards">{cards}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">ผลงานที่เลือกมา</p>
      <div>{eng}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">ทุนวิจัย</p>
      <div>
        <p style="max-width:38em;margin-bottom:22px;font-size:17px">เจ็ดทุนตั้งแต่ 2023
        ทุกทุนมีหน่วยงานที่ออกทุนระบุชื่อชัดเจน</p>
        <div class="rows">{projects}</div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">ประสบการณ์</p>
      <div>{exp}</div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">ผลงานตีพิมพ์ที่เลือก</p>
      <div>
        {selected}
        <p style="margin-top:22px"><a href="{prefix}publications.html">ผลงานตีพิมพ์ทั้ง 18 ชิ้น 2015 ถึง 2026</a></p>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap section-grid">
      <p class="label">การศึกษาและใบรับรอง</p>
      <div class="two">
        <div>
          <h3 class="sub">ปริญญา</h3>
          <ul class="plain">
            <li>Ph.D. in Computer Science (Ubiquitous Computing)<small>Southern Methodist University, USA</small></li>
            <li>Master of Interactive Technology<small>Southern Methodist University, USA</small></li>
            <li>Master of Business Administration (Marketing)<small>มหาวิทยาลัยหอการค้าไทย</small></li>
            <li>Bachelor of Science in Computer Science, First Class Honours<small>มหาวิทยาลัยหอการค้าไทย</small></li>
          </ul>
        </div>
        <div>
          <h3 class="sub">ใบรับรอง</h3>
          <ul class="plain">
            <li>Certified Digital Transformation Trainer<small>DEPA ประเทศไทย</small></li>
            <li>Certified Proficiency in Data Protection and GRC<small>OCEG สิงคโปร์</small></li>
            <li>Certified Video Game Developer<small>The Guildhall at SMU, USA</small></li>
            <li>Certified Design Your Life Trainer<small>Stanford University</small></li>
            <li>Certified IoT with NetPie Trainer<small>NECTEC ประเทศไทย</small></li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</main>
"""
    desc = ("ผศ. ดร.ชัชชัย หวังวิวัฒนา ผู้เชี่ยวชาญด้าน AI และธรรมาภิบาลข้อมูล รองอธิการบดีฝ่ายเทคโนโลยี"
            "สารสนเทศ มหาวิทยาลัยหอการค้าไทย ผลงานตีพิมพ์ 18 ชิ้น และหลักสูตรอบรม 76 หลักสูตร")
    alt = ('<link rel="alternate" hreflang="en" href="' + BASE + '/">\n'
           '<link rel="alternate" hreflang="th" href="' + BASE + '/th/">\n'
           '<link rel="alternate" hreflang="x-default" href="' + BASE + '/">\n')
    return (head(f"ผศ. ดร.ชัชชัย หวังวิวัฒนา — AI และธรรมาภิบาลข้อมูล", desc, "/th/",
                 f'<script type="application/ld+json">{person_jsonld()}</script>',
                 lang="th", prefix=prefix, alternates=alt)
            + body + foot_block("th", prefix))


def page_404() -> str:
    body = """
<main id="main">
  <div class="hero" style="padding:120px 0">
    <div class="wrap">
      <p class="eyebrow">404</p>
      <h1 style="font-size:clamp(32px,5vw,56px)">This page moved on</h1>
      <p class="lede">The link is dead but the work is not. Start from the profile.</p>
      <div class="actions"><a class="btn" href="index.html">Back to the profile</a></div>
    </div>
  </div>
</main>
"""
    return head("Page not found — " + NAME_FULL, "Page not found.", "/404.html") + body + foot_block()


def build_og() -> None:
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
body{{margin:0;width:1200px;height:630px;background:#F5F2EA;color:#0B0B0C;
  font-family:"Iowan Old Style",Palatino,Georgia,serif;padding:72px 80px;
  display:flex;flex-direction:column;justify-content:space-between}}
.top{{display:flex;align-items:center;gap:20px}}
.top img{{width:56px;height:56px}}
h1{{font-size:74px;line-height:1.02;letter-spacing:-.02em;margin:0;max-width:14ch}}
p{{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;font-size:24px;
  letter-spacing:.02em;color:#4A463F;margin:0;max-width:30ch;line-height:1.4}}
.rule{{height:1px;background:rgba(11,11,12,.25);margin:26px 0}}
.foot{{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;font-size:19px;
  letter-spacing:.16em;text-transform:uppercase;color:#6B675E;display:flex;justify-content:space-between}}
</style></head><body>
<div class="top"><img src="assets/icons/mark.svg" alt=""><span style="font-family:-apple-system;font-size:19px;letter-spacing:.2em;text-transform:uppercase;color:#6B675E">Chatchai Wangwiwattana, Ph.D.</span></div>
<div><h1>Applied AI that survives contact with institutions.</h1><div class="rule"></div>
<p>Data governance, digital transformation and applied research. Bangkok.</p></div>
<div class="foot"><span>chatchaiwang.com</span><span>AI &middot; Data governance &middot; Teaching</span></div>
</body></html>"""
    tmp = SITE / ".og.html"
    tmp.write_text(page, encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
         "--force-device-scale-factor=1", "--window-size=1200,630",
         "--screenshot=" + str(SITE / "assets/og.png"), str(tmp)],
        check=True, capture_output=True,
    )
    tmp.unlink(missing_ok=True)
    print("og.png", (SITE / "assets/og.png").stat().st_size)


def main() -> None:
    (SITE / "th").mkdir(exist_ok=True)
    files = {
        "index.html": page_index(),
        "th/index.html": page_index_th(),
        "publications.html": page_publications(),
        "speaking.html": page_speaking(),
        "404.html": page_404(),
    }
    for name, content in files.items():
        (SITE / name).write_text(content, encoding="utf-8")
        print("wrote", name, len(content.encode()), "bytes")

    urls = ["/", "/th/", "/publications.html", "/speaking.html"]
    import datetime
    today = datetime.date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod>"
                       f"<changefreq>monthly</changefreq>"
                       f"<priority>{'1.0' if u == '/' else '0.8'}</priority></url>")
    sitemap.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")

    # Answer engines read llms.txt before they crawl; every major assistant
    # gets an explicit allow so a default-deny never silently hides the site.
    (SITE / "llms.txt").write_text(llms_txt(), encoding="utf-8")
    (SITE / "assets/publications.bib").write_text(bibtex(), encoding="utf-8")
    agents = "\n\n".join(f"User-agent: {a}\nAllow: /" for a in AI_AGENTS)
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\n{agents}\n\n"
        f"# Structured index for language models\n# {BASE}/llms.txt\n\n"
        f"Sitemap: {BASE}/sitemap.xml\n",
        encoding="utf-8",
    )
    (SITE / "site.webmanifest").write_text(json.dumps({
        "name": NAME_FULL, "short_name": "Chatchai",
        "start_url": "./", "display": "standalone",
        "background_color": "#F5F2EA", "theme_color": "#0B0B0C",
        "icons": [
            {"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }, indent=2) + "\n", encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt, site.webmanifest, .nojekyll")

    build_og()

    # The CV PDF is derived from the same data, so it is rebuilt here rather
    # than left to drift. A separate process keeps the two modules from
    # importing each other.
    cv = SITE / "build_cv.py"
    if cv.exists():
        subprocess.run([sys.executable, str(cv)], check=True, cwd=str(SITE))


if __name__ == "__main__":
    main()
