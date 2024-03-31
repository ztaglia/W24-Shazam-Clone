document.getElementById('recordBtn').addEventListener('click', startRecording);

let mediaRecorder;
let audioChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = []; // Reset chunks array for new recording

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
                console.log("Received data chunk with size:", event.data.size, "bytes");
                console.log("Total chunks received:", audioChunks.length);
            });

            mediaRecorder.addEventListener("stop", () => {
                convertChunksToAudio(audioChunks);
            });

            mediaRecorder.start();
            document.getElementById('status').innerText = "Recording...";
            console.log("Recording started...");

            // Automatically stop recording after 5 seconds
            setTimeout(() => {
                if (mediaRecorder.state === "recording") {
                    mediaRecorder.stop();
                    document.getElementById('status').innerText = "Processing...";
                    console.log("Recording stopped.");
                }
            }, 5000); // 5000 milliseconds = 5 seconds
        })
        .catch(e => console.error(e));
}

function convertChunksToAudio(chunks) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const reader = new FileReader();

    reader.onload = function() {
        audioContext.decodeAudioData(reader.result, (buffer) => {
            // Log the properties of the buffer to debug
            console.log("Buffer length: ", buffer.length); // Total number of samples
            console.log("Sample rate: ", buffer.sampleRate); // Sample rate of the audio data
            console.log("Channel data length: ", buffer.getChannelData(0).length); // Length of the audio data in the first channel

            encodeAudioBufferToMp3(buffer);
        });
    };
    reader.readAsArrayBuffer(new Blob(chunks));
}

function encodeAudioBufferToMp3(buffer) {
    const lameEncoder = new lamejs.Mp3Encoder(1, buffer.sampleRate, 128); // 1 for mono, 128kbps
    const samples = buffer.getChannelData(0); // Assuming mono audio
    const mp3Data = [];
    const sampleBlockSize = 1152; // Number of samples per frame for mp3
    for (let i = 0; i < samples.length; i += sampleBlockSize) {
        const sampleChunk = samples.subarray(i, i + sampleBlockSize);
        const mp3buf = lameEncoder.encodeBuffer(sampleChunk);
        if (mp3buf.length > 0) {
            mp3Data.push(new Int8Array(mp3buf));
        }
    }
    const mp3bufEnd = lameEncoder.flush(); // Finish writing mp3
    if (mp3bufEnd.length > 0) {
        mp3Data.push(new Int8Array(mp3bufEnd));
    }

    const blob = new Blob(mp3Data, {type: 'audio/mp3'});
    const url = URL.createObjectURL(blob);
    downloadMp3(url);
}

function downloadMp3(url) {
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'recorded_audio.mp3';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    document.getElementById('status').innerText = "Recording finished and MP3 downloaded.";
}
