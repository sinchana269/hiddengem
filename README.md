# HiddenGem 🗺️

## An Intelligent Karnataka Tourism Discovery Platform Using NLP, NoSQL and UI/UX

**Built with:** Next.js · TypeScript · Tailwind CSS · FastAPI · Neo4j · spaCy

---

## 1. Project Overview

### Project Title

**HiddenGem: An Intelligent Karnataka Tourism Discovery Platform Using NLP, NoSQL and UI/UX**

### Theme

**Tourism Promotion through Innovative Approaches**

### Objective

HiddenGem is an intelligent tourism discovery platform designed to help travellers discover destinations across Karnataka based on their:

* Interests
* Activities
* Travel style
* Trip duration
* Budget
* Food preferences
* Trip type
* Group type

Instead of requiring users to browse through large lists of tourist destinations, HiddenGem allows them to describe their travel requirements using natural language.

For example:

> "I want a peaceful 2-day trip with waterfalls near Mysuru."

The system processes the query using **Natural Language Processing (NLP)**, extracts relevant travel preferences, compares them with tourism information stored in **Neo4j**, and returns personalized destination recommendations.

Users can then explore destination details and generate a destination-specific itinerary.

---

# 2. Problem Statement

Traditional tourism platforms commonly organize destinations using fixed categories such as:

* Popular destinations
* Hill stations
* Historical places
* Wildlife
* Waterfalls
* Beaches

This requires users to manually browse, filter and compare destinations.

However, travellers often describe their requirements naturally rather than using predefined categories.

For example:

> "I want a quiet weekend with nature and waterfalls."

A conventional category-based search system may not directly understand the combination of preferences in this query.

HiddenGem addresses this problem by providing a **natural-language tourism discovery interface** that extracts travel preferences and uses them to identify suitable destinations.

---

# 3. Proposed Solution

HiddenGem follows the following pipeline:

```text
User
  ↓
Natural Language Query
  ↓
NLP Query Parser
  ↓
Travel Preference Extraction
  ↓
Recommendation Engine
  ↓
Neo4j Tourism Graph
  ↓
Destination Matching
  ↓
Personalized Recommendations
  ↓
Destination Details
  ↓
Itinerary Generation
  ↓
Google Maps Route
```

The system combines natural-language search, graph-based tourism data, weighted recommendation logic and an interactive web interface.

---

# 4. Key Features

## 4.1 Natural Language Tourism Search

Users can enter travel requirements in natural language.

Examples:

```text
I want a peaceful trip near Mysuru
```

```text
I want a 2 day adventure trip with trekking
```

```text
I want waterfalls and nature near Mysuru
```

```text
I want a heritage trip with local food
```

```text
I want a weekend trip with friends
```

The NLP module processes these queries and identifies relevant travel preferences.

---

## 4.2 NLP-Based Preference Extraction

The system extracts information such as:

* Location
* Duration
* Budget
* Interests
* Activities
* Travel style
* Food preferences
* Trip type
* Group type

For example:

```text
"I want a peaceful 2-day trip with waterfalls near Mysuru"
```

can be interpreted as:

```text
Location: Mysuru
Duration: 2 days
Interest: Waterfalls
Travel style: Peaceful
```

The NLP module uses **spaCy, regular expressions and keyword-based matching** to identify these preferences.

---

## 4.3 Personalized Recommendations

The recommendation engine compares the extracted travel preferences with destination attributes stored in Neo4j.

The current base weighting is:

| Preference | Weight |
| ---------- | -----: |
| Interest   |     25 |
| Activity   |     20 |
| Location   |     20 |
| Duration   |     15 |
| Budget     |     10 |
| Food       |     10 |

These weights provide a structured method for combining multiple travel preferences.

The recommendation response can contain:

* Destination name
* Match score
* Matching reasons
* Destination description
* Category
* Best season
* Image
* Attractions
* Activities
* Food information

The matching reasons help users understand why a destination was recommended.

---

# 5. Karnataka Tourism Database

HiddenGem uses **Neo4j**, a graph-oriented NoSQL database, to represent tourism information and relationships between destinations and their associated tourism entities.

The current dataset includes:

* Mysuru
* Coorg
* Hampi
* Jog Falls
* Dandeli

The dataset contains destination descriptions and, where available, structured information about:

* Attractions
* Activities
* Food
* Opening hours
* Closing hours
* Coordinates

Different destinations currently contain different levels of structured information.

---

# 6. Destination Details

Each destination has a dedicated destination page.

The page can display:

* Destination name
* State/location
* Description
* Best time to visit
* Places to go
* Things to do
* What to eat
* Attraction information
* Opening and closing times
* Google Maps navigation
* Automated itinerary generation

The destination page follows the same visual design language as the homepage.

---

# 7. Places to Go

The destination page displays available attractions under:

## Places to go

Attraction data can be represented either as simple strings or structured attraction objects.

The frontend normalizes both formats before displaying them.

Structured attraction information can include:

* Attraction name
* Category
* Description
* Image
* Opening time
* Closing time
* Latitude
* Longitude

If no attraction information is available for a destination, the section is hidden instead of displaying an empty section.

---

# 8. Things to Do

Available activities are displayed using compact UI elements.

Examples include:

* Trekking
* Rafting
* Boating
* Photography
* Wildlife experiences
* Heritage exploration
* Camping
* Cycling

Activities can also be considered by the recommendation engine when calculating destination matches.

---

# 9. Local Food

Where tourism data is available, HiddenGem displays local food information under:

## What to eat

Examples of food-related preferences include:

* Vegetarian food
* Non-vegetarian food
* Local food
* South Indian food

Food preferences can also contribute to recommendation matching.

---

# 10. Automated Itinerary Generation

HiddenGem provides a destination-specific itinerary generator.

Users can enter requests such as:

```text
1 day, heritage and local food
```

```text
1 day, nature and photography
```

```text
2 days, peaceful and local food
```

The frontend sends the query to:

```http
POST /api/itinerary
```

The itinerary system considers available tourism information such as:

* Destination
* Attractions
* Attraction relevance
* Opening time
* Closing time
* Coordinates
* Estimated travel distance
* Estimated travel time
* Visit duration
* Meal timing
* Food preferences

A typical itinerary structure is:

```text
Breakfast
    ↓
Attraction
    ↓
Travel
    ↓
Attraction
    ↓
Lunch
    ↓
Attraction
    ↓
Dinner
```

The generated itinerary is organized day-by-day and can contain:

* Start time
* End time
* Attraction/meal name
* Travel distance
* Travel time
* Total daily distance
* Total travel time

The system also generates a Google Maps directions link for the itinerary.

### Itinerary Assumptions

The current itinerary engine uses configurable assumptions such as:

```text
Average visit duration: 90 minutes
Meal duration: 60 minutes
Travel buffer: 15 minutes
Average travel speed: 30 km/h

Day start: 9:00 AM
Breakfast start: 8:00 AM
Lunch start: 1:00 PM
Dinner start: 6:00 PM
```

Travel distances are estimated from attraction coordinates and should not be considered exact road distances.

---

# 11. Technology Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Responsive UI/UX

## Backend

* Python
* FastAPI
* Uvicorn

## NLP

* spaCy
* Regular expressions
* Keyword-based matching
* Preference extraction

## Database

* Neo4j
* Graph-based NoSQL data model

## Data Processing

* Python
* Tourism data cleaning
* Tourism website scraping

## Development

* Node.js
* npm
* Python virtual environment
* Git

---

# 12. System Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Next.js Frontend  │
                         │      React / TS      │
                         └──────────┬───────────┘
                                    │
                              HTTP / REST
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌──────────────┐       ┌──────────────┐
      │ NLP Parser  │       │ Recommendation│       │  Itinerary   │
      │   spaCy     │       │    Engine     │       │   Generator  │
      └──────┬──────┘       └──────┬───────┘       └──────┬───────┘
             │                     │                       │
             └─────────────────────┼───────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │        Neo4j         │
                         │   Tourism Graph DB   │
                         └──────────────────────┘
```

---

# 13. Project Structure

```text
hidden-gem/
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── destination/
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── globals.css
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── main.py
│   ├── recommender.py
│   ├── itinerary.py
│   │
│   ├── nlp/
│   │   └── query_parser.py
│   │
│   ├── scraper/
│   │   └── tourism_scraper.py
│   │
│   ├── requirements.txt
│   └── ...
│
├── data/
│   ├── raw/
│   └── cleaned/
│       └── scraped_destinations.json
│
├── .env.example
├── .gitignore
└── README.md
```

---

# 14. Backend API

The FastAPI backend runs locally on:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available through FastAPI Swagger:

```text
http://127.0.0.1:8000/docs
```

## 14.1 Root Endpoint

```http
GET /
```

Checks that the backend is running.

---

## 14.2 Health Endpoint

```http
GET /health
```

Returns backend health information.

---

## 14.3 API Health Endpoint

```http
GET /api/health
```

Checks API availability.

---

## 14.4 Neo4j Health Endpoint

```http
GET /api/neo4j-health
```

Checks the Neo4j database connection.

---

## 14.5 Initialize Schema

```http
GET /api/schema/init
```

Initializes the Neo4j schema required by the application.

---

## 14.6 Import Tourism Data

```http
POST /api/import
```

Imports prepared tourism data into Neo4j.

---

## 14.7 Generate Recommendations

```http
POST /api/recommend
```

### Request

```json
{
  "query": "I want a peaceful 2-day trip with waterfalls near Mysuru"
}
```

### Response

The endpoint returns information such as:

* Parsed preferences
* Recommended destinations
* Match scores
* Matching reasons

---

## 14.8 Destination Details

```http
GET /api/destination/{destination_id}
```

Example:

```text
/api/destination/hampi
```

Returns destination information and associated tourism data.

---

## 14.9 Generate Itinerary

```http
POST /api/itinerary
```

### Request

```json
{
  "query": "I want a 2 day heritage trip in Hampi"
}
```

The backend generates a structured itinerary using the available destination and attraction information.

---

# 15. NLP Module

The NLP module is located at:

```text
backend/nlp/query_parser.py
```

It combines **spaCy, regular expressions and keyword-based matching**.

## 15.1 Interests

The parser recognizes interests such as:

```text
nature
wildlife
heritage
beach
waterfalls
photography
spiritual
```

## 15.2 Activities

```text
trekking
rafting
camping
boating
cycling
wildlife
photography
heritage
```

## 15.3 Travel Styles

```text
peaceful
adventure
romantic
luxury
budget
```

## 15.4 Food Preferences

```text
vegetarian food
non-vegetarian food
local food
South Indian food
```

## 15.5 Trip Types

```text
road trip
weekend
day trip
```

## 15.6 Group Types

```text
friends
family
couple
solo
```

The parser also identifies Karnataka locations and common location aliases.

---

# 16. Recommendation Engine

The recommendation engine is located at:

```text
backend/recommender.py
```

The system uses a weighted matching approach.

Current base weights:

```text
Interest  → 25
Activity  → 20
Location  → 20
Duration  → 15
Budget    → 10
Food      → 10
```

The engine compares extracted preferences against tourism attributes associated with destinations.

It also generates matching reasons to make the recommendation output more understandable to the user.

For example:

```text
Query:
"I want a peaceful trip with waterfalls near Mysuru"

Extracted:
Location: Mysuru
Interest: Waterfalls
Travel style: Peaceful

↓

Destination Matching

↓

Recommended Destination
+ Match Score
+ Matching Reasons
```

---

# 17. Itinerary Engine

The itinerary engine is located at:

```text
backend/itinerary.py
```

It uses available attraction information and predefined planning assumptions to construct a day-by-day schedule.

The engine considers:

* Attraction relevance
* Opening time
* Closing time
* Coordinates
* Distance
* Estimated travel time
* Visit duration
* Meal timing
* Food preferences

The itinerary output is structured into days and itinerary items.

Example:

```text
Day 1

08:00 AM — Breakfast
09:00 AM — Attraction 1
10:30 AM — Travel
11:00 AM — Attraction 2
01:00 PM — Lunch
02:00 PM — Attraction 3
06:00 PM — Dinner
```

The system also provides total estimated distance and travel time.

---

# 18. Tourism Data Collection

HiddenGem includes a tourism data collection component located at:

```text
backend/scraper/tourism_scraper.py
```

The scraper is designed to collect tourism information from relevant Karnataka Tourism pages.

The data collection process includes:

* HTTP requests
* HTML parsing
* Heading extraction
* Paragraph extraction
* Section extraction
* Image extraction
* Link extraction

A request delay is used between pages to avoid sending requests continuously.

The cleaned dataset is stored at:

```text
data/cleaned/scraped_destinations.json
```

---

# 19. Current Tourism Dataset

The current cleaned tourism dataset contains five destinations:

| Destination | Attractions | Activities | Food |
| ----------- | ----------: | ---------: | ---: |
| Coorg       |           7 |          5 |    6 |
| Dandeli     |           0 |          0 |    0 |
| Hampi       |           6 |          1 |    0 |
| Jog Falls   |           5 |          2 |    0 |
| Mysuru      |           6 |          2 |    6 |

All five destinations currently contain destination descriptions.

The availability of structured attraction, activity and food information varies between destinations.

This difference is reflected in the recommendation and destination-detail experience.

---

# 20. Neo4j Data Model

Neo4j is used as the NoSQL graph database for HiddenGem.

A simplified conceptual model is:

```text
Destination
     │
     ├── HAS_ATTRACTION ──> Attraction
     │
     ├── HAS_ACTIVITY ────> Activity
     │
     └── HAS_FOOD ────────> Food
```

An attraction can contain properties such as:

```text
name
latitude
longitude
opening_time
closing_time
```

The graph structure allows tourism entities and their relationships to be represented naturally.

---

# 21. Frontend

The main homepage is located at:

```text
frontend/app/page.tsx
```

The destination page is located at:

```text
frontend/app/destination/[id]/page.tsx
```

The homepage provides:

* Navigation
* Hero section
* Natural-language search
* Category exploration
* Travel preference summary
* Personalized recommendations
* Destination cards
* Light/dark mode
* Text-size controls
* Scroll-to-top interaction

The destination page provides:

* Destination information
* Places to go
* Things to do
* Local food
* Itinerary generation
* Google Maps navigation

---

# 22. UI/UX Design

HiddenGem follows a nature-inspired visual identity based on Karnataka tourism.

### Primary Green

```text
#174d35
```

### Dark Green

```text
#102b1e
```

### Gold

```text
#c8943e
```

### Light Background

```text
#f7f5ef
```

### Dark Background

```text
#101713
```

### Light Green Surface

```text
#e8f0ea
```

### Dark Card

```text
#18211c
```

The interface uses:

* Rounded cards
* Soft borders
* Subtle shadows
* Large tourism imagery
* Gold accent typography
* Dark green primary buttons
* Responsive layouts
* Light and dark themes
* Consistent spacing and typography

The homepage and destination pages use the same visual language to provide a consistent user experience.

---

# 23. Accessibility and User Experience

The frontend includes several usability and accessibility features:

* Semantic headings
* Accessible button labels
* Keyboard interaction for search
* Responsive layouts
* Text-size controls
* Light/dark mode
* Visible focus states
* Alternative text for images
* Reduced-motion support

Theme and text-size preferences are stored locally in the browser.

---

# 24. Example User Flow

### Step 1 — Open HiddenGem

The user opens the HiddenGem tourism platform.

### Step 2 — Enter a Natural-Language Query

For example:

```text
I want a peaceful 2-day trip with waterfalls near Mysuru
```

### Step 3 — Send Query

The frontend sends:

```json
{
  "query": "I want a peaceful 2-day trip with waterfalls near Mysuru"
}
```

to:

```http
POST /api/recommend
```

### Step 4 — Extract Preferences

The NLP module identifies relevant information such as:

```text
Location → Mysuru
Duration → 2 days
Interest → Waterfalls
Travel Style → Peaceful
```

### Step 5 — Match Destinations

The recommendation engine compares the extracted preferences with tourism data stored in Neo4j.

### Step 6 — Display Recommendations

The user receives destination suggestions with match scores and matching reasons.

### Step 7 — Explore a Destination

The user selects a destination and opens its dedicated page.

### Step 8 — View Destination Information

The page displays:

```text
Destination
     ↓
Description
     ↓
Places to Go
     ↓
Things to Do
     ↓
What to Eat
```

### Step 9 — Build an Itinerary

The user enters a request such as:

```text
1 day, heritage and local food
```

### Step 10 — View Travel Plan

The system generates:

```text
Day 1
   ↓
Breakfast
   ↓
Attraction
   ↓
Travel
   ↓
Attraction
   ↓
Lunch
   ↓
Attraction
   ↓
Dinner
```

The user can then open the generated route in Google Maps.

---

# 25. Example Queries

Users can try:

```text
I want a peaceful trip near Mysuru
```

```text
I want a 2 day heritage trip
```

```text
I want an adventure trip with trekking
```

```text
I want waterfalls and photography
```

```text
I want wildlife near Karnataka
```

```text
I want local food and heritage
```

```text
I want a weekend trip with friends
```

```text
I want a budget trip for 2 days
```

```text
I want a peaceful nature trip with my family
```

---

# 26. Testing

The NLP parser has been manually tested against representative tourism queries.

Current manual test result:

```text
6 / 6 manual tests passed
```

The backend can also be checked using:

```http
GET /health
```

and:

```http
GET /api/neo4j-health
```

FastAPI Swagger provides an interactive interface for testing backend endpoints.

---

# 27. Error Handling

The frontend handles situations such as:

* Empty search queries
* Backend connection failures
* Failed recommendation requests
* Empty recommendation results
* Missing destination images
* Missing attraction information
* Missing optional destination fields

For example, when an image cannot be loaded, the destination interface displays a fallback visual instead of leaving a broken image element.

Similarly, unavailable backend services produce an appropriate error message instead of causing the application to crash.

---

# 28. Image Handling

Destination images are loaded dynamically from destination data.

The frontend provides fallback UI when an image cannot be loaded.

Images can use:

```text
loading="lazy"
```

where appropriate.

External image requests use:

```text
referrerPolicy="no-referrer"
```

to reduce loading problems with external image hosts.

---

# 29. Security and Privacy

HiddenGem does not require sensitive personal information for its basic recommendation workflow.

The recommendation process primarily uses the travel query entered by the user.

Theme and text-size preferences are stored locally in the browser.

Neo4j connection credentials are configured through environment variables rather than being hard-coded into the application.

---

# 30. Current Project Scope

The current implementation focuses on:

```text
Karnataka
    ↓
Tourism Discovery
    ↓
Natural Language Search
    ↓
Preference Extraction
    ↓
Personalized Recommendations
    ↓
Destination Information
    ↓
Itinerary Generation
    ↓
Travel Route
```

The project demonstrates the integration of:

* Natural Language Processing
* NoSQL graph databases
* Recommendation systems
* Web development
* UI/UX
* Tourism data processing
* Automated itinerary planning

---

# 31. Advantages

HiddenGem provides:

1. Natural-language tourism search.
2. Personalized destination discovery.
3. Graph-based tourism data management.
4. Preference-aware recommendations.
5. Destination-specific information.
6. Automated itinerary generation.
7. Food-preference consideration.
8. Responsive user interface.
9. Light and dark themes.
10. A tourism-focused user experience.

---

# 32. Limitations

## 32.1 Tourism Dataset

Recommendation quality depends on the availability and completeness of structured tourism data.

Some destinations currently contain more detailed information than others.

## 32.2 Travel Distance

Itinerary travel distances are estimated using attraction coordinates and an assumed average travel speed.

They are not guaranteed road distances.

## 32.3 NLP

The current NLP system primarily uses spaCy, keywords and regular expressions rather than a large language model.

Therefore, highly complex or unusual natural-language queries may not always be interpreted correctly.

## 32.4 Real-Time Information

The current system does not provide guaranteed real-time information about:

* Traffic
* Weather
* Hotel availability
* Ticket availability
* Attraction crowd levels

---

# 33. Future Enhancements

Possible future improvements include:

* Adding more Karnataka destinations
* Adding more tourism attributes
* Improving semantic NLP
* Supporting multilingual queries
* Kannada-language support
* Real-time weather integration
* Real road-distance calculations
* Hotel recommendations
* Transport information
* Tourism event information
* User accounts
* Saved trips
* Trip history
* More advanced recommendation algorithms
* Mobile application
* Larger tourism knowledge graph

These are proposed future enhancements and are not part of the current implementation unless explicitly implemented later.

---

# 34. Prerequisites

| Tool    | Version  |
| ------- | -------- |
| Node.js | ≥ 18     |
| Python  | ≥ 3.10   |
| npm     | ≥ 9      |
| Neo4j   | Required |

---

# 35. Environment Variables

Create a `.env` file based on `.env.example`.

| Variable              | Description                      |
| --------------------- | -------------------------------- |
| `NEO4J_URI`           | Neo4j connection URI             |
| `NEO4J_USERNAME`      | Neo4j username                   |
| `NEO4J_PASSWORD`      | Neo4j password                   |
| `NEXT_PUBLIC_API_URL` | Backend URL used by the frontend |

Example Neo4j URI:

```text
bolt://localhost:7687
```

Do not commit credentials or secrets to Git.

---

# 36. Running the Project

## Step 1 — Start Neo4j

Make sure Neo4j is running and accessible.

Configure the required Neo4j connection values in the backend environment.

---

## Step 2 — Start the Backend

Open a terminal:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment variables.

### Windows

```powershell
copy ..\.env.example .env
```

### macOS/Linux

```bash
cp ../.env.example .env
```

Edit `.env` with the required Neo4j credentials.

Start FastAPI:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 37. Running the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

The frontend normally runs at:

```text
http://localhost:3000
```

---

# 38. Frontend API Configuration

The frontend uses an environment variable to determine the backend URL.

The recommended variable is:

```text
NEXT_PUBLIC_API_BASE_URL
```

If the variable is not provided, the destination page currently falls back to:

```text
http://127.0.0.1:8000
```

For local development, a frontend `.env.local` file can be configured with the backend URL.

Example:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

# 39. Quick Start

### Backend

```bash
cd backend

python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 40. Workflow Summary

```text
                         USER
                           │
                           ▼
                 Natural Language Query
                           │
                           ▼
                    NLP Query Parser
                           │
                           ▼
              Extract Travel Preferences
                           │
                           ▼
                 Recommendation Engine
                           │
                           ▼
                    Neo4j Graph DB
                           │
                           ▼
                  Destination Matching
                           │
                           ▼
                  Personalized Results
                           │
                           ▼
                Destination Information
                           │
                           ▼
                 Itinerary Generation
                           │
                           ▼
                    Travel Plan
                           │
                           ▼
                    Google Maps
```

---

# 41. Conclusion

HiddenGem demonstrates how **Natural Language Processing, NoSQL graph databases, recommendation algorithms and modern UI/UX** can be combined to create an intelligent tourism discovery platform.

Instead of requiring travellers to manually browse through large lists of destinations, HiddenGem allows them to describe what they want from a trip using natural language.

The system extracts travel preferences, matches them with Karnataka tourism data stored in a Neo4j graph database, provides destination recommendations, presents detailed destination information and generates an itinerary based on available tourism data.

The project therefore demonstrates a practical application of **NLP, NoSQL, recommendation systems, web development and UI/UX for tourism promotion**.

---

# 42. Project Summary

| Component            | Implementation                   |
| -------------------- | -------------------------------- |
| Domain               | Karnataka Tourism                |
| Frontend             | Next.js, React, TypeScript       |
| Styling              | Tailwind CSS                     |
| Backend              | Python, FastAPI                  |
| Database             | Neo4j                            |
| Database Type        | NoSQL Graph Database             |
| NLP                  | spaCy + Regex + Keyword Matching |
| Recommendation       | Weighted Preference Matching     |
| Itinerary            | Rule/constraint-based generation |
| Data Collection      | Python-based tourism scraping    |
| Navigation           | Google Maps Directions           |
| UI                   | Responsive, Light/Dark Theme     |
| Current Destinations | 5                                |
| Manual NLP Tests     | 6/6                              |

---

# HiddenGem 🗺️

### Discover Karnataka differently.

> Find places, experiences and journeys worth discovering across Karnataka.
