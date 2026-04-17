from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

# تحديد المسارات الأساسية
base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(base_dir, "../Frontend"))

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

    # مسار ملف الكوكيز داخل مجلد Backend
    cookies_path = os.path.join(base_dir, "cookies.txt")

    # إعدادات متقدمة لتخطي الحظر وجلب الجودات
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'listformats': True,
        'cookiefile': cookies_path, # استخدام ملف الكوكيز لتجنب رسالة (Sign in to confirm)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            data = {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "formats": []
            }

            # تصفية الجودات الفريدة
            seen_resolutions = set()
            
            for f in info.get('formats', []):
                res = f.get('height')
                # نختار الصيغ التي تحتوي على فيديو وصوت معاً (أو نعتمد على جلب الرابط المباشر)
                if res and res not in seen_resolutions:
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
            data['audio_url'] = audio_formats[-1].get('url') if audio_formats else None
            
            return jsonify(data)
    except Exception as e:
        # إرجاع رسالة خطأ واضحة في حال فشل الاتصال
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)