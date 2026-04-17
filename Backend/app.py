from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

frontend_path = os.path.abspath("../Frontend")

app = Flask(__name__, 
            template_folder=frontend_path, 
            static_folder=frontend_path,
            static_url_path='')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-info', methods=['POST'])
def fetch_info():
    video_url = request.json.get('url')
    if not video_url:
        return jsonify({"error": "يرجى إدخال الرابط"}), 400

    # إعدادات متقدمة لجلب كل الجودات
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'listformats': True # يسمح باستخراج قائمة كاملة
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            data = {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": []
            }

            # تصفية الجودات الفريدة لضمان عدم التكرار
            seen_resolutions = set()
            
            for f in info.get('formats', []):
                # نركز على صيغة mp4 أو الجودات التي لها قيمة 'height' (دقة)
                res = f.get('height')
                if res and res not in seen_resolutions:
                    # إضافة الجودة للقائمة
                    data['formats'].append({
                        "quality": f"{res}p",
                        "url": f.get('url'),
                        "filename": f"{info.get('title')}_{res}p.mp4"
                    })
                    seen_resolutions.add(res)
            
            # ترتيب الجودات من الأعلى للأقل
            data['formats'].sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
            
            # رابط الصوت (أفضل جودة صوت متاحة)
            audio_formats = [f for f in info.get('formats', []) if f.get('vcodec') == 'none']
            data['audio_url'] = audio_formats[-1].get('url') if audio_formats else info.get('url')
            
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)