"""QUSAY - Drug Explorer
Section 1: adverse event reports (FDA FAERS via openFDA)
Section 2: drug names in the US, Europe (EMA) and Bulgaria
Section 3: forms, strengths and dosing text (FDA NDC and label data)
Run with:  streamlit run app.py
"""

import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

FDA_EVENT_URL = "https://api.fda.gov/drug/event.json"
FDA_NDC_URL = "https://api.fda.gov/drug/ndc.json"
FDA_LABEL_URL = "https://api.fda.gov/drug/label.json"
EMA_URL = (
    "https://www.ema.europa.eu/en/documents/report/"
    "medicines-output-medicines_json-report_en.json"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (QUSAY drug explorer)"}

# Drugs whose US name (USAN) differs from the international name (INN) used in Europe
US_TO_INN = {
    "acetaminophen": "paracetamol",
    "albuterol": "salbutamol",
    "epinephrine": "adrenaline",
    "norepinephrine": "noradrenaline",
    "meperidine": "pethidine",
    "rifampin": "rifampicin",
    "cyclosporine": "ciclosporin",
    "glyburide": "glibenclamide",
    "isoproterenol": "isoprenaline",
    "cephalexin": "cefalexin",
    "chlorpheniramine": "chlorphenamine",
    "hydroxyurea": "hydroxycarbamide",
    "aspirin": "acetylsalicylic acid",
    "furosemide": "furosemide",
}
INN_TO_US = {v: k for k, v in US_TO_INN.items()}

# Common drugs: INN in Cyrillic as used in Bulgaria
BG_NAMES = {
    "paracetamol": "парацетамол",
    "ibuprofen": "ибупрофен",
    "diclofenac": "диклофенак",
    "acetylsalicylic acid": "ацетилсалицилова киселина",
    "metformin": "метформин",
    "atorvastatin": "аторвастатин",
    "simvastatin": "симвастатин",
    "amoxicillin": "амоксицилин",
    "azithromycin": "азитромицин",
    "ciprofloxacin": "ципрофлоксацин",
    "ceftriaxone": "цефтриаксон",
    "omeprazole": "омепразол",
    "pantoprazole": "пантопразол",
    "salbutamol": "салбутамол",
    "adrenaline": "адреналин",
    "noradrenaline": "норадреналин",
    "furosemide": "фуроземид",
    "lisinopril": "лизиноприл",
    "ramipril": "рамиприл",
    "amlodipine": "амлодипин",
    "bisoprolol": "бисопролол",
    "losartan": "лозартан",
    "warfarin": "варфарин",
    "clopidogrel": "клопидогрел",
    "levothyroxine": "левотироксин",
    "tramadol": "трамадол",
    "morphine": "морфин",
    "diazepam": "диазепам",
    "insulin": "инсулин",
}

st.set_page_config(page_title="QUSAY", layout="wide")


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fda_get(url, search, count=None, limit=100):
    """Send one request to openFDA and return the answer as a dictionary."""
    params = {"search": search, "limit": limit}
    if count:
        params["count"] = count
    response = requests.get(url, params=params, timeout=30)
    if response.status_code == 404:  # openFDA's way of saying "nothing found"
        return {"results": [], "meta": {"results": {"total": 0}}}
    response.raise_for_status()
    return response.json()


def total_reports(search):
    return fda_get(FDA_EVENT_URL, search, limit=1)["meta"]["results"]["total"]


@st.cache_data(ttl=86400, show_spinner=False)
def load_ema():
    """Download the EMA list of centrally authorised medicines."""
    response = requests.get(EMA_URL, headers=HEADERS, timeout=90)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                data = value
                break
    return pd.DataFrame(data)


def find_col(df, *keys):
    """Find a column whose name contains one of the keys."""
    for key in keys:
        for col in df.columns:
            if key in str(col).lower().replace(" ", "_"):
                return col
    return None


# ---------------------------------------------------------------
# Section 1: safety reports
# ---------------------------------------------------------------
def safety_tab(drug, search_by, top_n, start_year):
    field = (
        "patient.drug.openfda.generic_name"
        if search_by == "Generic name"
        else "patient.drug.openfda.brand_name"
    )
    base = f'{field}:"{drug}"'

    total = total_reports(base)
    if total == 0:
        st.warning(
            f"No reports found for '{drug}'. Try the US name "
            "(for example 'acetaminophen') or switch between Generic and Brand name."
        )
        return
    serious = total_reports(base + " AND serious:1")
    deaths = total_reports(base + " AND seriousnessdeath:1")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total reports", f"{total:,}")
    c2.metric("Serious reports", f"{serious:,}", f"{serious / total:.0%} of all")
    c3.metric("Reports with death outcome", f"{deaths:,}")

    st.subheader("Most reported side effects")
    data = fda_get(FDA_EVENT_URL, base, count="patient.reaction.reactionmeddrapt.exact", limit=top_n)
    reactions = pd.DataFrame(data["results"]).rename(
        columns={"term": "Reaction", "count": "Reports"}
    )
    fig = px.bar(reactions.sort_values("Reports"), x="Reports", y="Reaction", orientation="h")
    fig.update_layout(height=max(350, 28 * len(reactions)))
    st.plotly_chart(fig, width="stretch")
    st.download_button(
        "Download this table (CSV)", reactions.to_csv(index=False), file_name=f"{drug}_reactions.csv"
    )

    st.subheader("Reports per year")
    rows = []
    for year in range(int(start_year), datetime.date.today().year + 1):
        query = f"{base} AND receivedate:[{year}0101 TO {year}1231]"
        rows.append({"Year": year, "Reports": total_reports(query)})
    fig = px.line(pd.DataFrame(rows), x="Year", y="Reports", markers=True)
    st.plotly_chart(fig, width="stretch")
    st.caption("The current year is incomplete, so its last point is lower.")

    left, right = st.columns(2)
    with left:
        st.subheader("Reports by sex")
        sex = pd.DataFrame(fda_get(FDA_EVENT_URL, base, count="patient.patientsex", limit=10)["results"])
        if not sex.empty:
            names = {0: "Unknown", 1: "Male", 2: "Female"}
            sex["Sex"] = sex["term"].astype(int).map(names).fillna("Unknown")
            st.plotly_chart(px.pie(sex, names="Sex", values="count"), width="stretch")
        else:
            st.write("No sex data available.")
    with right:
        st.subheader("Reports by age group")
        ages = pd.DataFrame(
            fda_get(
                FDA_EVENT_URL,
                base + " AND patient.patientonsetageunit:801",
                count="patient.patientonsetage",
                limit=1000,
            )["results"]
        )
        if not ages.empty:
            ages["term"] = pd.to_numeric(ages["term"], errors="coerce")
            ages = ages[(ages["term"] >= 0) & (ages["term"] <= 110)]
            ages["Age group"] = pd.cut(
                ages["term"],
                bins=[0, 18, 35, 50, 65, 80, 111],
                labels=["0-17", "18-34", "35-49", "50-64", "65-79", "80+"],
                right=False,
            )
            grouped = ages.groupby("Age group", observed=True)["count"].sum().reset_index()
            st.plotly_chart(
                px.bar(grouped, x="Age group", y="count", labels={"count": "Reports"}),
                width="stretch",
            )
            st.caption("Only reports where age was given in years.")
        else:
            st.write("No age data available.")

    st.caption(
        "Limits: voluntary reporting, possible duplicates, no information on how many "
        "people took the drug, and a report does not prove causation."
    )


# ---------------------------------------------------------------
# Section 2: names in US / Europe / Bulgaria
# ---------------------------------------------------------------
def names_tab(typed, inn, us, bg):
    st.subheader("Name of the active substance in each region")
    table = pd.DataFrame(
        [
            {"Region": "United States (FDA, USAN)", "Name": us},
            {"Region": "Europe (EMA, INN)", "Name": inn},
            {"Region": "Bulgaria (INN in Cyrillic)", "Name": bg or "not in the built-in list"},
        ]
    )
    st.dataframe(table, width="stretch", hide_index=True)
    if us == inn:
        st.caption("For this drug the US and European names are the same.")
    else:
        st.info(
            f"Names differ: the US uses '{us}' and Europe uses '{inn}'. "
            "This matters when you search databases in different regions."
        )
    st.caption(
        "The built-in list covers common drugs only. For other drugs, check the "
        "WHO INN list or the Bulgarian register below."
    )

    # ---- Europe ----
    st.subheader("Europe: centrally authorised medicines (EMA)")
    try:
        with st.spinner("Loading the EMA medicines list..."):
            ema = load_ema()
    except (requests.RequestException, ValueError) as error:
        st.warning(
            "Could not load the EMA list right now. You can search it directly at "
            f"https://www.ema.europa.eu/en/medicines (details: {error})"
        )
        ema = None

    if ema is not None and not ema.empty:
        sub = find_col(ema, "active_substance")
        inn_col = find_col(ema, "international_non")
        name = find_col(ema, "name_of_medicine", "medicine_name", "name")
        status = find_col(ema, "medicine_status", "status")
        atc = find_col(ema, "atc")
        url = find_col(ema, "medicine_url", "url")
        cat = find_col(ema, "category")
        holder = find_col(ema, "holder", "marketing_authorisation")

        mask = pd.Series(False, index=ema.index)
        for term in {inn.lower(), typed.lower()}:
            for col in (sub, inn_col, name):
                if col:
                    mask |= ema[col].astype(str).str.lower().str.contains(term, regex=False, na=False)
        found = ema[mask]
        if cat and (found[cat].astype(str).str.lower() == "human").any():
            found = found[found[cat].astype(str).str.lower() == "human"]

        if found.empty:
            st.write(
                "No centrally authorised product found. This is normal for many older "
                "generic drugs: they are authorised by national agencies (including "
                "the Bulgarian Drug Agency), not by the EMA."
            )
        else:
            st.write(f"{len(found)} centrally authorised product(s) found.")
            shown = [c for c in (name, sub, status, atc, holder, url) if c]
            view = found[shown].astype(str)
            labels = {name: "Product", sub: "Active substance", status: "Status",
                      atc: "ATC code", holder: "Marketing authorisation holder", url: "EMA page"}
            view = view.rename(columns={c: labels[c] for c in shown})
            config = {"EMA page": st.column_config.LinkColumn("EMA page")} if url else None
            st.dataframe(view, width="stretch", hide_index=True, column_config=config)
        st.caption("Source: EMA. Covers centrally authorised products only.")

    # ---- Bulgaria ----
    st.subheader("Bulgaria")
    st.write(
        f"Search for **{bg or inn}** in the official Bulgarian Drug Agency register of "
        "medicinal products. There you find every authorised product, its forms and "
        "strengths, the SmPC (КХП) and the patient leaflet."
    )
    st.link_button("Open Bulgarian Drug Agency (bda.bg)", "https://www.bda.bg/")
    st.link_button("Open National Council on Prices and Reimbursement (ncpr.bg)", "https://www.ncpr.bg/")

    uploaded = st.file_uploader(
        "Optional: upload a Bulgarian drug list you downloaded (CSV or Excel) "
        "and this page will search it for you",
        type=["csv", "xlsx", "xls"],
    )
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                try:
                    bgdf = pd.read_csv(uploaded, sep=None, engine="python", encoding="utf-8-sig")
                except UnicodeDecodeError:
                    uploaded.seek(0)
                    bgdf = pd.read_csv(uploaded, sep=None, engine="python", encoding="cp1251")
            else:
                bgdf = pd.read_excel(uploaded)
            terms = [t.lower() for t in {typed, inn, bg} if t]
            text = bgdf.astype(str).agg(" ".join, axis=1).str.lower()
            hit = pd.Series(False, index=bgdf.index)
            for term in terms:
                hit |= text.str.contains(term, regex=False)
            result = bgdf[hit]
            st.write(f"{len(result)} matching row(s) in your file.")
            st.dataframe(result.astype(str).head(500), width="stretch", hide_index=True)
        except Exception as error:  # noqa: BLE001 - show any file problem in plain words
            st.error(f"Could not read this file: {error}")


# ---------------------------------------------------------------
# Section 3: forms, strengths, dosing text
# ---------------------------------------------------------------
def forms_tab(us, inn):
    st.subheader("Dosage forms and strengths on the US market")
    data = fda_get(FDA_NDC_URL, f'generic_name:"{us}"', limit=1000)
    rows = []
    for product in data["results"]:
        ingredients = product.get("active_ingredients") or []
        rows.append(
            {
                "Form": product.get("dosage_form"),
                "Route": ", ".join(product.get("route") or []),
                "Strength": " + ".join(i.get("strength", "") for i in ingredients),
                "Ingredients": len(ingredients),
                "Brand": product.get("brand_name"),
                "Category": product.get("marketing_category"),
            }
        )
    products = pd.DataFrame(rows)
    if products.empty:
        st.warning(f"No US product listing found for '{us}'.")
    else:
        single = st.checkbox("Single-ingredient products only", value=True)
        if single:
            products = products[products["Ingredients"] == 1]
        summary = (
            products.groupby(["Form", "Route", "Strength"], dropna=False)
            .size()
            .reset_index(name="Products")
            .sort_values(["Form", "Strength"])
        )
        st.write(f"{len(summary)} different form and strength combinations "
                 f"({len(products)} products).")
        st.dataframe(summary.astype(str), width="stretch", hide_index=True)
        with st.expander("Show all individual products"):
            st.dataframe(products.drop(columns=["Ingredients"]).astype(str),
                         width="stretch", hide_index=True)
        st.caption("Source: FDA National Drug Code directory. These are US products.")

    st.subheader("Dosage and administration (from the US label)")
    labels = fda_get(FDA_LABEL_URL, f'openfda.generic_name:"{us}"', limit=10)["results"]
    chosen = None
    for label in labels:
        if label.get("dosage_and_administration"):
            names = [n.lower() for n in label.get("openfda", {}).get("generic_name", [])]
            if us.lower() in names:
                chosen = label
                break
            chosen = chosen or label
    if chosen:
        brand = ", ".join(chosen.get("openfda", {}).get("brand_name", [])[:2])
        st.caption(f"Label shown: {brand or us}")
        text = " ".join(chosen["dosage_and_administration"])
        with st.expander("Read dosage and administration text", expanded=False):
            st.write(text[:5000] + (" ..." if len(text) > 5000 else ""))
    else:
        st.write("No label dosing text found.")

    st.subheader("Europe and Bulgaria")
    st.info(
        "Valid forms, strengths and doses in Europe and Bulgaria are set in each "
        "product's SmPC (Summary of Product Characteristics; in Bulgarian: КХП). "
        "Doses are in section 4.2 'Posology and method of administration' and forms "
        "and strengths are in section 2 and 3. Open the EMA page from the Names tab "
        "or search the Bulgarian register at bda.bg."
    )
    st.warning(
        f"Doses depend on age, kidney and liver function, indication and the specific "
        f"product, so this page is for learning only. Always use the current SmPC or "
        f"label of the exact product. (INN: {inn})"
    )


# ---------------------------------------------------------------
# Page
# ---------------------------------------------------------------
st.title("QUSAY")
st.subheader("Drug Explorer: safety reports, names and forms")

with st.sidebar:
    st.header("Search")
    drug_input = st.text_input("Drug name", value="ibuprofen")
    search_by = st.radio("Search safety reports by", ["Generic name", "Brand name"])
    top_n = st.slider("Number of reactions to show", 5, 30, 15)
    start_year = st.number_input("Trend starts at year", 2004, 2025, 2012)

typed = drug_input.replace('"', "").strip().lower()
if not typed:
    st.info("Type a drug name in the sidebar to begin.")
    st.stop()

inn = US_TO_INN.get(typed, typed)
us = INN_TO_US.get(typed, typed)
bg = BG_NAMES.get(inn)

tab1, tab2, tab3 = st.tabs(["Safety reports", "Names: US, Europe, Bulgaria", "Forms and doses"])

with tab1:
    try:
        with st.spinner("Asking the FDA database..."):
            safety_tab(us if search_by == "Generic name" else typed, search_by, top_n, start_year)
    except requests.RequestException as error:
        st.error(f"Could not get data from the FDA server: {error}")

with tab2:
    names_tab(typed, inn, us, bg)

with tab3:
    try:
        forms_tab(us, inn)
    except requests.RequestException as error:
        st.error(f"Could not get data from the FDA server: {error}")

st.divider()
st.caption("For learning and portfolio use only, not for clinical decisions.")
