let burger = document.querySelector(".header__burger-menu");
let menu = document.querySelector(".navigation");
let body = document.querySelector("body");
burger.onclick = () => {
  menu.classList.toggle("navigation--active");
  body.classList.toggle("body--stop-scroll");
  burger.classList.toggle("burger--active");
};

menu.onclick = () => {
    menu.classList.toggle("navigation--active");
    burger.classList.toggle("burger--active");
};

