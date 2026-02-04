const form = document.getElementById("registerForm");
const message = document.getElementById("formMessage");

form.addEventListener("submit", e => {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const course = document.getElementById("course").value;

  if (!name || !email || !course) {
    message.textContent = "All fields are required.";
    message.style.color = "red";
    return;
  }

  localStorage.setItem("jpcsMember", JSON.stringify({ name, email, course }));
  message.textContent = "Registration successful!";
  message.style.color = "green";
  form.reset();
});
