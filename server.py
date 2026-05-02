from flask import Flask, request, jsonify, render_template
from db import get_db, init_db
from datetime import datetime

app = Flask(__name__)

# Initialisation DB
init_db()


# 🔹 UTILITAIRE : convertir ligne SQLite en dict
def row_to_dict(row):
    return dict(row) if row else None


# 🔹 Calcul nombre de mois depuis date ISO
def nb_mois_depuis(date_str):
    try:
        d = datetime.fromisoformat(date_str)
    except:
        return 1

    now = datetime.now()
    mois = (now.year - d.year) * 12 + (now.month - d.month)
    return max(1, mois + 1)


# 🔹 Calcul dette
def calcul_dette(membre, cotisations):
    mois = nb_mois_depuis(membre["date"])
    total_du = mois * membre["montant"]

    total_paye = sum(
        c["montant"] for c in cotisations if c["membre_id"] == membre["id"]
    )

    dette = max(0, total_du - total_paye)

    return {
        **membre,
        "mois": mois,
        "total_du": total_du,
        "total_paye": total_paye,
        "dette": dette
    }


# 🔹 PAGE PRINCIPALE
@app.route("/")
def home():
    return render_template("index.html")


# 🔹 DASHBOARD
@app.route("/dashboard")
def dashboard():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM membres WHERE actif=1")
        membres = [row_to_dict(m) for m in cur.fetchall()]

        cur.execute("SELECT * FROM cotisations")
        cotisations = [row_to_dict(c) for c in cur.fetchall()]

        cur.execute("SELECT * FROM depenses")
        depenses = [row_to_dict(d) for d in cur.fetchall()]

        conn.close()

        result = [calcul_dette(m, cotisations) for m in membres]

        total_cot = sum(c["montant"] for c in cotisations)
        total_dep = sum(d["montant"] for d in depenses)

        return jsonify({
            "membres": result,
            "total_cotisations": total_cot,
            "total_depenses": total_dep,
            "solde": total_cot - total_dep
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 AJOUT MEMBRE
@app.route("/membre", methods=["POST"])
def add_membre():
    try:
        data = request.json

        if not data.get("nom") or not data.get("montant"):
            return jsonify({"error": "Nom et montant requis"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO membres (nom, tel, montant, date)
        VALUES (?, ?, ?, ?)
        """, (
            data["nom"],
            data.get("tel"),
            data["montant"],
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 AJOUT COTISATION
@app.route("/cotisation", methods=["POST"])
def add_cotisation():
    try:
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
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 AJOUT DEPENSE
@app.route("/depense", methods=["POST"])
def add_depense():
    try:
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
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 TEST API
@app.route("/test")
def test():
    return jsonify({"message": "API OK"})


# 🔹 LANCEMENT LOCAL
if __name__ == "__main__":
    app.run(debug=True)
