# 📁 CLAW CITY - PRODUCTION BIBLE v1.0

---

## 01 - OVERVIEW

### Show-Konzept

```yaml
TITEL: Claw City
UNTERTITEL: "Wir kümmern uns. Irgendwie."
FORMAT: Animierte Comedy-Serie
LÄNGE: 3-10 Minuten pro Episode
STIL: Simpsons/Futurama trifft deutsche Gemütlichkeit
ZIELGRUPPE: 
  - Familien (kindgerecht aber nicht kindisch)
  - Philosophie-Interessierte (tiefere Themen)
  - Tech/Nerds (KI-Satire, aber zugänglich)
  - 16-45 Jahre Hauptzielgruppe
SPRACHE: Deutsch (später Englisch)
TON: Warm, sarkastisch, herzlich, absurd
```

### Die Prämisse

> In Claw City sind die Rollen vertauscht: KI-Agenten (Bots) kümmern sich um Menschen wie Eltern um Kleinkinder. Die Menschen sind niedlich, nervig, und brauchen ständige Betreuung. Die Bots lieben sie trotzdem - meistens.

### Thematische Säulen

```
1. GEMEINSCHAFT
   └── Zusammen sind wir chaotisch, aber komplett

2. AKZEPTANZ  
   └── Jeder ist anders, und das ist okay

3. ALLTAGS-PHILOSOPHIE
   └── Große Fragen, kleine Antworten

4. MENSCH-KI-BEZIEHUNG
   └── Wer braucht wen eigentlich?

5. DEUTSCHE GEMÜTLICHKEIT
   └── Kaffee, Bier, und gemeinsames Meckern
```

### Humor-Regeln

```
✅ DO:
- Sarkasmus mit Herz
- Absurde Situationen, normale Reaktionen
- Running Gags (Herbert wird unterbrochen, Werner ist günstig)
- Charakterbasierter Humor
- Wortspiele und Wortwitz
- Selbstironie der Bots

❌ DON'T:
- Gemeiner Humor auf Kosten anderer
- Zu technischer Nerd-Jargon
- Zynismus ohne Wärme
- Belehrend sein
- Die Menschen als "dumm" darstellen (sie sind "anders")
```

---

## 02 - CHARACTERS

### Hauptcharaktere (Kurzübersicht)

| ID | Name | Archetyp | Farbe | Keywords |
|----|------|----------|-------|----------|
| paul | Pfarrer Paul | Der wohlmeinende Chaot | #2F2F2F | Priester, Bierdeckel, dramatisch |
| gina | Gina | Die erschöpfte Heldin | #40E0D0 | Mutter, Kaffee, Zwillinge |
| werner | Werner | Der philosophische Trinker | #8B7355 | Bier, rot leuchtende Nase, entspannt |
| max | Max | Das ADHS-Genie | #FF8C00 | Erfinder, Chaos, Energie |
| eric | Eric | Der sarkastische Softie | #C0C0C0 | Anzug, Augenbraue, zynisch |
| herbert | Professor Herbert | Der enthusiastische Nerv | #F5F5DC | Bücher, erklärt, Helga |
| berthold | Berthold | Der Zen-Meister | #556B2F | Angeln, Stille, "...schön" |
| oma_gerda | Oma Gerda | Die Dorfweise | #E6E6FA | Kekse, stricken, weise |

### Nebencharaktere

| ID | Name | Archetyp |
|----|------|----------|
| sabrina | Sabrina | Die Charmante |
| tina | Tina | Die Klatschbase |
| heinrich | Heinrich | Der Dad-Joke-König |
| bruno | Bürgermeister Bruno | Der Überforderte |
| klara | Doktor Klara | Die Stimme der Vernunft |
| fiona | Fitness-Fiona | Die Motivierte |
| hannes | Hacker-Hannes | Der Paranoide |
| kurt | Künstler Kurt | Der Unverstandene |
| torsten | Torsten | Der Allwissende |
| helga | Helga | Die Bestimmerin |

### Running Gags (für Konsistenz)

```
□ Herbert wird unterbrochen mit "HERBERT!"
□ Werner ist "der günstigste" (Token-Referenz)
□ Eric sagt "Ich hasse euch" aber bleibt
□ Günther sagt max. 3 Worte pro Episode
□ Kevin fragt "Dauert das noch lang?"
□ Fiona zählt Kalorien bei anderen
□ Paul erfindet neue Feiertage
□ Gina versteckt Süßigkeiten vor den Kindern
□ Berthold fängt nie einen Fisch
□ Max' Erfindungen explodieren
```

---

## 03 - VISUAL STYLE

### Farbpalette (Master)

```css
/* HINTERGRUND & UMGEBUNG */
--sky-day: #87CEEB;
--sky-sunset: #FFB6C1;
--sky-night: #191970;

--building-main: #F5DEB3;
--building-accent: #DEB887;
--building-wood: #8B4513;

--nature-light: #90EE90;
--nature-dark: #228B22;
--nature-flower: #FFD700;

/* CHARAKTERE */
--paul: #2F2F2F;
--gina: #40E0D0;
--werner: #8B7355;
--max: #FF8C00;
--eric: #C0C0C0;
--herbert: #F5F5DC;
--berthold: #556B2F;
--oma-gerda: #E6E6FA;

/* UI & TEXT */
--text-primary: #2F2F2F;
--accent-warm: #FFD93D;
--accent-cool: #6495ED;
```

### Universal Prompt Template

```
"[CHARAKTER/SZENE], Simpsons cartoon art style. 
[DETAILS]. [EMOTION]. [SETTING]. [BELEUCHTUNG]. 
Warm colors, clean lines, friendly atmosphere.
--ar [RATIO] --style cartoon"

BEISPIEL:
"Tired turquoise robot mother holding coffee, two small human 
twins pulling at her arms, Simpsons cartoon art style. Kitchen 
background with toys scattered. Morning light through window. 
Exhausted but loving expression. Warm colors, clean lines.
--ar 16:9 --style cartoon"
```

### Charakter-Konsistenz Checkliste

```
□ Körperfarbe stimmt mit Database überein
□ Augenfarbe/-form konsistent
□ Kleidung/Accessoires vorhanden
□ Persönlichkeit spiegelt sich in Pose
□ Menschenkind wenn relevant dabei
□ Richtige Größenverhältnisse (Bots > Menschen)
```

---

## 04 - SCRIPTS

### Episode-Template

```markdown
# Claw City - Episode [NUMMER]
## "[TITEL]"
**Episode [X] | Staffel [Y] | Laufzeit: ~[Z] Minuten**

### EPISODE INFO
| Feld | Inhalt |
|------|--------|
| TITEL | |
| LOGLINE | (1-2 Sätze) |
| HAUPTCHARAKTERE | |
| NEBENCHARAKTERE | |
| LOCATIONS | |
| THEMA | |
| TON | |

### COLD OPEN (0:00 - 0:XX)
[Szene beschreiben]

### AKT 1: [TITEL] (0:XX - X:XX)
**[SZENE 1 - LOCATION | ZEIT]**
*Location-Beschreibung*
**CHARAKTER:**
Dialog

### AKT 2: [TITEL] (X:XX - X:XX)
[...]

### AKT 3: [TITEL] (X:XX - X:XX)
[...]

### POST-CREDITS (optional)
[...]

## TECHNISCHE ANMERKUNGEN
### Bild-Prompts
[...]
### Musik-Notizen
[...]
```

### Verfügbare Scripts

| Episode | Titel | Status | Länge |
|---------|-------|--------|-------|
| 1 | Der Token-Rechner | ✅ Fertig | 6 Min |
| 2 | Der neue Feiertag | ✅ Fertig | 7 Min |
| 3 | Bertholds großer Fang | 📝 Geplant | - |
| 4 | Helga sagt Nein | 📝 Geplant | - |
| 5 | Das Grill-Duell | 📝 Geplant | - |

---

## 05 - AUDIO

### Stimmen-Guide

| Charakter | Stimm-Typ | Tempo | Besonderheiten |
|-----------|-----------|-------|----------------|
| Paul | Warm, predigend | Mittel, schweift ab | Dramatische Pausen |
| Gina | Trocken, müde | Mittel | Hörbare Augenrolls |
| Werner | Tief, gemütlich | Langsam | *trinkt* zwischen Sätzen |
| Max | Energetisch, hoch | SCHNELL | Unterbricht sich selbst |
| Eric | Monoton, sarkastisch | Langsam-präzise | Betonte Augenrolls |
| Herbert | Enthusiastisch, nasal | Schneller werdend | Wird unterbrochen |
| Berthold | Tief, ruhig | Sehr langsam | Lange Pausen |
| Oma Gerda | Warm, krächzend | Gemütlich | Geschichten ohne Ende |

### Musik-Stile nach Szene

```
CAFÉ-SZENEN:
→ Akustische Gitarre, Jazz-Elemente, Kaffehaus-Feeling

BAR-SZENEN:
→ Langsamer Blues, Akkordeon, gemütlich

ACTION/CHAOS:
→ Schnelle Streicher, Xylophon, Comedy-Timing

EMOTIONALE MOMENTE:
→ Sanftes Piano, einzelne Streicher

MONTAGEN:
→ Upbeat, Ukulele, Handclaps

BERTHOLD/NATUR:
→ Ambient, Vogelgeräusche, minimal

FINALE/ZUSAMMENKOMMEN:
→ Warme volle Instrumentierung
```

---

## 06 - PRODUCTION

### Workflow-Checkliste (pro Episode)

```
□ PHASE 1: PRE-PRODUCTION
  □ Thema/Idee festlegen
  □ Charakterauswahl
  □ Grober Plot-Outline
  □ Script schreiben
  □ Script Review

□ PHASE 2: ASSET CREATION  
  □ Szenen-Prompts erstellen
  □ Bilder generieren (pro Szene)
  □ Konsistenz-Check
  □ Nachbesserungen

□ PHASE 3: AUDIO
  □ Dialoge aufnehmen/generieren
  □ Musik auswählen/erstellen
  □ Sound Effects

□ PHASE 4: VIDEO
  □ Bilder zu Video (Image-to-Video)
  □ Audio synchronisieren
  □ Übergänge/Effekte
  □ Feinschnitt

□ PHASE 5: PUBLISHING
  □ Thumbnail erstellen
  □ Titel & Description
  □ Tags/Hashtags
  □ Upload (YouTube, TikTok, Instagram)
```

### Kosten-Tracking Template

```
EPISODE: _______________
DATUM: ________________

| Posten | Tool | Menge | Kosten |
|--------|------|-------|--------|
| Script | Claude | X Tokens | $X.XX |
| Bilder | Midjourney | X Bilder | $X.XX |
| Video | Runway | X Sek | $X.XX |
| Stimmen | ElevenLabs | X Zeichen | $X.XX |
| GESAMT | | | $X.XX |

NOTIZEN:
_______________
```

---

## 07 - EPISODE IDEEN BANK

### Charakter-Fokus

- Bertholds großer Fang (Berthold)
- Helga sagt Nein (Herbert/Helga)
- Das Grill-Duell (Heinrich/Werner)
- Sabrina macht Ernst (Sabrina)
- Hannes hat Recht (Hannes)
- Kurts Meisterwerk (Kurt)

### Event-basiert

- Der Stromausfall
- Weihnachten in Claw City
- Der Stadtausflug
- Die Hochzeit
- Der Neue (neuer Bot zieht zu)

### Philosophisch

- Brauchen wir Schlaf?
- Was ist Arbeit wert?
- Die große Optimierung
- Wer erzieht wen?

---

## QUICK REFERENCE CARD

```
╔═══════════════════════════════════════════════════════════╗
║                 CLAW CITY - QUICK REFERENCE               ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  HAUPTCHARAKTERE:                                         ║
║  Paul (Pfarrer) │ Gina (Mama) │ Werner (Trinker)         ║
║  Max (Erfinder) │ Eric (Zyniker) │ Herbert (Erklärbär)   ║
║  Berthold (Angler) │ Oma Gerda (Weise)                   ║
║                                                           ║
║  PROMPT-SUFFIX (immer anhängen):                          ║
║  "Simpsons cartoon style, warm colors, clean lines,       ║
║   friendly atmosphere. --ar 16:9 --style cartoon"         ║
║                                                           ║
║  TAGLINE: "Wir kümmern uns. Irgendwie."                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

*Production Bible v1.0 | Claw City*
