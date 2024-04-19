function addField() {
  const addField = document.querySelector('.add-field');

  const newField = document.createElement('div');

  newField.classList.add('my-3', 'row');
  newField.innerHTML = `
<input type="text" class=" col-sm-2"  placeholder="Label" name="dynamic_label">
<div class="col-sm-4">
<select class="form-select" id="name" name="dynamic_type" onchange="checkSeletcted(this)">
<option value="text" >Text</option>
<option value="checkbox" >Checkbox</option> 
<option value="date" >Date</option>
<option value="email" >Email</option>
<option value="file" >File</option>
<option value="month" >Month</option>
<option value="number" >Number</option>
<option value="password" >Password</option>
<option value="time" >Time</option>
<option value="url" >URL</option>
<option value="dropdown" >Dropdown</option>

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

function checkSeletcted(e) {
  let selected = e.value;
  if (selected == 'dropdown') {
    const addOption = document.createElement('div');
    addOption.classList.add('my-3', 'row', 'ms-3');
    addOption.innerHTML = `
    <input type="text" class="col-sm-2"  placeholder="Option" name="dynamic_option">
    <a href="#" class="option add-option-btn col-sm-2" onclick="addOption(this)">
    <svg xmlns="http://www.w3.org/2000/svg" class="text-success icon icon-tabler icon-tabler-plus" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
    </a>
    <a href="#" class="delete-user-btn col-sm-2" onclick="deleteField(this)">
       <svg xmlns="http://www.w3.org/2000/svg" class="text-danger icon icon-tabler icon-tabler-trash" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 7l16 0" /><path d="M10 11l0 6" /><path d="M14 11l0 6" /><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" /><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" /></svg>
         </a>    
       </div>                 
    `;
    e.parentElement.nextElementSibling.insertAdjacentElement('afterEnd', addOption);

  }
}

function addOption(e) {
  const addOption = document.querySelector('.add-option-btn');

  const newOption = document.createElement('div');

  newOption.classList.add('my-3', 'row', 'ms-3');
  newOption.innerHTML = `
<input type="text" class=" col-sm-2"  placeholder="Option" name="dynamic_option">
<a href="#" class="option add-option-btn col-sm-2" onclick="addOption(this)">
<svg xmlns="http://www.w3.org/2000/svg" class="text-success icon icon-tabler icon-tabler-plus" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
</a>
<a href="#" class="delete-user-btn col-sm-2" onclick="deleteField(this)">
   <svg xmlns="http://www.w3.org/2000/svg" class="text-danger icon icon-tabler icon-tabler-trash" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 7l16 0" /><path d="M10 11l0 6" /><path d="M14 11l0 6" /><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2l1 -12" /><path d="M9 7v-3a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v3" /></svg>
     </a>                 
`;

  e.parentElement.insertAdjacentElement('afterEnd', newOption);
  
  
}

function submitForm() {
  const options = document.querySelectorAll('.option');
  options.forEach(option => {
    
    option.parentElement.parentElement.children[0].value = option.parentElement.parentElement.children[0].value + ',' + option.parentElement.children[0].value;
  // console.log(e.parentElement.parentElement.children[0].value)
  });
}