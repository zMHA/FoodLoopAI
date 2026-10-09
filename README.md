# FoodLoop AI 🌱

### Rescue Surplus Food. Reduce Waste. Strengthen Communities.

**FoodLoop AI** is an AI + Climate hackathon MVP designed to help businesses redistribute surplus food to eligible recipient organizations. It combines transparent, explainable recipient ranking with donation reservation and rescue tracking to demonstrate how technology can support food recovery and more efficient resource use.

The platform helps users create surplus food listings, identify suitable recipients, coordinate reservations, and track completed food rescues through a simple interactive dashboard.

> **Project status:** Hackathon MVP
> **Track:** AI + Climate
> **Core approach:** Explainable, rule-based recipient matching
> **Application:** Python + Streamlit

---

## 🌍 The Problem

Edible surplus food can go unused while community organizations face challenges sourcing food for the people they serve. Coordinating donations involves more than finding a recipient: food categories, recipient capacity, pickup availability, distance, and collection deadlines all matter.

FoodLoop AI explores how a transparent digital workflow can help connect surplus food with suitable recipient organizations and make donation coordination easier to demonstrate, evaluate, and improve.

## 💡 Our Solution

FoodLoop AI provides a lightweight workflow for managing surplus food donations, from listing available food to recording completed collections.

Its explainable matching system ranks eligible recipient organizations using configurable criteria and presents the reasons behind the ranking. This makes the matching process easier to inspect and understand than an unexplained score.

The MVP uses synthetic demonstration records and local JSON persistence, making it suitable for local demonstrations and early-stage experimentation.

## ✨ Key Features

* **📊 Overview Dashboard** — View available surplus listings, donation status, and recorded rescue metrics.
* **🥗 Surplus Food Listings** — Create listings with food categories, quantities, storage notes, and pickup deadlines.
* **🤖 Explainable Recipient Matching** — Rank candidate organizations using category compatibility, capacity, pickup availability, distance, and urgency.
* **🔍 Matching Explanations** — Inspect the factors contributing to recipient rankings and understand why a candidate is suitable.
* **📦 Donation Reservations** — Reserve a listing for a selected recipient organization.
* **✅ Rescue Tracking** — Mark reserved donations as collected and update their recorded status.
* **📈 Impact Reporting** — Summarize completed donations and estimate meal portions using a configurable conversion.
* **📄 CSV Export** — Export donation records for reporting and further analysis.
* **💾 Local Data Persistence** — Store demo application data in JSON files between local runs.

## 🧠 How the Matching System Works

FoodLoop AI uses a **transparent weighted-ranking heuristic**, not a trained machine-learning model.

The system evaluates recipient candidates against relevant donation requirements and assigns scores based on configured matching criteria.

| Matching criterion          | Purpose                                                                                            |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| Food category compatibility | Assesses whether the recipient can use the listed food category.                                   |
| Recipient capacity          | Considers whether the organization can accommodate the donation quantity.                          |
| Pickup availability         | Evaluates whether collection can be arranged within the required timeframe.                        |
| Distance                    | Considers the distance between the donor and recipient, based on the application's available data. |
| Urgency                     | Accounts for the listing's pickup deadline and time sensitivity.                                   |

The ranking is intended to support decision-making, not replace human judgment or food-safety checks. A high score does not independently establish that a donation is safe, legally compliant, or operationally feasible.

**Important:** The table describes the matching criteria at a conceptual level. Actual eligibility rules, score weights, normalization, and tie-breaking behavior should be verified against `app.py` before being documented as exact implementation details.

## 🛠️ Technology Stack

* **Python** — Application logic and data processing
* **Streamlit** — Interactive web application and dashboard
* **Pandas** — Tabular data handling and reporting
* **Weighted heuristic ranking** — Explainable recipient prioritization
* **JSON** — Local persistence for demonstration data
* **CSV** — Donation record export

## 🚀 Getting Started

### Prerequisites

* Python 3.10 or later
* Git
* A terminal such as Windows PowerShell, macOS Terminal, or Linux shell

### 1. Clone the repository

```bash
git clone https://github.com/zMHA/FoodLoopAI.git
cd FoodLoopAI
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks virtual-environment activation, consult the Python documentation or your system's PowerShell execution-policy guidance.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch FoodLoop AI

```bash
streamlit run app.py
```

Streamlit will display a local URL in your terminal, usually:

```text
http://localhost:8501
```

Open that URL in your browser to interact with the application.

## 🎬 Hackathon Demo Walkthrough

A suggested 2–4 minute demonstration:

1. **Explore the dashboard:** Introduce the surplus listings and current donation statuses.
2. **Create a listing:** Add a sample food donation with a quantity, category, and pickup deadline.
3. **Run recipient matching:** Select the listing and inspect the ranked recipient organizations.
4. **Explain the ranking:** Show how category compatibility, capacity, pickup availability, distance, and urgency contribute to the recommendations.
5. **Reserve the donation:** Select an eligible recipient and record the reservation.
6. **Complete the rescue:** Mark the reserved donation as collected.
7. **Review the impact report:** Show the updated completed-donation metrics and estimated meal portions.
8. **Clarify the demonstration data:** Explain which records are synthetic and which metrics are illustrative rather than verified real-world outcomes.

## 📊 Impact Measurement

FoodLoop AI demonstrates how donation workflows can record potential food recovery activity. Its impact report may include completed donation counts and estimated meal portions.

These measures must be interpreted carefully:

* **Listed food is not rescued food.** A listing alone does not establish that a donation was collected.
* **A reservation is not a completed rescue.** Completion metrics should reflect the application's recorded collection status.
* **Estimated portions are not verified meals served.** Estimates depend on the configured conversion and the underlying quantity data.
* **Environmental benefits are not automatically measured.** Avoid reporting avoided emissions, landfill diversion, or other climate benefits without an appropriate methodology and supporting evidence.

For a production deployment, impact calculations should document their units, conversion assumptions, data provenance, and verification process.

## 🔐 Data, Safety, and Limitations

* **Synthetic demo data:** Seed listings and recipient profiles are fictional demonstration records and should not be presented as verified organizations or actual donations.
* **No trained ML model:** Matching uses a weighted heuristic; its scores are not probabilities, learned predictions, or evidence of model accuracy.
* **Local storage:** JSON persistence is intended for a prototype. It does not provide the reliability, concurrency controls, access management, or auditability expected of a production database.
* **Food safety:** Users must verify applicable local food-donation requirements, storage and temperature controls, allergens, packaging, collection arrangements, and recipient eligibility before a real donation.
* **Operational verification:** A recommendation does not guarantee recipient acceptance, transport availability, food safety, or successful collection.
* **Privacy and security:** The MVP should not be assumed to provide production-grade authentication, authorization, encryption, or audit logging.

## 🛣️ Roadmap

Potential next steps toward a production-ready food recovery platform:

* [ ] Add authentication and separate donor and recipient roles.
* [ ] Introduce a managed database and reliable transaction handling.
* [ ] Verify recipient organizations and food-safety eligibility.
* [ ] Integrate geocoding and more reliable route-distance calculations.
* [ ] Add notifications, reservation expiry, and pickup confirmations.
* [ ] Evaluate matching weights against real, consented donation outcomes.
* [ ] Improve data validation, error handling, privacy, and security.
* [ ] Add audit logs and operational monitoring.
* [ ] Develop a documented methodology for estimating environmental benefits.

## 🌱 Hackathon Track: AI + Climate

FoodLoop AI explores the intersection of **explainable AI-inspired decision support, food recovery, and climate-conscious resource use**.

By making surplus listings, recipient prioritization, reservations, and collection tracking part of one workflow, the project demonstrates a potential digital approach to improving coordination between food donors and recipient organizations.

Its current contribution is a functional prototype and a transparent matching workflow—not a claim of proven waste reduction or measured climate impact.

## 📁 Repository Structure

```text
FoodLoopAI/
├── app.py
├── data/
├── requirements.txt
├── README.md
└── .gitignore
```

The `data/` directory contains local application data or demo records, depending on the current project configuration. Local virtual-environment files are excluded from version control.

## 📜 License

No license has been specified yet. Until a license is added, the repository should not be assumed to grant permission to reuse, modify, or redistribute its code.

---

**FoodLoop AI — Making Surplus Food Recovery Easier to Coordinate.**
