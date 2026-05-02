from flask import Flask, request, jsonify, render_template
from db import get_db, init_db
from datetime import datetime

app = Flask(__name__)
init_db()

def nb_mois_depuis(date_str):
    d = datetime.strptime(date_str, "%d/%m/%Y")
    now = datetime.now()
    return max(1, (now.year - d.year)*12 + (now.month - d.month) + 1)

def calcul_dette(membre, cotisations):
    mois = nb_mois_depuis(membre["date"])
    total_du = mois * membre["montant"]

    total_paye = sum(c["montant"] for c in cotisations if c["membre_id"] == membre["id"])
    dette = max(0, total_du - total_paye)

    return {**membre, "mois": mois, "dette": dette}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM membres WHERE actif=1")
    membres = cur.fetchall()

    cur.execute("SELECT * FROM cotisations")
    cotisations = cur.fetchall()

    cur.execute("SELECT * FROM depenses")
    depenses = cur.fetchall()

    conn.close()

    membres_list = [
        {"id": m[0], "nom": m[1], "tel": m[2], "montant": m[3], "date": m[5]}
        for m in membres
    ]

    cotis_list = [{"membre_id": c[1], "montant": c[2]} for c in cotisations]

    result = [calcul_dette(m, cotis_list) for m in membres_list]

    total_cot = sum(c["montant"] for c in cotis_list)
    total_dep = sum(d[2] for d in depenses)

    return jsonify({
        "membres": result,
        "total_cotisations": total_cot,
        "total_depenses": total_dep,
        "solde": total_cot - total_dep
    })

@app.route("/membre", methods=["POST"])
def add_membre():
    data = request.json
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO membres (nom, tel, montant, date)
    VALUES (?, ?, ?, ?)
    """, (
        data["nom"],
        data.get("tel"),
        data["montant"],
        datetime.now().strftime("%d/%m/%Y")
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/cotisation", methods=["POST"])
def add_cotisation():
    data = request.json
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO cotisations (membre_id, montant, periode, date)
    VALUES (?, ?, ?, ?)
    """, (
        data["membre_id"],
        data["montant"],
        data["periode"],
        datetime.now().strftime("%d/%m/%Y")
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/depense", methods=["POST"])
def add_depense():
    data = request.json
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO depenses (motif, montant, par, date)
    VALUES (?, ?, ?, ?)
    """, (
        data["motif"],
        data["montant"],
        data.get("par"),
        datetime.now().strftime("%d/%m/%Y")
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
