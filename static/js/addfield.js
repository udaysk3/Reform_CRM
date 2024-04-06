function addField() {
  const addField = document.querySelector('.add-field');

  const newField = document.createElement('div');

  newField.classList.add('my-3', 'row');
  newField.innerHTML = `
<input type="text" class=" col-sm-2"  placeholder="Label" name="dynamic_label">
<div class="col-sm-4">
<select class="form-select" id="name" name="dynamic_type">
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
<a href="#" class="delete-user-btn col-sm-2" onclick="deleteField(this)">
   <svg xmlns="http://www.w3.org/2000/svg" class="text-danger icon icon-tabler icon-tabler-trash" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 7l16 0" /><path d="M10 11l0 6" /><path d="M14 11l0 6" /><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" /><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" /></svg>
     </a>    
   </div>                 
`;

  addField.parentElement.insertAdjacentElement('beforeBegin', newField);

}

function deleteField(e) {
  e.parentElement.remove()
}
