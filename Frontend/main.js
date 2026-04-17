let videoInfo = null;

document.getElementById('btnFetch').addEventListener('click', async function() {
    const url = document.getElementById('videoUrl').value.trim();
    if (!url) return alert("الرجاء إدخال الرابط أولاً");

    const loader = document.getElementById('loader');
    const resultArea = document.getElementById('resultArea');

    loader.classList.remove('d-none');
    resultArea.classList.add('d-none');

    try {
        const response = await fetch('/fetch-info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();

        if (data.error) {
            alert("خطأ في الفحص: " + data.error);
        } else {
            videoInfo = data;
            document.getElementById('videoThumb').src = data.thumbnail;
            document.getElementById('videoTitle').innerText = data.title;
            
            const qualityDiv = document.getElementById('qualityOptions');
            qualityDiv.innerHTML = '';

            data.formats.forEach((f, index) => {
                const label = document.createElement('label');
                label.className = 'quality-item d-flex w-100';
                label.innerHTML = `
                    <input type="radio" name="videoQuality" value="${f.url}" data-name="${f.filename}" ${index === 0 ? 'checked' : ''}>
                    <span class="text-white">جودة ${f.quality} (MP4)</span>
                `;
                qualityDiv.appendChild(label);
            });

            resultArea.classList.remove('d-none');
        }
    } catch (e) {
        alert("فشل السيرفر في الاستجابة");
    } finally {
        loader.classList.add('d-none');
    }
});

document.getElementById('btnDownload').addEventListener('click', function() {
    const isAudioOnly = document.getElementById('audioOnly').checked;
    const selectedInput = document.querySelector('input[name="videoQuality"]:checked');
    
    if (!selectedInput && !isAudioOnly) return alert("يرجى اختيار الجودة");

    const downloadUrl = isAudioOnly ? videoInfo.audio_url : selectedInput.value;
    const fileName = isAudioOnly ? `${videoInfo.title}.mp3` : selectedInput.getAttribute('data-name');

    // محاولة التحميل المباشر وتسمية الملف
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = fileName; // محاولة فرض الاسم
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});