
import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="FoodLoop AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
FOOD_FILE = DATA_DIR / "donations.json"
ORG_FILE = DATA_DIR / "organizations.json"

CATEGORIES = [
    "Produce", "Bakery", "Prepared meals",
    "Dairy", "Packaged goods", "Other",
]
STORAGE_OPTIONS = [
    "Ambient",
    "Ambient / cool",
    "Refrigerated",
    "Keep refrigerated / hot-hold as applicable",
]
STATUSES = ["Available", "Reserved", "Collected", "Cancelled"]

SEED_FOOD = [
    {
        "id": "FL-1001",
        "food": "Fresh produce boxes",
        "category": "Produce",
        "quantity_kg": 18.0,
        "meals_per_kg": 2.0,
        "donor": "Green Basket Market",
        "address": "Campus District",
        "lat": 37.7749,
        "lon": -122.4194,
        "listed_at": datetime.now().isoformat(timespec="minutes"),
        "pickup_by": (
            datetime.now() + timedelta(hours=5)
        ).isoformat(timespec="minutes"),
        "storage": "Ambient / cool",
        "notes": "Apples, carrots and leafy greens; inspected at listing.",
        "status": "Available",
        "recipient": "",
    },
    {
        "id": "FL-1002",
        "food": "Bakery assortment",
        "category": "Bakery",
        "quantity_kg": 12.0,
        "meals_per_kg": 1.5,
        "donor": "Sunrise Bakery",
        "address": "Market Street",
        "lat": 37.7790,
        "lon": -122.4140,
        "listed_at": datetime.now().isoformat(timespec="minutes"),
        "pickup_by": (
            datetime.now() + timedelta(hours=3)
        ).isoformat(timespec="minutes"),
        "storage": "Ambient",
        "notes": "Bread and rolls, packed today.",
        "status": "Available",
        "recipient": "",
    },
    {
        "id": "FL-1003",
        "food": "Prepared vegetarian meals",
        "category": "Prepared meals",
        "quantity_kg": 10.0,
        "meals_per_kg": 1.0,
        "donor": "Campus Kitchen",
        "address": "University Avenue",
        "lat": 37.7695,
        "lon": -122.4150,
        "listed_at": datetime.now().isoformat(timespec="minutes"),
        "pickup_by": (
            datetime.now() + timedelta(hours=2)
        ).isoformat(timespec="minutes"),
        "storage": "Keep refrigerated / hot-hold as applicable",
        "notes": (
            "Only accept if safe temperature control and local "
            "food-safety rules can be maintained."
        ),
        "status": "Available",
        "recipient": "",
    },
    {
        "id": "FL-1004",
        "food": "Sealed dairy products",
        "category": "Dairy",
        "quantity_kg": 8.0,
        "meals_per_kg": 1.0,
        "donor": "Corner Grocer",
        "address": "Civic Center",
        "lat": 37.7810,
        "lon": -122.4200,
        "listed_at": datetime.now().isoformat(timespec="minutes"),
        "pickup_by": (
            datetime.now() + timedelta(hours=8)
        ).isoformat(timespec="minutes"),
        "storage": "Refrigerated",
        "notes": "Sealed items; verify labels and cold chain before accepting.",
        "status": "Available",
        "recipient": "",
    },
]

SEED_ORGS = [
    {
        "name": "Community Kitchen A",
        "type": "Community kitchen",
        "categories": ["Produce", "Bakery", "Prepared meals"],
        "capacity_kg": 35.0,
        "distance_km": 1.2,
        "pickup_available": True,
        "storage": STORAGE_OPTIONS,
        "people_served": 80,
    },
    {
        "name": "Neighborhood Food Bank",
        "type": "Food bank",
        "categories": ["Produce", "Bakery", "Dairy"],
        "capacity_kg": 50.0,
        "distance_km": 3.5,
        "pickup_available": True,
        "storage": ["Ambient", "Ambient / cool", "Refrigerated"],
        "people_served": 120,
    },
    {
        "name": "Student Support Pantry",
        "type": "Student pantry",
        "categories": ["Produce", "Bakery", "Dairy"],
        "capacity_kg": 15.0,
        "distance_km": 2.4,
        "pickup_available": False,
        "storage": ["Ambient", "Ambient / cool", "Refrigerated"],
        "people_served": 40,
    },
    {
        "name": "Shelter C",
        "type": "Shelter",
        "categories": ["Bakery", "Prepared meals"],
        "capacity_kg": 8.0,
        "distance_km": 4.8,
        "pickup_available": True,
        "storage": [
            "Ambient",
            "Keep refrigerated / hot-hold as applicable",
        ],
        "people_served": 35,
    },
]


# ---------------------------------------------------------
# DATA STORAGE
# ---------------------------------------------------------

def load_json(path, seed):
    """Load local JSON data or initialize a missing file."""
    if not path.exists():
        path.write_text(
            json.dumps(seed, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return json.loads(json.dumps(seed))

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Expected a JSON list")
        return data
    except (OSError, ValueError, json.JSONDecodeError):
        st.error(
            f"Could not read {path.name}. "
            "Please check the JSON file before continuing."
        )
        return json.loads(json.dumps(seed))


def save_json(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_food(items):
    save_json(FOOD_FILE, items)


def save_orgs(items):
    save_json(ORG_FILE, items)


def hours_left(value):
    try:
        deadline = datetime.fromisoformat(value)
        now = (
            datetime.now(deadline.tzinfo)
            if deadline.tzinfo
            else datetime.now()
        )
        return (deadline - now).total_seconds() / 3600
    except (TypeError, ValueError):
        return 0.0


def display_datetime(value):
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return str(value)


# ---------------------------------------------------------
# EXPLAINABLE MATCHING ALGORITHM
# ---------------------------------------------------------

def rank_org(food, org):
    """
    Weighted, explainable heuristic.
    This is not a trained machine-learning model.
    """
    reasons = []

    if food.get("category") not in org.get("categories", []):
        return 0, ["Food category not accepted"]

    quantity = float(food.get("quantity_kg", 0))
    capacity = float(org.get("capacity_kg", 0))

    if quantity > capacity:
        return 0, ["Donation exceeds stated capacity"]

    if not org.get("pickup_available", False):
        return 0, ["Pickup is not currently available"]

    if food.get("storage") not in org.get("storage", []):
        return 0, [
            "Recipient storage does not support this handling requirement"
        ]

    score = 35
    reasons.append("Accepts this food category (+35)")

    score += 25
    reasons.append("Donation fits recipient capacity (+25)")

    score += 20
    reasons.append("Pickup is available (+20)")

    distance = max(0.0, float(org.get("distance_km", 0)))
    distance_score = max(0, 20 - distance * 3)

    score += distance_score
    reasons.append(
        f"Distance: {distance:.1f} km (+{distance_score:.0f})"
    )

    remaining = max(0.0, hours_left(food.get("pickup_by", "")))

    if remaining <= 2:
        score += 10
        reasons.append("Urgent pickup window (+10)")
    elif remaining <= 5:
        score += 6
        reasons.append("Pickup window approaching (+6)")

    return min(100, round(score)), reasons


def matches_for(food, organizations):
    results = []

    for org in organizations:
        score, reasons = rank_org(food, org)

        if score > 0:
            results.append({
                "organization": org["name"],
                "score": score,
                "distance_km": float(org.get("distance_km", 0)),
                "reasons": reasons,
            })

    return sorted(
        results,
        key=lambda item: (-item["score"], item["distance_km"]),
    )


# ---------------------------------------------------------
# USER FEEDBACK AND BUTTON CALLBACKS
# ---------------------------------------------------------

def flash(kind, message):
    st.session_state["flash"] = (kind, message)


def show_flash():
    message_data = st.session_state.pop("flash", None)

    if message_data:
        kind, message = message_data
        display_function = getattr(
            st,
            kind if kind in ("success", "warning", "error", "info") else "info",
        )
        display_function(message)


def go_to_matching(food_id):
    st.session_state["selected_food_id"] = food_id
    st.session_state["page"] = "AI matching"


def reserve_donation(food_id, organization_name):
    """
    Reload data inside the callback to prevent stale-data updates.
    Validate eligibility again before saving a reservation.
    """
    foods = load_json(FOOD_FILE, SEED_FOOD)

    food = next(
        (item for item in foods if item.get("id") == food_id),
        None,
    )

    if food is None:
        flash("error", "Donation not found. Refresh and try again.")
        return

    if food.get("status") != "Available":
        flash("warning", "This donation is no longer available to reserve.")
        return

    organizations = load_json(ORG_FILE, SEED_ORGS)

    org = next(
        (
            item for item in organizations
            if item.get("name") == organization_name
        ),
        None,
    )

    if org is None:
        flash("error", "Recipient organization was not found.")
        return

    score, _ = rank_org(food, org)

    if score <= 0:
        flash(
            "warning",
            "This recipient is no longer eligible for this donation.",
        )
        return

    food["status"] = "Reserved"
    food["recipient"] = organization_name
    save_food(foods)

    flash(
        "success",
        f"{food_id} reserved for {organization_name}. "
        "Coordinate pickup and verify food safety.",
    )


def mark_collected(food_id):
    foods = load_json(FOOD_FILE, SEED_FOOD)

    food = next(
        (item for item in foods if item.get("id") == food_id),
        None,
    )

    if food is None:
        flash("error", "Donation not found.")
        return

    if food.get("status") != "Reserved":
        flash("warning", "Only reserved donations can be marked collected.")
        return

    food["status"] = "Collected"
    food["collected_at"] = datetime.now().isoformat(timespec="minutes")

    save_food(foods)
    flash("success", f"{food['food']} marked as collected.")


def cancel_donation(food_id):
    foods = load_json(FOOD_FILE, SEED_FOOD)

    food = next(
        (item for item in foods if item.get("id") == food_id),
        None,
    )

    if food is None:
        flash("error", "Donation not found.")
        return

    if food.get("status") not in ("Available", "Reserved"):
        flash("warning", "Only available or reserved donations can be cancelled.")
        return

    food["status"] = "Cancelled"
    save_food(foods)

    flash("success", f"{food['food']} cancelled.")


def delete_donation(food_id):
    foods = load_json(FOOD_FILE, SEED_FOOD)

    food = next(
        (item for item in foods if item.get("id") == food_id),
        None,
    )

    if food is None:
        flash("error", "Donation not found.")
        return

    if food.get("status") == "Collected":
        flash(
            "warning",
            "Collected donations are retained for impact reporting.",
        )
        return

    updated_foods = [
        item for item in foods if item.get("id") != food_id
    ]

    save_food(updated_foods)
    flash("success", "Donation deleted.")


def add_organization(org):
    organizations = load_json(ORG_FILE, SEED_ORGS)

    if any(
        item.get("name", "").casefold() == org["name"].casefold()
        for item in organizations
    ):
        flash("error", "An organization with that name already exists.")
        return

    organizations.append(org)
    save_orgs(organizations)

    flash("success", f"Organization '{org['name']}' added.")


def remove_organization(name):
    organizations = load_json(ORG_FILE, SEED_ORGS)

    save_orgs([
        item for item in organizations
        if item.get("name") != name
    ])

    st.session_state.pop("confirm_remove_org", None)
    flash("success", f"Organization '{name}' removed.")


# ---------------------------------------------------------
# INITIALIZE APP
# ---------------------------------------------------------

foods = load_json(FOOD_FILE, SEED_FOOD)
orgs = load_json(ORG_FILE, SEED_ORGS)

if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

if "selected_food_id" not in st.session_state:
    st.session_state["selected_food_id"] = ""

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
.hero {
    background: linear-gradient(120deg, #073b2c, #148451);
    padding: 28px 32px;
    border-radius: 20px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    font-size: 2.35rem;
    margin: 0;
}
.hero p {
    color: #e2f5e9;
    font-size: 1.05rem;
    margin: 8px 0 0;
}
div[data-testid="stMetric"] {
    background: #f4faf6;
    border: 1px solid #dcefe2;
    padding: 14px 16px;
    border-radius: 14px;
}
div.stButton > button[kind="primary"] {
    background: #12804d;
    border-color: #12804d;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero">'
    '<h1>🌱 FoodLoop AI</h1>'
    '<p>Good food shouldn’t go to waste. Match surplus food with '
    'community need—faster, smarter, transparently.</p>'
    '</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🌿 FoodLoop AI")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Surplus listings",
            "AI matching",
            "Add donation",
            "Recipient organizations",
            "Impact report",
        ],
        key="page",
    )

    st.divider()
    st.caption("Hackathon MVP · Demo data")
    st.caption("Scores use a transparent weighted-ranking algorithm.")

show_flash()

# Reload records so the page reflects callback changes immediately.
foods = load_json(FOOD_FILE, SEED_FOOD)
orgs = load_json(ORG_FILE, SEED_ORGS)

available = [
    item for item in foods
    if item.get("status") == "Available"
]
reserved = [
    item for item in foods
    if item.get("status") == "Reserved"
]
rescued = [
    item for item in foods
    if item.get("status") == "Collected"
]

total_kg = sum(
    float(item.get("quantity_kg", 0))
    for item in rescued
)
potential_meals = sum(
    float(item.get("quantity_kg", 0))
    * float(item.get("meals_per_kg", 1))
    for item in rescued
)


# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------

if page == "Overview":
    st.subheader("Your food rescue command center")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Available donations", len(available))
    col2.metric(
        "Food available",
        f"{sum(float(item['quantity_kg']) for item in available):.1f} kg",
    )
    col3.metric("Completed rescues", len(rescued))
    col4.metric("Food rescued", f"{total_kg:.1f} kg")

    st.markdown("### Priority opportunities")

    urgent = sorted(
        available,
        key=lambda item: hours_left(item.get("pickup_by", "")),
    )

    if urgent:
        columns = st.columns(min(3, len(urgent)))

        for column, food in zip(columns, urgent[:3]):
            remaining = hours_left(food["pickup_by"])

            with column:
                st.markdown(f"**{food['food']}**")
                st.caption(
                    f"{food['donor']} · {food['quantity_kg']} kg"
                )
                st.progress(max(0.0, min(1.0, remaining / 12)))
                st.write(
                    f"Pickup in **{max(0, remaining):.1f} hours**"
                )

                ranked = matches_for(food, orgs)

                if ranked:
                    st.success(
                        f"Top match: {ranked[0]['organization']} · "
                        f"{ranked[0]['score']}/100"
                    )

                    st.button(
                        "Find recipient",
                        key=f"overview_match_{food['id']}",
                        on_click=go_to_matching,
                        args=(food["id"],),
                    )
                else:
                    st.warning("No eligible match yet.")
    else:
        st.info("No available donations. Add a listing to begin.")

    st.markdown("### How it works")

    steps = st.columns(5)

    for column, (number, title, description) in zip(
        steps,
        [
            ("1", "List", "Donor adds surplus"),
            ("2", "Match", "Rank eligible recipients"),
            ("3", "Reserve", "Assign a recipient"),
            ("4", "Collect", "Confirm pickup"),
            ("5", "Measure", "Track rescued food"),
        ],
    ):
        with column:
            st.markdown(f"### {number}. {title}")
            st.caption(description)

    st.info(
        "Demo records are sample data. Impact totals count only "
        "donations marked Collected."
    )


# ---------------------------------------------------------
# SURPLUS LISTINGS
# ---------------------------------------------------------

elif page == "Surplus listings":
    st.subheader("Surplus food listings")

    status_filter = st.selectbox(
        "Status",
        ["All", *STATUSES],
    )

    query = st.text_input(
        "Search listings",
        placeholder="Search food, donor, ID, recipient, or category",
    )

    view = [
        food for food in foods
        if (
            status_filter == "All"
            or food.get("status") == status_filter
        )
        and query.casefold() in " ".join(
            str(food.get(key, ""))
            for key in ("id", "food", "donor", "recipient", "category")
        ).casefold()
    ]

    if not view:
        st.info("No listings match these filters.")

    for food in view:
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])

            with left:
                st.markdown(f"### {food.get('food', 'Unnamed food')}")
                st.write(
                    f"**{food.get('donor', 'Unknown donor')}** · "
                    f"{food.get('category', 'Uncategorized')}"
                )
                st.caption(food.get("notes", "No additional notes."))
                st.caption(
                    f"ID: {food['id']} · Recipient: "
                    f"{food.get('recipient') or 'Not assigned'}"
                )

            with middle:
                st.metric(
                    "Quantity",
                    f"{float(food.get('quantity_kg', 0)):.1f} kg",
                )
                st.write(
                    "Pickup by:",
                    display_datetime(food.get("pickup_by", "")),
                )
                st.write("Storage:", food.get("storage", "Not specified"))

            with right:
                st.write(
                    "Status:",
                    f"**{food.get('status', 'Unknown')}**",
                )

                if food.get("status") == "Available":
                    st.button(
                        "Find matches",
                        key=f"match_{food['id']}",
                        type="primary",
                        on_click=go_to_matching,
                        args=(food["id"],),
                    )

                    st.button(
                        "Cancel donation",
                        key=f"cancel_{food['id']}",
                        on_click=cancel_donation,
                        args=(food["id"],),
                    )

                elif food.get("status") == "Reserved":
                    st.write(
                        f"Reserved for: **{food.get('recipient') or 'Not recorded'}**"
                    )

                    st.button(
                        "Mark collected",
                        key=f"collect_{food['id']}",
                        type="primary",
                        on_click=mark_collected,
                        args=(food["id"],),
                    )

                    st.button(
                        "Cancel reservation",
                        key=f"cancel_{food['id']}",
                        on_click=cancel_donation,
                        args=(food["id"],),
                    )

                elif food.get("status") == "Collected":
                    st.success("Rescued ✓")

                if food.get("status") != "Collected":
                    with st.popover("More actions"):
                        st.warning(
                            "Deleting removes this record from the local demo dataset."
                        )

                        st.button(
                            "Delete donation",
                            key=f"delete_{food['id']}",
                            on_click=delete_donation,
                            args=(food["id"],),
                        )


# ---------------------------------------------------------
# AI MATCHING
# ---------------------------------------------------------

elif page == "AI matching":
    st.subheader("Explainable recipient matching")

    candidates = [
        food for food in foods
        if food.get("status") == "Available"
    ]

    if not candidates:
        st.info(
            "No available donations to match. Add a donation "
            "or review Surplus listings."
        )
    else:
        selected_id = st.session_state.get("selected_food_id", "")

        default_index = next(
            (
                index for index, food in enumerate(candidates)
                if food.get("id") == selected_id
            ),
            0,
        )

        chosen = st.selectbox(
            "Choose a donation",
            candidates,
            index=default_index,
            format_func=lambda food: (
                f"{food['food']} — {food['quantity_kg']} kg "
                f"({food['donor']})"
            ),
            key="matching_donation",
        )

        st.session_state["selected_food_id"] = chosen["id"]

        st.markdown(
            f"**Pickup deadline:** "
            f"{display_datetime(chosen.get('pickup_by', ''))} · "
            f"**Storage:** {chosen.get('storage', 'Not specified')}"
        )

        ranked = matches_for(chosen, orgs)

        if not ranked:
            st.warning(
                "No recipient satisfies category, capacity, pickup, "
                "and storage requirements."
            )

        for index, match in enumerate(ranked):
            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    prefix = "🏆 " if index == 0 else ""
                    st.markdown(
                        f"### {prefix}{match['organization']}"
                    )
                    st.progress(match["score"] / 100)
                    st.write("**Why this match?**")

                    for reason in match["reasons"]:
                        st.markdown(f"- {reason}")

                with right:
                    st.metric(
                        "Match score",
                        f"{match['score']}/100",
                    )
                    st.caption(
                        f"{match['distance_km']:.1f} km away"
                    )

                    # Callback ensures reservation is persisted and validated.
                    st.button(
                        "Reserve donation",
                        key=f"reserve_{chosen['id']}_{index}",
                        type="primary" if index == 0 else "secondary",
                        on_click=reserve_donation,
                        args=(chosen["id"], match["organization"]),
                    )

        with st.expander("How the score works"):
            st.write(
                "This is an explainable weighted heuristic, not a trained "
                "predictive model. It checks category, capacity, pickup "
                "availability, storage compatibility, distance, and urgency."
            )

    st.caption(
        "Confirm recipient acceptance, pickup arrangements, allergens, "
        "temperature control, and applicable food-safety rules."
    )


# ---------------------------------------------------------
# ADD DONATION
# ---------------------------------------------------------

elif page == "Add donation":
    st.subheader("List surplus food")

    st.caption(
        "Only list food that is safe to donate under applicable "
        "local food-safety rules."
    )

    with st.form("donation_form", clear_on_submit=True):
        left, right = st.columns(2)

        with left:
            food_name = st.text_input(
                "Food description",
                placeholder="e.g., Fresh vegetable boxes",
            )
            category = st.selectbox("Category", CATEGORIES)
            quantity = st.number_input(
                "Quantity (kg)",
                min_value=0.1,
                max_value=10000.0,
                value=10.0,
                step=0.5,
            )
            donor = st.text_input(
                "Donor / business name",
                placeholder="e.g., Green Street Cafe",
            )
            address = st.text_input(
                "Pickup area or address",
                placeholder="e.g., Downtown",
            )

        with right:
            pickup_date = st.date_input(
                "Pickup date",
                value=date.today(),
                min_value=date.today(),
            )
            pickup_time = st.time_input(
                "Pickup deadline",
                value=(
                    datetime.now() + timedelta(hours=4)
                ).time().replace(second=0, microsecond=0),
            )
            storage = st.selectbox(
                "Storage / handling",
                STORAGE_OPTIONS,
            )
            meals_per_kg = st.number_input(
                "Estimated meal portions per kg",
                min_value=0.0,
                max_value=10.0,
                value=1.0,
                step=0.5,
            )
            notes = st.text_area(
                "Additional details",
                placeholder="Packaging, allergens, handling notes, etc.",
            )

        submitted = st.form_submit_button(
            "Publish donation",
            type="primary",
        )

    if submitted:
        if not food_name.strip() or not donor.strip() or not address.strip():
            st.error(
                "Please fill in food description, donor, and pickup area."
            )
        else:
            deadline = datetime.combine(pickup_date, pickup_time)

            if deadline <= datetime.now():
                st.error("Pickup deadline must be in the future.")
            else:
                new_food = {
                    "id": "FL-" + uuid.uuid4().hex[:6].upper(),
                    "food": food_name.strip(),
                    "category": category,
                    "quantity_kg": float(quantity),
                    "meals_per_kg": float(meals_per_kg),
                    "donor": donor.strip(),
                    "address": address.strip(),
                    "lat": None,
                    "lon": None,
                    "listed_at": datetime.now().isoformat(timespec="minutes"),
                    "pickup_by": deadline.isoformat(timespec="minutes"),
                    "storage": storage,
                    "notes": notes.strip() or "No additional notes.",
                    "status": "Available",
                    "recipient": "",
                }

                latest_foods = load_json(FOOD_FILE, SEED_FOOD)
                latest_foods.insert(0, new_food)
                save_food(latest_foods)

                st.session_state["selected_food_id"] = new_food["id"]
                flash(
                    "success",
                    f"Donation published (ID {new_food['id']}).",
                )
                st.rerun()


# ---------------------------------------------------------
# RECIPIENT ORGANIZATIONS
# ---------------------------------------------------------

elif page == "Recipient organizations":
    st.subheader("Recipient organizations")

    st.caption(
        "Sample profiles. Verify identity, capacity, pickup ability, "
        "and safe handling before real-world use."
    )

    with st.expander("Add recipient organization"):
        with st.form("organization_form", clear_on_submit=True):
            name = st.text_input("Organization name")

            org_type = st.selectbox(
                "Organization type",
                [
                    "Community kitchen",
                    "Food bank",
                    "Student pantry",
                    "Shelter",
                    "Other",
                ],
            )

            categories = st.multiselect(
                "Accepted food categories",
                CATEGORIES,
                default=["Produce", "Bakery"],
            )

            capacity = st.number_input(
                "Maximum donation capacity (kg)",
                min_value=0.1,
                max_value=100000.0,
                value=20.0,
                step=1.0,
            )

            distance = st.number_input(
                "Estimated distance (km)",
                min_value=0.0,
                max_value=10000.0,
                value=2.0,
                step=0.5,
            )

            pickup = st.checkbox(
                "Pickup currently available",
                value=True,
            )

            storage = st.multiselect(
                "Supported storage / handling",
                STORAGE_OPTIONS,
                default=["Ambient"],
            )

            people = st.number_input(
                "People served (estimate)",
                min_value=0,
                max_value=1000000,
                value=50,
                step=5,
            )

            add_submitted = st.form_submit_button(
                "Add organization",
                type="primary",
            )

        if add_submitted:
            if not name.strip():
                st.error("Please enter an organization name.")
            elif not categories or not storage:
                st.error(
                    "Select at least one accepted category "
                    "and storage type."
                )
            else:
                add_organization({
                    "name": name.strip(),
                    "type": org_type,
                    "categories": categories,
                    "capacity_kg": float(capacity),
                    "distance_km": float(distance),
                    "pickup_available": bool(pickup),
                    "storage": storage,
                    "people_served": int(people),
                })
                st.rerun()

    orgs = load_json(ORG_FILE, SEED_ORGS)

    if not orgs:
        st.info("No recipient organizations have been added.")

    for org in orgs:
        with st.container(border=True):
            left, middle, right = st.columns([2, 2, 1])

            with left:
                st.markdown(f"### {org['name']}")
                st.write(org.get("type", "Organization"))
                st.caption(
                    "Accepts: " + ", ".join(org.get("categories", []))
                )
                st.caption(
                    "Storage: " + ", ".join(org.get("storage", []))
                )

            with middle:
                st.write(
                    f"**Capacity:** "
                    f"{float(org.get('capacity_kg', 0)):.1f} kg"
                )
                st.write(
                    f"**Distance:** "
                    f"{float(org.get('distance_km', 0)):.1f} km "
                    "(demo estimate)"
                )
                st.write(
                    f"**Pickup available:** "
                    f"{'Yes' if org.get('pickup_available') else 'No'}"
                )

            with right:
                st.metric(
                    "People served",
                    int(org.get("people_served", 0)),
                )

                if st.button(
                    "Remove organization",
                    key="remove_org_" + org["name"],
                ):
                    st.session_state["confirm_remove_org"] = org["name"]

            if st.session_state.get("confirm_remove_org") == org["name"]:
                st.warning(
                    f"Remove {org['name']}? Existing donation records "
                    "will retain their recipient text."
                )

                yes, no = st.columns(2)

                with yes:
                    st.button(
                        "Confirm remove",
                        key="confirm_remove_" + org["name"],
                        on_click=remove_organization,
                        args=(org["name"],),
                    )

                with no:
                    if st.button(
                        "Keep organization",
                        key="keep_org_" + org["name"],
                    ):
                        st.session_state.pop("confirm_remove_org", None)
                        st.rerun()


# ---------------------------------------------------------
# IMPACT REPORT
# ---------------------------------------------------------

elif page == "Impact report":
    st.subheader("Impact report")

    st.caption(
        "Only donations marked Collected count toward completed-rescue "
        "totals. Meal portions are estimates."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Food rescued", f"{total_kg:.1f} kg")
    col2.metric("Estimated meal portions", f"{potential_meals:.0f}")
    col3.metric("Completed donations", len(rescued))
    col4.metric(
        "Currently reserved",
        f"{sum(float(item.get('quantity_kg', 0)) for item in reserved):.1f} kg",
    )

    if rescued:
        dataframe = pd.DataFrame([
            {
                "ID": food.get("id"),
                "Donation": food.get("food"),
                "Donor": food.get("donor"),
                "Quantity (kg)": food.get("quantity_kg"),
                "Recipient": food.get("recipient") or "Not recorded",
                "Collected at": food.get("collected_at", "Not recorded"),
            }
            for food in rescued
        ])

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
        )

        st.bar_chart(
            dataframe.set_index("Donation")["Quantity (kg)"]
        )
    else:
        st.info(
            "No completed rescues yet. Reserve a donation, then mark "
            "it collected in Surplus listings."
        )

    st.download_button(
        "Download donations (CSV)",
        pd.DataFrame(foods).to_csv(index=False).encode("utf-8"),
        "foodloop_donations.csv",
        "text/csv",
    )

    st.download_button(
        "Download organizations (CSV)",
        pd.DataFrame(orgs).to_csv(index=False).encode("utf-8"),
        "foodloop_organizations.csv",
        "text/csv",
    )

    st.download_button(
        "Download donations (JSON)",
        json.dumps(foods, indent=2).encode("utf-8"),
        "foodloop_donations.json",
        "application/json",
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "FoodLoop AI · Hackathon prototype · Use verified data and "
    "follow local food-safety requirements before real-world deployment."
)