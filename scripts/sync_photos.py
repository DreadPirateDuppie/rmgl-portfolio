#!/usr/bin/env python3
import os
import sys
import shutil
import json
import subprocess
from datetime import datetime

SYNC_SRC = "/Users/chiiefbaka/Documents/Photos/RMGL_Portfolio_Sync"
REPO_DIR = "/Users/chiiefbaka/Desktop/rmgl-portfolio"
LOG_FILE = os.path.join(REPO_DIR, "sync.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}\n"
    print(entry, end="")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(entry)
    except Exception:
        pass

def run_sync():
    log("Checking for new photos in RMGL_Portfolio_Sync...")
    if not os.path.exists(SYNC_SRC):
        log(f"Sync source folder {SYNC_SRC} does not exist. Skipping.")
        return

    categories = {
        "Portraits": "portraits",
        "Skating": "skating",
        "Landscape": "landscape"
    }

    new_files_count = 0

    img_dir = os.path.join(REPO_DIR, "img")
    disp_dir = os.path.join(REPO_DIR, "display")
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(disp_dir, exist_ok=True)

    galleries_json_path = os.path.join(REPO_DIR, "galleries.json")
    if os.path.exists(galleries_json_path):
        with open(galleries_json_path, "r") as f:
            galleries = json.load(f)
    else:
        galleries = {"portraits": [], "skating": [], "landscape": []}

    for folder_name, cat_key in categories.items():
        cat_src = os.path.join(SYNC_SRC, folder_name)
        if not os.path.exists(cat_src):
            continue

        existing_cat_files = set(galleries.get(cat_key, []))
        
        for file in sorted(os.listdir(cat_src)):
            if file.startswith(".") or not file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            
            # Destination file name
            dest_img = os.path.join(img_dir, file)
            dest_disp = os.path.join(disp_dir, file)
            src_file = os.path.join(cat_src, file)

            if not os.path.exists(dest_img) or file not in existing_cat_files:
                log(f"New photo detected: {folder_name}/{file}")
                shutil.copy2(src_file, dest_img)
                shutil.copy2(src_file, dest_disp)
                
                if cat_key not in galleries:
                    galleries[cat_key] = []
                if file not in galleries[cat_key]:
                    galleries[cat_key].append(file)
                
                new_files_count += 1

    if new_files_count > 0:
        log(f"Processed {new_files_count} new photo(s). Updating galleries.json...")
        with open(galleries_json_path, "w") as f:
            json.dump(galleries, f, indent=1)

        # Commit and push to git
        log("Committing and pushing to GitHub Pages...")
        try:
            subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True)
            subprocess.run([
                "git", "-c", "user.email=ryan.m.g.lothian@gmail.com",
                "-c", "user.name=DreadPirateDuppie",
                "commit", "-m", f"Auto-sync {new_files_count} new photo(s) from RMGL_Portfolio_Sync"
            ], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
            log("Successfully published new photos to GitHub Pages!")
        except Exception as e:
            log(f"Error pushing changes to git: {e}")
    else:
        log("No new photos found. Sync up to date.")

if __name__ == "__main__":
    run_sync()
