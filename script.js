let objects = [];

function createObject() {
    const rank = document.getElementById('rank').value;
    const classValue = document.getElementById('class').value;
    const type = document.getElementById('type').value;
    const label = document.getElementById('label').value;

    if (rank && classValue && type) {
        objects.push({ rank: parseInt(rank), class: classValue, type, label });
        updateObjectCount();
        clearInputs();
    } else {
        alert('Please fill all fields');
    }
}

function updateObjectCount() {
    document.getElementById('objectCount').textContent = objects.length;
}

function clearInputs() {
    ['rank', 'class', 'type', 'label'].forEach(id => document.getElementById(id).value = '');
}

function openImagePopup(imageUrls) {
    const popup = document.getElementById('imagePopup');
    const tabContainer = popup.querySelector('.tab');
    const tabContent = popup.querySelector('.tab-content');

    // Clear existing tabs and content
    tabContainer.innerHTML = '';
    tabContent.innerHTML = '';

    // Create tabs and content for each image
    imageUrls.forEach((url, index) => {
        const tabButton = document.createElement('button');
        tabButton.className = 'tablinks';
        tabButton.textContent = `Image ${index + 1}`;
        tabButton.onclick = (event) => openTab(event, `image${index}`);
        tabContainer.appendChild(tabButton);

        const tabPane = document.createElement('div');
        tabPane.id = `image${index}`;
        tabPane.className = 'tab-content';
        const img = document.createElement('img');
        img.src = url;
        tabPane.appendChild(img);
        tabContent.appendChild(tabPane);
    });

    // Open the first tab by default
    tabContainer.firstChild.click();

    popup.style.display = 'block';
}

function openTab(evt, tabName) {
    const tabContent = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = 'none';
    }

    const tabLinks = document.getElementsByClassName('tablinks');
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(' active', '');
    }

    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.className += ' active';
}

function closeImagePopup() {
    document.getElementById('imagePopup').style.display = 'none';
}

// Example usage:
function submitObjects() {
    // ... your existing code ...

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(objects)
    })
        .then(response => response.json())
        .then(data => {
            if (data.imageUrls) {
                openImagePopup(data.imageUrls);
            }
        })
        .catch(error => console.error('Error:', error));
}

