import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import requests
import pandas as pd

app = dash.Dash(__name__)
app.title = "ThreatMind"

BASE = "http://127.0.0.1:5000/api"
BG = "#0d1117"; CARD = "#161b22"; BORDER = "#30363d"
RED = "#ff4d4d"; ORANGE = "#f97316"; YELLOW = "#facc15"
GREEN = "#22c55e"; BLUE = "#38bdf8"; TEXT = "#e6edf3"; SUBTEXT = "#8b949e"

def safe_get(endpoint):
    try:
        r = requests.get(f"{BASE}/{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API error [{endpoint}]: {e}")
        return None

def safe_post(endpoint, payload):
    try:
        r = requests.post(f"{BASE}/{endpoint}", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API error [{endpoint}]: {e}")
        return None

def card(children, style=None):
    base = {"background": CARD, "border": f"1px solid {BORDER}",
            "borderRadius": "12px", "padding": "20px"}
    if style: base.update(style)
    return html.Div(children, style=base)

def metric_card(label, value, color=BLUE, icon=""):
    return card([
        html.Div(f"{icon} {label}", style={"color": SUBTEXT, "fontSize": "12px",
                                            "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(str(value), style={"color": color, "fontSize": "32px",
                                    "fontWeight": "800", "marginTop": "6px"}),
    ], {"flex": "1", "minWidth": "150px"})

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Span("🛡️", style={"fontSize": "28px"}),
            html.Span(" ThreatMind", style={"fontSize": "26px", "fontWeight": "800",
                                             "color": RED, "marginLeft": "10px"})
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div("ML-Based Insider Threat Detection Platform",
                 style={"color": SUBTEXT, "fontSize": "13px", "marginTop": "4px"})
    ], style={"background": CARD, "border": f"1px solid {BORDER}", "borderRadius": "14px",
              "padding": "24px 32px", "marginBottom": "24px"}),

    html.Div(id="summary-cards",
             style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

    html.Div([
        card([html.H3("📈 Daily Risk Trend", style={"color": TEXT, "margin": "0 0 16px"}),
              dcc.Graph(id="trend-chart", style={"height": "280px"})],
             {"flex": "2", "minWidth": "380px"}),
        card([html.H3("🚨 Live Alerts", style={"color": RED, "margin": "0 0 16px"}),
              html.Div(id="alerts-list", style={"maxHeight": "280px", "overflowY": "auto"})],
             {"flex": "1", "minWidth": "280px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"}),

    card([html.H3("👥 User Risk Overview", style={"color": TEXT, "margin": "0 0 16px"}),
          html.Div(id="user-table")], {"marginBottom": "24px"}),

    html.Div([
        card([html.H3("🎯 Risk Distribution", style={"color": TEXT, "margin": "0 0 16px"}),
              dcc.Graph(id="risk-dist", style={"height": "280px"})],
             {"flex": "1", "minWidth": "300px"}),
        card([
            html.H3("🔍 User Inspector", style={"color": TEXT, "margin": "0 0 16px"}),
            dcc.Input(id="user-input", type="text", placeholder="e.g. user_000",
                      debounce=True, style={"width": "100%", "padding": "10px 14px",
                          "background": "#0d1117", "border": f"1px solid {BORDER}",
                          "borderRadius": "8px", "color": TEXT, "fontSize": "14px",
                          "marginBottom": "12px", "boxSizing": "border-box"}),
            html.Div(id="user-detail")
        ], {"flex": "1", "minWidth": "300px"}),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

    card([
        html.H3("⚡ Live Threat Predictor", style={"color": TEXT, "margin": "0 0 20px"}),
        html.Div([
            *[html.Div([
                html.Label(label, style={"color": SUBTEXT, "fontSize": "12px",
                                          "textTransform": "uppercase", "letterSpacing": "1px"}),
                dcc.Input(id=id_, type="number", value=default, step=step, style={
                    "width": "100%", "padding": "8px 12px", "background": "#0d1117",
                    "border": f"1px solid {BORDER}", "borderRadius": "8px",
                    "color": TEXT, "fontSize": "14px", "marginTop": "4px", "boxSizing": "border-box"
                })
            ], style={"flex": "1", "minWidth": "140px"})
              for label, id_, default, step in [
                  ("Login Hour",     "p-login",   9,   1),
                  ("Files Accessed", "p-files",   10,  1),
                  ("Emails Sent",    "p-emails",  20,  1),
                  ("Session (min)",  "p-session", 420, 10),
                  ("Failed Logins",  "p-failed",  0,   1),
                  ("VPN (0/1)",      "p-vpn",     0,   1),
                  ("Upload (MB)",    "p-upload",  10,  5),
              ]],
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"}),
        html.Button("🔍 Analyze Behavior", id="predict-btn", n_clicks=0, style={
            "background": f"linear-gradient(135deg, {RED}, {ORANGE})", "color": "white",
            "border": "none", "borderRadius": "8px", "padding": "12px 28px",
            "fontSize": "14px", "fontWeight": "700", "cursor": "pointer"
        }),
        html.Div(id="predict-result", style={"marginTop": "16px"})
    ]),

    dcc.Interval(id="refresh", interval=30000, n_intervals=0),
], style={"background": BG, "minHeight": "100vh", "padding": "28px",
          "fontFamily": "'Segoe UI', system-ui, sans-serif", "color": TEXT,
          "maxWidth": "1400px", "margin": "0 auto"})


@app.callback(Output("summary-cards", "children"), Input("refresh", "n_intervals"))
def update_summary(_):
    s = safe_get("summary")
    if not s:
        return [html.Div("⚠️ API not reachable — is app.py running?", style={"color": RED})]
    return [
        metric_card("Total Users",    s["total_users"],    BLUE,   "👤"),
        metric_card("Flagged Users",  s["flagged_users"],  RED,    "🚨"),
        metric_card("High Risk",      s["high_risk_users"],ORANGE, "⚠️"),
        metric_card("Anomaly Events", s["anomaly_events"], YELLOW, "📌"),
        metric_card("Detection Rate", f"{s['detection_rate']}%", GREEN, "✅"),
    ]

@app.callback(Output("trend-chart", "figure"), Input("refresh", "n_intervals"))
def update_trend(_):
    data = safe_get("trend")
    if not data:
        return go.Figure()
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["avg_risk"], mode="lines+markers",
        name="Avg Risk", line=dict(color=RED, width=2),
        fill="tozeroy", fillcolor="rgba(255,77,77,0.08)"))
    fig.add_trace(go.Bar(x=df["date"], y=df["anomalies"], name="Anomalies",
        marker_color=ORANGE, opacity=0.5, yaxis="y2"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT, margin=dict(l=0,r=0,t=0,b=0),
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(gridcolor=BORDER, title="Risk Score"),
        yaxis2=dict(overlaying="y", side="right", title="Anomalies", showgrid=False),
        xaxis=dict(gridcolor=BORDER))
    return fig

@app.callback(Output("alerts-list", "children"), Input("refresh", "n_intervals"))
def update_alerts(_):
    alerts = safe_get("alerts")
    if not alerts:
        return [html.Div("No alerts available", style={"color": SUBTEXT})]
    items = []
    for a in alerts[:8]:
        color = RED if a["risk_score"] >= 80 else ORANGE if a["risk_score"] >= 60 else YELLOW
        items.append(html.Div([
            html.Div([
                html.Span(a["user_id"], style={"fontWeight": "700", "color": TEXT}),
                html.Span(f" • {a['department']}", style={"color": SUBTEXT, "fontSize": "11px"}),
                html.Span(f"  {a['risk_score']}", style={"color": color, "fontWeight": "800",
                                                           "float": "right", "fontSize": "15px"}),
            ]),
            html.Div(", ".join(a["reasons"]),
                     style={"color": SUBTEXT, "fontSize": "11px", "marginTop": "3px"}),
            html.Div(a["date"], style={"color": BORDER, "fontSize": "10px", "marginTop": "2px"}),
        ], style={"padding": "10px 12px", "marginBottom": "8px", "background": "#0d1117",
                  "borderRadius": "8px", "borderLeft": f"3px solid {color}"}))
    return items

@app.callback(Output("user-table", "children"), Input("refresh", "n_intervals"))
def update_table(_):
    users = safe_get("users")
    if not users:
        return html.Div("⚠️ Could not load users — check app.py is running", style={"color": RED})
    df = pd.DataFrame(users).head(15)
    rows = []
    for _, r in df.iterrows():
        color = (RED if r["max_risk_score"] >= 80 else ORANGE if r["max_risk_score"] >= 60
                 else YELLOW if r["max_risk_score"] >= 40 else GREEN)
        rows.append(html.Tr([
            html.Td(r["user_id"],      style={"color": BLUE,  "fontWeight": "600", "padding": "8px 12px"}),
            html.Td(r["department"],   style={"color": TEXT,  "padding": "8px 12px"}),
            html.Td(r["threat_level"], style={"color": color, "fontWeight": "700", "padding": "8px 12px"}),
            html.Td(f'{r["avg_risk_score"]:.1f}', style={"color": color, "padding": "8px 12px"}),
            html.Td(f'{r["max_risk_score"]:.1f}', style={"color": RED, "fontWeight": "700", "padding": "8px 12px"}),
            html.Td(str(int(r["anomaly_count"])), style={"color": ORANGE, "padding": "8px 12px"}),
        ]))
    return html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color": SUBTEXT, "padding": "8px 12px", "textAlign": "left",
                               "fontSize": "11px", "textTransform": "uppercase",
                               "letterSpacing": "1px", "borderBottom": f"1px solid {BORDER}"})
            for h in ["User ID", "Department", "Threat Level", "Avg Risk", "Max Risk", "Anomalies"]
        ])),
        html.Tbody(rows)
    ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"})

@app.callback(Output("risk-dist", "figure"), Input("refresh", "n_intervals"))
def update_dist(_):
    users = safe_get("users")
    if not users:
        return go.Figure()
    scores = [u["avg_risk_score"] for u in users]
    fig = go.Figure(go.Histogram(x=scores, nbinsx=20,
        marker=dict(color=scores,
            colorscale=[[0, GREEN],[0.4, YELLOW],[0.7, ORANGE],[1, RED]],
            line=dict(width=0))))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT, margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(title="Risk Score", gridcolor=BORDER),
        yaxis=dict(title="Users", gridcolor=BORDER), showlegend=False)
    return fig

@app.callback(Output("user-detail", "children"), Input("user-input", "value"))
def update_user_detail(user_id):
    if not user_id:
        return html.Div("Enter a user ID above to inspect.", style={"color": SUBTEXT, "fontSize": "13px"})
    data = safe_get(f"user/{user_id}")
    if not data or "error" in data:
        return html.Div("❌ User not found", style={"color": RED})
    color = (RED if data["max_risk"] >= 80 else ORANGE if data["max_risk"] >= 60
             else YELLOW if data["max_risk"] >= 40 else GREEN)
    last5 = data["timeline"][-5:]
    rows = [html.Tr([
        html.Td(r["date"], style={"color": SUBTEXT, "fontSize": "11px", "padding": "4px 8px"}),
        html.Td(f'{r["risk_score"]:.0f}', style={"color": RED if r["predicted_anomaly"] else GREEN,
                                                   "fontWeight": "700", "padding": "4px 8px"}),
        html.Td("⚠️" if r["predicted_anomaly"] else "✅", style={"padding": "4px 8px"}),
    ]) for r in last5]
    return html.Div([
        html.Div([
            html.Span(f"🏢 {data['department']}", style={"color": SUBTEXT, "fontSize": "12px"}),
            html.Span(f"  Max Risk: ", style={"color": SUBTEXT, "fontSize": "12px"}),
            html.Span(f"{data['max_risk']}", style={"color": color, "fontWeight": "800"}),
            html.Span(f"  Anomaly Days: {data['anomaly_days']}", style={"color": ORANGE, "fontSize": "12px"}),
        ], style={"marginBottom": "10px"}),
        html.Table([
            html.Thead(html.Tr([html.Th(h, style={"color": SUBTEXT, "fontSize": "10px",
                "textTransform": "uppercase", "padding": "4px 8px",
                "borderBottom": f"1px solid {BORDER}"}) for h in ["Date", "Risk", "Status"]])),
            html.Tbody(rows)
        ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "12px"})
    ])

@app.callback(
    Output("predict-result", "children"),
    Input("predict-btn", "n_clicks"),
    [dash.dependencies.State(id_, "value") for id_ in
     ["p-login", "p-files", "p-emails", "p-session", "p-failed", "p-vpn", "p-upload"]],
    prevent_initial_call=True
)
def predict(n, login, files, emails, session, failed, vpn, upload):
    payload = {"login_hour": login or 9, "files_accessed": files or 10,
               "emails_sent": emails or 20, "session_duration_min": session or 420,
               "failed_logins": failed or 0, "vpn_usage": vpn or 0, "data_uploaded_mb": upload or 10}
    r = safe_post("predict", payload)
    if not r:
        return html.Div("⚠️ Prediction failed — check app.py is running", style={"color": RED})
    color = RED if r["risk_score"] >= 80 else ORANGE if r["risk_score"] >= 60 else GREEN
    return html.Div([
        html.Div(f"{'🚨' if r['is_threat'] else '✅'} {r['message']}",
                 style={"fontSize": "16px", "fontWeight": "700", "color": color}),
        html.Div([
            html.Span("Risk Score: ", style={"color": SUBTEXT}),
            html.Span(f"{r['risk_score']:.1f}", style={"color": color, "fontWeight": "800", "fontSize": "22px"}),
            html.Span(" / 100", style={"color": SUBTEXT}),
            html.Span("  Level: ", style={"color": SUBTEXT, "marginLeft": "16px"}),
            html.Span(r["threat_level"], style={"color": color, "fontWeight": "700"}),
        ], style={"marginTop": "8px"})
    ], style={"background": "#0d1117", "borderRadius": "10px",
              "padding": "16px 20px", "borderLeft": f"4px solid {color}"})

if __name__ == "__main__":
    print("🖥️  ThreatMind Dashboard → http://127.0.0.1:8050")
    app.run(debug=False, port=8050)
