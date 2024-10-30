const body = document.querySelector("body");
const darkLight = document.querySelector("#darkLight");
const sidebar = document.querySelector(".sidebar");
const submenuItems = document.querySelectorAll(".submenu_item");
const sidebarOpen = document.querySelector("#sidebarOpen");
const sidebarClose = document.querySelector(".collapse_sidebar");
const sidebarExpand = document.querySelector(".expand_sidebar");
const full_logo = document.querySelector(".full_logo");
const logo = document.querySelector(".logo");
const main_content = document.querySelector(".main_content");
sidebarOpen.addEventListener("click", () => sidebar.classList.toggle("close"));
sidebarOpen.addEventListener("click", () => main_content.classList.toggle("open"));

sidebarClose.addEventListener("click", () => {
  sidebar.classList.add("close", "hoverable");
  main_content.classList.remove("open", "hoverable");
});
sidebarExpand.addEventListener("click", () => {
  sidebar.classList.remove("close", "hoverable");
  main_content.classList.add("open", "hoverable");
});

sidebar.addEventListener("mouseenter", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.remove("close");
    main_content.classList.add("open");
  }
});
sidebar.addEventListener("mouseleave", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.add("close");
    main_content.classList.remove("open");
  }
});

sidebarClose.addEventListener("click", () => {
  if (sidebar.classList.contains("close")) {
    main_content.classList.add('open');
    full_logo.style.display = 'none';
    logo.style.display = 'flex';
  } else{
    main_content.classList.remove('open');
    full_logo.style.display = 'flex';
    logo.style.display = 'none';
  }
});
sidebarExpand.addEventListener("click", () => {
    if (sidebar.classList.contains("close")) {
      main_content.classList.add('open');
      full_logo.style.display = 'none';
      logo.style.display = 'flex';
    } else{
      main_content.classList.remove('open');
        full_logo.style.display = 'flex';
        logo.style.display = 'none';
    }
});

sidebar.addEventListener("mouseenter", () => {
  if (sidebar.classList.contains("close")) {
    main_content.classList.add('open');
    full_logo.style.display = 'none';
    logo.style.display = 'flex';
  } else{
    main_content.classList.remove('open');
    full_logo.style.display = 'flex';
    logo.style.display = 'none';
  }
});
sidebar.addEventListener("mouseleave", () => {
  if (sidebar.classList.contains("close")) {
    main_content.classList.add('open');
    full_logo.style.display = 'none';
    logo.style.display = 'flex';
  } else{
    main_content.classList.remove('open');
    full_logo.style.display = 'flex';
    logo.style.display = 'none';
  }
});


submenuItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    item.classList.toggle("show_submenu");
    submenuItems.forEach((item2, index2) => {
      if (index !== index2) {
        item2.classList.remove("show_submenu");
      }
    });
  });
});

if (window.innerWidth < 768) {
  sidebar.classList.add("close");
} else {
  sidebar.classList.remove("close");
}