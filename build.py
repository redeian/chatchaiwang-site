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


def logo_bands() -> str:
    # Emblems read smaller than wordmarks at the same cap height, so the two
    # seal-shaped marks get a few extra pixels to hold their optical weight.
    emblems = {"senate", "dpim", "smu-seal"}
    out = []
    for heading, sub, items in LOGO_BANDS:
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
@media (prefers-color-scheme:dark){
  :root{ --paper:#0B0B0C; --ink:#F5F2EA; --muted:#9C978C; --line:rgba(245,242,234,.15);
         --line-strong:rgba(245,242,234,.32); --tile:#F5F2EA; --tile-ink:#0B0B0C; }
}
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
@media (max-width:720px){ .foot{grid-template-columns:1fr} .links{justify-content:flex-start} }

/* organisation band */
.band{padding:30px 0 26px;border-bottom:1px solid var(--line)}
.band + .band{border-bottom:0;padding-top:0}
.band h3{font-size:11.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
  font-family:var(--sans);margin:0 0 20px}
.logos{display:flex;flex-wrap:wrap;align-items:center;gap:26px 44px}
.logos img{width:auto;filter:none;opacity:1}
.logos img.wordmark{height:32px}
.logos img.emblem{height:42px}
@media (prefers-color-scheme:dark){
  /* colour marks need a light plate on a dark page; recolouring brand logos is
     worse than giving them the surface they were drawn for */
  .band .logos{background:#F5F2EA;padding:20px 22px}
}
@media (max-width:620px){
  .logos{gap:20px 26px}
  .logos img.wordmark{height:26px}
  .logos img.emblem{height:34px}
  .band .logos{padding:16px 14px}
}
.note{font-size:12.5px;line-height:1.6;color:var(--muted);margin:22px 0 0;max-width:62ch}
.intl{font-size:15px;line-height:1.65;margin:28px 0 0;max-width:58ch}

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


def head(title: str, desc: str, path: str, extra: str = "") -> str:
    url = BASE + path
    preload = ""
    if path == "/":
        preload = ('<link rel="preload" as="image" type="image/webp" '
                   'imagesrcset="assets/img/portrait-480.webp 480w, assets/img/portrait-960.webp 960w" '
                   'imagesizes="(max-width:860px) 320px, 360px" fetchpriority="high">\n')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="author" content="{NAME}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}/assets/og.png">
<meta name="theme-color" content="#F5F2EA" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#0B0B0C" media="(prefers-color-scheme:dark)">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="assets/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
{preload}<style>{CSS}</style>
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="{NAME}, home">{MARK_INLINE}<span>{NAME}</span></a>
    <nav class="nav" aria-label="Primary">{"".join(nav_items(path))}</nav>
  </div>
</header>
"""


def nav_items(current: str) -> list[str]:
    items = [("index.html", "Profile"), ("publications.html", "Publications"), ("speaking.html", "Speaking")]
    out = []
    for href, label in items:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return out


def foot_block() -> str:
    return f"""
<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <h2>Work with me</h2>
        <p>Three ways in. An AI governance baseline for your institution. An executive programme
        for the leadership team. A ninety-day AI champion programme that leaves your own people
        able to run it.</p>
      </div>
      <div class="links">
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="{LINKEDIN}" rel="me noopener">LinkedIn</a>
        <a href="{YOUTUBE}" rel="me noopener">Mark Digital Academy</a>
        <a href="assets/cv.pdf">CV, PDF</a>
      </div>
    </div>
    <div class="fine">
      <span>&copy; 2026 {NAME}. Bangkok, Thailand.</span>
      <span>Static page. No trackers, no cookies.</span>
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
                "name": "Mark Digital Academy",
                "url": YOUTUBE,
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
        "sameAs": [LINKEDIN, YOUTUBE],
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
        <a href="https://www.youtube.com/@markdigitalacademy" rel="me noopener">Mark Digital Academy</a>.</p>
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
    return head(f"{NAME_FULL} — Applied AI and Data Governance", desc, "/", ld) + body + foot_block()


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
    files = {
        "index.html": page_index(),
        "publications.html": page_publications(),
        "speaking.html": page_speaking(),
        "404.html": page_404(),
    }
    for name, content in files.items():
        (SITE / name).write_text(content, encoding="utf-8")
        print("wrote", name, len(content.encode()), "bytes")

    urls = ["/", "/publications.html", "/speaking.html"]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{BASE}{u}</loc><changefreq>monthly</changefreq>"
                       f"<priority>{'1.0' if u == '/' else '0.8'}</priority></url>")
    sitemap.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
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
