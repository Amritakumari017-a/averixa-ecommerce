document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector(".menu-toggle");
  const mobileNav = document.querySelector(".mobile-nav");
  if (menuButton && mobileNav) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      mobileNav.classList.toggle("is-open", !open);
    });
  }
  document.querySelectorAll(".message-close").forEach(button => {
    button.addEventListener("click", () => button.closest(".message")?.remove());
  });
  document.querySelectorAll("input[type='number']").forEach(input => {
    input.addEventListener("change", () => {
      const min = Number(input.min || 0);
      const max = Number(input.max || 999);
      const value = Number(input.value || min);
      input.value = String(Math.min(max, Math.max(min, value)));
    });
  });
});
