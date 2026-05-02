const API = "";

async function loadDashboard(){
  const res = await fetch(API + "/dashboard");
  const data = await res.json();

  console.log("DATA:", data);

  // Exemple affichage simple
  document.getElementById("sidebar-solde").textContent =
    data.solde.toLocaleString() + " FCFA";
}

async function ajouterMembre(){
  const nom = document.getElementById("m-nom").value;
  const tel = document.getElementById("m-tel").value;
  const montant = parseFloat(document.getElementById("m-montant").value);

  await fetch(API + "/membre", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({nom, tel, montant})
  });

  alert("Membre ajouté !");
  loadDashboard();
}

window.onload = loadDashboard;
