function addField() {
  const addField = document.querySelector('.add-field');

  const newField = document.createElement('div');

  newField.classList.add('my-3', 'row');
  newField.innerHTML = `
<input type="text" class=" col-sm-2"  placeholder="Label">
<div class="col-sm-4">
<select class="form-select" id="name">
<option selected>Open this select menu</option>
<option value="button">button</option>
<option value="checkbox">checkbox</option>
<option value="color">color</option>
<option value="date">date</option>
<option value="datetime-local">datetime-local</option>
<option value="email">email</option>
<option value="file">file</option>
<option value="image">image</option>
<option value="month">month</option>
<option value="number">number</option>
<option value="password">password</option>
<option value="radio">radio</option>
<option value="range">range</option>
<option value="text">text</option>
<option value="time">time</option>
<option value="url">url</option>
<option value="week">week</option>

</select>
</div>
<button type="button" class="btn btn-primary col-sm-2 add-field" onclick="addField()">
  <i class="bi bi-plus-lg"></i> Add Field
</button>
</div>
`;

  addField.parentElement.insertAdjacentElement('afterend', newField);
  addField.remove();
}


