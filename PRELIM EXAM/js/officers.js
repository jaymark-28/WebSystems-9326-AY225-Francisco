const officers = [
  { name: "Juan Dela Cruz", position: "President", description: "Leads the organization." },
  { name: "Maria Santos", position: "Vice President", description: "Assists the president." },
  { name: "Carlos Reyes", position: "Secretary", description: "Manages documentation." }
];

const list = document.getElementById("officerList");
const modal = document.getElementById("officerModal");
const closeBtn = document.querySelector(".close-btn");

officers.forEach(o => {
  const card = document.createElement("div");
  card.className = "officer-card";
  card.innerHTML = `
    <img src="assets/images/officer-placeholder.png">
    <h4>${o.name}</h4>
    <p>${o.position}</p>
  `;
  card.onclick = () => {
    modal.style.display = "block";
    officerName.innerText = o.name;
    officerPosition.innerText = o.position;
    officerDescription.innerText = o.description;
  };
  list.appendChild(card);
});

closeBtn.onclick = () => modal.style.display = "none";
