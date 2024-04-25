const dropArea = document.querySelector('.drop-section')
const listSection = document.querySelector('.list-section')
const listContainer = document.querySelector('.list')
const fileSelector = document.querySelector('.file-selector')
const fileSelectorInput = document.querySelector('.file-selector-input')

// upload files with browse button
fileSelector.onclick = () => fileSelectorInput.click()
fileSelectorInput.onchange = () => {
    [...fileSelectorInput.files].forEach((file) => {
        if(typeValidation(file.type)){
            uploadFile(file)
        }
    })
}

// check the file type
function typeValidation(type){
    var splitType = type.split('/')[0]
    if(type == 'application/pdf'){
        return true
    }
}

// when file is over the drag area
dropArea.ondragover = (e) => {
    e.preventDefault();
    [...e.dataTransfer.items].forEach((item) => {
        if(typeValidation(item.type)){
            dropArea.classList.add('drag-over-effect')
        }
    })
}
// when file leave the drag area
dropArea.ondragleave = () => {
    dropArea.classList.remove('drag-over-effect')
}
// when file drop on the drag area
dropArea.ondrop = (e) => {
    e.preventDefault();
    dropArea.classList.remove('drag-over-effect')
    if(e.dataTransfer.items){
        [...e.dataTransfer.items].forEach((item) => {
            if(item.kind === 'file'){
                const file = item.getAsFile();
                if(typeValidation(file.type)){
                    uploadFile(file)
                }
            }
        })
    }else{
        [...e.dataTransfer.files].forEach((file) => {
            if(typeValidation(file.type)){
                uploadFile(file)
            }
        })
    }
}

// Array to store uploaded files
let queuedFiles = [];

// Upload file function
function uploadFile(file) {
    listSection.style.display = 'block';
    var li = document.createElement('li');
    li.classList.add('in-prog');
    li.innerHTML = `
        <div class="col">
            <img src="icons/${iconSelector(file.type)}" alt="">
        </div>
        <div class="col">
            <div class="file-name">
                <div class="name">${file.name}</div>
                <span></span>
            </div>
            <div class="file-size">${(file.size / (1024 * 1024)).toFixed(2)} MB</div>
        </div>
        <div class="col">
            <svg xmlns="http://www.w3.org/2000/svg" class="cross" height="20" width="20"><path d="m5.979 14.917-.854-.896 4-4.021-4-4.062.854-.896 4.042 4.062 4-4.062.854.896-4 4.062 4 4.021-.854.896-4-4.063Z"/></svg>
            <svg xmlns="http://www.w3.org/2000/svg" class="tick" height="20" width="20"><path d="m8.229 14.438-3.896-3.917 1.438-1.438 2.458 2.459 6-6L15.667 7Z"/></svg>
        </div>
    `;
    listContainer.prepend(li);

    // Create FormData object and append necessary fields
    var data = new FormData();
    data.append('documents', file);
    // Add file to queued files
    queuedFiles.push({ file: file, formData: data, listItem: li });

    // Set up remove handler
    li.querySelector('.cross').onclick = () => {
        // Remove file from queuedFiles array
        const index = queuedFiles.findIndex((item) => item.file === file);
        if (index !== -1) {
            queuedFiles.splice(index, 1);
        }
        // Remove the list item from the DOM
        li.remove();
    };
    console.log(queuedFiles)
}

// Submit button click handler
document.querySelector('#submitBtn').addEventListener('click', () => {
    var name = document.querySelector('#name').value;
    var description = document.querySelector('#description').value;
    console.log(name, description, queuedFiles)

    // Create FormData object for all files
    var allData = new FormData();
    allData.append('name', name);
    allData.append('description', description);
    queuedFiles.forEach((queuedFile) => {
        allData.append('document', queuedFile.file);
    });

    // Add CSRF token to headers
    var csrftoken = getCookie('csrftoken');

    var http = new XMLHttpRequest();
    http.onload = () => {
        // Handle response as needed
        console.log('Files uploaded successfully');
        // Clear queued files and remove list items
        queuedFiles = [];
        document.querySelector('.list').innerHTML = '';
        // Optionally, redirect the user after successful upload
        window.location.href = "/funding_route";
    };

    http.open('POST', '/add_funding_route', true);
    http.setRequestHeader('X-CSRFToken', csrftoken);
    http.send(allData);
});

// Helper function to get CSRF token from cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// find icon for file
function iconSelector(type){
    var splitType = (type.split('/')[0] == 'application') ? type.split('/')[1] : type.split('/')[0];
    return splitType + '.png'
}