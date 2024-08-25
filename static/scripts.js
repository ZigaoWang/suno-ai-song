document.getElementById('generateForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const prompt = document.getElementById('prompt').value;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').innerHTML = '';

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'prompt': prompt
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('loading').style.display = 'none';

            if (data.error) {
                document.getElementById('result').innerHTML = `<p>Error: ${data.error}</p>`;
            } else {
                data.forEach(song => {
                    const songElement = document.createElement('div');
                    songElement.classList.add('song');
                    songElement.innerHTML = `
                        <h3>${song.title}</h3>
                        <img src="${song.image_url}" alt="Song Image">
                        <audio controls>
                            <source src="${song.audio_url}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                        <video controls>
                            <source src="${song.video_url}" type="video/mp4">
                            Your browser does not support the video element.
                        </video>
                    `;
                    document.getElementById('result').appendChild(songElement);
                });
            }
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
        });
});