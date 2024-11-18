function loadContent(route) {
    fetch(route)
        .then(response => response.text())
        .then(data => {
            document.getElementById('main-content').innerHTML = data;

            // Update active link
            const links = document.querySelectorAll('.sidebar ul li a');
            links.forEach(link => link.classList.remove('active'));
            const activeLink = Array.from(links).find(link => link.getAttribute('onclick').includes(route));
            if (activeLink) activeLink.classList.add('active');
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
