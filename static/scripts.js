document.addEventListener('DOMContentLoaded', function() {
    fetchCachedSongs();
});

document.getElementById('generateForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const prompt = document.getElementById('prompt').value;
    document.getElementById('loading').style.display = 'block';
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
                    fetchCachedSongs();  // Refresh the playlist after generating
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(6));

                        if (data.error) {
                            document.getElementById('loading').style.display = 'none';
                            document.getElementById('status').textContent = `Error: ${data.error}`;
                        } else if (data.result) {
                            document.getElementById('loading').style.display = 'none';
                            displaySongs(data.result, true);
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
        document.getElementById('status').textContent = `Error: ${error.message}`;
    });
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

function displaySongs(songs, prepend = false) {
    const result = document.getElementById('result');
    if (prepend) {
        // If prepend is true, add the new songs at the top
        songs.forEach(song => {
            if (!song.image_url || !song.audio_url || !song.video_url) {
                console.error('Missing data for song:', song);
                return;
            }

            const songElement = createSongElement(song);
            result.insertBefore(songElement, result.firstChild);
        });
    } else {
        result.innerHTML = '';  // Clear previous results
        songs.forEach(song => {
            if (!song.image_url || !song.audio_url || !song.video_url) {
                console.error('Missing data for song:', song);
                return;
            }

            const songElement = createSongElement(song);
            result.appendChild(songElement);
        });
    }
}

function createSongElement(song) {
    const songElement = document.createElement('div');
    songElement.classList.add('song');
    songElement.innerHTML = `
        <img src="${song.image_url}" alt="Song Image">
        <div class="song-details">
            <div class="song-title">${song.title}</div>
            <audio controls>
                <source src="${song.audio_url}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </div>
    `;
    songElement.addEventListener('click', () => {
        document.querySelectorAll('.song').forEach(el => el.classList.remove('active'));
        songElement.classList.add('active');
        showPopup(song.video_url, song.lyrics);
    });
    return songElement;
}

function showPopup(videoUrl, lyrics) {
    const video = document.getElementById('popupVideo');
    const lyricsContainer = document.getElementById('lyrics');
    video.src = videoUrl;
    lyricsContainer.textContent = lyrics;
}