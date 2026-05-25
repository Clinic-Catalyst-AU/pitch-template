#!/usr/bin/env python3
"""
CC Pitch Deck Generator
Takes a client JSON file, fills the template, saves to output path.
Copies static slide images alongside the output.

Usage:
  python3 generate.py rav-infinity.json ~/Clients/Rav_Infinity_Skincare/Deliverables/pitch-deck.html
"""

import json
import sys
import os
import re
import shutil

def make_browser_frame(image_path=None, video_path=None, poster_path=None, placeholder_text="Screenshot will go here"):
    """Generate browser mockup HTML - with video, image, or placeholder."""
    bar = '''<div class="browser-frame">
  <div class="browser-bar"><span class="browser-dot r"></span><span class="browser-dot y"></span><span class="browser-dot g"></span></div>'''
    if video_path:
        poster_attr = f' poster="{poster_path}"' if poster_path else ''
        return bar + f'\n  <video src="{video_path}"{poster_attr} muted playsinline preload="metadata" onclick="this.paused?this.play():this.pause()"></video>\n</div>\n<p class="play-hint">Click to play</p>'
    elif image_path:
        return bar + f'\n  <img src="{image_path}" alt="Mockup">\n</div>'
    else:
        return bar + f'\n  <div class="placeholder">{placeholder_text}</div>\n</div>'

def make_demo_link(url=None, text="View Demo"):
    """Generate demo link HTML."""
    if url:
        return f'<a href="{url}" target="_blank" class="demo-link">{text} &#8594;</a>'
    return ''

def generate(data_path, output_path):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(template_dir, 'template.html')
    slides_src = os.path.join(template_dir, 'slides')

    with open(template_path, 'r') as f:
        html = f.read()
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Copy static slides to output directory
    output_dir = os.path.dirname(os.path.abspath(output_path))
    slides_dst = os.path.join(output_dir, 'slides')
    if os.path.exists(slides_src):
        if os.path.exists(slides_dst):
            shutil.rmtree(slides_dst)
        shutil.copytree(slides_src, slides_dst)

    # Build "What You've Built" tiles
    def make_tile(text, icon="&#10003;"):
        if not text:
            return '<div></div>'
        return f'<div class="card" style="display:flex; gap:0.8rem; align-items:flex-start; padding:1rem;"><span style="color:var(--teal-bright); font-size:1.1rem; font-weight:700; flex-shrink:0;">{icon}</span><p style="font-size:0.82rem; color:var(--text-mid); line-height:1.5; margin:0;">{text}</p></div>'

    for i in range(1, 7):
        tile_text = data.get(f'built_tile_{i}', '')
        html = html.replace(f'{{{{BUILT_TILE_{i}}}}}', make_tile(tile_text))

    # Owner photo
    owner_photo = data.get('owner_photo', '')
    if owner_photo:
        photo_html = f'<img src="{owner_photo}" alt="{data.get("owner_name", "")}" style="width:100%; max-width:280px; border-radius:10px; margin-top:1.5rem; object-fit:cover; aspect-ratio:3/4;">'
    else:
        photo_html = '<div style="width:100%; max-width:280px; height:300px; border-radius:10px; margin-top:1.5rem; background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.15); display:flex; align-items:center; justify-content:center;"><p style="font-size:0.7rem; color:var(--text-faint); font-style:italic;">Owner photo</p></div>'
    html = html.replace('{{OWNER_PHOTO_HTML}}', photo_html)

    # Build image/link HTML for each task
    for prefix in ['task1', 'task2', 'task3', 'task4', 'task5', 'task6', 'bonus']:
        img = data.get(f'{prefix}_image', '')
        vid = data.get(f'{prefix}_video', '')
        poster = data.get(f'{prefix}_poster', '')
        link = data.get(f'{prefix}_link', '')
        link_text = data.get(f'{prefix}_link_text', 'View Demo')

        img_html = make_browser_frame(
            image_path=img if img else None,
            video_path=vid if vid else None,
            poster_path=poster if poster else None
        )
        link_html = make_demo_link(link, link_text) if link else ''

        html = html.replace(f'{{{{{prefix.upper()}_IMAGE_HTML}}}}', img_html)
        html = html.replace(f'{{{{{prefix.upper()}_LINK_HTML}}}}', link_html)

    # Simple replacements
    replacements = {
        '{{SLIDES_PATH}}': 'slides/',
        '{{TEAM_PHOTO}}': data.get('team_photo', 'kelly-alicia-headshot.jpg'),
        '{{CLINIC_NAME}}': data.get('clinic_name', 'CLINIC NAME'),
        '{{OWNER_NAME}}': data.get('owner_name', ''),
        '{{GOOGLE_RATING}}': data.get('google_rating', '-'),
        '{{GOOGLE_REVIEWS}}': data.get('google_reviews', '-'),
        '{{YEARS_EXPERIENCE}}': data.get('years_experience', '-'),
        '{{SOCIAL_FOLLOWERS}}': data.get('social_followers', '-'),
        '{{WHAT_BUILT_INTRO}}': data.get('what_built_intro', ''),
        '{{WEEKLY_PRICE}}': data.get('weekly_price', '$699'),
        '{{DISCOUNT_NAME}}': data.get('discount_name', ''),
        '{{DISCOUNT_PRICE}}': data.get('discount_price', ''),
        '{{DISCOUNT_EXPIRY}}': data.get('discount_expiry', ''),
        '{{GOALS_HTML}}': data.get('goals_html', ''),
        '{{STRATEGY_CALL_LINK}}': data.get('strategy_call_link', 'https://calendly.com/mintpeachmedia/new-client-onboarding'),
    }

    for i in range(1, 7):
        t = f'task{i}'
        replacements[f'{{{{{t.upper()}_HOOK}}}}'] = data.get(f'{t}_hook', '')
        replacements[f'{{{{{t.upper()}_TITLE}}}}'] = data.get(f'{t}_title', '')
        replacements[f'{{{{{t.upper()}_BODY}}}}'] = data.get(f'{t}_body', '')

    replacements['{{BONUS_HOOK}}'] = data.get('bonus_hook', '')
    replacements['{{BONUS_TITLE}}'] = data.get('bonus_title', '')
    replacements['{{BONUS_BODY}}'] = data.get('bonus_body', '')

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Check for unfilled placeholders
    remaining = re.findall(r'\{\{[A-Z_]+\}\}', html)
    if remaining:
        print(f"Warning: unfilled placeholders: {set(remaining)}")

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Deck generated: {output_path}")
    print(f"Static slides copied to: {slides_dst}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 generate.py <client-data.json> <output.html>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
