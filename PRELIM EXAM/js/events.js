const events = [
  {
    title: "Web Development Seminar",
    date: "March 10, 2026",
    category: "Seminar",
    description: "A seminar on modern web technologies."
  },
  {
    title: "JavaScript Workshop",
    date: "March 18, 2026",
    category: "Workshop",
    description: "Hands-on JavaScript training."
  },
  {
    title: "Coding Competition",
    date: "April 2, 2026",
    category: "Competition",
    description: "Programming competition for students."
  }
];

const eventList = document.getElementById("eventList");
const filter = document.getElementById("categoryFilter");
const modal = document.getElementById("eventModal");
const closeBtn = document.querySelector(".close-btn");

function renderEvents(data) {
  eventList.innerHTML = "";
  data.forEach(e => {
    const card = document.createElement("div");
    card.className = "event-card";
    card.innerHTML = `<h4>${e.title}</h4><p>${e.date}</p><p>${e.category}</p>`;
    card.onclick = () => {
      modal.style.display = "block";
      document.getElementById("modalTitle").innerText = e.title;
      document.getElementById("modalDate").innerText = e.date;
      document.getElementById("modalCategory").innerText = e.category;
      document.getElementById("modalDescription").innerText = e.description;
    };
    eventList.appendChild(card);
  });
}

filter.onchange = () => {
  if (filter.value === "all") renderEvents(events);
  else renderEvents(events.filter(e => e.category === filter.value));
};

closeBtn.onclick = () => modal.style.display = "none";
renderEvents(events);
