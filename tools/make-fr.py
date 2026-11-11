#!/usr/bin/env python3
"""Generate fr/index.html from index.html.

The French page is a real URL rather than a JavaScript toggle, so recruiters can
paste it and search engines can index it. Keeping the translation here instead of
hand-editing a second file means an English edit that has no French counterpart
fails loudly: every pair below must match exactly once.

    python tools/make-fr.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHADI_FR = (
    'Ghaith est une personne assidue et travailleuse, avec qui j’ai eu le plaisir de collaborer. Son sens de l’innovation et son esprit créatif ont été déterminants pour faire passer notre projet à un niveau supérieur, ce qui lui a apporté de la valeur et élargi sa portée. Je recommande vivement Ghaith pour son éthique de travail et sa constance à livrer des résultats.'
)

# ---------------------------------------------------------------- head + paths
HEAD = [
('<html lang="en">', '<html lang="fr">'),

('<title>Ghaith Mefteh, Technical Director | Full-Stack &amp; Flutter</title>',
 '<title>Ghaith Mefteh, Directeur Technique | Full-Stack et Flutter</title>'),

('<meta name="description" content="Full-stack and Flutter engineer, Technical Director at AzertyUI leading a team of 4. .NET, Symfony, Angular, Flutter. Remote or EU relocation.">',
 '<meta name="description" content="Ingénieur full-stack et Flutter, Directeur Technique chez AzertyUI, à la tête d\'une équipe de 4. .NET, Symfony, Angular, Flutter. Télétravail ou UE.">'),

('<link rel="canonical" href="https://ghaithmeftah.github.io/">',
 '<link rel="canonical" href="https://ghaithmeftah.github.io/fr/">'),

('<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="fr_FR">'),

('<meta property="og:title" content="Ghaith Mefteh — Full-Stack and Mobile Engineer">',
 '<meta property="og:title" content="Ghaith Mefteh — Ingénieur full-stack et mobile">'),

('<meta property="og:description" content=".NET · Symfony · Angular · Flutter. Full-stack and mobile engineer, Technical Director at AzertyUI leading a team of 4. Open to remote roles and EU relocation.">',
 '<meta property="og:description" content=".NET · Symfony · Angular · Flutter. Ingénieur full-stack et mobile, Directeur Technique chez AzertyUI à la tête d\'une équipe de 4. Ouvert au télétravail et à une mobilité dans l\'UE.">'),

('<meta property="og:url" content="https://ghaithmeftah.github.io/">',
 '<meta property="og:url" content="https://ghaithmeftah.github.io/fr/">'),

('<meta name="twitter:title" content="Ghaith Mefteh — Full-Stack and Mobile Engineer">',
 '<meta name="twitter:title" content="Ghaith Mefteh — Ingénieur full-stack et mobile">'),

('<meta name="twitter:description" content=".NET · Symfony · Angular · Flutter. Full-stack and mobile engineer, Technical Director. Open to remote roles and EU relocation.">',
 '<meta name="twitter:description" content=".NET · Symfony · Angular · Flutter. Ingénieur full-stack et mobile, Directeur Technique. Ouvert au télétravail et à une mobilité dans l\'UE.">'),

('<meta property="og:image:alt" content="Ghaith Mefteh — full-stack and mobile engineer. Symfony, FastAPI, Flutter.">',
 '<meta property="og:image:alt" content="Ghaith Mefteh — ingénieur full-stack et mobile. Symfony, FastAPI, Flutter.">'),
]

BODY = [
# ---- the CV download buttons (hire lane, contact) ----
('<a class="btn btn-solid" href="cv.html">Read the CV</a>\n        <a class="btn btn-ghost btn-dl" href="assets/Ghaith_Mefteh_Resume_FullStack.pdf" download>CV · full-stack (PDF)</a>\n        <a class="btn btn-ghost btn-dl" href="assets/Ghaith_Mefteh_Resume_Mobile.pdf" download>CV · mobile (PDF)</a>',
 '<a class="btn btn-solid" href="cv.html">Lire le CV</a>\n        <a class="btn btn-ghost btn-dl" href="../assets/Ghaith_Mefteh_CV_FullStack_FR.pdf" download>CV · full-stack (PDF)</a>\n        <a class="btn btn-ghost btn-dl" href="../assets/Ghaith_Mefteh_CV_Mobile_FR.pdf" download>CV · mobile (PDF)</a>'),
('<a class="btn btn-ghost btn-dl" href="assets/Ghaith_Mefteh_Resume_FullStack.pdf" download>CV · full-stack (PDF)</a>\n    <a class="btn btn-ghost btn-dl" href="assets/Ghaith_Mefteh_Resume_Mobile.pdf" download>CV · mobile (PDF)</a>',
 '<a class="btn btn-ghost btn-dl" href="../assets/Ghaith_Mefteh_CV_FullStack_FR.pdf" download>CV · full-stack (PDF)</a>\n    <a class="btn btn-ghost btn-dl" href="../assets/Ghaith_Mefteh_CV_Mobile_FR.pdf" download>CV · mobile (PDF)</a>'),

# ---- recruiter-brief fixes: the promotion, work authorization, more work ----
('<p class="work-more">Also at AzertyUI: the company\'s management platform on .NET microservices, and before that an L-Mobile warehouse terminal on Dynamics 365. Both are on <a href="services/dotnet/">the .NET page</a>.</p>',
 '<p class="work-more">Aussi chez AzertyUI : la plateforme de gestion de l\'entreprise en microservices .NET, et avant cela un terminal d\'entrepôt L-Mobile sur Dynamics 365. Les deux sont sur <a href="services/dotnet/">la page .NET</a>.</p>'),
('''    <li>
      <p class="tl-when">Jan 2026 — now</p>''',
 '''    <li>
      <p class="tl-when">2 — 10 nov. 2026</p>
      <div>
        <h3>Mission d'une semaine pour Alpilink Groupe, via AzertyUI</h3>
        <p>Développement d'une roue de jeu pour 10&nbsp;000+ utilisateurs, testée en charge avec un simulateur et mise en production. J'ai aussi trouvé et corrigé une faille de sécurité hors du périmètre de la tâche, sur sa propre branche, envoyée au responsable technique pour relecture et fusion. <a href="#case-alpilink">Détails</a></p>
      </div>
    </li>
    <li>
      <p class="tl-when">janv. 2026 — aujourd'hui</p>'''),
("<p>Promoted from first engineering hire. I lead a team of four engineers, review every pull request and report to the CEO. Led the chalet-montagne.com rebuild to delivery in July 2026; since August 2026, the company's management platform on .NET microservices, plus its server monitoring.</p>",
 "<p>Promu après avoir été le premier ingénieur recruté. Je dirige une équipe de quatre ingénieurs, je relis chaque pull request et je suis rattaché au CEO. J'ai mené la refonte de chalet-montagne.com jusqu'à sa livraison en juillet 2026 ; depuis août 2026, la plateforme de gestion de l'entreprise en microservices .NET, et la supervision de ses serveurs.</p>"),
('<p class="tl-when">Aug 2024 — Dec 2025</p>',
 '<p class="tl-when">août 2024 — déc. 2025</p>'),
('<h3>Software engineer, first engineering hire, AzertyUI</h3>',
 '<h3>Ingénieur logiciel, premier ingénieur recruté, AzertyUI</h3>'),
('<p>Joined as the first engineer. Built SOC Rugby solo and shipped it to both stores, then built the core of the chalet-montagne.com rebuild on Symfony.</p>',
 "<p>Arrivé comme premier ingénieur. J'ai développé seul SOC Rugby et l'ai publiée sur les deux stores, puis développé le cœur de la refonte de chalet-montagne.com sur Symfony.</p>"),
('<dt>Work authorization</dt>\n          <dd>Tunisian citizen: no permit needed for remote work; needs an EU work permit for on-site roles (EU Blue Card eligible)</dd>',
 '<dt>Autorisation de travail</dt>\n          <dd>Nationalité tunisienne : aucun permis requis en télétravail ; permis de travail UE nécessaire pour un poste sur site (éligible Carte bleue européenne)</dd>'),

# ---- services: links to the landing pages (tools/make-pages.py) and their schema ----
('<script type="application/ld+json">\n{\n "@context": "https://schema.org",\n "@type": "ProfessionalService",\n "@id": "https://ghaithmeftah.github.io/#services",\n "name": "Ghaith Mefteh, full-stack and mobile software engineering",\n "url": "https://ghaithmeftah.github.io/",\n "image": "https://ghaithmeftah.github.io/assets/og-card.png",\n "email": "ghaithmeftah@gmail.com",\n "telephone": "+21653324763",\n "founder": {\n  "@id": "https://ghaithmeftah.github.io/#ghaith"\n },\n "address": {\n  "@type": "PostalAddress",\n  "addressLocality": "Nabeul",\n  "addressCountry": "TN"\n },\n "areaServed": [\n  {\n   "@type": "Place",\n   "name": "Europe"\n  },\n  {\n   "@type": "Country",\n   "name": "France"\n  },\n  {\n   "@type": "Country",\n   "name": "Tunisia"\n  },\n  {\n   "@type": "Place",\n   "name": "Worldwide (remote)"\n  }\n ],\n "availableLanguage": [\n  "en",\n  "fr",\n  "de"\n ],\n "hasOfferCatalog": {\n  "@type": "OfferCatalog",\n  "name": "Software engineering services",\n  "itemListElement": [\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Full-stack web and mobile development",\n     "url": "https://ghaithmeftah.github.io/services/full-stack/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Flutter mobile app development",\n     "url": "https://ghaithmeftah.github.io/services/flutter/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Symfony and PHP web development",\n     "url": "https://ghaithmeftah.github.io/services/symfony/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": ".NET and ASP.NET Core backend development",\n     "url": "https://ghaithmeftah.github.io/services/dotnet/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   }\n  ]\n }\n}\n</script>\n',
 '<script type="application/ld+json">\n{\n "@context": "https://schema.org",\n "@type": "ProfessionalService",\n "@id": "https://ghaithmeftah.github.io/#services",\n "name": "Ghaith Mefteh, ingénierie logicielle full-stack et mobile",\n "url": "https://ghaithmeftah.github.io/fr/",\n "image": "https://ghaithmeftah.github.io/assets/og-card.png",\n "email": "ghaithmeftah@gmail.com",\n "telephone": "+21653324763",\n "founder": {\n  "@id": "https://ghaithmeftah.github.io/#ghaith"\n },\n "address": {\n  "@type": "PostalAddress",\n  "addressLocality": "Nabeul",\n  "addressCountry": "TN"\n },\n "areaServed": [\n  {\n   "@type": "Place",\n   "name": "Europe"\n  },\n  {\n   "@type": "Country",\n   "name": "France"\n  },\n  {\n   "@type": "Country",\n   "name": "Tunisie"\n  },\n  {\n   "@type": "Place",\n   "name": "Monde entier (à distance)"\n  }\n ],\n "availableLanguage": [\n  "en",\n  "fr",\n  "de"\n ],\n "hasOfferCatalog": {\n  "@type": "OfferCatalog",\n  "name": "Services d\'ingénierie logicielle",\n  "itemListElement": [\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Développement web et mobile full-stack",\n     "url": "https://ghaithmeftah.github.io/fr/services/full-stack/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Développement d\'applications mobiles Flutter",\n     "url": "https://ghaithmeftah.github.io/fr/services/flutter/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Développement web Symfony et PHP",\n     "url": "https://ghaithmeftah.github.io/fr/services/symfony/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   },\n   {\n    "@type": "Offer",\n    "itemOffered": {\n     "@type": "Service",\n     "name": "Développement backend .NET et ASP.NET Core",\n     "url": "https://ghaithmeftah.github.io/fr/services/dotnet/",\n     "provider": {\n      "@id": "https://ghaithmeftah.github.io/#ghaith"\n     }\n    }\n   }\n  ]\n }\n}\n</script>\n'),
('<h3 id="svc-h">Freelance projects</h3>',
 '<h3 id="svc-h">Projets en freelance</h3>'),
('<li><a href="services/full-stack/">Full-stack freelance</a></li>',
 '<li><a href="services/full-stack/">Full-stack en freelance</a></li>'),
('<li><a href="services/flutter/">Flutter mobile apps</a></li>',
 '<li><a href="services/flutter/">Applications mobiles Flutter</a></li>'),
('<li><a href="services/symfony/">Symfony and PHP web</a></li>',
 '<li><a href="services/symfony/">Web Symfony et PHP</a></li>'),
('<li><a href="services/dotnet/">.NET backends and APIs</a></li>',
 '<li><a href="services/dotnet/">Backends et API .NET</a></li>'),
('<li><a href="hire/">Hiring a remote engineer</a></li>',
 '<li><a href="recrutement/">Recruter un ingénieur à distance</a></li>'),

# ---- header / nav ----
('<a class="skip" href="#work">Skip to work</a>', '<a class="skip" href="#work">Aller aux projets</a>'),
('<nav aria-label="Site">', '<nav aria-label="Site">'),
('<a href="#work">Work</a>', '<a href="#work">Projets</a>'),
('<a href="#path">Path</a>', '<a href="#path">Parcours</a>'),
('<a href="#hire">Hire me</a>', '<a href="#hire">Me recruter</a>'),
('<a class="nav-cv" href="cv.html">CV</a>', '<a class="nav-cv" href="cv.html">CV</a>'),
('<a class="nav-lang" href="fr/" hreflang="fr" lang="fr">FR</a>',
 '<a class="nav-lang" href="../" hreflang="en" lang="en">EN</a>'),

# ---- hero ----
('<span>Ghaith Mefteh — technical director at AzertyUI · Nabeul, Tunisia · remote or relocating in the EU</span>',
 '<span>Ghaith Mefteh — directeur technique chez AzertyUI · Nabeul, Tunisie · télétravail ou mobilité dans l\'UE</span>'),
('<h1>I build the whole<br>request<span class="accent">.</span></h1>',
 '<h1>Je construis toute<br>la requête<span class="accent">.</span></h1>'),
('      Full-stack and mobile engineer, 2+ years full-time plus a year part-time during my degree,\n      now Technical Director leading a team of four. I own features from the screen to the\n      database and ship them with tests and numbers: .NET&nbsp;and Symfony behind, Angular and\n      React in front, Flutter on both stores.',
 "      Ingénieur full-stack et mobile, plus de 2 ans à temps plein et un an à temps partiel pendant mes\n      études, aujourd'hui Directeur Technique à la tête d'une équipe de quatre. Je porte une fonctionnalité\n      de l'écran à la base de données, et je la livre avec des tests et des chiffres : .NET&nbsp;et Symfony\n      derrière, Angular et React devant, Flutter sur les deux stores."),
('      Open to remote roles and EU relocation · answers within the day',
 "      Ouvert au télétravail et à une mobilité dans l'UE · réponse dans la journée"),
('<a class="btn btn-solid" href="#work">See the work</a>', '<a class="btn btn-solid" href="#work">Voir les projets</a>'),
('<a class="btn btn-ghost" href="cv.html">Read the CV</a>', '<a class="btn btn-ghost" href="cv.html">Lire le CV</a>'),
('href="mailto:ghaithmeftah@gmail.com?subject=Opportunity%20for%20Ghaith">ghaithmeftah@gmail.com</a>',
 'href="mailto:ghaithmeftah@gmail.com?subject=Opportunit%C3%A9%20pour%20Ghaith">ghaithmeftah@gmail.com</a>'),

# ---- proof ----
('    Results: on a marketplace of <em><span data-count="10000">10,000</span>+ chalets</em>,\n    search pages went from <em>20–50&nbsp;s to 4–6&nbsp;s</em> behind a test suite grown to\n    <em><span data-count="390">390</span>+ tests</em>; a Flutter app at\n    <em><span data-count="99.8" data-decimals="1">99.8</span>% crash-free</em> sessions for\n    <em><span data-count="2000">2,000</span>+ fans</em>; a health app used by\n    <em><span data-count="3000">3,000</span>+ patients</em>; and a wheel game built for\n    <em><span data-count="10000">10,000</span>+ users</em>, load-tested and live within a week.',
 '    Résultats : sur une place de marché de <em>+<span data-count="10000">10&nbsp;000</span> chalets</em>,\n    des pages de recherche passées de <em>20–50&nbsp;s à 4–6&nbsp;s</em> derrière une suite portée à\n    <em>+<span data-count="390">390</span> tests</em> ; une application Flutter à\n    <em><span data-count="99.8" data-decimals="1">99,8</span>&nbsp;% de sessions sans crash</em> pour\n    <em>+<span data-count="2000">2&nbsp;000</span> supporters</em> ; une application de santé utilisée par\n    <em>+<span data-count="3000">3&nbsp;000</span> patients</em> ; et une roue de jeu conçue pour\n    <em>+<span data-count="10000">10&nbsp;000</span> utilisateurs</em>, testée en charge et en ligne en une semaine.'),

# ---- trust strip ----
('<section class="clients" aria-label="Organizations whose software I have shipped">',
 '<section class="clients" aria-label="Organisations pour lesquelles j\'ai livré des logiciels">'),
('<p class="clients-label">Shipped for</p>', '<p class="clients-label">Livré pour</p>'),

# ---- at a glance ----
('<h2 id="glance-h">At a glance</h2>', '<h2 id="glance-h">En bref</h2>'),
('<dt>Role</dt>', '<dt>Poste</dt>'),
('<dd>Full-stack and mobile software engineer, technical director at AzertyUI</dd>',
 '<dd>Ingénieur logiciel full-stack et mobile, directeur technique chez AzertyUI</dd>'),
('<dt>Experience</dt>', '<dt>Expérience</dt>'),
('<dd>2+ years full-time, plus a year part-time during my degree · leading a team of 4 since January 2026</dd>',
 "<dd>Plus de 2 ans à temps plein, plus un an à temps partiel pendant mes études · à la tête d'une équipe de 4 depuis janvier 2026</dd>"),
('<dt>Data</dt>', '<dt>Données</dt>'),
('<dt>Beyond code</dt>', '<dt>Hors du code</dt>'),
('<dd>Treasurer, IEEE IAS student branch at ENISo (2022–2023)</dd>',
 "<dd>Trésorier, branche étudiante IEEE IAS de l'ENISo (2022–2023)</dd>"),
('<dt>Frontend</dt>', '<dt>Frontend</dt>'),
('<dd>Flutter · Dart · SwiftUI · GetX · Provider, shipped to the App Store and Google Play</dd>',
 '<dd>Flutter · Dart · SwiftUI · GetX · Provider, publié sur l\'App Store et Google Play</dd>'),
('<dt>Education</dt>', '<dt>Formation</dt>'),
("<dd>Engineering degree, ENISo Sousse (EUR-ACE, 2024) · summer exchange at Murang'a University of Technology, Kenya</dd>",
 "<dd>Diplôme d'ingénieur, ENISo Sousse (EUR-ACE, 2024) · échange d'été à Murang'a University of Technology, Kenya</dd>"),
('''<dt>Languages</dt>
      <dd>French (B2) · English (B2, TOEIC) · German (B1)</dd>''',
 '''<dt>Langues</dt>
      <dd>Français (B2) · Anglais (B2, TOEIC) · Allemand (B1)</dd>'''),
('<dt>Based</dt>', '<dt>Basé à</dt>'),
('<dd>Nabeul, Tunisia (CET / UTC+1) · open to relocation in the EU</dd>',
 '<dd>Nabeul, Tunisie (CET / UTC+1) · ouvert à une mobilité dans l\'UE</dd>'),
('<dt>Available for</dt>', '<dt>Disponible pour</dt>'),
('<dd>Remote roles, or on-site in the EU</dd>',
 "<dd>Postes en télétravail, ou sur site dans l'UE</dd>"),

# ---- work ----
('<h2>Selected work</h2>', '<h2>Projets sélectionnés</h2>'),
('<p class="case-role">Software engineer, then technical director · core built solo, then a team of 4 led · AzertyUI · Apr 2025 – Jul 2026</p>',
 '<p class="case-role">Ingénieur logiciel, puis directeur technique · cœur développé seul, puis équipe de 4 dirigée · AzertyUI · avr. 2025 – juil. 2026</p>'),
('        A French ski-chalet rental marketplace listing 10,000+ chalets, on a legacy stack where a\n        search page could take 50 seconds to render. I built the core of the Symfony rebuild solo\n        from April 2025, then led a team of four through the rest of it until delivery in July 2026.\n      </p>\n      <p>\n        The site kept selling the whole time, so the legacy data and the business logic moved\n        first, with functional parity as the bar. Then we rewrote the search and listing engine\n        behind caching, query optimization and parallelized data processing, and images became\n        on-demand WebP served in several sizes. The code follows SOLID with SonarQube as the\n        gate, and ships through GitLab CI/CD, Docker Compose and Apache2.',
 "        Une marketplace française de location de chalets au ski, plus de 10&nbsp;000 chalets en\n        ligne, sur une stack héritée où une page de recherche pouvait mettre 50 secondes à\n        s'afficher. J'ai développé seul le cœur de la refonte Symfony à partir d'avril 2025, puis\n        dirigé une équipe de quatre jusqu'à la livraison en juillet 2026.\n      </p>\n      <p>\n        Le site a continué de vendre pendant toute la refonte : les données et les règles métier\n        sont passées en premier, à parité fonctionnelle. Puis nous avons réécrit le moteur de\n        recherche et de listing derrière du cache, de l'optimisation de requêtes et du traitement\n        parallélisé, et les images sont devenues du WebP à la demande, servi en plusieurs tailles.\n        Le code suit SOLID avec SonarQube comme garde-fou, et part en production via GitLab CI/CD,\n        Docker Compose et Apache2."),
('''        Around the public site we delivered an owner back office, where chalet owners set up
        their listings and availability with automated emails and reminders, and an admin
        dashboard for revenue tracking, blocking users and a secure "log in as this user" for
        support. Seasonal pricing, two-way iCal sync, cron jobs that clean the database and a
        detector for logins from unusual countries complete it.''',
 '''        Autour du site public, nous avons livré un back-office où les propriétaires créent leurs
        annonces et gèrent leurs disponibilités, avec e-mails et rappels automatiques, et un
        tableau de bord admin pour suivre les revenus, bloquer des utilisateurs et « se connecter
        en tant que » cet utilisateur, en toute sécurité, pour le support. Tarification
        saisonnière, synchronisation iCal bidirectionnelle, tâches cron de nettoyage de la base et
        détection des connexions depuis des pays inhabituels complètent l'ensemble.'''),
('''      <p class="case-outcome"><b>Result:</b> search pages load in 4–6 s instead of 20–50 s, image
        bandwidth fell about 60%, and a test suite that did not exist reached 390+ tests behind a
        CI pipeline the team releases through.</p>''',
 '''      <p class="case-outcome"><b>Résultat :</b> les pages de recherche s'affichent en 4–6 s au
        lieu de 20–50 s, la bande passante images a baissé d'environ 60%, et une suite de tests
        inexistante atteint 390+ tests derrière un pipeline CI par lequel l'équipe livre.</p>'''),
('aria-label="Search page load time: before 20 to 50 seconds, after 4 to 6 seconds."',
 'aria-label="Temps de chargement de la page de recherche : avant 20 à 50 secondes, après 4 à 6 secondes."'),
('<p class="widget-title">Search page load time</p>', '<p class="widget-title">Temps de chargement de la recherche</p>'),
('<span class="loadbar-name">before</span>', '<span class="loadbar-name">avant</span>'),
('<span class="loadbar-name">after</span>', '<span class="loadbar-name">après</span>'),
('<p class="widget-foot">plus ~60% less image bandwidth: on-demand WebP, multi-size caching</p>',
 '<p class="widget-foot">et ~60% de bande passante images en moins: WebP à la demande, cache multi-tailles</p>'),
('<p class="widget-title">The site, page by page</p>', '<p class="widget-title">Le site, page par page</p>'),
('<p class="carousel-cap">Accueil — search by destination, dates, travellers</p>',
 '<p class="carousel-cap">Accueil — recherche par destination, dates, voyageurs</p>'),
('<p class="carousel-cap">Locations — filters over the rewritten search engine</p>',
 '<p class="carousel-cap">Locations — filtres sur le moteur de recherche réécrit</p>'),
("<p class=\"carousel-cap\">Détail d'une location — gallery, dispo, contact owner</p>",
 "<p class=\"carousel-cap\">Détail d'une location — galerie, disponibilités, contact propriétaire</p>"),
('<p class="carousel-cap">Assurance annulation — partner-backed cover</p>',
 '<p class="carousel-cap">Assurance annulation — couverture via partenaire</p>'),
("<p class=\"carousel-note\">Some of the site's pages — not all of them.</p>",
 '<p class="carousel-note">Quelques pages du site — pas toutes.</p>'),
('<p class="widget-foot">live at chalet-montagne.com</p>', '<p class="widget-foot">en ligne sur chalet-montagne.com</p>'),
('aria-label="Previous page">‹</button>', 'aria-label="Page précédente">‹</button>'),
('aria-label="Next page">›</button>', 'aria-label="Page suivante">›</button>'),

('<p class="case-role">Software engineer · AzertyUI · built solo, shipped to both stores · Aug 2024 – Mar 2025</p>',
 '<p class="case-role">Ingénieur logiciel · AzertyUI · développée seul, publiée sur les deux stores · août 2024 – mars 2025</p>'),
('        The official app of the Chambéry rugby club: match calendar and reminders, live scores,\n        rankings, in-app messaging and push notifications. Built solo in Flutter with GetX and SQLite,\n        plus an iOS home-screen widget in SwiftUI, and used by 2,000+ fans. They refresh it at full time and it holds.',
 "        L'application officielle du club de rugby de Chambéry : calendrier et rappels des matchs,\n        scores en direct, classements, messagerie et notifications push. Développée seul en Flutter avec\n        GetX et SQLite, plus un widget d'écran d'accueil iOS en SwiftUI, et utilisée par plus de 2&nbsp;000 supporters. Ils la\n        rafraîchissent au coup de sifflet final et elle tient."),
('''        Like every Flutter project I build, it started from a Figma design that I translated
        screen by screen into clean Dart&nbsp;/&nbsp;Flutter widgets. I owned the releases end to
        end: Codemagic CI/CD, signing certificates, provisioning profiles, Xcode builds and store
        review, with Sentry watching production.''',
 '''        Comme sur chacun de mes projets Flutter, tout est parti d'une maquette Figma que j'ai
        traduite écran par écran en widgets Dart&nbsp;/&nbsp;Flutter propres. J'ai porté les
        publications de bout en bout : CI/CD Codemagic, certificats de signature, profils de
        provisionnement, builds Xcode et validation des stores, avec Sentry qui surveille la
        production.'''),
('''      <p class="case-outcome"><b>Shipped:</b> a club with no app now has one on both stores, used by
        2,000+ fans at 99.8% crash-free sessions, and unveiled to its sponsors at the season
        evening below.</p>''',
 '''      <p class="case-outcome"><b>Livré :</b> un club sans application en a désormais une sur les
        deux stores, utilisée par plus de 2&nbsp;000 supporters avec 99,8&nbsp;% de sessions sans
        crash, et dévoilée à ses partenaires lors de la soirée ci-dessous.</p>'''),
('<p class="widget-title">The app, screen by screen</p>', '<p class="widget-title">L\'application, écran par écran</p>'),
('<p class="carousel-cap">Résultats — live scores by matchday</p>',
 '<p class="carousel-cap">Résultats — scores en direct par journée</p>'),
('<p class="carousel-cap">Classement — full league table</p>',
 '<p class="carousel-cap">Classement — tableau complet du championnat</p>'),
('<p class="carousel-cap">Calendrier — matches and club events</p>',
 '<p class="carousel-cap">Calendrier — matches et événements du club</p>'),
('<p class="carousel-cap">Évènements — filterable by date</p>',
 '<p class="carousel-cap">Évènements — filtrables par date</p>'),
("<p class=\"carousel-cap\">Détail d'un événement</p>", "<p class=\"carousel-cap\">Détail d'un événement</p>"),
('<p class="carousel-cap">Billetterie</p>', '<p class="carousel-cap">Billetterie</p>'),
('<p class="widget-foot widget-foot-dark">real screens, real season, shipped to App Store and Google Play</p>',
 '<p class="widget-foot widget-foot-dark">écrans réels, saison réelle, publié sur l\'App Store et Google Play</p>'),
('''        Unveiled by AzertyUI at the SOC Rugby sponsors' evening, Château de Tresserve, Bonport (Chambéry).''',
 '''        Dévoilée par AzertyUI lors de la soirée des partenaires du SOC Rugby, Château de Tresserve, Bonport (Chambéry).'''),

('<p class="case-role">Mobile engineer, part-time, remote, alongside studies · Hope Horizon Health &amp; Care · Jul 2023 – Aug 2024</p>',
 '<p class="case-role">Ingénieur mobile, temps partiel, télétravail, en parallèle des études · Hope Horizon Health &amp; Care · juil. 2023 – août 2024</p>'),
('''        A patient–doctor app for Tunisia, live on Google Play and used by 40+ doctors and 3,000+
        patients: appointment booking and reminders, real-time messaging, push notifications,
        ambulance calls on Google Maps, Google Sign-In, QR code scanning and medical AI features.
        I was the only mobile engineer, and I also wrote the FastAPI backend on MongoDB, deployed
        to AWS with GitHub Actions, and the ReactJS web.''',
 '''        Une application patients–médecins pour la Tunisie, disponible sur Google Play et utilisée
        par plus de 40 médecins et 3&nbsp;000 patients : prise de rendez-vous et rappels, messagerie
        temps réel, notifications push, appels d'ambulance sur Google Maps, Google Sign-In, scan de
        QR codes et fonctions d'IA médicale. J'étais le seul ingénieur mobile, et j'ai aussi écrit
        le backend FastAPI sur MongoDB, déployé sur AWS avec GitHub Actions, et le web ReactJS.'''),
('''        As on every Flutter project I build, the app started as a Figma design and I
        translated it screen by screen into clean, reusable Dart&nbsp;/&nbsp;Flutter widgets,
        with Provider and GetX for state and Hive on the device. I built it part-time, alongside
        my engineering degree.''',
 '''        Comme sur chacun de mes projets Flutter, l'application est partie d'une maquette Figma
        que j'ai traduite écran par écran en widgets Dart&nbsp;/&nbsp;Flutter propres et
        réutilisables, avec Provider et GetX pour l'état et Hive sur l'appareil. Je l'ai
        construite à temps partiel, en parallèle de mon diplôme d'ingénieur.'''),
('''      <p class="case-outcome"><b>One engineer, four deliverables:</b> Android app, web app, API
        and infrastructure, in production for 40+ doctors and 3,000+ patients.</p>''',
 '''      <p class="case-outcome"><b>Un ingénieur, quatre livrables :</b> application Android,
        application web, API et infrastructure, en production pour plus de 40 médecins et
        3&nbsp;000 patients.</p>'''),
('rel="noopener">See SmartCare on Google Play</a>', 'rel="noopener">Voir SmartCare sur Google Play</a>'),
('<p class="widget-title">The Flutter app, screen by screen</p>',
 '<p class="widget-title">L\'application Flutter, écran par écran</p>'),
('<p class="carousel-cap">Accueil — every feature one tap away</p>',
 '<p class="carousel-cap">Accueil — chaque fonction à un geste</p>'),
('<p class="carousel-cap">Doctor profile — book from the next free slot</p>',
 '<p class="carousel-cap">Profil médecin — réserver au prochain créneau libre</p>'),
('<p class="carousel-cap">Request sent — confirmation</p>',
 '<p class="carousel-cap">Demande envoyée — confirmation</p>'),
('<p class="carousel-cap">Call detail — live map and patient info</p>',
 '<p class="carousel-cap">Détail de l\'appel — carte en direct et infos patient</p>'),
('<p class="carousel-cap">Flagged interaction pairs, with dosage and form</p>',
 '<p class="carousel-cap">Paires signalées, avec dosage et forme</p>'),
('<p class="widget-foot">real screens from the Flutter app, in production for patients and doctors</p>',
 '<p class="widget-foot">écrans réels de l\'application Flutter, en production pour patients et médecins</p>'),


# ---- lab ----

# ---- path ----
('<h2>The path so far</h2>', '<h2>Le parcours jusqu\'ici</h2>'),
('<h3>Technical director, AzertyUI</h3>', '<h3>Directeur technique, AzertyUI</h3>'),
('<h3>Engineering degree, ENISo</h3>', '<h3>Diplôme d\'ingénieur, ENISo</h3>'),
("<p>Applied Computer Science (EUR-ACE accredited), National School of Engineers of Sousse. Then a summer exchange at Murang'a University of Technology, Kenya, in July and August 2024, where I designed a React Native app so students could register remotely instead of on paper.</p>",
 "<p>Informatique appliquée (accréditation EUR-ACE), École Nationale d'Ingénieurs de Sousse. Puis un échange d'été à Murang'a University of Technology, au Kenya, en juillet et août 2024, où j'ai conçu une application React Native pour que les étudiants s'inscrivent à distance plutôt que sur papier.</p>"),
("<p class=\"tl-caption\">Murang'a University of Technology, Kenya — summer exchange, 2024</p>",
 "<p class=\"tl-caption\">Murang'a University of Technology, Kenya — échange d'été, 2024</p>"),
('<h3>Mobile engineer, Hope Horizon</h3>', '<h3>Ingénieur mobile, Hope Horizon</h3>'),
('<p>SmartCare, part-time and remote alongside the degree: the only mobile engineer, plus the FastAPI backend and the ReactJS web. 40+ doctors and 3,000+ patients use it.</p>',
 '<p>SmartCare, à temps partiel et à distance, en parallèle du diplôme : seul ingénieur mobile, plus le backend FastAPI et le web ReactJS. Plus de 40 médecins et 3&nbsp;000 patients l\'utilisent.</p>'),

# ---- hire ----
('<h2 id="hire-h">Hiring me</h2>',
 '<h2 id="hire-h">Me recruter</h2>'),
('<p class="lane-kicker">For recruiters and hiring managers</p>',
 '<p class="lane-kicker">Pour les recruteurs et managers</p>'),
('<h3>A remote engineer you can slot in</h3>', '<h3>Un ingénieur à distance, prêt à intégrer</h3>'),
('<dt>Roles I fit</dt>', '<dt>Postes visés</dt>'),
('<dd>Full-stack · backend (.NET, Symfony/PHP or Python/FastAPI) · Flutter mobile · tech lead for a small team</dd>',
 '<dd>Full-stack · backend (.NET, Symfony/PHP ou Python/FastAPI) · mobile Flutter · lead technique d\'une petite équipe</dd>'),
('<dt>Setup</dt>', '<dt>Organisation</dt>'),
('<dd>Remote from Nabeul, Tunisia (UTC+1), or relocating within the EU. A full European day of overlap, plus the US Eastern morning</dd>',
 '<dd>À distance depuis Nabeul, Tunisie (UTC+1), ou en m\'installant dans l\'UE. Une journée européenne entière en commun, plus la matinée US Est</dd>'),
('<dt>Contract</dt>', '<dt>Contrat</dt>'),
('<dd>Employment through an employer of record, or a contractor agreement, tell me what your company uses</dd>',
 '<dd>Salariat via un employer of record, ou contrat de prestation, dites-moi ce que votre entreprise utilise</dd>'),
('<dt>Start</dt>', '<dt>Disponibilité</dt>'),
('<dd>On a date agreed for the role</dd>',
 '<dd>À une date convenue pour le poste</dd>'),
('''<dt>Languages</dt>
          <dd>English (B2, TOEIC) and French for daily work, German B1</dd>''',
 '''<dt>Langues</dt>
          <dd>Français et anglais (B2, TOEIC) au quotidien, allemand B1</dd>'''),
('<p class="hero-now"><b>Latest, 2–10 Nov 2026:</b> shipped a wheel game for 10,000+ users to production in a week, <a href="#case-alpilink">load-tested first</a>. Day to day: AzertyUI\'s company platform with a team of four, .NET microservices and Angular&nbsp;21.</p>',
 '<p class="hero-now"><b>Dernièrement, 2–10 nov. 2026 :</b> une roue de jeu pour 10&nbsp;000+ utilisateurs mise en production en une semaine, <a href="#case-alpilink">testée en charge avant</a>. Au quotidien : la plateforme de gestion d\'AzertyUI avec une équipe de quatre, microservices .NET et Angular&nbsp;21.</p>'),
('<p class="colophon">Hand-built with HTML, CSS and plain JavaScript. No framework, no tracker. Last updated <time datetime="2026-11">November 2026</time>.</p>',
 '<p class="colophon">Fait main en HTML, CSS et JavaScript natif. Aucun framework, aucun traceur. Mis à jour en <time datetime="2026-11">novembre 2026</time>.</p>'),
('<li><b>Promoted from first hire</b><span>software engineer to technical director in 17 months</span></li>',
 "<li><b>Du premier recrutement à la direction technique</b><span>d'ingénieur logiciel à directeur technique en 17 mois</span></li>"),
('<li><b>Tests and CI, not promises</b><span>390+ tests and a pipeline on the last marketplace</span></li>',
 '<li><b>Des tests et de la CI, pas des promesses</b><span>390+ tests et un pipeline sur la dernière marketplace</span></li>'),
('<li><b>Code review as a habit</b><span>I review every pull request on a team of four</span></li>',
 "<li><b>La revue de code comme habitude</b><span>je relis chaque pull request d'une équipe de quatre</span></li>"),
('<li><b>Design to code</b><span>Figma translated screen by screen, not approximated</span></li>',
 '<li><b>De la maquette au code</b><span>Figma traduit écran par écran, pas approximé</span></li>'),
('<li><b>Security beyond the ticket</b><span>found a flaw outside my task, fixed it on its own branch for review</span></li>',
 "<li><b>La sécurité au-delà du ticket</b><span>une faille trouvée hors de ma tâche, corrigée sur sa propre branche pour relecture</span></li>"),

# ---- contact ----
('<p class="avail-badge"><span class="avail-dot"></span>Open to new roles</p>',
 '<p class="avail-badge"><span class="avail-dot"></span>Ouvert à de nouveaux postes</p>'),
("<h2>Let's build the next one</h2>", '<h2>Construisons le prochain</h2>'),
('    Open to remote roles and relocation in the EU: full-stack, backend-leaning, or mobile.\n    Email or call.',
 "    Ouvert au télétravail et à une mobilité dans l'UE : full-stack, orienté backend, ou mobile.\n    Un mail ou un appel."),
('body=Hi%20Ghaith%2C%0A%0AI%20saw%20your%20portfolio%20and%20would%20like%20to%20talk%20about...">Email me</a>',
 'body=Bonjour%20Ghaith%2C%0A%0AJ%27ai%20vu%20votre%20portfolio%20et%20j%27aimerais%20parler%20de...">M\'écrire</a>'),
('<p class="contact-meta">Nabeul, Tunisia (CET) · open to EU relocation · ', '<p class="contact-meta">Nabeul, Tunisie (CET) · mobilité UE possible · '),

# ---- dock ----
('  <a class="btn btn-solid" href="mailto:ghaithmeftah@gmail.com?subject=Opportunity%20for%20Ghaith">Email me</a>',
 '  <a class="btn btn-solid" href="mailto:ghaithmeftah@gmail.com?subject=Opportunit%C3%A9%20pour%20Ghaith">M\'écrire</a>'),
# ---- recommendations band ----
('<a href="#said">Said</a>', '<a href="#said">Avis</a>'),
('<h2 id="says-h">In their words</h2>', '<h2 id="says-h">Ce qu\'ils en disent</h2>'),
('''    <p class="says-lede">Three recommendations from my LinkedIn profile, copied word for word, in
      the language they were written in. <a class="says-verify" href="https://www.linkedin.com/in/ghaith-mefteh-995a18157/details/recommendations/" rel="noopener">Read them on LinkedIn</a></p>''',
 '''    <p class="says-lede">Trois recommandations de mon profil LinkedIn, reprises mot pour mot, dans
      la langue où elles ont été écrites. <a class="says-verify" href="https://www.linkedin.com/in/ghaith-mefteh-995a18157/details/recommendations/" rel="noopener">Les lire sur LinkedIn</a></p>'''),
('<span class="say-role">Founder, ALPIUM</span>',
 '<span class="say-role">G\u00e9rant fondateur, ALPIUM</span>'),
('<span class="say-role">Project manager and software engineer, Hope Horizon</span>',
 '<span class="say-role">Chef de projet et ing\u00e9nieur logiciel, Hope Horizon</span>'),
('<span class="say-role">Software engineer, AzertyUI</span>',
 '<span class="say-role">Ing\u00e9nieur logiciel, AzertyUI</span>'),
('<span class="say-rel">The client · chalet-montagne.com</span>',
 '<span class="say-rel">Le client · chalet-montagne.com</span>'),
('<span class="say-rel">Worked with me on SmartCare</span>',
 '<span class="say-rel">A travaill\u00e9 avec moi sur SmartCare</span>'),
('<span class="say-rel">Same team at AzertyUI</span>',
 '<span class="say-rel">M\u00eame \u00e9quipe chez AzertyUI</span>'),
('<time datetime="2026-01">January 2026</time>', '<time datetime="2026-01">janvier 2026</time>'),

# ---- image alt text ----
('alt="Portrait of Ghaith Mefteh"',
 "alt=\"Portrait de Ghaith Mefteh\""),
('alt="chalet-montagne.com home page, search bar for destination, dates and travellers over a mountain terrace photo"',
 "alt=\"Page d'accueil de chalet-montagne.com : barre de recherche par destination, dates et voyageurs sur une photo de terrasse en montagne\""),
('alt="chalet-montagne.com rentals listing page, filter sidebar for price, capacity and rental type beside a grid of chalet cards with weekly prices"',
 "alt=\"Page des locations de chalet-montagne.com : filtres de prix, capacité et type de location à côté d'une grille de chalets avec les tarifs à la semaine\""),
('alt="chalet-montagne.com rental detail page, photo gallery, check-in and check-out times, contact panel and verified-owner badge"',
 "alt=\"Page de détail d'une location chalet-montagne.com : galerie photo, horaires d'arrivée et de départ, panneau de contact et badge propriétaire vérifié\""),
('alt="chalet-montagne.com cancellation insurance page, hero headline Voyagez l\'esprit plus léger with three guarantee highlights"',
 "alt=\"Page assurance annulation de chalet-montagne.com : titre Voyagez l'esprit plus léger et trois garanties mises en avant\""),
('alt="SOC Chambéry club crest"',
 "alt=\"Blason du SOC Chambéry\""),
('alt="SOC Rugby app, Résultats screen: SENIOR M1 24–0 CS Bourgoin-Jallieu, 21–6 Olympique Marcquois, 45–3 Stade Langonnais"',
 "alt=\"Application SOC Rugby, écran Résultats : SENIOR M1 24–0 CS Bourgoin-Jallieu, 21–6 Olympique Marcquois, 45–3 Stade Langonnais\""),
('alt="SOC Rugby app, Classement screen with SOC Rugby Chambéry top of the table on 61 points"',
 "alt=\"Application SOC Rugby, écran Classement avec le SOC Rugby Chambéry en tête à 61 points\""),
('alt="SOC Rugby app, Calendrier screen showing December 2024 month view with event markers"',
 "alt=\"Application SOC Rugby, écran Calendrier affichant décembre 2024 avec les événements marqués\""),
('alt="SOC Rugby app, Évenements list filtered by date range"',
 "alt=\"Application SOC Rugby, liste des Évènements filtrée par période\""),
('alt="SOC Rugby app, event detail screen for Sample Event02, organiser SOC Rugby"',
 "alt=\"Application SOC Rugby, détail de l'événement Sample Event02, organisé par le SOC Rugby\""),
('alt="SOC Rugby app, Billetterie screen with a Mes billets button"',
 "alt=\"Application SOC Rugby, écran Billetterie avec un bouton Mes billets\""),
('alt="Château de Tresserve façade at night, the venue logo projected on the wall and a SOC Chambéry banner by the entrance"',
 "alt=\"Façade du Château de Tresserve la nuit, le logo du lieu projeté sur le mur et une banderole SOC Chambéry près de l'entrée\""),
('alt="Presentation slide on the venue screen titled Application Partenaires, showing the SOC Rugby partners app welcome screen"',
 "alt=\"Diapositive projetée sur place, intitulée Application Partenaires, montrant l'écran d'accueil de l'application partenaires du SOC Rugby\""),
('alt="Presentation slide crediting the app to NEXTIES and AzertyUI"',
 "alt=\"Diapositive créditant l'application à NEXTIES et AzertyUI\""),
('alt="SmartCare app, Accueil home screen with a grid of feature tiles: global search, medical profile, AI assistance, ambulance call, my doctors, share profile"',
 "alt=\"Application SmartCare, écran Accueil avec une grille de fonctions : recherche globale, dossier médical, assistance IA, appel d'ambulance, mes médecins, partage du profil\""),
('alt="SmartCare app, doctor profile screen with the next free appointment slot"',
 "alt=\"Application SmartCare, fiche d'un médecin avec le prochain créneau libre\""),
('alt="SmartCare app, success dialog confirming the appointment request was sent"',
 "alt=\"Application SmartCare, confirmation que la demande de rendez-vous a bien été envoyée\""),
('alt="SmartCare app, urgent call detail with a Google Map of the patient location, status, and patient information"',
 "alt=\"Application SmartCare, détail d'un appel urgent avec la carte Google du lieu, le statut et les informations du patient\""),
('alt="SmartCare app, drug interaction results listing flagged medicine pairs with dosage and form"',
 "alt=\"Application SmartCare, résultats des interactions listant les paires de médicaments signalées avec dosage et forme\""),
('alt="Ghaith with fellow exchange student and faculty member at the Murang\'a University of Technology monument"',
 "alt=\"Ghaith avec un autre étudiant en échange et un enseignant devant le monument de Murang'a University of Technology\""),
('alt="Murang\'a University of Technology, engineering building"',
 "alt=\"Murang'a University of Technology, bâtiment d'ingénierie\""),
('alt="Murang\'a University of Technology, campus grounds"',
 "alt=\"Murang'a University of Technology, le campus\""),
]

# strings that legitimately appear more than once (both carousels share a caption)
MISSION_FR = """<article id="case-alpilink" class="mission" aria-labelledby="mission-h">
    <div class="mission-head">
      <span class="mission-logo"><img src="assets/alpilink-logo.webp" alt="Alpilink Groupe" width="360" height="154" loading="lazy"></span>
      <div>
        <p class="case-role">Dernière mission chez AzertyUI · 2–10 nov. 2026 · une semaine pour Alpilink Groupe · fonctionnalité de roue de jeu, du développement à la production</p>
        <h3 id="mission-h">Une roue de jeu pour 10&nbsp;000+ utilisateurs, en production après une semaine</h3>
      </div>
    </div>
    <p class="mission-lede">
      Alpilink Groupe est une entreprise française forte de plus de 30 ans d'expérience dans la gestion des flux.
      Dans le cadre de mon travail chez AzertyUI, j'ai passé une semaine, du 2 au 10 novembre 2026, à développer pour eux une fonctionnalité de roue de jeu, que j'ai portée du premier
      commit à la production. Sur une mission aussi courte, pas question de rendre le travail à moitié fini :
      la roue tient sous trafic réel et l'équipe n'hérite d'aucun nettoyage.
    </p>
    <ul class="mission-facts">
      <li><b>10&nbsp;000+</b><span>utilisateurs que la roue est conçue pour servir</span></li>
      <li><b>Testée en charge</b><span>avec un simulateur de trafic avant la mise en ligne</span></li>
      <li><b>En production</b><span>utilisée par de vrais utilisateurs aujourd'hui</span></li>
    </ul>
    <div id="wheel" class="wheel"></div>
    <div class="mission-added">
      <p class="mission-sub">Ce que j'ai apporté au-delà de la tâche</p>
      <ul>
        <li><b>Pensée pour la foule, pas pour une démo.</b> Une fonctionnalité de jeu reçoit beaucoup d'utilisateurs au même instant. J'ai développé la roue pour servir plus de 10&nbsp;000 utilisateurs.</li>
        <li><b>La preuve avant la mise en ligne.</b> Je l'ai testée avec un simulateur qui reproduit ce volume d'utilisateurs avant le lancement. « Ça devrait tenir » n'est pas un résultat de test.</li>
      </ul>
    </div>
    <aside class="mission-sec">
      <p class="mission-sub">Hors du ticket : une faille de sécurité</p>
      <p>
        En travaillant dans le code, j'ai repéré une faille de sécurité que personne ne m'avait demandé de chercher.
        Je ne l'ai pas noyée dans la fonctionnalité : je l'ai corrigée sur sa propre branche et l'ai envoyée au
        responsable technique pour relecture et fusion, afin que le correctif soit jugé seul et que la livraison de
        la fonctionnalité reste propre. Les détails restent privés ; je serai ravi d'expliquer en entretien comment
        je l'ai trouvée et pourquoi j'ai procédé ainsi.
      </p>
    </aside>
  </article>"""

GLOBAL = [
('>Book a 30-min call</a>', '>Réserver un appel de 30 min</a>'),
('<span class="say-src-kind">LinkedIn recommendation</span>', '<span class="say-src-kind">Recommandation LinkedIn</span>'),
('<time datetime="2026-09">September 2026</time>', '<time datetime="2026-09">septembre 2026</time>'),
('aria-label="Next screen">›</button>', 'aria-label="Écran suivant">›</button>'),
('aria-label="Previous screen">‹</button>', 'aria-label="Écran précédent">‹</button>'),
]

PATHS = [
('href="style.css"', 'href="../style.css"'),
('href="fonts.css"', 'href="../fonts.css"'),
('src="script.js"', 'src="../script.js"'),
('href="assets/', 'href="../assets/'),
('src="assets/', 'src="../assets/'),
('poster="assets/', 'poster="../assets/'),
]


# ---------------------------------------------------------------- the CV sheet
CV = [
# the whole CV body, rewritten to the confirmed timeline (recruiter brief)
('<div class="cv-bar">\n  <a class="btn btn-ghost" href="index.html">← Portfolio</a>\n  <a class="btn btn-solid" href="assets/Ghaith_Mefteh_Resume_FullStack.pdf" download>CV · full-stack (PDF)</a>\n  <a class="btn btn-ghost" href="assets/Ghaith_Mefteh_Resume_Mobile.pdf" download>CV · mobile (PDF)</a>\n  <a class="btn btn-ghost" href="fr/cv.html" hreflang="fr" data-lang-switch>Version française</a>\n  <span>The PDFs are one-page, ATS-friendly versions.</span>\n</div>\n\n<main class="sheet">\n\n  <header class="cv-head">\n    <img class="cv-portrait" src="assets/ghaith.webp" alt="Portrait of Ghaith Mefteh" width="83" height="83">\n    <div>\n      <h1 class="cv-name">Ghaith Mefteh<span class="accent">.</span></h1>\n      <p class="cv-role">Full-stack and mobile software engineer · technical director</p>\n      <p class="cv-contact">\n        <span><a href="mailto:ghaithmeftah@gmail.com">ghaithmeftah@gmail.com</a></span>\n        <span><a href="tel:+21653324763">+216 53 32 47 63</a></span>\n        <span>Nabeul, Tunisia · remote, or relocating within the EU</span>\n        <span><a href="https://ghaithmeftah.github.io/">Portfolio</a></span>\n        <span><a href="https://www.linkedin.com/in/ghaith-mefteh-995a18157">LinkedIn</a></span>\n        <span><a href="https://github.com/Ghaithmeftah">GitHub</a></span>\n      </p>\n    </div>\n  </header>\n\n  <div class="cv-main">\n\n    <section class="cv-sec">\n      <h2>Profile</h2>\n      <p class="cv-summary">\n        Full-stack and mobile engineer with 2+ years full-time, plus a year of part-time\n        production work during my degree. First engineering hire at AzertyUI, now technical\n        director leading a team of four. Led a Symfony marketplace rebuild and ships Flutter apps\n        to both stores.\n      </p>\n      <ul class="cv-metrics">\n        <li><b>20–50 s → 4–6 s</b><span>search pages after the chalet-montagne.com rebuild</span></li>\n        <li><b>390+</b><span>tests behind its CI pipeline</span></li>\n        <li><b>99.8%</b><span>crash-free sessions, SOC Rugby app</span></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Experience</h2>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Technical director — AzertyUI</h3>\n          <p class="cv-job-when">Jan 2026 — present</p>\n        </div>\n        <p class="cv-job-org">AzertyUI · Malissard, France · remote · early-stage startup building web and mobile products for French clients</p>\n        <ul>\n          <li>Lead a <b>team of 4 engineers</b>: planning, code review on every pull request, technical decisions and releases; report directly to the CEO.</li>\n          <li><b>Alpilink Groupe</b> (1-week mission, Nov 2026): shipped a wheel game for <b>10,000+ users</b>, load-tested with a simulator; fixed a security flaw found outside the task, on its own branch.</li>\n          <li>Led the <b>chalet-montagne.com</b> rebuild to delivery (Jan – Jul 2026): search pages from <b>20–50 s to 4–6 s</b>, image bandwidth down ~60%, 390+ PHPUnit tests behind GitLab CI/CD.</li>\n          <li>Since Aug 2026, leading the company management platform: <b>.NET microservices</b> behind an API Gateway, gRPC between services, Angular 21; plus the server monitoring dashboard.</li>\n        </ul>\n        <p class="cv-tools">.NET · ASP.NET Core · gRPC · Angular 21 · Symfony · PHPUnit · GitLab CI/CD · Docker</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Software engineer, first engineering hire — AzertyUI</h3>\n          <p class="cv-job-when">Aug 2024 — Dec 2025</p>\n        </div>\n        <p class="cv-job-org">AzertyUI · grew from solo engineer to a team of 4</p>\n        <ul>\n          <li><b>SOC Rugby</b> (Aug 2024 – Mar 2025): built solo and published the Chambéry rugby club\'s Flutter app to the App Store and Google Play, with an iOS home-screen widget in SwiftUI; <b>2,000+ fans</b>, <b>99.8% crash-free</b> sessions.</li>\n          <li><b>chalet-montagne.com</b> (from Apr 2025): built the core of the rebuild solo for a marketplace of 10,000+ ski chalets, moving the legacy data and business logic to Symfony while the site kept selling.</li>\n        </ul>\n        <p class="cv-tools">Flutter · Dart · GetX · SQLite · SwiftUI · Codemagic · Symfony · Doctrine · MySQL</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Mobile engineer (part-time, remote, alongside studies) — SmartCare</h3>\n          <p class="cv-job-when">Jul 2023 — Aug 2024</p>\n        </div>\n        <p class="cv-job-org">Hope Horizon Health &amp; Care · Tunisia · remote</p>\n        <ul>\n          <li>Only mobile engineer on a patient–doctor app live on Google Play, used by <b>40+ doctors and 3,000+ patients</b>: messaging, push notifications, appointments and reminders, Google Maps, QR scanning, medical AI.</li>\n          <li>Built the FastAPI and MongoDB backend on AWS with GitHub Actions, and the ReactJS web.</li>\n        </ul>\n        <p class="cv-tools">Flutter · Provider · GetX · Hive · FastAPI · MongoDB · ReactJS · AWS</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Engineering intern — warehouse terminal</h3>\n          <p class="cv-job-when">Feb — Jun 2024</p>\n        </div>\n        <p class="cv-job-org">L-Mobile · Nabeul, Tunisia</p>\n        <ul>\n          <li>Shipped <b>five warehouse-management modules</b> and a forklift tablet app on Microsoft Dynamics 365 Business Central, over C#/.NET and REST.</li>\n        </ul>\n        <p class="cv-tools">C# · .NET · D365 Business Central · REST</p>\n      </article>\n    </section>\n  </div>\n\n  <aside class="cv-side">\n\n    <section class="cv-sec">\n      <h2>Stack</h2>\n      <dl class="cv-skills">\n        <dt>Backend</dt>\n        <dd>.NET, ASP.NET Core, microservices, gRPC, API Gateway, Symfony, PHP, Doctrine, FastAPI, Python, REST, WebSockets</dd>\n        <dt>Frontend</dt>\n        <dd>Angular 21, React, TypeScript, JavaScript, HTML, CSS</dd>\n        <dt>Mobile</dt>\n        <dd>Flutter, Dart, SwiftUI (iOS widgets), GetX, Provider, Firebase, Xcode, App Store and Google Play releases</dd>\n        <dt>Databases</dt>\n        <dd>MySQL, PostgreSQL, MongoDB, SQLite, Hive</dd>\n        <dt>DevOps</dt>\n        <dd>Docker, GitLab CI/CD, GitHub Actions, Codemagic, AWS, Linux, WireGuard</dd>\n        <dt>Quality</dt>\n        <dd>PHPUnit, PyTest, Flutter widget and integration tests, SonarQube, Sentry, code review, SOLID</dd>\n      </dl>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Education</h2>\n      <ul>\n        <li>\n          <b>Engineering degree, Applied Computer Science</b>\n          National School of Engineers of Sousse (ENISo), Tunisia — EUR-ACE accredited\n          <em>Jul 2024</em>\n        </li>\n        <li>\n          <b>Summer exchange</b>\n          Murang\'a University of Technology, Kenya — a React Native registration app\n          <em>Jul – Aug 2024</em>\n        </li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Languages</h2>\n      <ul>\n        <li><b>French</b><em>B2 — daily working language with French clients</em></li>\n        <li><b>English</b><em>B2 — TOEIC</em></li>\n        <li><b>German</b><em>B1</em></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Activities</h2>\n      <ul>\n        <li><b>Treasurer, IEEE IAS student branch</b>ENISo · <em>2022 – 2023</em></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec cv-avail">\n      <h2>Availability</h2>\n      <p>\n        Open to remote roles and relocation within the EU. Based at UTC+1, overlapping a full\n        European day. Tunisian citizen: no permit needed for remote work; needs an EU work permit\n        for on-site roles (EU Blue Card eligible).\n      </p>\n    </section>\n  </aside>',
 '<div class="cv-bar">\n  <a class="btn btn-ghost" href="index.html">← Portfolio</a>\n  <a class="btn btn-solid" href="assets/Ghaith_Mefteh_CV_FullStack_FR.pdf" download>CV · full-stack (PDF)</a>\n  <a class="btn btn-ghost" href="assets/Ghaith_Mefteh_CV_Mobile_FR.pdf" download>CV · mobile (PDF)</a>\n  <a class="btn btn-ghost" href="../cv.html" hreflang="en" data-lang-switch>English version</a>\n  <span>Les PDF sont des versions d\'une page, lisibles par les ATS.</span>\n</div>\n\n<main class="sheet">\n\n  <header class="cv-head">\n    <img class="cv-portrait" src="assets/ghaith.webp" alt="Portrait de Ghaith Mefteh" width="83" height="83">\n    <div>\n      <h1 class="cv-name">Ghaith Mefteh<span class="accent">.</span></h1>\n      <p class="cv-role">Ingénieur logiciel full-stack et mobile · directeur technique</p>\n      <p class="cv-contact">\n        <span><a href="mailto:ghaithmeftah@gmail.com">ghaithmeftah@gmail.com</a></span>\n        <span><a href="tel:+21653324763">+216 53 32 47 63</a></span>\n        <span>Nabeul, Tunisie · télétravail, ou mobilité dans l\'UE</span>\n        <span><a href="https://ghaithmeftah.github.io/fr/">Portfolio</a></span>\n        <span><a href="https://www.linkedin.com/in/ghaith-mefteh-995a18157">LinkedIn</a></span>\n        <span><a href="https://github.com/Ghaithmeftah">GitHub</a></span>\n      </p>\n    </div>\n  </header>\n\n  <div class="cv-main">\n\n    <section class="cv-sec">\n      <h2>Profil</h2>\n      <p class="cv-summary">\n        Ingénieur full-stack et mobile : plus de 2 ans à temps plein, plus un an de production à\n        temps partiel pendant mes études. Premier ingénieur recruté chez AzertyUI, aujourd\'hui\n        directeur technique à la tête d\'une équipe de quatre. J\'ai mené une refonte Symfony et je\n        publie des applications Flutter sur les deux stores.\n      </p>\n      <ul class="cv-metrics">\n        <li><b>20–50&nbsp;s → 4–6&nbsp;s</b><span>pages de recherche après la refonte de chalet-montagne.com</span></li>\n        <li><b>+390</b><span>tests derrière sa CI</span></li>\n        <li><b>99,8&nbsp;%</b><span>de sessions sans crash, application SOC Rugby</span></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Expérience</h2>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Directeur technique — AzertyUI</h3>\n          <p class="cv-job-when">janv. 2026 — aujourd\'hui</p>\n        </div>\n        <p class="cv-job-org">AzertyUI · Malissard, France · télétravail · start-up qui conçoit des produits web et mobiles pour des clients français</p>\n        <ul>\n          <li>Direction d\'une <b>équipe de 4 ingénieurs</b> : planification, revue de chaque pull request, décisions techniques et mises en production ; rattaché directement au CEO.</li>\n          <li><b>Alpilink Groupe</b> (mission d\'une semaine, nov. 2026) : roue de jeu pour <b>+10 000 utilisateurs</b>, testée en charge par simulateur ; faille de sécurité hors périmètre corrigée sur une branche dédiée.</li>\n          <li>Refonte de <b>chalet-montagne.com</b> menée jusqu\'à la livraison (janv. – juil. 2026) : recherche de <b>20–50&nbsp;s à 4–6&nbsp;s</b>, ~60&nbsp;% de bande passante image en moins, +390 tests PHPUnit sous GitLab CI/CD.</li>\n          <li>Depuis août 2026, direction de la plateforme de gestion de l\'entreprise : <b>microservices .NET</b> derrière une API Gateway, gRPC entre services, Angular 21 ; plus le tableau de bord de supervision des serveurs (connexions SSH, accès WireGuard, conteneurs, sauvegardes).</li>\n        </ul>\n        <p class="cv-tools">.NET · ASP.NET Core · gRPC · Angular 21 · Symfony · PHPUnit · GitLab CI/CD · Docker</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Ingénieur logiciel, premier ingénieur recruté — AzertyUI</h3>\n          <p class="cv-job-when">août 2024 — déc. 2025</p>\n        </div>\n        <p class="cv-job-org">AzertyUI · passée d\'un ingénieur seul à une équipe de 4</p>\n        <ul>\n          <li><b>SOC Rugby</b> (août 2024 – mars 2025) : développement en solo et publication de l\'application Flutter du club de rugby de Chambéry sur l\'App Store et Google Play, avec un widget d\'écran d\'accueil iOS en SwiftUI ; <b>+2&nbsp;000 supporters</b>, <b>99,8&nbsp;% de sessions sans crash</b>.</li>\n          <li><b>chalet-montagne.com</b> (à partir d\'avril 2025) : développement en solo du cœur de la refonte d\'une place de marché de +10&nbsp;000 chalets, données et logique métier legacy migrées vers Symfony pendant que le site continuait de vendre.</li>\n        </ul>\n        <p class="cv-tools">Flutter · Dart · GetX · SQLite · SwiftUI · Codemagic · Symfony · Doctrine · MySQL</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Ingénieur mobile (temps partiel, télétravail, en parallèle des études) — SmartCare</h3>\n          <p class="cv-job-when">juil. 2023 — août 2024</p>\n        </div>\n        <p class="cv-job-org">Hope Horizon Health &amp; Care · Tunisie · télétravail</p>\n        <ul>\n          <li>Seul ingénieur mobile d\'une application patients–médecins en ligne sur Google Play, utilisée par <b>+40 médecins et +3&nbsp;000 patients</b> : messagerie, notifications push, rendez-vous et rappels, Google Maps, QR codes, IA médicale.</li>\n          <li>Backend FastAPI et MongoDB sur AWS avec GitHub Actions, et le web en ReactJS.</li>\n        </ul>\n        <p class="cv-tools">Flutter · Provider · GetX · Hive · FastAPI · MongoDB · ReactJS · AWS</p>\n      </article>\n\n      <article class="cv-job">\n        <div class="cv-job-head">\n          <h3>Stage d\'ingénieur — terminal d\'entrepôt</h3>\n          <p class="cv-job-when">févr. — juin 2024</p>\n        </div>\n        <p class="cv-job-org">L-Mobile · Nabeul, Tunisie</p>\n        <ul>\n          <li><b>Cinq modules de gestion d\'entrepôt</b> et une application tablette pour caristes livrés sur Microsoft Dynamics 365 Business Central, en C#/.NET et REST.</li>\n        </ul>\n        <p class="cv-tools">C# · .NET · D365 Business Central · REST</p>\n      </article>\n    </section>\n  </div>\n\n  <aside class="cv-side">\n\n    <section class="cv-sec">\n      <h2>Compétences</h2>\n      <dl class="cv-skills">\n        <dt>Backend</dt>\n        <dd>.NET, ASP.NET Core, microservices, gRPC, API Gateway, Symfony, PHP, Doctrine, FastAPI, Python, REST, WebSockets</dd>\n        <dt>Frontend</dt>\n        <dd>Angular 21, React, TypeScript, JavaScript, HTML, CSS</dd>\n        <dt>Mobile</dt>\n        <dd>Flutter, Dart, SwiftUI (widgets iOS), GetX, Provider, Firebase, Xcode, publications App Store et Google Play</dd>\n        <dt>Bases de données</dt>\n        <dd>MySQL, PostgreSQL, MongoDB, SQLite, Hive</dd>\n        <dt>DevOps</dt>\n        <dd>Docker, GitLab CI/CD, GitHub Actions, Codemagic, AWS, Linux, WireGuard</dd>\n        <dt>Qualité</dt>\n        <dd>PHPUnit, PyTest, tests de widgets et d\'intégration Flutter, SonarQube, Sentry, revue de code, SOLID</dd>\n      </dl>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Formation</h2>\n      <ul>\n        <li>\n          <b>Diplôme d\'ingénieur en informatique appliquée</b>\n          École Nationale d\'Ingénieurs de Sousse (ENISo), Tunisie — accréditation EUR-ACE\n          <em>juil. 2024</em>\n        </li>\n        <li>\n          <b>Échange d\'été</b>\n          Murang\'a University of Technology, Kenya — une application React Native d\'inscription\n          <em>juil. – août 2024</em>\n        </li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Langues</h2>\n      <ul>\n        <li><b>Français</b><em>B2 — langue de travail quotidienne avec des clients français</em></li>\n        <li><b>Anglais</b><em>B2 — TOEIC</em></li>\n        <li><b>Allemand</b><em>B1</em></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec">\n      <h2>Activités</h2>\n      <ul>\n        <li><b>Trésorier, branche étudiante IEEE IAS</b>ENISo · <em>2022 – 2023</em></li>\n      </ul>\n    </section>\n\n    <section class="cv-sec cv-avail">\n      <h2>Disponibilité</h2>\n      <p>\n        Ouvert au télétravail et à une mobilité dans l\'UE. Basé en UTC+1, une journée européenne\n        entière en commun. Nationalité tunisienne : aucun permis requis en télétravail ; permis de\n        travail UE nécessaire pour un poste sur site (éligible Carte bleue européenne).\n      </p>\n    </section>\n  </aside>'),
('<html lang="en">', '<html lang="fr">'),
('<title>Ghaith Mefteh — CV | Full-Stack and Mobile Engineer</title>',
 '<title>Ghaith Mefteh — CV | Ingénieur full-stack et mobile</title>'),
('<meta name="description" content="CV of Ghaith Mefteh, full-stack and mobile engineer and technical director at AzertyUI: .NET, Symfony, Angular, Flutter. PDFs in English and French.">',
 '<meta name="description" content="CV de Ghaith Mefteh, ingénieur full-stack et mobile, directeur technique chez AzertyUI : .NET, Symfony, Angular, Flutter. PDF en français et anglais.">'),
('<link rel="canonical" href="https://ghaithmeftah.github.io/cv.html">',
 '<link rel="canonical" href="https://ghaithmeftah.github.io/fr/cv.html">'),













]


def main():
    src = os.path.join(ROOT, 'index.html')
    s = open(src, encoding='utf-8').read()

    for old, new in GLOBAL:
        if old not in s:
            sys.exit("make-fr: global string vanished: " + old[:110])
        s = s.replace(old, new)

    for old, new in HEAD + BODY:
        if s.count(old) != 1:
            sys.exit(f"make-fr: expected exactly one match, found {s.count(old)}:\n  {old[:110]}")
        s = s.replace(old, new)

    # language alternates flip round on the French page
    s = s.replace('<link rel="alternate" hreflang="en" href="https://ghaithmeftah.github.io/">\n'
                  '<link rel="alternate" hreflang="fr" href="https://ghaithmeftah.github.io/fr/">',
                  '<link rel="alternate" hreflang="fr" href="https://ghaithmeftah.github.io/fr/">\n'
                  '<link rel="alternate" hreflang="en" href="https://ghaithmeftah.github.io/">')

    s, n = re.subn(r'<article id="case-alpilink".*?</article>', lambda m: MISSION_FR, s, count=1, flags=re.S)
    if n != 1:
        sys.exit('make-fr: mission block not found')

    for old, new in PATHS:
        s = s.replace(old, new)

    # Recommendations keep the language their author wrote them in. On the French
    # page the English glosses under the two French quotes are redundant, and it is
    # Chadi's English one that needs a French gloss instead.
    s = re.sub(r'\n\s*<details class="say-tr" lang="en">.*?</details>', '', s, flags=re.S)
    chadi_open = '<blockquote lang="en"><p>'
    if chadi_open in s:
        end = s.index('</p></blockquote>', s.index(chadi_open)) + len('</p></blockquote>')
        gloss = ('\n        <details class="say-tr" lang="fr">'
                 '\n          <summary>Lire en fran\u00e7ais</summary>'
                 '\n          <p>' + CHADI_FR + '</p>'
                 '\n        </details>')
        s = s[:end] + gloss + s[end:]

    # the structured data block stays English-keyed but points at the French URL
    s = s.replace('"inLanguage": "en"', '"inLanguage": "fr"')

    s = s.replace('<body>', '<body>\n<!-- Generated by tools/make-fr.py from index.html — edit that, then regenerate. -->', 1)

    out_dir = os.path.join(ROOT, 'fr')
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(s)
    print('fr/index.html written')

    # any English left in visible text is a translation we forgot
    leftovers = [w for w in ('Read the CV', 'By the end', 'Hire me', 'At a glance', 'Selected work')
                 if w in s]
    if leftovers:
        sys.exit('untranslated strings still present: ' + ', '.join(leftovers))

    # ---- the CV sheet ----
    c = open(os.path.join(ROOT, 'cv.html'), encoding='utf-8').read()
    for old, new in CV:
        if c.count(old) != 1:
            sys.exit("make-fr (cv): expected one match, found %d: %s" % (c.count(old), old[:110]))
        c = c.replace(old, new)
    c = c.replace('<link rel="alternate" hreflang="en" href="https://ghaithmeftah.github.io/cv.html">\n'
                  '<link rel="alternate" hreflang="fr" href="https://ghaithmeftah.github.io/fr/cv.html">',
                  '<link rel="alternate" hreflang="fr" href="https://ghaithmeftah.github.io/fr/cv.html">\n'
                  '<link rel="alternate" hreflang="en" href="https://ghaithmeftah.github.io/cv.html">')
    for old, new in PATHS + [('href="cv.css"', 'href="../cv.css"'), ('href="index.html"', 'href="./"')]:
        c = c.replace(old, new)
    c = c.replace('<body>', '<body>\n<!-- Generated by tools/make-fr.py from cv.html - edit that, then regenerate. -->', 1)
    open(os.path.join(out_dir, 'cv.html'), 'w', encoding='utf-8').write(c)
    print('fr/cv.html written')


if __name__ == '__main__':
    main()
