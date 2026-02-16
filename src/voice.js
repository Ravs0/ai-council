
const API_BASE = window.location.origin;

export async function speak(text, language = 'hi-IN') {
    try {
        const response = await fetch(`${API_BASE}/api/voice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'tts',
                text: text,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error(`Voice API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success' && data.audio) {
            const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
            await audio.play();
            return audio;
        } else {
            console.error("Voice API returned error:", data.message);
            throw new Error(data.message || "Unknown error");
        }
    } catch (e) {
        console.error("Failed to generate speech:", e);
        throw e;
    }
}

export async function transcribe(audioBlob, language = 'hi-IN') {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];
            try {
                const response = await fetch(`${API_BASE}/api/voice`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: 'stt',
                        audio: base64Audio,
                        language: language
                    })
                });

                if (!response.ok) throw new Error(`STT API error: ${response.status}`);

                const data = await response.json();
                if (data.status === 'success') {
                    resolve(data.text);
                } else {
                    reject(data.message || "STT failed");
                }
            } catch (e) {
                reject(e);
            }
        };
        reader.readAsDataURL(audioBlob);
    });
}
