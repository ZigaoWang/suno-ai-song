document.addEventListener('DOMContentLoaded', function() {
    fetchCachedSongs();
});

document.getElementById('generateForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const prompt = document.getElementById('prompt').value;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').innerHTML = '';
    document.getElementById('status').textContent = 'Generating...';
    document.getElementById('progress').textContent = '0%';

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
        return response.body;
    })
    .then(body => {
        const reader = body.getReader();
        const decoder = new TextDecoder();

        function read() {
            return reader.read().then(({ value, done }) => {
                if (done) {
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(6));

                        if (data.error) {
                            document.getElementById('loading').style.display = 'none';
                            document.getElementById('result').innerHTML = `<p>Error: ${data.error}</p>`;
                        } else if (data.result) {
                            document.getElementById('loading').style.display = 'none';
                            if (Array.isArray(data.result)) {
                                displaySongs(data.result);
                            } else {
                                displaySongs([data.result]);
                            }
                        } else {
                            document.getElementById('status').textContent = `Status: ${data.status}`;
                            document.getElementById('progress').textContent = `Progress: ${data.progress}`;
                        }
                    }
                });

                return read();
            });
        }

        return read();
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
    });
});

document.getElementById('previewButton').addEventListener('click', function () {
    const result = document.getElementById('result');
    const previewButton = document.getElementById('previewButton');

    if (result.innerHTML) {
        result.innerHTML = '';
        previewButton.textContent = 'Preview with Cached Songs';
    } else {
        document.getElementById('loading').style.display = 'block';

        fetch('/cached_songs', {
            method: 'GET'
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
                displaySongs(data);
                previewButton.textContent = 'Close Preview';
            }
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
        });
    }
});

function fetchCachedSongs() {
    fetch('/cached_songs', {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            displaySongs(data);
        }
    })
    .catch(error => {
        document.getElementById('result').innerHTML = `<p>Error: ${error.message}</p>`;
    });
}

function displaySongs(songs) {
    const result = document.getElementById('result');
    result.innerHTML = '';  // 清空之前的结果
    songs.forEach(song => {
        if (!song.image_url || !song.audio_url || !song.video_url) {
            console.error('Missing data for song:', song);
            return;
        }

        const songElement = document.createElement('div');
        songElement.classList.add('song');
        songElement.innerHTML = `
            <img src="${song.image_url}" alt="Song Image">
            <div class="song-details">
                <div class="song-title">${song.title}</div>
                <div class="song-tags">Energetic Pop</div>
                <audio controls>
                    <source src="${song.audio_url}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
                <div class="show-video" onclick="showPopup('${song.video_url}')">
                    <i class="fas fa-video"></i> Show Video
                </div>
            </div>
        `;
        result.appendChild(songElement);
    });
}

function showPopup(videoUrl) {
    const popup = document.getElementById('videoPopup');
    const video = document.getElementById('popupVideo');
    video.src = videoUrl;
    popup.classList.add('show');
}

function closePopup() {
    const popup = document.getElementById('videoPopup');
    const video = document.getElementById('popupVideo');
    video.pause();
    popup.classList.remove('show');
}