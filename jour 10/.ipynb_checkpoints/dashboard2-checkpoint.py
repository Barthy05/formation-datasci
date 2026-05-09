import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Dataset
np.random.seed(42)
n = 300
df = pd.DataFrame({
    "date": pd.date_range(start="2025-01-01", periods=n, freq="D"),
    "ville": np.random.choice(["Douala", "Yaoundé", "Bafoussam", "Garoua"], n),
    "produit": np.random.choice(["Laptop", "Téléphone", "Tablette", "Accessoire"], n),
    "categorie": np.random.choice(["Electronique", "Accessoire"], n),
    "montant": np.random.randint(10000, 500000, n),
    "quantite": np.random.randint(1, 10, n),
    "satisfaction": np.random.randint(1, 6, n),
    "vendeur": np.random.choice(["Alice", "Bob", "Carol", "David"], n)
})
df["ca_total"] = df["montant"] * df["quantite"]
df["mois"] = df["date"].dt.strftime("%Y-%m")

# Initialiser l'application
app = dash.Dash(__name__)

# Layout du dashboard
app.layout = html.Div([
    # Titre
    html.H1("Dashboard Ventes Cameroun 2025",
            style={"textAlign": "center", "color": "#7F77DD"}),
    
    # Filtres
    html.Div([
        html.Div([
            html.Label("Ville :"),
            dcc.Dropdown(
                id="filtre-ville",
                options=[{"label": v, "value": v} for v in df["ville"].unique()],
                value=None,
                multi=True,
                placeholder="Toutes les villes..."
            )
        ], style={"width": "48%", "display": "inline-block"}),
        
        html.Div([
            html.Label("Produit :"),
            dcc.Dropdown(
                id="filtre-produit",
                options=[{"label": p, "value": p} for p in df["produit"].unique()],
                value=None,
                multi=True,
                placeholder="Tous les produits..."
            )
        ], style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
    ], style={"margin": "20px"}),
    
    # Métriques clés
    html.Div([
        html.Div(id="metric-ca", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-commandes", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-satisfaction", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        }),
        html.Div(id="metric-panier", style={
            "width": "23%", "display": "inline-block",
            "textAlign": "center", "background": "#f8f9fa",
            "padding": "15px", "margin": "1%",
            "borderRadius": "8px"
        })
    ], style={"margin": "20px"}),
    
    # Graphiques
    html.Div([
        html.Div([
            dcc.Graph(id="graph-ca-ville")
        ], style={"width": "48%", "display": "inline-block"}),
        
        html.Div([
            dcc.Graph(id="graph-evolution")
        ], style={"width": "48%", "display": "inline-block"})
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id="graph-produit")
        ], style={"width": "48%", "display": "inline-block"}),
        
        html.Div([
            dcc.Graph(id="graph-satisfaction")
        ], style={"width": "48%", "display": "inline-block"})
    ])
])

# Callbacks — la magie du dashboard interactif !
@app.callback(
    [Output("metric-ca", "children"),
     Output("metric-commandes", "children"),
     Output("metric-satisfaction", "children"),
     Output("metric-panier", "children"),
     Output("graph-ca-ville", "figure"),
     Output("graph-evolution", "figure"),
     Output("graph-produit", "figure"),
     Output("graph-satisfaction", "figure")],
    [Input("filtre-ville", "value"),
     Input("filtre-produit", "value")]
)
def update_dashboard(villes, produits):
    # Filtrer les données
    dff = df.copy()
    if villes:
        dff = dff[dff["ville"].isin(villes)]
    if produits:
        dff = dff[dff["produit"].isin(produits)]
    
    # Métriques
    ca_total = dff["ca_total"].sum()
    nb_commandes = len(dff)
    satisfaction = dff["satisfaction"].mean()
    panier_moyen = dff["ca_total"].mean()
    
    metric_ca = [
        html.H3(f"{ca_total/1e6:.1f}M", style={"color": "#7F77DD"}),
        html.P("CA Total (FCFA)")
    ]
    metric_commandes = [
        html.H3(f"{nb_commandes}", style={"color": "#1D9E75"}),
        html.P("Commandes")
    ]
    metric_satisfaction = [
        html.H3(f"{satisfaction:.1f}/5", style={"color": "#EF9F27"}),
        html.P("Satisfaction")
    ]
    metric_panier = [
        html.H3(f"{panier_moyen/1000:.0f}K", style={"color": "#D85A30"}),
        html.P("Panier moyen")
    ]
    
    # Graphique 1 : CA par ville
    ca_ville = dff.groupby("ville")["ca_total"].sum().reset_index()
    fig1 = px.bar(ca_ville, x="ville", y="ca_total",
                  color="ville", title="CA par ville",
                  labels={"ca_total": "CA (FCFA)"})
    
    # Graphique 2 : Evolution temporelle
    ca_mois = dff.groupby("mois")["ca_total"].sum().reset_index()
    fig2 = px.line(ca_mois, x="mois", y="ca_total",
                   title="Evolution du CA",
                   markers=True,
                   labels={"ca_total": "CA (FCFA)", "mois": "Mois"})
    
    # Graphique 3 : CA par produit
    ca_produit = dff.groupby("produit")["ca_total"].sum().reset_index()
    fig3 = px.pie(ca_produit, values="ca_total", names="produit",
                  title="Répartition par produit", hole=0.4)
    
    # Graphique 4 : Satisfaction par vendeur
    sat_vendeur = dff.groupby("vendeur")["satisfaction"].mean().reset_index()
    fig4 = px.bar(sat_vendeur, x="vendeur", y="satisfaction",
                  color="vendeur", title="Satisfaction par vendeur",
                  labels={"satisfaction": "Score moyen"})
    
    return (metric_ca, metric_commandes, metric_satisfaction, 
            metric_panier, fig1, fig2, fig3, fig4)

# Lancer le serveur
if __name__ == "__main__":
    app.run(debug=True, port=8050)