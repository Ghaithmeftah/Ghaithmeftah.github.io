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

('<title>Ghaith Mefteh — Full-Stack and Mobile Engineer | .NET, Symfony, Flutter</title>',
 '<title>Ghaith Mefteh — Ingénieur full-stack et mobile | .NET, Symfony, Flutter</title>'),

('<meta name="description" content="Ghaith Mefteh — full-stack and mobile software engineer, technical director at AzertyUI. .NET, Symfony, Angular, Flutter. 3+ years in production, leads a team of 4. Open to remote work and relocation in the EU.">',
 '<meta name="description" content="Ghaith Mefteh — ingénieur logiciel full-stack et mobile, directeur technique chez AzertyUI. .NET, Symfony, Angular, Flutter. Plus de 3 ans en production, dirige une équipe de 4. Ouvert au télétravail et à une mobilité dans l\'UE.">'),

('<link rel="canonical" href="https://ghaithmeftah.github.io/">',
 '<link rel="canonical" href="https://ghaithmeftah.github.io/fr/">'),

('<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="fr_FR">'),

('<meta property="og:title" content="Ghaith Mefteh — Full-Stack and Mobile Engineer">',
 '<meta property="og:title" content="Ghaith Mefteh — Ingénieur full-stack et mobile">'),

('<meta property="og:description" content=".NET · Symfony · Angular · Flutter. I ship production systems end to end — 3+ years in production, technical director at AzertyUI. Open to remote roles, EU relocation and freelance.">',
 '<meta property="og:description" content=".NET · Symfony · Angular · Flutter. Je livre des systèmes de bout en bout — plus de 3 ans en production, directeur technique chez AzertyUI. Ouvert au télétravail, à une mobilité dans l\'UE et au freelance.">'),

('<meta property="og:url" content="https://ghaithmeftah.github.io/">',
 '<meta property="og:url" content="https://ghaithmeftah.github.io/fr/">'),

('<meta name="twitter:title" content="Ghaith Mefteh — Full-Stack and Mobile Engineer">',
 '<meta name="twitter:title" content="Ghaith Mefteh — Ingénieur full-stack et mobile">'),

('<meta name="twitter:description" content=".NET · Symfony · Angular · Flutter. Production systems end to end. Open to remote roles, EU relocation and freelance.">',
 '<meta name="twitter:description" content=".NET · Symfony · Angular · Flutter. Des systèmes en production, de bout en bout. Ouvert au télétravail, à une mobilité dans l\'UE et au freelance.">'),

('<meta property="og:image:alt" content="Ghaith Mefteh — full-stack and mobile engineer. Symfony, FastAPI, Flutter.">',
 '<meta property="og:image:alt" content="Ghaith Mefteh — ingénieur full-stack et mobile. Symfony, FastAPI, Flutter.">'),
]

BODY = [
# ---- header / nav ----
('<a class="skip" href="#work">Skip to work</a>', '<a class="skip" href="#work">Aller aux projets</a>'),
('<nav aria-label="Site">', '<nav aria-label="Site">'),
('<a href="#work">Work</a>', '<a href="#work">Projets</a>'),
('<a href="#lab">Lab</a>', '<a href="#lab">Labo</a>'),
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
('''      Full-stack and mobile engineer, 3+ years in production, leading a team of four.
      I take a feature the whole way: the screen in the browser, the app on the phone,
      the API behind them, the database under that. .NET&nbsp;microservices and Symfony
      behind, Angular and React in front, Flutter on both stores.''',
 '''      Ingénieur full-stack et mobile, plus de 3 ans en production, à la tête d'une équipe de
      quatre. Je porte une fonctionnalité de bout en bout : l'écran dans le navigateur,
      l'application sur le téléphone, l'API derrière, la base de données en dessous.
      Microservices&nbsp;.NET et Symfony derrière, Angular et React devant, Flutter sur les
      deux stores.'''),
('      Open to remote roles, EU relocation and freelance · answers within the day',
 '      Ouvert au télétravail, à une mobilité dans l\'UE et au freelance · réponse dans la journée'),
('<a class="btn btn-solid" href="#work">See the work</a>', '<a class="btn btn-solid" href="#work">Voir les projets</a>'),
('<a class="btn btn-ghost" href="cv.html">Read the CV</a>', '<a class="btn btn-ghost" href="cv.html">Lire le CV</a>'),
('href="mailto:ghaithmeftah@gmail.com?subject=Opportunity%20for%20Ghaith">ghaithmeftah@gmail.com</a>',
 'href="mailto:ghaithmeftah@gmail.com?subject=Opportunit%C3%A9%20pour%20Ghaith">ghaithmeftah@gmail.com</a>'),

# ---- diagram ----
('aria-label="Animated diagram: a request travels from a React or Angular web app or a Flutter mobile app to a Symfony or FastAPI backend, then to MySQL or MongoDB, and back. The web and mobile skeletons link to the matching projects below."',
 'aria-label="Schéma animé : une requête part d\'une application web React ou Angular, ou d\'une application mobile Flutter, vers un backend Symfony ou FastAPI, puis vers MySQL ou MongoDB, et revient. Les silhouettes web et mobile mènent aux projets correspondants."'),
('aria-label="Mobile — see the Flutter projects below"', 'aria-label="Mobile — voir les projets Flutter ci-dessous"'),
('data-tip="Flutter — tap to jump to the mobile projects"', 'data-tip="Flutter — touchez pour aller aux projets mobiles"'),
('aria-label="Web — see the Angular and React projects below"', 'aria-label="Web — voir les projets Angular et React ci-dessous"'),
('data-tip="Angular and React — tap to jump to the web projects"', 'data-tip="Angular et React — touchez pour aller aux projets web"'),
('data-tip="Symfony + Doctrine — chalet-montagne.com, 10,000+ chalets, 390+ tests"',
 'data-tip="Symfony + Doctrine — chalet-montagne.com, +10 000 chalets, +390 tests"'),
('data-tip="FastAPI — SmartCare healthcare backend on AWS"', 'data-tip="FastAPI — backend santé SmartCare sur AWS"'),
('data-tip="MySQL and MongoDB — query optimization, caching, migrations"',
 'data-tip="MySQL et MongoDB — optimisation des requêtes, cache, migrations"'),
('<figcaption class="diagram-tip" id="diagram-tip">Tap the mobile or web screen to see those projects.</figcaption>',
 '<figcaption class="diagram-tip" id="diagram-tip">Touchez l\'écran mobile ou web pour voir ces projets.</figcaption>'),

# ---- proof ----
('''    Some numbers I stand behind: a marketplace of
    <em><span data-count="10000">10,000</span>+ chalets</em> whose pages went from
    <em>20–50&nbsp;s to 4–6&nbsp;s</em>, a test suite built from zero to
    <em><span data-count="390">390</span>+ tests</em>, a Flutter app at
    <em><span data-count="99.8" data-decimals="1">99.8</span>% crash-free</em> sessions, and apps used by
    <em><span data-count="5000">5,000</span>+ people</em> on iOS and Android.''',
 '''    Quelques chiffres que j'assume : une marketplace de
    <em>+<span data-count="10000">10&nbsp;000</span> chalets</em> dont les pages sont passées de
    <em>20–50&nbsp;s à 4–6&nbsp;s</em>, une suite de tests partie de zéro à
    <em>+<span data-count="390">390</span> tests</em>, une application Flutter à
    <em><span data-count="99.8" data-decimals="1">99,8</span>&nbsp;% de sessions sans crash</em>, et des
    applications utilisées par <em>+<span data-count="5000">5&nbsp;000</span> personnes</em> sur iOS et Android.'''),

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
('<dd>3+ years in production · leading teams of 4 since 2024</dd>',
 '<dd>Plus de 3 ans en production · à la tête d\'équipes de 4 depuis 2024</dd>'),
('<dt>Data</dt>', '<dt>Données</dt>'),
('<dt>Beyond code</dt>', '<dt>Hors du code</dt>'),
('<dd>Treasurer, IEEE IAS student branch at ENISo (2022–2023) · gym, cycling, camping</dd>',
 '<dd>Trésorier, branche étudiante IEEE IAS de l\'ENISo (2022–2023) · musculation, cyclisme, camping</dd>'),
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
('<dd>Remote or on-site roles in the EU, and freelance projects</dd>',
 '<dd>Postes en télétravail ou sur site dans l\'UE, et missions freelance</dd>'),

# ---- work ----
('<h2>Selected work</h2>', '<h2>Projets sélectionnés</h2>'),
('<p class="case-role">Technical director · leading a team of 4 · AzertyUI · now</p>',
 '<p class="case-role">Directeur technique · à la tête d\'une équipe de 4 · AzertyUI · en cours</p>'),
('<h3>Company management platform</h3>', '<h3>Plateforme de gestion d\'entreprise</h3>'),
('''        AzertyUI's own product: one place where developers, executives and accountants file
        absences, vacations, expenses, tickets and requests, and find their contracts, payslips
        and company paperwork. I lead the four engineers building it, from task planning to code
        review and deployment, and I write code alongside them.''',
 '''        Le produit d'AzertyUI : un seul endroit où développeurs, dirigeants et comptables déclarent
        absences, congés, notes de frais, tickets et demandes, et retrouvent contrats, fiches de paie
        et documents de l'entreprise. Je dirige les quatre ingénieurs qui le construisent, de la
        planification des tâches à la revue de code et au déploiement, et je code avec eux.'''),
('''        The backend is .NET (ASP.NET Core) split into microservices behind an API Gateway, with
        the services talking to each other over gRPC. The front is Angular&nbsp;21, and automated
        tests grow with every feature.''',
 '''        Le backend est en .NET (ASP.NET Core), découpé en microservices derrière une API Gateway,
        les services communiquant entre eux en gRPC. Le front est en Angular&nbsp;21, et les tests
        automatisés grandissent avec chaque fonctionnalité.'''),
('''        Next to it I built the company's server monitoring dashboard: every SSH login tracked and
        the suspicious ones flagged, per-developer access through generated WireGuard VPN configs,
        running containers at a glance, an alert to the admin when the master server goes down,
        and backups so a lost server never means lost data.''',
 '''        À côté, j'ai construit le tableau de bord de supervision des serveurs : chaque connexion SSH
        suivie et les suspectes signalées, des accès par développeur via des configurations VPN
        WireGuard générées, les conteneurs en cours d'un coup d'œil, une alerte à l'administrateur
        quand le serveur maître tombe, et des sauvegardes pour qu'un serveur perdu ne signifie
        jamais des données perdues.'''),
('''      <p class="case-outcome"><b>Where it stands:</b> the platform is in active development ahead
        of its internal release, and the monitoring dashboard already watches the company's
        servers.</p>''',
 '''      <p class="case-outcome"><b>Où on en est :</b> la plateforme est en plein développement avant
        sa mise en service interne, et le tableau de bord surveille déjà les serveurs de
        l'entreprise.</p>'''),
('<p class="widget-title">How a request travels</p>', '<p class="widget-title">Le trajet d\'une requête</p>'),
('aria-label="Diagram: the Angular 21 app calls an API Gateway, which routes to four .NET microservices for absences, expenses, documents and tickets; the services call each other over gRPC."',
 'aria-label="Schéma : l\'application Angular 21 appelle une API Gateway, qui route vers quatre microservices .NET pour les absences, les notes de frais, les documents et les tickets ; les services communiquent entre eux en gRPC."'),
('<text x="54" y="144" class="arch-sub">web app</text>', '<text x="54" y="144" class="arch-sub">app web</text>'),
('<text x="352" y="102" class="arch-name">Expenses</text>', '<text x="352" y="102" class="arch-name">Frais</text>'),
('<text x="352" y="258" class="arch-sub">gRPC between services</text>', '<text x="352" y="258" class="arch-sub">gRPC entre services</text>'),
('aria-label="Illustration of the server monitoring feed: SSH logins, a flagged login from a new country, a WireGuard config issued, containers running, nightly backup done."',
 'aria-label="Illustration du flux de supervision : connexions SSH, une connexion depuis un nouveau pays signalée, une configuration WireGuard émise, conteneurs actifs, sauvegarde nocturne faite."'),
('<p class="widget-title">Server monitoring</p>', '<p class="widget-title">Supervision des serveurs</p>'),
('<span class="mon-live"><span class="mon-dot"></span>watching</span>', '<span class="mon-live"><span class="mon-dot"></span>en veille</span>'),
('<span>login from a new country</span><span class="mon-warn">flagged</span>',
 '<span>connexion, nouveau pays</span><span class="mon-warn">signalée</span>'),
('<span>WireGuard config → dev-03</span><span class="mon-ok">issued</span>',
 '<span>config WireGuard → dev-03</span><span class="mon-ok">émise</span>'),
('<span>containers on master</span><span class="mon-ok">12 / 12 up</span>',
 '<span>conteneurs sur master</span><span class="mon-ok">12 / 12 actifs</span>'),
('<span>nightly snapshot</span><span class="mon-ok">done</span>',
 '<span>sauvegarde nocturne</span><span class="mon-ok">faite</span>'),
('<p class="widget-foot widget-foot-dark">illustration of what the dashboard tracks, not live data</p>',
 '<p class="widget-foot widget-foot-dark">illustration de ce que suit le tableau de bord, pas des données réelles</p>'),
('<p class="case-role">Team lead · team of 4 · 14 months · AzertyUI, France · 2024 — 2025</p>',
 '<p class="case-role">Team lead · équipe de 4 · 14 mois · AzertyUI, France · 2024 — 2025</p>'),
('''        A French ski-chalet rental marketplace listing 10,000+ chalets, on a legacy stack where a
        search page could take 50 seconds to render. I led four engineers through the rebuild on
        Symfony, from the backend architecture to the last screen.
      </p>
      <p>
        The site kept selling the whole time, so the legacy data and the business logic moved
        first, with functional parity as the bar. Then we rewrote the search and listing engine
        behind caching, query optimization and parallelized data processing, and images became
        on-demand WebP served in several sizes. The code follows SOLID with SonarQube as the
        gate, and ships through GitLab CI/CD, Docker Compose and Apache2.''',
 '''        Une marketplace française de location de chalets au ski, plus de 10&nbsp;000 chalets en
        ligne, sur une stack héritée où une page de recherche pouvait mettre 50 secondes à
        s'afficher. J'ai dirigé quatre ingénieurs pour la refonte sur Symfony, de l'architecture
        backend jusqu'au dernier écran.
      </p>
      <p>
        Le site a continué de vendre pendant toute la refonte : les données et les règles métier
        sont passées en premier, à parité fonctionnelle. Puis nous avons réécrit le moteur de
        recherche et de listing derrière du cache, de l'optimisation de requêtes et du traitement
        parallélisé, et les images sont devenues du WebP à la demande, servi en plusieurs tailles.
        Le code suit SOLID avec SonarQube comme garde-fou, et part en production via GitLab CI/CD,
        Docker Compose et Apache2.'''),
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

('<p class="case-role">Mobile engineer · AzertyUI · shipped to both stores · 2024</p>',
 '<p class="case-role">Ingénieur mobile · AzertyUI · publié sur les deux stores · 2024</p>'),
('''        The official app of the Chambéry rugby club: match calendar and reminders, live scores,
        rankings, in-app messaging and push notifications. Built in Flutter with GetX and SQLite,
        plus SwiftUI, and used by 2,000+ fans. They refresh it at full time and it holds.''',
 '''        L'application officielle du club de rugby de Chambéry : calendrier et rappels des matchs,
        scores en direct, classements, messagerie et notifications push. Développée en Flutter avec
        GetX et SQLite, plus SwiftUI, et utilisée par plus de 2&nbsp;000 supporters. Ils la
        rafraîchissent au coup de sifflet final et elle tient.'''),
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

('<p class="case-role">Mobile engineer, part-time, remote · Hope Horizon Health &amp; Care · 2023 – 2024</p>',
 '<p class="case-role">Ingénieur mobile, temps partiel, télétravail · Hope Horizon Health &amp; Care · 2023 – 2024</p>'),
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
('<p class="carousel-cap">Date picker — busy and closed days flagged</p>',
 '<p class="carousel-cap">Choix de la date — jours chargés et fermés signalés</p>'),
('<p class="carousel-cap">Time slots, with hour-range preferences</p>',
 '<p class="carousel-cap">Créneaux horaires, avec préférences de plage</p>'),
('<p class="carousel-cap">Visit reason — searchable symptom picker</p>',
 '<p class="carousel-cap">Motif de consultation — recherche de symptômes</p>'),
('<p class="carousel-cap">Review before sending the request</p>',
 '<p class="carousel-cap">Récapitulatif avant envoi de la demande</p>'),
('<p class="carousel-cap">Request sent — confirmation</p>',
 '<p class="carousel-cap">Demande envoyée — confirmation</p>'),
('<p class="carousel-cap">Push notification back to the patient</p>',
 '<p class="carousel-cap">Notification push renvoyée au patient</p>'),
('<p class="carousel-cap">Doctor side — accept or reject the request</p>',
 '<p class="carousel-cap">Côté médecin — accepter ou refuser la demande</p>'),
('<p class="carousel-cap">Urgent calls — nearby requests, by distance</p>',
 '<p class="carousel-cap">Appels urgents — demandes proches, par distance</p>'),
('<p class="carousel-cap">Push alert when a contact calls for help nearby</p>',
 '<p class="carousel-cap">Alerte push quand un proche appelle à l\'aide</p>'),
('<p class="carousel-cap">Call detail — live map and patient info</p>',
 '<p class="carousel-cap">Détail de l\'appel — carte en direct et infos patient</p>'),
("<p class=\"carousel-cap\">Drug interactions — pick the patient's medicines</p>",
 '<p class="carousel-cap">Interactions médicamenteuses — sélection des traitements</p>'),
('<p class="carousel-cap">Flagged interaction pairs, with dosage and form</p>',
 '<p class="carousel-cap">Paires signalées, avec dosage et forme</p>'),
('<p class="widget-foot">real screens from the Flutter app, in production for patients and doctors</p>',
 '<p class="widget-foot">écrans réels de l\'application Flutter, en production pour patients et médecins</p>'),

('<p class="case-role">Engineering internship · L-Mobile · 2024</p>',
 '<p class="case-role">Stage d\'ingénieur · L-Mobile · 2024</p>'),
('Forklift-mounted warehouse terminal</h3>', 'Terminal d\'entrepôt monté sur chariot élévateur</h3>'),
('''        Tablets bolted onto forklifts, so warehouse operators read live inventory while moving.
        Five warehouse-management modules against Microsoft Dynamics 365 Business Central over
        C#/.NET and REST, in an enterprise stack I had never written a line of before I started.''',
 '''        Des tablettes fixées sur des chariots élévateurs, pour que les opérateurs lisent leur
        stock en direct, en mouvement. Cinq modules de gestion d'entrepôt sur Microsoft Dynamics
        365 Business Central en C#/.NET et REST, dans une stack d'entreprise dont je n'avais jamais
        écrit une ligne avant d'arriver.'''),
('''      <p class="case-outcome"><b>By the end:</b> five modules shipped inside the internship.</p>''',
 '''      <p class="case-outcome"><b>À la fin :</b> cinq modules livrés dans le temps du stage.</p>'''),
('<p class="widget-title">Where the terminals live</p>', '<p class="widget-title">Là où vivent les terminaux</p>'),
('<p class="widget-foot">tablets ride the forklifts, live inventory and picking data while the operator moves</p>',
 '<p class="widget-foot">les tablettes roulent avec les chariots, stock et préparation en direct pendant le déplacement</p>'),

# ---- lab ----
('<h2>The lab</h2>', '<h2>Le labo</h2>'),
('<p>Remote control for farm water pumps, a Flutter-style Expo app talking MQTT to an ESP32 in the field. Arabic, French and English, built for farmers who are none of them online all day.</p>',
 '<p>Commande à distance des pompes d\'irrigation, une application Expo qui parle MQTT à un ESP32 au champ. Arabe, français et anglais, pensée pour des agriculteurs qui ne sont pas connectés toute la journée.</p>'),
('<p>An AI writing companion for LinkedIn, drafts posts in your own voice, mobile-first. Design system and MVP built to feel like a product, not a demo.</p>',
 '<p>Un assistant d\'écriture IA pour LinkedIn, rédige des posts dans votre propre voix, pensé mobile d\'abord. Design system et MVP construits pour ressembler à un produit, pas à une démo.</p>'),
('<p>Audits documents against legal obligations, rule-based checks like forbidden vocabulary, backed by a structured catalog of legal requirements.</p>',
 '<p>Audite des documents au regard d\'obligations légales, contrôles par règles, comme le vocabulaire interdit, adossés à un catalogue structuré d\'exigences juridiques.</p>'),
('<p class="lab-tags">Expo · AI · product design</p>', '<p class="lab-tags">Expo · IA · design produit</p>'),
('<p class="lab-tags">Compliance · rules engine</p>', '<p class="lab-tags">Conformité · moteur de règles</p>'),

# ---- path ----
('<h2>The path so far</h2>', '<h2>Le parcours jusqu\'ici</h2>'),
('<p class="tl-when">2024 — now</p>', '<p class="tl-when">2024 — aujourd\'hui</p>'),
('<h3>Technical director, AzertyUI</h3>', '<h3>Directeur technique, AzertyUI</h3>'),
("<p>Shipped SOC Rugby to both stores, led four engineers for 14 months on chalet-montagne.com, and now lead the team building AzertyUI's own management platform on .NET microservices, plus the company's server monitoring.</p>",
 "<p>SOC Rugby publiée sur les deux stores, quatre ingénieurs dirigés pendant 14 mois sur chalet-montagne.com, et aujourd'hui l'équipe qui construit la plateforme de gestion d'AzertyUI en microservices .NET, plus la supervision des serveurs de l'entreprise.</p>"),
('<h3>Engineering degree, ENISo</h3>', '<h3>Diplôme d\'ingénieur, ENISo</h3>'),
("<p>Applied Computer Science (EUR-ACE accredited), National School of Engineers of Sousse. Then a summer exchange at Murang'a University of Technology, Kenya, in July and August 2024: I fixed network problems across the campus departments and designed a React Native app so students could register remotely instead of on paper.</p>",
 "<p>Informatique appliquée (accréditation EUR-ACE), École Nationale d'Ingénieurs de Sousse. Puis un échange d'été à Murang'a University of Technology, au Kenya, en juillet et août 2024 : j'ai résolu des problèmes réseau dans les départements du campus et conçu une application React Native pour que les étudiants s'inscrivent à distance plutôt que sur papier.</p>"),
("<p class=\"tl-caption\">Murang'a University of Technology, Kenya — summer exchange, 2024</p>",
 "<p class=\"tl-caption\">Murang'a University of Technology, Kenya — échange d'été, 2024</p>"),
('<h3>Mobile engineer, Hope Horizon</h3>', '<h3>Ingénieur mobile, Hope Horizon</h3>'),
('<p>SmartCare, part-time and remote alongside the degree: the only mobile engineer, plus the FastAPI backend and the ReactJS web. 40+ doctors and 3,000+ patients use it.</p>',
 '<p>SmartCare, à temps partiel et à distance, en parallèle du diplôme : seul ingénieur mobile, plus le backend FastAPI et le web ReactJS. Plus de 40 médecins et 3&nbsp;000 patients l\'utilisent.</p>'),
('<h3>First production code</h3>', '<h3>Premier code en production</h3>'),
("<p>Started shipping for real users, and haven't stopped. Treasurer of the IEEE IAS student branch at ENISo the same year. French and English at B2 (TOEIC), German at B1, comfortable in international teams across time zones.</p>",
 "<p>J'ai commencé à livrer pour de vrais utilisateurs, et je n'ai plus arrêté. Trésorier de la branche étudiante IEEE IAS de l'ENISo la même année. Français et anglais B2 (TOEIC), allemand B1, à l'aise dans des équipes internationales, d'un fuseau à l'autre.</p>"),

# ---- hire ----
('<h2 id="hire-h">Two ways to work with me</h2>', '<h2 id="hire-h">Deux façons de travailler avec moi</h2>'),
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
('<dd>Start date on request</dd>', '<dd>Date de démarrage sur demande</dd>'),
('''<dt>Languages</dt>
          <dd>English (B2, TOEIC) and French for daily work, German B1</dd>''',
 '''<dt>Langues</dt>
          <dd>Français et anglais (B2, TOEIC) au quotidien, allemand B1</dd>'''),
('<a class="btn btn-solid" href="cv.html">Read the CV</a>\n        <a class="btn btn-ghost btn-dl" href="assets/Ghaith-Mefteh-CV-EN.pdf" download>CV · full-stack (PDF)</a>\n        <a class="btn btn-ghost btn-dl" href="assets/Ghaith-Mefteh-CV-Mobile-EN.pdf" download>CV · mobile (PDF)</a>',
 '<a class="btn btn-solid" href="cv.html">Lire le CV</a>\n        <a class="btn btn-ghost btn-dl" href="../assets/Ghaith-Mefteh-CV-FR.pdf" download>CV · full-stack (PDF)</a>\n        <a class="btn btn-ghost btn-dl" href="../assets/Ghaith-Mefteh-CV-Mobile-FR.pdf" download>CV · mobile (PDF)</a>'),
('<p class="lane-kicker">For founders and agencies</p>', '<p class="lane-kicker">Pour les fondateurs et agences</p>'),
('<h3>One engineer who carries the whole feature</h3>', '<h3>Un ingénieur qui porte la fonctionnalité entière</h3>'),
('<dt>What I take on</dt>', '<dt>Ce que je prends en charge</dt>'),
('<dd>A product that got slow and needs rebuilding · a feature from database to screen · an app shipped to both stores · an API and the infrastructure under it</dd>',
 '<dd>Un produit devenu lent qu\'il faut reconstruire · une fonctionnalité de la base de données à l\'écran · une application publiée sur les deux stores · une API et l\'infrastructure dessous</dd>'),
('<dt>How it starts</dt>', '<dt>Comment ça démarre</dt>'),
('<dd>A short call, then a written scope and a first milestone we can both check against</dd>',
 '<dd>Un appel court, puis un périmètre écrit et un premier jalon vérifiable des deux côtés</dd>'),
('<dt>How you see progress</dt>', '<dt>Comment vous suivez l\'avancement</dt>'),
('<dd>Work in the open on your repo: reviewable commits, tests, and a deployed build you can click</dd>',
 '<dd>Du travail visible sur votre dépôt: des commits relisibles, des tests, et une version déployée que vous pouvez cliquer</dd>'),
('<dt>Rate</dt>', '<dt>Tarif</dt>'),
('<dd>On request, quoted per project or per day once the scope is clear</dd>',
 '<dd>Sur demande, au projet ou à la journée une fois le périmètre clair</dd>'),
('href="mailto:ghaithmeftah@gmail.com?subject=Project%20for%20Ghaith&amp;body=Hi%20Ghaith%2C%0A%0AWe%20need%20help%20with...">Describe the project</a>',
 'href="mailto:ghaithmeftah@gmail.com?subject=Projet%20pour%20Ghaith&amp;body=Bonjour%20Ghaith%2C%0A%0ANous%20avons%20besoin%20d%27aide%20sur...">Décrire le projet</a>'),
('<a class="btn btn-ghost" href="tel:+21653324763">Call me</a>', '<a class="btn btn-ghost" href="tel:+21653324763">M\'appeler</a>'),
('<li><b>Answers within the day</b><span>usually a few hours, in CET working time</span></li>',
 '<li><b>Réponse dans la journée</b><span>souvent en quelques heures, aux horaires CET</span></li>'),
('<li><b>Tests and CI, not promises</b><span>390+ tests and a pipeline on the last marketplace</span></li>',
 '<li><b>Des tests et de la CI, pas des promesses</b><span>390+ tests et un pipeline sur la dernière marketplace</span></li>'),
('<li><b>Code review as a habit</b><span>I set the review standard for two teams of four</span></li>',
 '<li><b>La revue de code comme habitude</b><span>j\'ai posé le standard de revue de deux équipes de quatre</span></li>'),
('<li><b>Design to code</b><span>Figma translated screen by screen, not approximated</span></li>',
 '<li><b>De la maquette au code</b><span>Figma traduit écran par écran, pas approximé</span></li>'),

# ---- contact ----
('<p class="avail-badge"><span class="avail-dot"></span>Available for new roles and freelance projects</p>',
 '<p class="avail-badge"><span class="avail-dot"></span>Disponible pour de nouveaux postes et missions freelance</p>'),
("<h2>Let's build the next one</h2>", '<h2>Construisons le prochain</h2>'),
('''    Open to remote roles, relocation in the EU and freelance work: full-stack, backend-leaning,
    or mobile. Email or call, I usually answer within the day.''',
 '''    Ouvert au télétravail, à une mobilité dans l'UE et aux missions freelance : full-stack,
    orienté backend, ou mobile. Un mail ou un appel, je réponds en général dans la journée.'''),
('body=Hi%20Ghaith%2C%0A%0AI%20saw%20your%20portfolio%20and%20would%20like%20to%20talk%20about...">Email me</a>',
 'body=Bonjour%20Ghaith%2C%0A%0AJ%27ai%20vu%20votre%20portfolio%20et%20j%27aimerais%20parler%20de...">M\'écrire</a>'),
('<a class="btn btn-ghost btn-dl" href="assets/Ghaith-Mefteh-CV-EN.pdf" download>CV · full-stack (PDF)</a>\n    <a class="btn btn-ghost btn-dl" href="assets/Ghaith-Mefteh-CV-Mobile-EN.pdf" download>CV · mobile (PDF)</a>',
 '<a class="btn btn-ghost btn-dl" href="../assets/Ghaith-Mefteh-CV-FR.pdf" download>CV · full-stack (PDF)</a>\n    <a class="btn btn-ghost btn-dl" href="../assets/Ghaith-Mefteh-CV-Mobile-FR.pdf" download>CV · mobile (PDF)</a>'),
('<p class="contact-meta">Nabeul, Tunisia (CET) · open to EU relocation · ', '<p class="contact-meta">Nabeul, Tunisie (CET) · mobilité UE possible · '),

# ---- dock ----
('  <a class="btn btn-solid" href="mailto:ghaithmeftah@gmail.com?subject=Opportunity%20for%20Ghaith">Email me</a>',
 '  <a class="btn btn-solid" href="mailto:ghaithmeftah@gmail.com?subject=Opportunit%C3%A9%20pour%20Ghaith">M\'écrire</a>'),
# ---- recommendations band ----
('<a href="#said">Said</a>', '<a href="#said">Avis</a>'),
('<h2 id="says-h">In their words</h2>', '<h2 id="says-h">Ce qu\'ils en disent</h2>'),
('''    <p class="says-lede">Three people who worked with me, quoted as written, in the language they
      wrote it in.</p>''',
 '''    <p class="says-lede">Trois personnes qui ont travaillé avec moi, citées telles quelles, dans
      la langue d'origine.</p>'''),
('<p class="say-tag say-tag-peer">AzertyUI \u00b7 the team</p>',
 '<p class="say-tag say-tag-peer">AzertyUI \u00b7 l\'\u00e9quipe</p>'),
('<span class="say-role">Founder, ALPIUM</span>',
 '<span class="say-role">G\u00e9rant fondateur, ALPIUM</span>'),
('<span class="say-role">Project manager and software engineer, Hope Horizon</span>',
 '<span class="say-role">Chef de projet et ing\u00e9nieur logiciel, Hope Horizon</span>'),
('<span class="say-role">Software engineer, AzertyUI</span>',
 '<span class="say-role">Ing\u00e9nieur logiciel, AzertyUI</span>'),
('<span class="say-meta">The client \u00b7 September 2026</span>',
 '<span class="say-meta">Le client \u00b7 septembre 2026</span>'),
('<span class="say-meta">Worked with me \u00b7 January 2026</span>',
 '<span class="say-meta">A travaill\u00e9 avec moi \u00b7 janvier 2026</span>'),
('<span class="say-meta">Same team \u00b7 September 2026</span>',
 '<span class="say-meta">M\u00eame \u00e9quipe \u00b7 septembre 2026</span>'),

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
('alt="SmartCare app, calendar date picker with busy days and days off flagged"',
 "alt=\"Application SmartCare, choix de la date avec les jours chargés et les jours fermés signalés\""),
('alt="SmartCare app, time-slot picker with morning and afternoon hour-range sliders"',
 "alt=\"Application SmartCare, choix du créneau avec des plages horaires matin et après-midi\""),
('alt="SmartCare app, visit reason screen with a searchable symptom picker"',
 "alt=\"Application SmartCare, motif de consultation avec un sélecteur de symptômes recherchable\""),
('alt="SmartCare app, appointment review screen before sending the request"',
 "alt=\"Application SmartCare, récapitulatif du rendez-vous avant l'envoi de la demande\""),
('alt="SmartCare app, success dialog confirming the appointment request was sent"',
 "alt=\"Application SmartCare, confirmation que la demande de rendez-vous a bien été envoyée\""),
('alt="SmartCare app, Android push notification confirming the appointment request"',
 "alt=\"Application SmartCare, notification push Android confirmant la demande de rendez-vous\""),
('alt="SmartCare app, doctor\'s screen to accept or reject the pending appointment request"',
 "alt=\"Application SmartCare, écran du médecin pour accepter ou refuser la demande en attente\""),
('alt="SmartCare app, urgent calls screen listing nearby ambulance requests sorted by distance, with take-charge and itinerary actions"',
 "alt=\"Application SmartCare, liste des appels urgents à proximité triés par distance, avec prise en charge et itinéraire\""),
('alt="SmartCare app, push notifications alerting that a nearby contact launched an ambulance call"',
 "alt=\"Application SmartCare, notifications push signalant qu'un contact proche a lancé un appel d'ambulance\""),
('alt="SmartCare app, urgent call detail with a Google Map of the patient location, status, and patient information"',
 "alt=\"Application SmartCare, détail d'un appel urgent avec la carte Google du lieu, le statut et les informations du patient\""),
('alt="SmartCare app, drug interaction feature, selecting several medicines then Detect interactions"',
 "alt=\"Application SmartCare, détection d'interactions : sélection de plusieurs médicaments puis lancement de l'analyse\""),
('alt="SmartCare app, drug interaction results listing flagged medicine pairs with dosage and form"',
 "alt=\"Application SmartCare, résultats des interactions listant les paires de médicaments signalées avec dosage et forme\""),
('alt="Warehouse aisle stacked with blue crates, forklifts driving between them, location pins marking tracked positions on the floor"',
 "alt=\"Allée d'entrepôt remplie de bacs bleus, des chariots élévateurs circulant entre eux, des repères marquant les positions suivies au sol\""),
('alt="Ghaith with fellow exchange student and faculty member at the Murang\'a University of Technology monument"',
 "alt=\"Ghaith avec un autre étudiant en échange et un enseignant devant le monument de Murang'a University of Technology\""),
('alt="Murang\'a University of Technology, engineering building"',
 "alt=\"Murang'a University of Technology, bâtiment d'ingénierie\""),
('alt="Murang\'a University of Technology, campus grounds"',
 "alt=\"Murang'a University of Technology, le campus\""),
]

# strings that legitimately appear more than once (both carousels share a caption)
GLOBAL = [
('aria-label="Next screen">›</button>', 'aria-label="Écran suivant">›</button>'),
('aria-label="Previous screen">‹</button>', 'aria-label="Écran précédent">‹</button>'),
]

PATHS = [
('href="style.css"', 'href="../style.css"'),
('href="fonts.css"', 'href="../fonts.css"'),
('src="script.js"', 'src="../script.js"'),
('href="assets/', 'href="../assets/'),
('src="assets/', 'src="../assets/'),
]


# ---------------------------------------------------------------- the CV sheet
CV = [
('<html lang="en">', '<html lang="fr">'),
('<title>Ghaith Mefteh — CV | Full-Stack and Mobile Engineer</title>',
 '<title>Ghaith Mefteh — CV | Ingénieur full-stack et mobile</title>'),
('<meta name="description" content="CV of Ghaith Mefteh, full-stack and mobile software engineer and technical director at AzertyUI. .NET, Symfony, Angular, Flutter. Based in Nabeul, Tunisia, open to remote work and relocation in the EU.">',
 '<meta name="description" content="CV de Ghaith Mefteh, ingénieur logiciel full-stack et mobile, directeur technique chez AzertyUI. .NET, Symfony, Angular, Flutter. Basé à Nabeul, Tunisie, ouvert au télétravail et à une mobilité dans l\'UE.">'),
('<link rel="canonical" href="https://ghaithmeftah.github.io/cv.html">',
 '<link rel="canonical" href="https://ghaithmeftah.github.io/fr/cv.html">'),

('<a class="btn btn-ghost" href="index.html">← Portfolio</a>', '<a class="btn btn-ghost" href="index.html">← Portfolio</a>'),
('<a class="btn btn-solid" href="assets/Ghaith-Mefteh-CV-EN.pdf" download>CV · full-stack (PDF)</a>',
 '<a class="btn btn-solid" href="../assets/Ghaith-Mefteh-CV-FR.pdf" download>CV · full-stack (PDF)</a>'),
('<a class="btn btn-ghost" href="assets/Ghaith-Mefteh-CV-Mobile-EN.pdf" download>CV · mobile (PDF)</a>',
 '<a class="btn btn-ghost" href="../assets/Ghaith-Mefteh-CV-Mobile-FR.pdf" download>CV · mobile (PDF)</a>'),
('<a class="btn btn-ghost" href="fr/cv.html" hreflang="fr" data-lang-switch>Version française</a>',
 '<a class="btn btn-ghost" href="../cv.html" hreflang="en" data-lang-switch>English version</a>'),
('<span>The PDFs are one-page, ATS-friendly versions.</span>',
 '<span>Les PDF sont des versions d\'une page, lisibles par les ATS.</span>'),

('alt="Portrait of Ghaith Mefteh"', 'alt="Portrait de Ghaith Mefteh"'),
('<p class="cv-role">Full-stack and mobile software engineer · technical director</p>',
 '<p class="cv-role">Ingénieur logiciel full-stack et mobile · directeur technique</p>'),
('<span>Nabeul, Tunisia · open to relocation (EU) / remote</span>',
 '<span>Nabeul, Tunisie · mobilité UE / télétravail</span>'),

('<h2>Profile</h2>', '<h2>Profil</h2>'),
("""        Engineer with 3+ years in production who leads teams of four end to end, from planning to
        deployment. Built a 10,000+ chalet rental marketplace from scratch and now a .NET
        microservices platform, and ships Flutter apps to both stores for 5,000+ people.""",
 """        Ingénieur, plus de 3 ans en production, qui dirige des équipes de quatre de bout en bout,
        de la planification au déploiement. A créé de zéro une marketplace de plus de 10&nbsp;000
        chalets, construit aujourd'hui une plateforme en microservices .NET, et publie des
        applications Flutter sur les deux stores pour plus de 5&nbsp;000 personnes."""),
('<li><b>10,000+</b><span>chalets on a marketplace I led</span></li>',
 '<li><b>+10 000</b><span>chalets sur une marketplace que j\'ai dirigée</span></li>'),
('<li><b>50 s → 5 s</b><span>search page load time on that marketplace</span></li>',
 '<li><b>50 s → 5 s</b><span>chargement de la recherche sur cette marketplace</span></li>'),
('<li><b>99.8%</b><span>crash-free sessions, SOC Rugby app</span></li>',
 '<li><b>99,8 %</b><span>de sessions sans crash, application SOC Rugby</span></li>'),

('<h2>Experience</h2>', '<h2>Expérience</h2>'),
('<h3>Technical director — AzertyUI</h3>', '<h3>Directeur technique — AzertyUI</h3>'),
('<p class="cv-job-when">2024 — present</p>', '<p class="cv-job-when">2024 — auj.</p>'),
('<p class="cv-job-org">AzertyUI · Malissard, France · remote</p>',
 '<p class="cv-job-org">AzertyUI · Malissard, France · télétravail</p>'),
('<li>Lead a <b>team of 4</b> (planning, coding, code review, deployment) building the company management platform: absences, expenses, payslips, contracts. <b>.NET microservices</b> behind an API Gateway, <b>gRPC</b> between services, <b>Angular 21</b>.</li>',
 '<li>Dirige une <b>équipe de 4</b> (planification, développement, revue de code, déploiement) sur la plateforme de gestion de l\'entreprise : absences, notes de frais, fiches de paie, contrats. <b>Microservices .NET</b> derrière une API Gateway, <b>gRPC</b> entre services, <b>Angular 21</b>.</li>'),
('<li>Built the server monitoring dashboard: SSH login tracking and alerts, per-developer <b>WireGuard VPN</b> access, container monitoring, downtime alerts, automated backups.</li>',
 '<li>Tableau de bord de supervision des serveurs : suivi des connexions SSH et alertes, accès <b>VPN WireGuard</b> par développeur, supervision des conteneurs, alertes de panne, sauvegardes automatisées.</li>'),

('<h3>Team lead — chalet-montagne.com</h3>', '<h3>Team lead — chalet-montagne.com</h3>'),
('<p class="cv-job-org">AzertyUI · ski-chalet rental marketplace, 10,000+ chalets</p>',
 '<p class="cv-job-org">AzertyUI · marketplace de location de chalets, +10 000 chalets</p>'),
('<li>Led <b>4 engineers for 14 months</b> building the platform from scratch on Symfony, SOLID and SonarQube-gated. Search pages went from <b>20–50 s to 4–6 s</b>, image bandwidth down <b>~60%</b>.</li>',
 '<li>Direction de <b>4 ingénieurs pendant 14 mois</b> pour créer la plateforme de zéro sur Symfony, selon SOLID et contrôlée par SonarQube. Pages de recherche passées de <b>20–50 s à 4–6 s</b>, bande passante images <b>~60 %</b> en moins.</li>'),
('<li>Delivered the public booking site, owner back office and admin dashboard (revenue tracking, user blocking, secure user impersonation), plus suspicious-login detection, cron jobs and <b>390+ PHPUnit tests</b> behind GitLab CI/CD.</li>',
 '<li>Livraison du site de réservation, du back-office propriétaires et du tableau de bord admin (suivi des revenus, blocage d\'utilisateurs, connexion sécurisée en tant qu\'utilisateur), plus la détection de connexions suspectes, des tâches cron et <b>+390 tests PHPUnit</b> derrière GitLab CI/CD.</li>'),

('<h3>Mobile engineer — SOC Rugby</h3>', '<h3>Ingénieur mobile — SOC Rugby</h3>'),
('<p class="cv-job-org">AzertyUI · official app of the Chambéry rugby club</p>',
 '<p class="cv-job-org">AzertyUI · application officielle du club de rugby de Chambéry</p>'),
('<li>Built and published the Flutter app to the App Store and Google Play for <b>2,000+ fans</b>: match calendar and reminders, live scores, messaging, screens translated from Figma.</li>',
 '<li>Application Flutter développée et publiée sur l\'App Store et Google Play pour <b>+2 000 supporters</b> : calendrier et rappels des matchs, scores en direct, messagerie, écrans traduits depuis Figma.</li>'),
('<li>Owned releases with Codemagic CI/CD, certificates and provisioning; <b>99.8% crash-free</b> sessions, monitored with Sentry.</li>',
 '<li>Publications portées de bout en bout avec Codemagic CI/CD, certificats et provisioning ; <b>99,8 % de sessions sans crash</b>, suivi via Sentry.</li>'),

('<h3>Mobile engineer (part-time) — SmartCare</h3>', '<h3>Ingénieur mobile (temps partiel) — SmartCare</h3>'),
('<p class="cv-job-org">Hope Horizon Health &amp; Care · Tunisia · remote</p>',
 '<p class="cv-job-org">Hope Horizon Health &amp; Care · Tunisie · télétravail</p>'),
('<li>Only mobile engineer on a patient–doctor app live on Google Play, used by <b>40+ doctors and 3,000+ patients</b>: messaging, push notifications, appointments and reminders, Google Maps, QR scanning, medical AI.</li>',
 '<li>Seul ingénieur mobile d\'une application patients–médecins disponible sur Google Play, utilisée par <b>+40 médecins et +3 000 patients</b> : messagerie, notifications push, rendez-vous et rappels, Google Maps, scan de QR codes, IA médicale.</li>'),
('<li>Built the FastAPI and MongoDB backend on AWS with GitHub Actions, and the ReactJS web.</li>',
 '<li>Développement du backend FastAPI et MongoDB sur AWS avec GitHub Actions, et du web ReactJS.</li>'),

('<h3>Engineering intern — warehouse terminal</h3>', "<h3>Stagiaire ingénieur — terminal d'entrepôt</h3>"),
('<li>Shipped <b>five warehouse-management modules</b> and a forklift tablet app on Microsoft Dynamics 365 Business Central, over C#/.NET and REST.</li>',
 "<li><b>Cinq modules de gestion d'entrepôt</b> et une application tablette pour caristes livrés sur Microsoft Dynamics 365 Business Central, en C#/.NET et REST.</li>"),

('<dt>Databases</dt>', '<dt>Bases de données</dt>'),
('<dd>Flutter, Dart, SwiftUI, GetX, Provider, Firebase, Xcode, App Store and Google Play releases</dd>',
 '<dd>Flutter, Dart, SwiftUI, GetX, Provider, Firebase, Xcode, publications App Store et Google Play</dd>'),
('<dt>Quality</dt>', '<dt>Qualité</dt>'),
('<dd>PHPUnit, PyTest, SonarQube, Sentry, code review, SOLID, AI-assisted development (Claude Code)</dd>',
 '<dd>PHPUnit, PyTest, SonarQube, Sentry, revue de code, SOLID, développement assisté par IA (Claude Code)</dd>'),

('<h2>Education</h2>', '<h2>Formation</h2>'),
('<b>Engineering degree, Applied Computer Science</b>', "<b>Diplôme d'ingénieur, informatique appliquée</b>"),
('          National School of Engineers of Sousse (ENISo), Tunisia — EUR-ACE accredited',
 "          École Nationale d'Ingénieurs de Sousse (ENISo), Tunisie — accréditation EUR-ACE"),
('<b>Summer exchange</b>', "<b>Échange d'été</b>"),
("          Murang'a University of Technology, Kenya — campus networking and a React Native registration app",
 "          Murang'a University of Technology, Kenya — réseau du campus et application d'inscription React Native"),
('<em>Jul – Aug 2024</em>', '<em>juil. – août 2024</em>'),

('<h2>Languages</h2>', '<h2>Langues</h2>'),
('<li><b>French</b><em>B2 — daily working language with French clients</em></li>',
 '<li><b>Français</b><em>B2 — langue de travail quotidienne avec les clients français</em></li>'),
('<li><b>English</b><em>B2 — TOEIC</em></li>', '<li><b>Anglais</b><em>B2 — TOEIC</em></li>'),
('<li><b>German</b><em>B1</em></li>', '<li><b>Allemand</b><em>B1</em></li>'),

('<h2>Activities</h2>', '<h2>Activités</h2>'),
('<li><b>Treasurer, IEEE IAS student branch</b>ENISo · <em>2022 – 2023</em></li>',
 '<li><b>Trésorier, branche étudiante IEEE IAS</b>ENISo · <em>2022 – 2023</em></li>'),
('<li><b>Interests</b>Gym, cycling, camping</li>', "<li><b>Centres d'intérêt</b>Musculation, cyclisme, camping</li>"),

('<h2>Availability</h2>', '<h2>Disponibilité</h2>'),
("""        Open to remote roles, relocation in the EU and freelance projects. Based at UTC+1,
        overlapping a full European day. Answers within the day. Start date on request.""",
 """        Ouvert au télétravail, à une mobilité dans l'UE et aux missions freelance. Basé à UTC+1,
        une journée européenne entière en commun. Réponse dans la journée. Date de démarrage sur
        demande."""),
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
