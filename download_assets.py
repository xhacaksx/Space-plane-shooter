import urllib.request
import os

def download_file(url, filename):
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    filepath = os.path.join('assets', filename)
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

# Free game assets from OpenGameArt.org and similar free sources
assets = {
    'player.png': 'https://opengameart.org/sites/default/files/styles/medium/public/fighter_plane_preview.png',
    'enemy.png': 'https://opengameart.org/sites/default/files/styles/medium/public/enemy_plane_preview.png',
    'bullet.png': 'https://opengameart.org/sites/default/files/styles/medium/public/bullet_preview.png',
    'shoot.wav': 'https://opengameart.org/sites/default/files/laser5.wav',
    'explosion.wav': 'https://opengameart.org/sites/default/files/explosion_1.wav',
    'hit.wav': 'https://opengameart.org/sites/default/files/hit.wav',
    'game_music.mp3': 'https://opengameart.org/sites/default/files/DST-TowerDefenseTheme.mp3'
}

def main():
    print("Downloading game assets...")
    for filename, url in assets.items():
        download_file(url, filename)
    print("Download complete!")

if __name__ == "__main__":
    main() 