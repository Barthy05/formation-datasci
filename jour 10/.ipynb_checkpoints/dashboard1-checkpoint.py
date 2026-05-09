import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# ============================================================
# 1. DATASET
# ============================================================
np.random.seed(42)
n = 400

df_livraison = pd.DataFrame({
    "commande_id": range(1, n+1),
    "date": pd.date_range(start="2025-01-01", periods=n, freq="D"),
    "ville": np.random.choice(["Douala", "Yaoundé", "Bafoussam", "Garoua"], n),
    "livreur": np.random.choice(["Jean", "Paul", "Marie", "Sophie", "Marc"], n),
    "produit": np.random.choice(["Alimentaire", "Electronique", "Vêtements", "Pharmacie"], n),
    "montant": np.random.randint(5000, 200000, n),
    "delai": np.random.normal(45, 15, n).round(0),
    "satisfaction": np.random.randint(1, 6, n),
    "statut": np.random.choice(["Livrée", "En cours", "Annulée"], n, p=[0.75, 0.15, 0.10])
})
df_livraison["mois"] = df_livraison["date"].dt.strftime("%Y-%m")
df_livraison["ca_total"] = df_livraison["montant"]

# ============================================================
# 2. INITIALISER L'APPLICATION DASH
# C'est comme créer une application web Flask — Dash gère tout !
# ============================================================
app = dash.Dash(__name__)

# ============================================================
# 3. LAYOUT — La structure visuelle du dashboard
# html.Div = une boîte (comme une div HTML)
# dcc = Dash Core Components (graphiques, dropdowns, sliders...)
# html = composants HTML (titres, paragraphes, labels...)
# ============================================================
app.layout = html.Div([

    # TITRE PRINCIPAL
    html.H1("Dashboard Livraison Cameroun 2025",
            style={"textAlign": "center", "color": "#7F77DD"}),

    # FILTRES — deux dropdowns côte à côte
    html.Div([
        # Filtre Ville (occupe 48% de la largeur)
        html.Div([
            html.Label("Ville :"),
            dcc.Dropdown(
                id="filtre-ville",  # ← ID unique pour ce composant
                options=[{"label": v, "value": v} 
                         for v in df_livraison["ville"].unique()],
                value=None,         # ← valeur par défaut (None = rien sélectionné)
                multi=True,         # ← permet de sélectionner plusieurs villes
                placeholder="Toutes les villes..."
            )
        ], style={"width": "48%", "display": "inline-block"}),

        # Filtre Livreur (occupe 48% de la largeur)
        html.Div([
            html.Label("Livreur :"),
            dcc.Dropdown(
                id="filtre-livreur",  # ← ID unique pour ce composant
                options=[{"label": p, "value": p} 
                         for p in df_livraison["livreur"].unique()],
                value=None,
                multi=True,
                placeholder="Tous les livreurs..."
            )
        ], style={"width": "48%", "display": "inline-block", 
                  "marginLeft": "4%"})
    ], style={"margin": "20px"}),

    # MÉTRIQUES CLÉS — 4 cartes côte à côte
    # Chaque html.Div a un ID unique — le callback va y injecter le contenu
    html.Div([
        html.Div(id="metric-ca_total", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-nb_livraison", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-delai_moyen", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-satisfaction_moyenne", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        })
    ], style={"margin": "20px"}),

    # GRAPHIQUES — ligne 1 (2 graphiques côte à côte)
    html.Div([
        html.Div([
            dcc.Graph(id="graph-ca_ville")   # ← ID unique pour ce graphique
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            dcc.Graph(id="graph-evolution")  # ← ID unique pour ce graphique
        ], style={"width": "48%", "display": "inline-block"})
    ]),

    # GRAPHIQUES — ligne 2 (2 graphiques côte à côte)
    html.Div([
        html.Div([
            dcc.Graph(id="graph-satisfaction")  # ← ID unique
        ], style={"width": "48%", "display": "inline-block"}),

        html.Div([
            dcc.Graph(id="graph-repartition")   # ← ID unique
        ], style={"width": "48%", "display": "inline-block"})
    ])
])

# ============================================================
# 4. CALLBACK — Le cerveau du dashboard
# 
# Un callback = une fonction qui se déclenche automatiquement
# quand l'utilisateur interagit avec un composant (filtre, slider...)
#
# @app.callback(
#     [Output(...)],  ← ce que la fonction VA METTRE À JOUR
#     [Input(...)]    ← ce qui DÉCLENCHE la mise à jour
# )
#
# RÈGLE IMPORTANTE :
# - Les IDs dans Output doivent correspondre aux IDs du layout
# - L'ordre des return doit correspondre à l'ordre des Output
# ============================================================
@app.callback(
    [
        # Les 4 métriques à mettre à jour
        # "children" = le contenu HTML de la div
        Output("metric-ca_total", "children"),        # ← même ID que le layout
        Output("metric-nb_livraison", "children"),    # ← même ID que le layout
        Output("metric-delai_moyen", "children"),     # ← même ID que le layout
        Output("metric-satisfaction_moyenne", "children"),  # ← même ID

        # Les 4 graphiques à mettre à jour
        # "figure" = la figure Plotly du graphique
        Output("graph-ca_ville", "figure"),       # ← même ID que le layout
        Output("graph-evolution", "figure"),      # ← même ID que le layout
        Output("graph-satisfaction", "figure"),   # ← même ID que le layout
        Output("graph-repartition", "figure")     # ← même ID que le layout
    ],
    [
        # Les filtres qui déclenchent la mise à jour
        # "value" = la valeur sélectionnée dans le dropdown
        Input("filtre-ville", "value"),    # ← même ID que le layout
        Input("filtre-livreur", "value")   # ← même ID que le layout
    ]
)
def update_dashboard(villes, livreurs):
    """
    Cette fonction est appelée automatiquement quand :
    - L'utilisateur sélectionne une ville
    - L'utilisateur sélectionne un livreur
    
    Elle reçoit les valeurs des filtres et retourne
    le nouveau contenu des métriques et graphiques
    """

    # FILTRAGE DES DONNÉES
    dff = df_livraison.copy()  # copie pour ne pas modifier l'original
    if villes:    # si une ville est sélectionnée
        dff = dff[dff["ville"].isin(villes)]
    if livreurs:  # si un livreur est sélectionné
        dff = dff[dff["livreur"].isin(livreurs)]

    # CALCUL DES MÉTRIQUES
    ca_total = dff["ca_total"].sum()
    nb_livraison = len(dff)
    delai_moyen = dff["delai"].mean()
    satisfaction_moyenne = dff["satisfaction"].mean()

    # CONTENU DES CARTES MÉTRIQUES
    # Chaque métrique retourne une liste de composants HTML
    metric_ca = [
        html.H3(f"{ca_total/1e6:.1f}M", style={"color": "#7F77DD"}),
        html.P("CA Total (FCFA)")
    ]
    metric_livraison = [
        html.H3(f"{nb_livraison}", style={"color": "#1D9E75"}),
        html.P("Nombre de livraisons")
    ]
    metric_delai = [
        html.H3(f"{delai_moyen:.1f} min", style={"color": "#EF9F27"}),  # ✅ corrigé
        html.P("Délai moyen")
    ]
    metric_satisfaction = [
        html.H3(f"{satisfaction_moyenne:.1f}/5", style={"color": "#D85A30"}),  # ✅ corrigé
        html.P("Satisfaction moyenne")
    ]

    # GRAPHIQUE 1 : CA par ville
    ca_ville = dff.groupby("ville")["ca_total"].sum().reset_index()
    fig1 = px.bar(ca_ville, x="ville", y="ca_total",
                  color="ville", title="CA par ville",
                  labels={"ca_total": "CA (FCFA)"})

    # GRAPHIQUE 2 : Evolution mensuelle du CA
    ca_mois = dff.groupby("mois")["ca_total"].sum().reset_index()
    fig2 = px.line(ca_mois, x="mois", y="ca_total",
                   title="Evolution du CA par mois",
                   markers=True,
                   labels={"ca_total": "CA (FCFA)", "mois": "Mois"})

    # GRAPHIQUE 3 : Satisfaction par livreur
    sat_livreur = dff.groupby("livreur")["satisfaction"].mean().reset_index()
    fig3 = px.bar(sat_livreur, x="livreur", y="satisfaction",
                  color="livreur", title="Satisfaction par livreur",
                  labels={"satisfaction": "Score moyen /5"})

    # GRAPHIQUE 4 : Répartition par statut
    ca_statut = dff.groupby("statut")["ca_total"].sum().reset_index()
    fig4 = px.pie(ca_statut, values="ca_total",
                  names="statut",  # ✅ corrigé — "statut" et non "produit"
                  title="Répartition par statut", hole=0.4)

    # RETOURNER DANS LE MÊME ORDRE QUE LES OUTPUT !
    # Output 1 → metric_ca
    # Output 2 → metric_livraison
    # Output 3 → metric_delai
    # Output 4 → metric_satisfaction
    # Output 5 → fig1 (ca_ville)
    # Output 6 → fig2 (evolution)
    # Output 7 → fig3 (satisfaction)
    # Output 8 → fig4 (repartition)
    return (metric_ca, metric_livraison, metric_delai,
            metric_satisfaction, fig1, fig2, fig3, fig4)

# ============================================================
# 5. LANCER LE SERVEUR
# debug=True → recharge automatiquement quand tu modifies le code
# port=8050 → accessible sur http://localhost:8050
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=8050)