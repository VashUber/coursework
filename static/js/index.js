const burger = document.querySelector(".header__burger-menu");
const menu = document.querySelector(".navigation");
const body = document.querySelector("body");

const menuActive = function() {
  menu.classList.toggle("navigation--active");
  body.classList.toggle("body--stop-scroll");
  burger.classList.toggle("burger--active");
}

burger.addEventListener("click", menuActive)
menu.addEventListener("click", menuActive)
