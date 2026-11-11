#!/usr/bin/env python3
"""Generate the service and hiring landing pages, in English and French.

One template, one content entry per page. Each page answers one search intent
(a client looking for a Flutter developer, a recruiter looking for a remote
engineer, ...) with facts already on the portfolio: no claim here that the
home page cannot back up.

    python tools/make-pages.py
"""

import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ghaithmeftah.github.io"
PERSON = SITE + "/#ghaith"
MAIL = "ghaithmeftah@gmail.com"
CAL = "https://calendly.com/ghaithmeftah/30min"
TODAY = "2026-10-31"

# the pages, by key: path in each language
PATHS = {
    "hire": {"en": "/hire/", "fr": "/fr/recrutement/"},
    "flutter": {"en": "/services/flutter/", "fr": "/fr/services/flutter/"},
    "symfony": {"en": "/services/symfony/", "fr": "/fr/services/symfony/"},
    "dotnet": {"en": "/services/dotnet/", "fr": "/fr/services/dotnet/"},
    "fullstack": {"en": "/services/full-stack/", "fr": "/fr/services/full-stack/"},
}
ORDER = ["fullstack", "flutter", "symfony", "dotnet", "hire"]

# ------------------------------------------------------------------ shared copy
UI = {
    "en": {
        "lang": "en", "locale": "en_US", "home": "/", "cv": "/cv.html", "other": "FR",
        "nav": [("/#work", "Work"), ("/#said", "Said"), ("/#lab", "Lab"), ("/#path", "Path"), ("/#hire", "Hire me")],
        "skip": "Skip to content", "crumb_home": "Ghaith Mefteh", "crumb_services": "Services",
        "call": "Book a 30-min call", "read_cv": "Read the CV",
        "avail": "Open to freelance projects · answers within the day",
        "avail_hire": "Open to remote roles and EU relocation · answers within the day",
        "faq_h": "Questions people ask first", "more_h": "Other ways I can help",
        "see_case": "See the case study",
        "contact_h": "Tell me what you are building",
        "contact_lede": "A short call or an email is enough to start, in CET working hours.",
        "email_me": "Email me", "dock_email": "Email me",
        "labels": {"hire": "Hiring a remote engineer", "flutter": "Flutter mobile apps", "symfony": "Symfony and PHP web",
                   "dotnet": ".NET backends and APIs", "fullstack": "Full-stack freelance"},
        "colophon": "Ghaith Mefteh · full-stack and mobile software engineer · Nabeul, Tunisia (CET) · remote or relocating in the EU",
    },
    "fr": {
        "lang": "fr", "locale": "fr_FR", "home": "/fr/", "cv": "/fr/cv.html", "other": "EN",
        "nav": [("/fr/#work", "Projets"), ("/fr/#said", "Avis"), ("/fr/#lab", "Labo"), ("/fr/#path", "Parcours"), ("/fr/#hire", "Me recruter")],
        "skip": "Aller au contenu", "crumb_home": "Ghaith Mefteh", "crumb_services": "Services",
        "call": "Réserver un appel de 30 min", "read_cv": "Lire le CV",
        "avail": "Ouvert aux missions freelance · réponse dans la journée",
        "avail_hire": "Ouvert au télétravail et à une mobilité dans l'UE · réponse dans la journée",
        "faq_h": "Les questions qu'on me pose d'abord", "more_h": "Les autres façons de travailler ensemble",
        "see_case": "Voir l'étude de cas",
        "contact_h": "Parlez-moi de votre projet",
        "contact_lede": "Un court appel ou un e-mail suffit pour commencer, aux heures de bureau (CET).",
        "email_me": "M'écrire", "dock_email": "M'écrire",
        "labels": {"hire": "Recruter un ingénieur à distance", "flutter": "Applications mobiles Flutter", "symfony": "Web Symfony et PHP",
                   "dotnet": "Backends et API .NET", "fullstack": "Full-stack en freelance"},
        "colophon": "Ghaith Mefteh · ingénieur logiciel full-stack et mobile · Nabeul, Tunisie (CET) · télétravail ou mobilité dans l'UE",
    },
}

# proof cards, reused across pages: image, size, and copy per language
CASES = {
    "soc": {
        "img": "soc-results", "w": 460, "h": 997, "anchor": "#case-soc",
        "en": ("SOC Rugby, Chambéry", "The rugby club's official app on the App Store and Google Play, built solo: calendar, live scores, rankings, messaging and push notifications. Flutter with GetX and SQLite, plus an iOS home-screen widget in SwiftUI; released through Codemagic, watched by Sentry.",
               "2,000+ fans · 99.8% crash-free sessions", "SOC Rugby app, results screen with the club's matchday scores"),
        "fr": ("SOC Rugby, Chambéry", "L'application officielle du club de rugby sur l'App Store et Google Play, développée seul : calendrier, scores en direct, classements, messagerie et notifications. Flutter avec GetX et SQLite, plus un widget d'écran d'accueil iOS en SwiftUI ; publiée via Codemagic, surveillée par Sentry.",
               "+2 000 supporters · 99,8 % de sessions sans crash", "Application SOC Rugby, écran des résultats par journée"),
    },
    "smartcare": {
        "img": "sc-home", "w": 460, "h": 997, "anchor": "#case-smartcare",
        "en": ("SmartCare", "A patient–doctor app for Tunisia, live on Google Play: booking and reminders, real-time messaging, ambulance calls on Google Maps. I was the only mobile engineer and also wrote the FastAPI backend on MongoDB, deployed to AWS, and the React web app.",
               "40+ doctors · 3,000+ patients", "SmartCare app, home screen with its feature tiles"),
        "fr": ("SmartCare", "Une application patient–médecin pour la Tunisie, en ligne sur Google Play : rendez-vous et rappels, messagerie en temps réel, appels d'ambulance sur Google Maps. Seul ingénieur mobile, j'ai aussi écrit le backend FastAPI sur MongoDB, déployé sur AWS, et l'application web React.",
               "+40 médecins · +3 000 patients", "Application SmartCare, écran d'accueil et ses fonctionnalités"),
    },
    "chalet": {
        "img": "cm-listings", "w": 1400, "h": 714, "anchor": "#case-chalet",
        "en": ("chalet-montagne.com", "A French ski-chalet marketplace rebuilt on Symfony while it kept selling: legacy data and business logic moved first, then a new search engine behind caching, query optimisation and on-demand WebP images. I built the core solo from April 2025, then led a team of four to delivery in July 2026.",
               "10,000+ chalets · search 20–50 s → 4–6 s · 390+ tests · ~60% less image bandwidth", "chalet-montagne.com listing page with filters and chalet cards"),
        "fr": ("chalet-montagne.com", "Une place de marché de chalets au ski refondue sur Symfony sans jamais arrêter de vendre : données et logique métier migrées d'abord, puis un nouveau moteur de recherche avec cache, requêtes optimisées et images WebP à la demande. J'ai développé seul le cœur à partir d'avril 2025, puis dirigé une équipe de quatre jusqu'à la livraison en juillet 2026.",
               "+10 000 chalets · recherche de 20–50 s à 4–6 s · +390 tests · ~60 % de bande passante image en moins", "Page de résultats chalet-montagne.com avec filtres et fiches de chalets"),
    },
    "platform": {
        "img": "motion/platform", "ext": "jpg", "w": 1600, "h": 900, "anchor": None,
        "en": ("AzertyUI company platform", "Absences, expenses, tickets, contracts and payslips in one place, on .NET (ASP.NET Core) microservices behind an API Gateway, talking over gRPC, with Angular 21 in front. I lead the four engineers building it, plus the company's server monitoring.",
               "team of 4 led · microservices · gRPC · Angular 21", "Schematic of the AzertyUI platform: Angular app, API Gateway, .NET services over gRPC"),
        "fr": ("Plateforme interne AzertyUI", "Absences, notes de frais, tickets, contrats et fiches de paie au même endroit, sur des microservices .NET (ASP.NET Core) derrière une API Gateway, qui se parlent en gRPC, avec Angular 21 devant. Je dirige les quatre ingénieurs qui la construisent, ainsi que la supervision des serveurs.",
               "équipe de 4 dirigée · microservices · gRPC · Angular 21", "Schéma de la plateforme AzertyUI : application Angular, API Gateway, services .NET en gRPC"),
    },
    "lmobile": {
        "img": "lmobile-warehouse", "w": 1200, "h": 600, "anchor": None,
        "en": ("L-Mobile warehouse terminal", "Five warehouse-management modules on tablets mounted on forklifts, integrated with Microsoft Dynamics 365 Business Central over C#/.NET and REST, in an enterprise stack I learned on the job.",
               "5 modules shipped · D365 Business Central", "Warehouse aisle with forklifts and tracked positions"),
        "fr": ("Terminal d'entrepôt L-Mobile", "Cinq modules de gestion d'entrepôt sur des tablettes montées sur chariots élévateurs, intégrés à Microsoft Dynamics 365 Business Central en C#/.NET et REST, dans une stack d'entreprise apprise sur le terrain.",
               "5 modules livrés · D365 Business Central", "Allée d'entrepôt avec chariots et positions suivies"),
    },
}

# how an engagement runs, shared by the service pages
HOW = {
    "en": [("A short call", "We talk through the product, the users and what is slow or missing today. Thirty minutes is usually enough."),
           ("A written scope and a first milestone", "You get a scope in plain words and a first milestone we can both check against, quoted per project or per day."),
           ("Work in the open", "Reviewable commits on your repository, tests that grow with each feature, and a deployed build you can click at every step.")],
    "fr": [("Un court appel", "On parle du produit, des utilisateurs et de ce qui est lent ou manquant aujourd'hui. Trente minutes suffisent en général."),
           ("Un périmètre écrit et un premier jalon", "Vous recevez un périmètre en mots simples et un premier jalon vérifiable par tous les deux, chiffré au projet ou à la journée."),
           ("Un travail visible", "Des commits relisibles sur votre dépôt, des tests qui grandissent avec chaque fonctionnalité, et une version déployée à cliquer à chaque étape.")],
}

FAQ_COMMON = {
    "en": [("How much does it cost?", "It depends on the scope, so I quote per project or per day once the scope is written down. The first call and the written scope are free."),
           ("Which timezone do you work in?", "Nabeul, Tunisia, at UTC+1: a full European working day of overlap, plus the US East Coast morning."),
           ("What languages do you work in?", "English and French every day (both B2, English certified by TOEIC), and German at B1.")],
    "fr": [("Combien ça coûte ?", "Cela dépend du périmètre : je chiffre au projet ou à la journée une fois le périmètre écrit. Le premier appel et le périmètre écrit sont gratuits."),
           ("Sur quel fuseau horaire travaillez-vous ?", "Nabeul, Tunisie, en UTC+1 : une journée de travail européenne entière en commun, plus la matinée de la côte Est des États-Unis."),
           ("Dans quelles langues travaillez-vous ?", "Français et anglais au quotidien (niveau B2, anglais certifié TOEIC), et allemand en B1.")],
}

# ------------------------------------------------------------------ the pages
PAGES = {
    "fullstack": {
        "film": "hero", "case_keys": ["chalet", "smartcare", "platform"], "mail_subject": "Full-stack project",
        "en": {
            "title": "Freelance Full-Stack Developer, Remote | Ghaith Mefteh",
            "desc": "Freelance full-stack developer: database, API, web front end and mobile app. .NET, Symfony, FastAPI, Angular, React, Flutter. Remote from UTC+1.",
            "crumb": "Full-stack", "service": "Full-stack web and mobile development",
            "h1": "A freelance full-stack developer who builds the whole feature",
            "answer": "I take a feature from the database to the screen: the schema, the API, the web front end and the mobile app, deployed and tested. Technical director at AzertyUI leading a team of four, with apps used by 2,000+ fans and 3,000+ patients.",
            "what_h": "What I build",
            "what": ["Web applications with Angular or React in front of a .NET, Symfony or FastAPI backend",
                     "Mobile apps in Flutter, released to the App Store and Google Play",
                     "REST APIs and microservices, with the tests and CI pipeline that keep them safe to change",
                     "Rebuilds of slow or ageing products, migrated while the business keeps running",
                     "The infrastructure under them: Docker, GitLab CI or GitHub Actions, AWS, monitoring"],
            "proof_h": "Products I have shipped end to end",
            "how_h": "How a project runs",
            "faq": [("Do you work on the frontend or the backend?", "Both, and the database under them. Most of my projects needed the whole path, and owning it end to end is where I am most useful."),
                    ("Can you join an existing team and codebase?", "Yes. I review every pull request on a team of four, and rebuilt a legacy marketplace while it was still in production.")],
        },
        "fr": {
            "title": "Développeur full-stack freelance à distance | Ghaith Mefteh",
            "desc": "Développeur full-stack freelance : base de données, API, front web et application mobile. .NET, Symfony, FastAPI, Angular, React, Flutter. UTC+1.",
            "crumb": "Full-stack", "service": "Développement web et mobile full-stack",
            "h1": "Un développeur full-stack freelance qui construit la fonctionnalité entière",
            "answer": "Je mène une fonctionnalité de la base de données jusqu'à l'écran : le schéma, l'API, le front web et l'application mobile, déployés et testés. Directeur technique chez AzertyUI à la tête d'une équipe de quatre, avec des applications utilisées par +2 000 supporters et +3 000 patients.",
            "what_h": "Ce que je construis",
            "what": ["Des applications web en Angular ou React devant un backend .NET, Symfony ou FastAPI",
                     "Des applications mobiles Flutter, publiées sur l'App Store et Google Play",
                     "Des API REST et des microservices, avec les tests et la CI qui permettent de les faire évoluer sans risque",
                     "La refonte de produits lents ou vieillissants, migrés pendant que l'activité continue",
                     "L'infrastructure en dessous : Docker, GitLab CI ou GitHub Actions, AWS, supervision"],
            "proof_h": "Des produits livrés de bout en bout",
            "how_h": "Comment se déroule un projet",
            "faq": [("Vous travaillez sur le front ou le back ?", "Les deux, et la base de données en dessous. La plupart de mes projets demandaient tout le chemin, et c'est en le portant de bout en bout que je suis le plus utile."),
                    ("Pouvez-vous rejoindre une équipe et un code existants ?", "Oui. Je relis chaque pull request d'une équipe de quatre, et j'ai refondu une place de marché legacy encore en production.")],
        },
    },
    "flutter": {
        "film": "soc", "case_keys": ["soc", "smartcare"], "mail_subject": "Flutter app project",
        "en": {
            "title": "Freelance Flutter Developer, iOS & Android | Ghaith Mefteh",
            "desc": "Freelance Flutter developer shipping to the App Store and Google Play: SOC Rugby (2,000+ fans, 99.8% crash-free), SmartCare (3,000+ patients).",
            "crumb": "Flutter", "service": "Flutter mobile app development",
            "h1": "A freelance Flutter developer who ships to both stores",
            "answer": "I build Flutter apps from the Figma design to the App Store and Google Play, and I can write the API behind them too. SOC Rugby runs at 99.8% crash-free sessions for 2,000+ fans; SmartCare serves 40+ doctors and 3,000+ patients.",
            "what_h": "What I build",
            "what": ["iOS and Android apps in Flutter and Dart, from your Figma design, screen by screen",
                     "State with GetX or Provider, offline data with SQLite or Hive, widget and integration tests, iOS home-screen widgets in SwiftUI",
                     "Push notifications, real-time messaging, maps, Google Sign-In and QR scanning",
                     "Releases end to end: Codemagic CI/CD, signing, provisioning, Xcode builds and store review",
                     "The backend when you need one: FastAPI or Symfony, MongoDB or MySQL, on AWS"],
            "proof_h": "Flutter apps in production",
            "how_h": "How a project runs",
            "faq": [("Do you handle the App Store and Google Play releases?", "Yes, end to end: certificates, provisioning profiles, Xcode builds, Codemagic pipelines and store review, with Sentry watching production."),
                    ("Can you build the backend as well?", "Yes. For SmartCare I wrote the FastAPI backend on MongoDB, deployed to AWS with GitHub Actions, alongside the Flutter app.")],
        },
        "fr": {
            "title": "Développeur Flutter freelance iOS, Android | Ghaith Mefteh",
            "desc": "Développeur Flutter freelance, publié sur l'App Store et Google Play : SOC Rugby (+2 000 supporters, 99,8 % sans crash), SmartCare (+3 000 patients).",
            "crumb": "Flutter", "service": "Développement d'applications mobiles Flutter",
            "h1": "Un développeur Flutter freelance qui publie sur les deux stores",
            "answer": "Je construis des applications Flutter de la maquette Figma jusqu'à l'App Store et Google Play, et je peux aussi écrire l'API derrière. SOC Rugby tourne à 99,8 % de sessions sans crash pour +2 000 supporters ; SmartCare sert +40 médecins et +3 000 patients.",
            "what_h": "Ce que je construis",
            "what": ["Des applications iOS et Android en Flutter et Dart, depuis votre maquette Figma, écran par écran",
                     "L'état avec GetX ou Provider, les données hors ligne avec SQLite ou Hive, des tests de widgets et d'intégration, des widgets d'écran d'accueil iOS en SwiftUI",
                     "Notifications push, messagerie en temps réel, cartes, connexion Google et lecture de QR codes",
                     "Les publications de bout en bout : CI/CD Codemagic, signature, provisioning, builds Xcode et validation des stores",
                     "Le backend si vous en avez besoin : FastAPI ou Symfony, MongoDB ou MySQL, sur AWS"],
            "proof_h": "Des applications Flutter en production",
            "how_h": "Comment se déroule un projet",
            "faq": [("Vous gérez les publications App Store et Google Play ?", "Oui, de bout en bout : certificats, profils de provisioning, builds Xcode, pipelines Codemagic et validation des stores, avec Sentry pour surveiller la production."),
                    ("Pouvez-vous aussi construire le backend ?", "Oui. Pour SmartCare, j'ai écrit le backend FastAPI sur MongoDB, déployé sur AWS avec GitHub Actions, en même temps que l'application Flutter.")],
        },
    },
    "symfony": {
        "film": "chalet", "case_keys": ["chalet"], "mail_subject": "Symfony project",
        "en": {
            "title": "Freelance Symfony Developer, PHP Rebuilds | Ghaith Mefteh",
            "desc": "Freelance Symfony and PHP developer. Rebuilt chalet-montagne.com (10,000+ chalets): search from 20–50 s to 4–6 s, 390+ tests. Slow PHP sites made fast.",
            "crumb": "Symfony", "service": "Symfony and PHP web development",
            "h1": "A Symfony developer for PHP products that grew slow",
            "answer": "I rebuild and extend Symfony applications without stopping the business behind them. On a 10,000-chalet marketplace, search pages went from 20–50 seconds to 4–6, and a test suite grew from zero to 390+ tests.",
            "what_h": "What I build",
            "what": ["Rebuilds of legacy PHP sites on Symfony and Doctrine, migrated with functional parity as the bar",
                     "Search and listing engines that stay fast: caching, query optimisation, parallel data processing",
                     "Back offices and admin dashboards: owners, revenue tracking, secure impersonation for support",
                     "Integrations: iCal sync, scheduled jobs, automated e-mails and reminders",
                     "Quality that holds: PHPUnit, SonarQube as the gate, GitLab CI/CD and Docker"],
            "proof_h": "The rebuild behind these numbers",
            "how_h": "How a project runs",
            "faq": [("Can you speed up our existing Symfony site without a full rewrite?", "Often, yes. The first step is measuring where the time goes; on chalet-montagne.com it was the search queries and the images, and both were fixed in place."),
                    ("Do you work with legacy PHP that is not on Symfony?", "Yes. chalet-montagne.com started on a legacy stack; the data and business logic were migrated first, while the site kept selling.")],
        },
        "fr": {
            "title": "Développeur Symfony freelance, refonte PHP | Ghaith Mefteh",
            "desc": "Développeur Symfony et PHP freelance. Refonte de chalet-montagne.com (+10 000 chalets) : recherche de 20–50 s à 4–6 s, +390 tests.",
            "crumb": "Symfony", "service": "Développement web Symfony et PHP",
            "h1": "Un développeur Symfony pour les produits PHP devenus lents",
            "answer": "Je refonds et fais évoluer des applications Symfony sans arrêter l'activité qui en dépend. Sur une place de marché de 10 000 chalets, les pages de recherche sont passées de 20–50 secondes à 4–6, et une suite de tests est passée de zéro à plus de 390 tests.",
            "what_h": "Ce que je construis",
            "what": ["La refonte de sites PHP legacy sur Symfony et Doctrine, migrés avec la parité fonctionnelle comme exigence",
                     "Des moteurs de recherche et de listes qui restent rapides : cache, optimisation des requêtes, traitements parallèles",
                     "Des back-offices et tableaux de bord : propriétaires, suivi du chiffre d'affaires, connexion sécurisée « en tant que » pour le support",
                     "Des intégrations : synchronisation iCal, tâches planifiées, e-mails et relances automatiques",
                     "Une qualité qui tient : PHPUnit, SonarQube comme garde-fou, CI/CD GitLab et Docker"],
            "proof_h": "La refonte derrière ces chiffres",
            "how_h": "Comment se déroule un projet",
            "faq": [("Pouvez-vous accélérer notre site Symfony sans tout réécrire ?", "Souvent, oui. La première étape est de mesurer où part le temps ; sur chalet-montagne.com, c'étaient les requêtes de recherche et les images, corrigées sur place."),
                    ("Travaillez-vous sur du PHP legacy hors Symfony ?", "Oui. chalet-montagne.com partait d'une stack legacy ; les données et la logique métier ont été migrées d'abord, pendant que le site continuait de vendre.")],
        },
    },
    "dotnet": {
        "film": "platform", "case_keys": ["platform", "lmobile"], "mail_subject": ".NET backend project",
        "en": {
            "title": ".NET Backend Developer, ASP.NET Core APIs | Ghaith Mefteh",
            "desc": ".NET and ASP.NET Core backend developer: microservices behind an API Gateway, gRPC, Angular in front, Dynamics 365 integrations. Remote, UTC+1.",
            "crumb": ".NET", "service": ".NET and ASP.NET Core backend development",
            "h1": "A .NET backend developer for APIs and microservices",
            "answer": "I design and build ASP.NET Core backends: microservices behind an API Gateway, gRPC between them, and the Angular front end that uses them. I lead the team of four building AzertyUI's company platform this way.",
            "what_h": "What I build",
            "what": ["ASP.NET Core REST APIs and microservices, split by business domain",
                     "API Gateways and service-to-service calls over gRPC",
                     "Angular front ends on top, so the feature ships whole",
                     "Integrations with enterprise systems such as Microsoft Dynamics 365 Business Central",
                     "The operations around them: Docker, CI, server monitoring, VPN access and backups"],
            "proof_h": ".NET in production",
            "how_h": "How a project runs",
            "faq": [("Microservices or a monolith?", "Whichever the product needs. AzertyUI's platform is split into services because its domains (absences, expenses, documents, tickets) change independently; a smaller product is often better as one service."),
                    ("Can you also own the front end?", "Yes. On the AzertyUI platform the front end is Angular 21, built by the same team I lead.")],
        },
        "fr": {
            "title": "Développeur .NET backend, API ASP.NET Core | Ghaith Mefteh",
            "desc": "Développeur backend .NET et ASP.NET Core : microservices derrière une API Gateway, gRPC, Angular devant, intégrations Dynamics 365. UTC+1.",
            "crumb": ".NET", "service": "Développement backend .NET et ASP.NET Core",
            "h1": "Un développeur .NET backend pour vos API et microservices",
            "answer": "Je conçois et construis des backends ASP.NET Core : des microservices derrière une API Gateway, du gRPC entre eux, et le front Angular qui les utilise. C'est ainsi que je dirige l'équipe de quatre qui construit la plateforme interne d'AzertyUI.",
            "what_h": "Ce que je construis",
            "what": ["Des API REST et des microservices ASP.NET Core, découpés par domaine métier",
                     "Des API Gateways et des appels entre services en gRPC",
                     "Les fronts Angular au-dessus, pour livrer la fonctionnalité entière",
                     "Des intégrations avec des systèmes d'entreprise comme Microsoft Dynamics 365 Business Central",
                     "L'exploitation autour : Docker, CI, supervision des serveurs, accès VPN et sauvegardes"],
            "proof_h": ".NET en production",
            "how_h": "Comment se déroule un projet",
            "faq": [("Microservices ou monolithe ?", "Ce dont le produit a besoin. La plateforme d'AzertyUI est découpée en services parce que ses domaines (absences, notes de frais, documents, tickets) évoluent séparément ; un produit plus petit est souvent mieux en un seul service."),
                    ("Pouvez-vous aussi prendre le front ?", "Oui. Sur la plateforme d'AzertyUI, le front est en Angular 21, construit par l'équipe que je dirige.")],
        },
    },
    "hire": {
        "film": "hero", "case_keys": ["platform", "chalet", "soc"], "mail_subject": "Opportunity for Ghaith", "is_hire": True,
        "en": {
            "title": "Hire a Remote Software Engineer (EU) | Ghaith Mefteh",
            "desc": "Full-stack and mobile engineer for remote roles or EU relocation: .NET, Symfony, Angular, React, Flutter. Technical director, UTC+1, EU Blue Card eligible.",
            "crumb": "Hiring", "service": None,
            "h1": "A remote software engineer you can hire, or relocate to the EU",
            "answer": "Full-stack and mobile engineer: 2+ years full-time, plus a year part-time during my degree. First engineering hire at AzertyUI, promoted to technical director, I lead a team of four. Remote from Nabeul at UTC+1, or relocating within the EU.",
            "what_h": "Roles I fit",
            "what": ["Full-stack engineer: .NET or Symfony behind, Angular or React in front",
                     "Backend engineer: ASP.NET Core microservices, Symfony/PHP or Python/FastAPI",
                     "Mobile engineer: Flutter apps shipped to the App Store and Google Play",
                     "Tech lead for a small team: planning, code review standards, releases",
                     "Engineering degree in applied computer science, ENISo Sousse (EUR-ACE accredited, 2024)"],
            "proof_h": "What I have shipped",
            "how_h": "How hiring me works",
            "how": [("Remote, or relocation within the EU", "I work from Nabeul, Tunisia, at UTC+1: a full European day of overlap, plus the US East Coast morning. I am also open to relocating within the EU."),
                    ("Employment or contract", "Employment through an employer of record, or a contractor agreement. Tell me what your company uses."),
                    ("A start date agreed for the role", "CVs in English and French are on the CV page, in full-stack and mobile versions.")],
            "faq": [("Do you need a work permit?", "Tunisian citizen: no permit needed for remote work; needs an EU work permit for on-site roles (EU Blue Card eligible)."),
                    ("What do your colleagues and clients say?", "Three recommendations are on my LinkedIn profile and quoted word for word on the portfolio, from the client of chalet-montagne.com, a SmartCare project manager and an AzertyUI teammate.")],
        },
        "fr": {
            "title": "Recruter un ingénieur logiciel à distance | Ghaith Mefteh",
            "desc": "Ingénieur full-stack et mobile, en télétravail ou mobilité UE : .NET, Symfony, Angular, React, Flutter. Directeur technique, UTC+1, éligible Carte bleue UE.",
            "crumb": "Recrutement", "service": None,
            "h1": "Un ingénieur logiciel à recruter, à distance ou avec mobilité dans l'UE",
            "answer": "Ingénieur full-stack et mobile : plus de 2 ans à temps plein, plus un an à temps partiel pendant mes études. Premier ingénieur recruté chez AzertyUI, promu directeur technique, je dirige une équipe de quatre. En télétravail depuis Nabeul en UTC+1, ou avec mobilité dans l'UE.",
            "what_h": "Les postes qui me correspondent",
            "what": ["Ingénieur full-stack : .NET ou Symfony derrière, Angular ou React devant",
                     "Ingénieur backend : microservices ASP.NET Core, Symfony/PHP ou Python/FastAPI",
                     "Ingénieur mobile : applications Flutter publiées sur l'App Store et Google Play",
                     "Lead technique d'une petite équipe : planification, standards de revue de code, mises en production",
                     "Diplôme d'ingénieur en informatique appliquée, ENISo Sousse (accrédité EUR-ACE, 2024)"],
            "proof_h": "Ce que j'ai livré",
            "how_h": "Comment me recruter",
            "how": [("Télétravail, ou mobilité dans l'UE", "Je travaille depuis Nabeul, en Tunisie, en UTC+1 : une journée européenne entière en commun, plus la matinée de la côte Est américaine. Je suis aussi ouvert à une mobilité dans l'UE."),
                    ("Salariat ou contrat", "Un emploi via une société de portage (employer of record), ou un contrat de prestation. Dites-moi ce que votre entreprise utilise."),
                    ("Une date de début convenue pour le poste", "Les CV en français et en anglais sont sur la page CV, en versions full-stack et mobile.")],
            "faq": [("Avez-vous besoin d'un permis de travail ?", "Nationalité tunisienne : aucun permis requis en télétravail ; permis de travail UE nécessaire pour un poste sur site (éligible Carte bleue européenne)."),
                    ("Que disent vos collègues et clients ?", "Trois recommandations figurent sur mon profil LinkedIn et sont citées mot pour mot sur le portfolio : le client de chalet-montagne.com, un chef de projet SmartCare et un collègue d'AzertyUI.")],
        },
    },
}


# ------------------------------------------------------------------ template
e = html.escape


def url(key, lang):
    return SITE + PATHS[key][lang]


def jsonld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"


def schema(key, lang, c, faq):
    u, ui = url(key, lang), UI[lang]
    crumbs = [{"@type": "ListItem", "position": 1, "name": ui["crumb_home"], "item": SITE + ui["home"]}]
    if key != "hire":
        crumbs.append({"@type": "ListItem", "position": 2, "name": ui["crumb_services"], "item": SITE + ui["home"] + "#hire"})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": c["crumb"], "item": u})
    graph = [
        {"@type": "WebPage", "@id": u, "url": u, "name": c["title"], "description": c["desc"], "inLanguage": lang,
         "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": PERSON}, "dateModified": TODAY},
        {"@type": "BreadcrumbList", "itemListElement": crumbs},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]
    if c["service"]:
        graph.append({"@type": "Service", "name": c["service"], "serviceType": c["service"], "url": u,
                      "provider": {"@id": PERSON}, "availableLanguage": ["en", "fr"],
                      "areaServed": [{"@type": "Place", "name": "Europe"}, {"@type": "Country", "name": "France"},
                                     {"@type": "Country", "name": "Tunisia"}, {"@type": "Place", "name": "Worldwide (remote)"}]})
    return jsonld({"@context": "https://schema.org", "@graph": graph})


def case_card(k, lang, ui):
    cs = CASES[k]
    title, text, nums, alt = cs[lang]
    src = "/assets/" + cs["img"] + "." + cs.get("ext", "webp")
    return f"""      <article class="pcard">
        <img src="{src}" alt="{e(alt)}" width="{cs['w']}" height="{cs['h']}" loading="lazy">
        <div class="pcard-body">
          <h3>{e(title)}</h3>
          <p>{e(text)}</p>
          <p class="pcard-nums">{e(nums)}</p>
          {f'<a class="pcard-link" href="{ui["home"]}{cs["anchor"]}">{e(ui["see_case"])}</a>' if cs['anchor'] else ''}
        </div>
      </article>"""


def page(key, lang):
    p, c, ui = PAGES[key], PAGES[key][lang], UI[lang]
    other = "fr" if lang == "en" else "en"
    faq = c["faq"] + FAQ_COMMON[lang] if not p.get("is_hire") else c["faq"] + FAQ_COMMON[lang][1:]
    how = c.get("how") or HOW[lang]
    film = p["film"]
    subject = p["mail_subject"].replace(" ", "%20")
    nav = "\n".join(f'    <a href="{h}">{e(t)}</a>' for h, t in ui["nav"])
    crumbs = [f'<a href="{ui["home"]}">{e(ui["crumb_home"])}</a>']
    if key != "hire":
        crumbs.append(f'<a href="{ui["home"]}#hire">{e(ui["crumb_services"])}</a>')
    crumbs.append(f'<span aria-current="page">{e(c["crumb"])}</span>')
    more = "\n".join(f'      <li><a href="{PATHS[k][lang]}">{e(ui["labels"][k])}</a></li>' for k in ORDER if k != key)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<link rel="canonical" href="{url(key, lang)}">
<link rel="alternate" hreflang="{lang}" href="{url(key, lang)}">
<link rel="alternate" hreflang="{other}" href="{url(key, other)}">
<link rel="alternate" hreflang="x-default" href="{url(key, 'en')}">
<meta name="author" content="Ghaith Mefteh">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#2B50E0">
<meta name="color-scheme" content="light dark">
<script>
  (function () {{
    var t;
    try {{ t = localStorage.getItem("gm-theme"); }} catch (e) {{}}
    if (t !== "light" && t !== "dark") t = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", t);
  }})();
</script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ghaith Mefteh">
<meta property="og:locale" content="{ui['locale']}">
<meta property="og:title" content="{e(c['title'])}">
<meta property="og:description" content="{e(c['desc'])}">
<meta property="og:url" content="{url(key, lang)}">
<meta property="og:image" content="{SITE}/assets/og-card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" as="image" href="/assets/motion/{film}.jpg" fetchpriority="high">
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/style.css">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{schema(key, lang, c, faq)}
</head>
<body>

<a class="skip" href="#main">{e(ui['skip'])}</a>

<header class="top">
  <span class="top-progress" aria-hidden="true"></span>
  <a class="mark" href="{ui['home']}">gm<span class="mark-dot">.</span></a>
  <nav aria-label="Site">
{nav}
    <a class="nav-cv" href="{ui['cv']}">CV</a>
    <a class="nav-lang" href="{PATHS[key][other]}" hreflang="{other}" lang="{other}">{ui['other']}</a>
  </nav>
</header>

<section class="hero hero-page">
  <video class="hero-film" muted loop playsinline preload="metadata" poster="/assets/motion/{film}.jpg" aria-hidden="true"><source src="/assets/motion/{film}-m.mp4" type="video/mp4" media="(max-width: 900px)"><source src="/assets/motion/{film}.mp4" type="video/mp4"></video>
  <div class="hero-copy">
    <nav class="crumbs" aria-label="Breadcrumb">{' <span aria-hidden="true">/</span> '.join(crumbs)}</nav>
    <h1>{e(c['h1'])}</h1>
    <p class="hero-lede">{e(c['answer'])}</p>
    <div class="hero-actions">
      <a class="btn btn-solid" href="mailto:{MAIL}?subject={subject}">{e(ui['email_me'])}</a>
      <a class="btn btn-ghost" href="{CAL}" target="_blank" rel="noopener">{e(ui['call'])}</a>
    </div>
    <p class="hero-avail"><span class="avail-dot"></span>{e(ui['avail_hire'] if p.get('is_hire') else ui['avail'])}</p>
  </div>
</section>

<main id="main" class="page">
  <section class="page-block">
    <h2>{e(c['what_h'])}</h2>
    <ul class="page-list">
{chr(10).join('      <li>' + e(x) + '</li>' for x in c['what'])}
    </ul>
  </section>

  <section class="page-block">
    <h2>{e(c['proof_h'])}</h2>
    <div class="pcards">
{chr(10).join(case_card(k, lang, ui) for k in p['case_keys'])}
    </div>
  </section>

  <section class="page-block">
    <h2>{e(c['how_h'])}</h2>
    <ol class="page-steps">
{chr(10).join('      <li><h3>' + e(t) + '</h3><p>' + e(d) + '</p></li>' for t, d in how)}
    </ol>
  </section>

  <section class="page-block">
    <h2>{e(ui['faq_h'])}</h2>
    <div class="faq">
{chr(10).join('      <details><summary>' + e(q) + '</summary><p>' + e(a) + '</p></details>' for q, a in faq)}
    </div>
  </section>

  <section class="page-block">
    <h2>{e(ui['more_h'])}</h2>
    <ul class="svc-links">
{more}
    </ul>
  </section>
</main>

<footer id="contact" class="contact">
  <h2>{e(ui['contact_h'])}</h2>
  <p class="contact-lede">{e(ui['contact_lede'])}</p>
  <div class="contact-links">
    <a class="btn btn-solid" href="mailto:{MAIL}?subject={subject}">{e(ui['email_me'])}</a>
    <a class="btn btn-call btn-cal" href="{CAL}" target="_blank" rel="noopener">{e(ui['call'])}</a>
    <a class="btn btn-ghost" href="{ui['cv']}">{e(ui['read_cv'])}</a>
  </div>
  <p class="contact-meta"><a href="mailto:{MAIL}">{MAIL}</a> · <a href="https://www.linkedin.com/in/ghaith-mefteh-995a18157" rel="me noopener">LinkedIn</a> · <a href="https://github.com/Ghaithmeftah" rel="me noopener">GitHub</a></p>
  <p class="colophon">{e(ui['colophon'])}</p>
</footer>

<div class="dock" aria-hidden="false">
  <a class="btn btn-solid" href="mailto:{MAIL}?subject={subject}">{e(ui['dock_email'])}</a>
  <a class="btn btn-ghost" href="{ui['cv']}">CV</a>
</div>

<script src="/script.js"></script>
</body>
</html>
"""


def main():
    for key in ORDER:
        for lang in ("en", "fr"):
            out = os.path.join(ROOT, PATHS[key][lang].strip("/"), "index.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(page(key, lang))
            print(os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
