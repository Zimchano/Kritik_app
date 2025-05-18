import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///critic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER_COVERS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'covers')
app.config['UPLOAD_FOLDER_SAVES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'saves')
app.config['UPLOAD_FOLDER_SCREENSHOTS'] = os.path.join(app.config['UPLOAD_FOLDER'], 'screenshots')

@app.route('/files/<path:filename>')
def send_file(filename):
    folder, file = filename.split('/')
    file_path = os.path.join(app.config[f'UPLOAD_FOLDER_{folder.upper()}'], file)
    
    # Определяем MIME-тип по расширению
    mimetypes = {
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.sav': 'application/octet-stream',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }
    ext = os.path.splitext(file)[1].lower()
    
    response = send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))
    if ext in mimetypes:
        response.headers['Content-Type'] = mimetypes[ext]
        if ext in ('.zip', '.rar', '.sav'):
            response.headers['Content-Disposition'] = f'attachment; filename="{file}"'
    
    return response

@app.route('/delete_screenshot/<int:screenshot_id>', methods=['DELETE'])
def delete_screenshot(screenshot_id):
    try:
        screenshot = Screenshot.query.get_or_404(screenshot_id)
        
        # Удаляем файл
        file_path = os.path.join(app.config['UPLOAD_FOLDER_SCREENSHOTS'], screenshot.image_file)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Удаляем запись из БД
        db.session.delete(screenshot)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/delete_save/<int:save_id>', methods=['DELETE'])
def delete_save(save_id):
    try:
        save = GameSave.query.get_or_404(save_id)
        
        # Удаляем файл
        file_path = os.path.join(app.config['UPLOAD_FOLDER_SAVES'], save.save_file)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Удаляем запись из БД
        db.session.delete(save)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@app.route('/delete_game/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    try:
        game = Game.query.get_or_404(game_id)
        
        # Удаление всех связанных файлов
        # Обложка
        if game.cover_image:
            cover_path = os.path.join(app.config['UPLOAD_FOLDER_COVERS'], game.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        
        # Скриншоты
        for screenshot in game.screenshots:
            screenshot_path = os.path.join(app.config['UPLOAD_FOLDER_SCREENSHOTS'], screenshot.image_file)
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
        
        # Сохранения
        for save in game.saves:
            save_path = os.path.join(app.config['UPLOAD_FOLDER_SAVES'], save.save_file)
            if os.path.exists(save_path):
                os.remove(save_path)
        
        # Удаление записи из БД
        db.session.delete(game)
        db.session.commit()
        
        return {'redirect': url_for('index')}, 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500

# Инициализация db
db = SQLAlchemy()
db.init_app(app)

# Модели базы данных
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(100))
    opinion = db.Column(db.Text)
    rating = db.Column(db.Integer)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    play_time_hours = db.Column(db.Integer, nullable=True)
    saves = db.relationship('GameSave', backref='game', lazy=True)
    screenshots = db.relationship('Screenshot', backref='game', lazy=True)

class GameSave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    save_file = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Screenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    image_file = db.Column(db.String(100), nullable=False)

# Создаем базу данных
with app.app_context():
    db.create_all()

    # Функции для загрузки файлов
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def upload_file(file, folder, allowed_ext):
    if file and allowed_file(file.filename, allowed_ext):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config[f'UPLOAD_FOLDER_{folder.upper()}'], filename))
        return filename
    return None

# Маршруты
@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form['title']
        opinion = request.form['opinion']
        rating = int(request.form['rating'])
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        play_time_hours = request.form.get('play_time_hours')
        play_time_hours = int(play_time_hours) if play_time_hours and play_time_hours.strip() != '' else None

        cover_image = upload_file(request.files['cover_image'], 'covers', {'png', 'jpg', 'jpeg', 'gif'})
        
        game = Game(
            title=title, 
            cover_image=cover_image,
            opinion=opinion,
            rating=rating,
            start_date=start_date,
            end_date=end_date,
            play_time_hours=play_time_hours
        )
        
        db.session.add(game)
        db.session.commit()
        
        # Обработка сохранений
        save_files = request.files.getlist('save_files')
        save_descriptions = request.form.getlist('save_description')
        
        for i, save_file in enumerate(save_files):
            if save_file.filename != '':
                save_filename = upload_file(save_file, 'saves', {'zip', 'rar', 'sav'})
                if save_filename:
                    game_save = GameSave(
                        game_id=game.id,
                        save_file=save_filename,
                        description=save_descriptions[i] if i < len(save_descriptions) else ''
                    )
                    db.session.add(game_save)
        
        # Обработка скриншотов
        screenshot_files = request.files.getlist('screenshots')
        for screenshot in screenshot_files:
            if screenshot.filename != '':
                screenshot_filename = upload_file(screenshot, 'screenshots', {'png', 'jpg', 'jpeg', 'gif'})
                if screenshot_filename:
                    screenshot_obj = Screenshot(
                        game_id=game.id,
                        image_file=screenshot_filename
                    )
                    db.session.add(screenshot_obj)
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('add_game.html')

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game_detail.html', game=game)

@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if request.method == 'POST':
        
        game.title = request.form['title']
        game.opinion = request.form['opinion']
        game.rating = int(request.form['rating'])
        game.start_date = request.form.get('start_date')
        game.end_date = request.form.get('end_date')
        game.play_time_hours = int(request.form.get('play_time_hours', 0))

        # Обновление обложки, если загружена новая
        if 'cover_image' in request.files and request.files['cover_image'].filename != '':
            new_cover = upload_file(request.files['cover_image'], 'covers', {'png', 'jpg', 'jpeg', 'gif'})
            if new_cover:
                game.cover_image = new_cover
        
        # Добавление новых сохранений
        save_files = request.files.getlist('save_files')
        save_descriptions = request.form.getlist('save_description')
        
        for i, save_file in enumerate(save_files):
            if save_file.filename != '':
                save_filename = upload_file(save_file, 'saves', {'zip', 'rar', 'sav'})
                if save_filename:
                    game_save = GameSave(
                        game_id=game.id,
                        save_file=save_filename,
                        description=save_descriptions[i] if i < len(save_descriptions) else ''
                    )
                    db.session.add(game_save)
        
        # Добавление новых скриншотов
        screenshot_files = request.files.getlist('screenshots')
        for screenshot in screenshot_files:
            if screenshot.filename != '':
                screenshot_filename = upload_file(screenshot, 'screenshots', {'png', 'jpg', 'jpeg', 'gif'})
                if screenshot_filename:
                    screenshot_obj = Screenshot(
                        game_id=game.id,
                        image_file=screenshot_filename
                    )
                    db.session.add(screenshot_obj)
        
        db.session.commit()
        return redirect(url_for('game_detail', game_id=game.id))
    
    return render_template('edit_game.html', game=game)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER_COVERS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_SAVES'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_SCREENSHOTS'], exist_ok=True)
    app.run(debug=True)