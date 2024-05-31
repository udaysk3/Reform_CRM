document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#city").addEventListener("input", event => {
        city_from(event);
    });

    document.querySelector("#city").addEventListener("focus", event => {
        city_from(event, true);
    });
});


function showplaces(input) {
    let box = input.parentElement.querySelector(".places_box");
    box.style.display = 'block';
}


function hideplaces(input) {
    let box = input.parentElement.querySelector(".places_box");
    setTimeout(() => {
        box.style.display = 'none';
    }, 300);
}

function selectplace(option) {
    let input = option.parentElement.parentElement.querySelector('input[type=text]');
    input.value = option.dataset.value.toUpperCase();
    input.dataset.value = option.dataset.value;
}

function city_from(event, focus=false) {
    let input = event.target;
    let list = document.querySelector('#city_from');
    showplaces(input);
    if(!focus) {
        input.dataset.value = '';
    }
    if(input.value.length > 0) {
        fetch('/query/cities/'+input.value)
        .then(response => response.json())
        .then(places => {
            list.innerHTML = '';
            places.forEach(element => {
                let div = document.createElement('div');
                div.setAttribute('class', 'each_city_from_list');
                div.classList.add('places__list');
                div.setAttribute('onclick', "selectplace(this)");
                div.setAttribute('data-value', element.city);
                div.innerText = `${element.city}`;
                list.append(div);
            });
        });
    }
}
















document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#county").addEventListener("input", (event) => {
    county_from(event);
  });

  document.querySelector("#county").addEventListener("focus", (event) => {
    county_from(event, true);
  });
});

function showplaces(input) {
  let box = input.parentElement.querySelector(".places_box");
  box.style.display = "block";
}

function hideplaces(input) {
  let box = input.parentElement.querySelector(".places_box");
  setTimeout(() => {
    box.style.display = "none";
  }, 300);
}

function selectplace(option) {
  let input =
    option.parentElement.parentElement.querySelector("input[type=text]");
  input.value = option.dataset.value.toUpperCase();
  input.dataset.value = option.dataset.value;
}

function county_from(event, focus = false) {
  let input = event.target;
  let list = document.querySelector("#county_from");
  showplaces(input);
  if (!focus) {
    input.dataset.value = "";
  }
  if (input.value.length > 0) {
    fetch("/query/countys/" + input.value)
      .then((response) => response.json())
      .then((places) => {
        list.innerHTML = "";
        places.forEach((element) => {
          let div = document.createElement("div");
          div.setAttribute("class", "each_county_from_list");
          div.classList.add("places__list");
          div.setAttribute("onclick", "selectplace(this)");
          div.setAttribute("data-value", element.county);
          div.innerText = `${element.county}`;
          list.append(div);
        });
      });
  }
}














document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#country").addEventListener("input", (event) => {
    country_from(event);
  });

  document.querySelector("#country").addEventListener("focus", (event) => {
    country_from(event, true);
  });
});

function showplaces(input) {
  let box = input.parentElement.querySelector(".places_box");
  box.style.display = "block";
}

function hideplaces(input) {
  let box = input.parentElement.querySelector(".places_box");
  setTimeout(() => {
    box.style.display = "none";
  }, 300);
}

function selectplace(option) {
  let input =
    option.parentElement.parentElement.querySelector("input[type=text]");
  input.value = option.dataset.value.toUpperCase();
  input.dataset.value = option.dataset.value;
}

function country_from(event, focus = false) {
  let input = event.target;
  let list = document.querySelector("#country_from");
  showplaces(input);
  if (!focus) {
    input.dataset.value = "";
  }
  if (input.value.length > 0) {
    fetch("/query/countries/" + input.value)
      .then((response) => response.json())
      .then((places) => {
        list.innerHTML = "";
        places.forEach((element) => {
          let div = document.createElement("div");
          div.setAttribute("class", "each_country_from_list");
          div.classList.add("places__list");
          div.setAttribute("onclick", "selectplace(this)");
          div.setAttribute("data-value", element.city);
          div.innerText = `${element.city}`;
            list.append(div);
            console.log(element);
        });
      });
  }
}