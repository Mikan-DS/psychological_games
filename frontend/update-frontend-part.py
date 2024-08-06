import glob
import os
import shutil

if os.path.basename(os.getcwd()) != 'psychological_games_frontend':
    os.chdir('psychological_games_frontend')
os.system('npm run build')

# Получаем список файлов в директории
js_files = glob.glob('build/static/js/*.js')

os.makedirs("../static/frontend/js/", exist_ok=True)
# Копируем файлы в нужную директорию
for file in js_files:
    shutil.copy(file, '../static/frontend/js/psychological_games-app.js')

# Получаем список файлов в директории
css_files = glob.glob('build/static/css/*.css')

os.makedirs("../static/frontend/css/", exist_ok=True)
# Копируем файлы в нужную директорию
for file in css_files:
    shutil.copy(file, '../static/frontend/css/psychological_games-app.css')

shutil.rmtree("../static/media", ignore_errors=True)
shutil.copytree("build/static/media", "../static/media", dirs_exist_ok=True)
