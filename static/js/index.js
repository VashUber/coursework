const burger = document.querySelector(".header__burger-menu");
const menu = document.querySelector(".navigation");
const header = document.querySelector(".header")
const body = document.querySelector("body");

let lastScroll = 0
window.addEventListener('scroll', function(){
  let topScroll = window.pageYOffset 
  if (topScroll > lastScroll) {
    header.style.top = '-56px'
  }
  else {
    header.style.top = '0px'
  }
  lastScroll = topScroll
})

const menuActive = function() {
  menu.classList.toggle("navigation--active");
  body.classList.toggle("body--stop-scroll");
  burger.classList.toggle("burger--active");
}

burger.addEventListener("click", menuActive)
menu.addEventListener("click", menuActive)
