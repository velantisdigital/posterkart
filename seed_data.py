import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posterkart.settings')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from store.models import Category, PosterSize, FrameOption, Poster, PosterImage, Review
from cart.models import Coupon
from accounts.models import Address, UserProfile

from PIL import Image, ImageDraw, ImageFont
import io
import random


def generate_poster_artwork(title, category_name, bg_gradient_start, bg_gradient_end, accent_color, style_type="modern"):
    """Generate high-resolution aesthetic poster artwork using Pillow"""
    width, height = 800, 1100
    img = Image.new("RGB", (width, height), bg_gradient_start)
    draw = ImageDraw.Draw(img)

    # Draw vertical gradient background
    r1, g1, b1 = bg_gradient_start
    r2, g2, b2 = bg_gradient_end
    for y in range(height):
        factor = y / height
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add geometric/artistic patterns based on style
    if style_type == "anime":
        # Cyberpunk / Neon grid & sun
        draw.ellipse([200, 200, 600, 600], fill=accent_color)
        for i in range(12):
            y_line = 400 + i * 20
            draw.line([(150, y_line), (650, y_line)], fill=bg_gradient_start, width=4)
        # Perspective grid
        for i in range(15):
            y_grid = 650 + (i ** 1.6) * 15
            if y_grid < height - 120:
                draw.line([(40, int(y_grid)), (width - 40, int(y_grid))], fill=(255, 255, 255, 60), width=1)
    elif style_type == "movies":
        # Editorial Film Style
        draw.rectangle([80, 100, width - 80, height - 180], outline=accent_color, width=3)
        draw.ellipse([250, 250, 550, 550], outline=(255, 255, 255), width=2)
        draw.polygon([(400, 300), (520, 500), (280, 500)], fill=accent_color)
    elif style_type == "nature":
        # Sun and Mountain layers
        draw.ellipse([300, 180, 500, 380], fill=accent_color)
        # Mountains
        draw.polygon([(0, 650), (280, 380), (560, 650)], fill=(30, 45, 55))
        draw.polygon([(250, 680), (520, 320), (800, 680)], fill=(45, 65, 80))
        draw.polygon([(100, 780), (420, 450), (750, 780)], fill=(20, 30, 40))
    elif style_type == "cars":
        # Speed lines & Minimalist silhouette box
        for i in range(8):
            draw.line([(60 + i * 90, 200), (140 + i * 90, 700)], fill=accent_color, width=4)
        draw.rectangle([150, 350, 650, 550], fill=(15, 15, 15), outline=(255, 255, 255), width=3)
    elif style_type == "quotes":
        # Minimalist typographic focus
        draw.rectangle([60, 60, width - 60, height - 60], outline=(255, 255, 255, 100), width=1)
        draw.ellipse([350, 200, 450, 300], fill=accent_color)
    elif style_type == "gaming":
        # Neon glowing diamond and polygon
        draw.polygon([(400, 200), (600, 400), (400, 600), (200, 400)], outline=accent_color, width=6)
        draw.polygon([(400, 260), (540, 400), (400, 540), (260, 400)], fill=accent_color)
    else:  # Minimalist / Aesthetic
        # Abstract arches & circles
        draw.pieslice([150, 150, 650, 650], 180, 360, fill=accent_color)
        draw.ellipse([320, 420, 480, 580], fill=(245, 240, 230))
        draw.line([(100, 650), (700, 650)], fill=(255, 255, 255), width=2)

    # Frame border guideline
    draw.rectangle([30, 30, width - 30, height - 30], outline=(255, 255, 255, 50), width=1)

    # Text overlay
    # Header tag
    draw.text((60, 70), f"POSTERKART EXCLUSIVE • {category_name.upper()}", fill=(200, 200, 200))

    # Poster Title
    # Try using default font with clean sizing
    draw.text((60, height - 160), title.upper(), fill=(255, 255, 255))
    draw.text((60, height - 120), "ARCHIVAL MATTE FINISH • 300 GSM PREMIUM ART PAPER", fill=(170, 170, 170))
    draw.text((60, height - 90), "LIMITED EDITION WALL ARTWORK", fill=accent_color)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return ContentFile(buf.getvalue(), name=f"{title.lower().replace(' ', '_')}.jpg")


def seed_database():
    print("🎨 Seeding PosterKart Database...")

    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@posterkart.com', 'admin123')
        admin_user.first_name = "PosterKart"
        admin_user.last_name = "Admin"
        admin_user.save()
        admin_user.profile.phone_number = "9876543210"
        admin_user.profile.save()
        print("  ✓ Created superuser (admin / admin123)")
    else:
        admin_user = User.objects.get(username='admin')

    # Create demo customer
    if not User.objects.filter(username='rahul').exists():
        demo_user = User.objects.create_user('rahul', 'rahul@example.com', 'rahul123')
        demo_user.first_name = "Rahul"
        demo_user.last_name = "Sharma"
        demo_user.save()
        demo_user.profile.phone_number = "9876500000"
        demo_user.profile.save()
        
        # Sample address for demo user
        Address.objects.create(
            user=demo_user,
            full_name="Rahul Sharma",
            phone_number="9876500000",
            address_line_1="Flat 402, Sunshine Heights, MG Road",
            address_line_2="Indiranagar",
            city="Bengaluru",
            state="Karnataka",
            pin_code="560038",
            landmark="Near Metro Station",
            is_default=True
        )
        print("  ✓ Created demo customer (rahul / rahul123)")
    else:
        demo_user = User.objects.get(username='rahul')

    # 2. Poster Sizes
    sizes_data = [
        {'name': 'A4 (8.3 × 11.7 in)', 'code': 'A4', 'extra_price': Decimal('0.00'), 'dimensions': '21.0 × 29.7 cm', 'is_default': True, 'sort_order': 1},
        {'name': 'A3 (11.7 × 16.5 in)', 'code': 'A3', 'extra_price': Decimal('100.00'), 'dimensions': '29.7 × 42.0 cm', 'is_default': False, 'sort_order': 2},
        {'name': 'A2 (16.5 × 23.4 in)', 'code': 'A2', 'extra_price': Decimal('250.00'), 'dimensions': '42.0 × 59.4 cm', 'is_default': False, 'sort_order': 3},
    ]
    for s in sizes_data:
        PosterSize.objects.update_or_create(code=s['code'], defaults=s)
    print("  ✓ Created Poster Sizes (A4, A3, A2)")

    # 3. Frame Options
    frames_data = [
        {'name': 'No Frame (Rolled Canvas)', 'frame_type': 'none', 'extra_price': Decimal('0.00'), 'color_code': '#3F3F46', 'is_default': True, 'sort_order': 1},
        {'name': 'Matte Black Wood Frame', 'frame_type': 'black', 'extra_price': Decimal('200.00'), 'color_code': '#18181B', 'is_default': False, 'sort_order': 2},
        {'name': 'Modern White Gallery Frame', 'frame_type': 'white', 'extra_price': Decimal('200.00'), 'color_code': '#F4F4F5', 'is_default': False, 'sort_order': 3},
        {'name': 'Classic Natural Walnut Frame', 'frame_type': 'wooden', 'extra_price': Decimal('300.00'), 'color_code': '#8B5A2B', 'is_default': False, 'sort_order': 4},
    ]
    for f in frames_data:
        FrameOption.objects.update_or_create(frame_type=f['frame_type'], defaults=f)
    print("  ✓ Created Frame Options (No Frame, Black, White, Wooden)")

    # 4. Categories (10 distinct categories)
    categories_info = [
        ('Movies', 'bi-film', 'Iconic cinema posters, cult classics, and cinematic visual masterpieces.', (20, 24, 33), (10, 12, 18), (229, 9, 20), 'movies'),
        ('Anime', 'bi-stars', 'Stunning anime art, studio aesthetics, cyberpunk vibes and hero portraits.', (26, 16, 43), (12, 8, 24), (255, 75, 145), 'anime'),
        ('Cars & Bikes', 'bi-speedometer2', 'Supercars, vintage automotive classics, racing circuits, and motorbike art.', (20, 20, 20), (35, 35, 35), (255, 107, 0), 'cars'),
        ('Gaming', 'bi-controller', 'Retro arcade, futuristic RPGs, neon landscapes, and esports tributes.', (15, 23, 42), (8, 12, 22), (0, 225, 255), 'gaming'),
        ('Quotes', 'bi-chat-quote', 'Inspiring words, motivational mantras, and clean typography wall quotes.', (30, 30, 30), (15, 15, 15), (234, 179, 8), 'quotes'),
        ('Sports', 'bi-trophy', 'Legends of football, basketball, cricket, F1, and champion moments.', (18, 30, 49), (10, 16, 28), (59, 130, 246), 'sports'),
        ('Nature', 'bi-tree', 'Serene mountain peaks, lush rainforests, sunsets, and botanical wonders.', (22, 38, 28), (12, 22, 16), (34, 197, 94), 'nature'),
        ('Music', 'bi-music-note-beamed', 'Vintage vinyl vibes, legendary rock bands, jazz notes, and acoustic tones.', (36, 20, 30), (18, 10, 15), (244, 63, 94), 'music'),
        ('Minimalist', 'bi-square', 'Geometric harmony, negative space, modern line art, and Scandinavian forms.', (40, 40, 40), (20, 20, 20), (212, 212, 216), 'minimalist'),
        ('Aesthetic', 'bi-palette', 'Dreamy pastel hues, vaporwave palettes, retro-futurism, and mood boards.', (45, 28, 50), (22, 14, 25), (168, 85, 247), 'aesthetic'),
    ]

    cat_map = {}
    for name, icon, desc, c_start, c_end, c_acc, style in categories_info:
        cat, _ = Category.objects.get_or_create(
            name=name,
            defaults={'description': desc, 'icon': icon}
        )
        if not cat.image:
            art_file = generate_poster_artwork(name, name, c_start, c_end, c_acc, style)
            cat.image.save(f"cat_{cat.slug}.jpg", art_file, save=True)
        cat_map[name] = cat

    print("  ✓ Created 10 Poster Categories")

    # 5. Sample Posters (20+ rich posters)
    posters_data = [
        # Movies
        {
            'title': 'Interstellar Odyssey',
            'category': 'Movies',
            'base_price': Decimal('299.00'),
            'description': 'A breathtaking visual tribute to the cosmic journey across gargantua, black holes, and dimensions. Premium 300 GSM matte art paper with rich blacks and stellar contrast.',
            'stock': 45, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'movies, sci-fi, space, interstellar, christopher nolan, cosmos',
            'colors': ((10, 15, 30), (5, 8, 15), (255, 180, 0), 'movies')
        },
        {
            'title': 'The Dark Knight Minimalist',
            'category': 'Movies',
            'base_price': Decimal('329.00'),
            'description': 'Gotham skyline framed in the iconic bat silhouette. Moody, dramatic, and sleekly styled for modern living rooms and entertainment lounges.',
            'stock': 60, 'rating': Decimal('5.0'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'batman, dark knight, gotham, movies, cinema',
            'colors': ((15, 15, 18), (5, 5, 8), (220, 38, 38), 'movies')
        },
        # Anime
        {
            'title': 'Neon Tokyo Cyberpunk 2099',
            'category': 'Anime',
            'base_price': Decimal('349.00'),
            'description': 'Rain-slicked neon streets, futuristic kanji signs, and glowing cyber aesthetics. Vibrant pigment print that pops in any gaming or creative studio setup.',
            'stock': 80, 'rating': Decimal('4.8'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'anime, cyberpunk, tokyo, neon, japan, aesthetic',
            'colors': ((30, 10, 45), (10, 5, 20), (255, 0, 128), 'anime')
        },
        {
            'title': 'Spirited Sky Castle',
            'category': 'Anime',
            'base_price': Decimal('299.00'),
            'description': 'Dreamlike watercolor clouds and soaring retro airships reminiscent of classic studio anime masterpieces. Warm, nostalgic, and peaceful.',
            'stock': 35, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': False, 'is_bestseller': False,
            'tags': 'anime, ghibli, sky, clouds, fantasy, studio',
            'colors': ((25, 40, 65), (15, 20, 35), (255, 200, 100), 'anime')
        },
        # Cars & Bikes
        {
            'title': 'Porsche 911 Turbo Classic',
            'category': 'Cars & Bikes',
            'base_price': Decimal('399.00'),
            'description': 'Pure automotive perfection. The unmistakable silhouette of the timeless 911 Turbo captured in clean monochrome line art with racing yellow accents.',
            'stock': 50, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'cars, porsche, 911, turbo, automotive, supercar, german',
            'colors': ((20, 20, 22), (10, 10, 12), (250, 204, 21), 'cars')
        },
        {
            'title': 'Monaco Grand Prix Vintage 1976',
            'category': 'Cars & Bikes',
            'base_price': Decimal('319.00'),
            'description': 'Retro F1 motorsport racing poster depicting the legendary Monte Carlo street circuit and classic open-wheel racers.',
            'stock': 40, 'rating': Decimal('4.7'), 'is_featured': False, 'is_trending': True, 'is_bestseller': False,
            'tags': 'f1, monaco, racing, motorsport, vintage cars, speed',
            'colors': ((28, 20, 20), (12, 10, 10), (239, 68, 68), 'cars')
        },
        # Gaming
        {
            'title': 'Pixel Quest Arcade Realm',
            'category': 'Gaming',
            'base_price': Decimal('289.00'),
            'description': 'Nostalgic 16-bit retro arcade aesthetic mixed with modern synthwave glow. The ultimate accent piece for battlestations and gaming dens.',
            'stock': 75, 'rating': Decimal('4.8'), 'is_featured': True, 'is_trending': False, 'is_bestseller': False,
            'tags': 'gaming, arcade, retro, 8bit, synthwave, controller',
            'colors': ((18, 12, 38), (8, 5, 18), (6, 182, 212), 'gaming')
        },
        {
            'title': 'Elden Warrior In Solitude',
            'category': 'Gaming',
            'base_price': Decimal('359.00'),
            'description': 'Golden erdtree glow illuminating a lone tarnished knight atop a jagged cliff. Majestic fantasy composition with incredible depth.',
            'stock': 30, 'rating': Decimal('5.0'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'gaming, souls, fantasy, elden, knight, epic',
            'colors': ((25, 20, 10), (12, 10, 5), (245, 158, 11), 'gaming')
        },
        # Quotes
        {
            'title': 'Stay Hungry, Stay Foolish',
            'category': 'Quotes',
            'base_price': Decimal('279.00'),
            'description': 'Timeless bold typography designed with Swiss modernist layout principles. Inspires ambition, relentless curiosity and grit every morning.',
            'stock': 90, 'rating': Decimal('4.8'), 'is_featured': False, 'is_trending': True, 'is_bestseller': True,
            'tags': 'quotes, motivation, steve jobs, typography, office, inspiration',
            'colors': ((24, 24, 27), (9, 9, 11), (244, 63, 94), 'quotes')
        },
        {
            'title': 'Do Epic Shit Daily',
            'category': 'Quotes',
            'base_price': Decimal('269.00'),
            'description': 'Energetic, modern minimal typography printed with high-density pigment ink on premium heavyweight paper. Perfect desk companion.',
            'stock': 65, 'rating': Decimal('4.7'), 'is_featured': False, 'is_trending': False, 'is_bestseller': False,
            'tags': 'quotes, typography, daily, hustle, motivation',
            'colors': ((30, 28, 24), (15, 14, 12), (234, 179, 8), 'quotes')
        },
        # Sports
        {
            'title': 'Mamba Mentality 24',
            'category': 'Sports',
            'base_price': Decimal('349.00'),
            'description': 'A tribute to relentless dedication and championship excellence. Bold silhouette in signature purple and gold tones.',
            'stock': 55, 'rating': Decimal('5.0'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'sports, basketball, kobe, mamba, lakers, champion',
            'colors': ((35, 15, 45), (15, 5, 20), (234, 179, 8), 'sports')
        },
        {
            'title': 'The Greatest GOAT 10',
            'category': 'Sports',
            'base_price': Decimal('349.00'),
            'description': 'Celebration of football magic and world cup glory. Clean editorial design featuring iconic jersey number 10.',
            'stock': 70, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': True, 'is_bestseller': False,
            'tags': 'football, soccer, messi, goat, world cup, sports',
            'colors': ((15, 30, 48), (8, 15, 24), (56, 189, 248), 'sports')
        },
        # Nature
        {
            'title': 'Misty Alpine Sunrise',
            'category': 'Nature',
            'base_price': Decimal('299.00'),
            'description': 'Layers of evergreen pine forests emerging through morning mist beneath snowcapped alpine peaks. Calming, restorative atmosphere for bedrooms.',
            'stock': 40, 'rating': Decimal('4.8'), 'is_featured': False, 'is_trending': False, 'is_bestseller': False,
            'tags': 'nature, mountains, sunrise, forest, landscape, peace',
            'colors': ((20, 35, 30), (10, 18, 15), (251, 146, 60), 'nature')
        },
        {
            'title': 'Golden Hour Pacific Wave',
            'category': 'Nature',
            'base_price': Decimal('319.00'),
            'description': 'Powerful ocean wave curling against the setting sun. Brings natural ocean energy and soothing warmth to any interior.',
            'stock': 45, 'rating': Decimal('4.7'), 'is_featured': False, 'is_trending': True, 'is_bestseller': False,
            'tags': 'ocean, wave, surf, sunset, sea, nature',
            'colors': ((18, 32, 45), (8, 16, 25), (245, 158, 11), 'nature')
        },
        # Music
        {
            'title': 'Abbey Road Crosswalk',
            'category': 'Music',
            'base_price': Decimal('329.00'),
            'description': 'Iconic musical heritage reimagined in a clean Bauhaus geometry style. A must-have for classic rock lovers and vinyl enthusiasts.',
            'stock': 50, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': False, 'is_bestseller': False,
            'tags': 'music, beatles, rock, vinyl, retro, london',
            'colors': ((28, 22, 28), (14, 10, 14), (244, 63, 94), 'music')
        },
        {
            'title': 'Midnight Jazz Club NYC',
            'category': 'Music',
            'base_price': Decimal('299.00'),
            'description': 'Saxophone melodies swirling in moody midnight blue and warm brass tones. Evokes vintage Greenwich Village speakeasies.',
            'stock': 35, 'rating': Decimal('4.8'), 'is_featured': False, 'is_trending': False, 'is_bestseller': False,
            'tags': 'jazz, music, saxophone, new york, vintage',
            'colors': ((15, 20, 35), (8, 10, 18), (217, 119, 6), 'music')
        },
        # Minimalist
        {
            'title': 'Bauhaus Geometric Balance',
            'category': 'Minimalist',
            'base_price': Decimal('349.00'),
            'description': 'Pure form, primary balance, and architectural geometry. Printed on archival cotton-blend paper for high visual prestige.',
            'stock': 60, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': True, 'is_bestseller': True,
            'tags': 'minimalist, bauhaus, geometry, scandinavian, modern, abstract',
            'colors': ((30, 30, 32), (18, 18, 20), (225, 29, 72), 'minimalist')
        },
        {
            'title': 'Zen Circle Enso Flow',
            'category': 'Minimalist',
            'base_price': Decimal('289.00'),
            'description': 'Single-stroke sumi ink enso circle symbolizing presence, focus, and quiet strength. Brings mindful calm to workspaces.',
            'stock': 40, 'rating': Decimal('4.7'), 'is_featured': False, 'is_trending': False, 'is_bestseller': False,
            'tags': 'zen, enso, circle, japanese, minimalist, focus',
            'colors': ((25, 25, 28), (12, 12, 15), (200, 200, 200), 'minimalist')
        },
        # Aesthetic
        {
            'title': 'Pastel Dunes Oasis',
            'category': 'Aesthetic',
            'base_price': Decimal('329.00'),
            'description': 'Soft terracotta, blush pink, and sage green architectural arches framing desert dunes. On-trend modern boho aesthetic.',
            'stock': 55, 'rating': Decimal('4.9'), 'is_featured': True, 'is_trending': True, 'is_bestseller': False,
            'tags': 'aesthetic, pastel, boho, dunes, terracotta, modern art',
            'colors': ((45, 30, 38), (22, 15, 18), (244, 114, 182), 'aesthetic')
        },
        {
            'title': 'Vaporwave Sunset Horizon',
            'category': 'Aesthetic',
            'base_price': Decimal('299.00'),
            'description': '80s retro-futurism with purple chrome sun, palm silhouettes, and wireframe grids. Vibrant and atmospheric.',
            'stock': 48, 'rating': Decimal('4.8'), 'is_featured': False, 'is_trending': True, 'is_bestseller': False,
            'tags': 'vaporwave, aesthetic, 80s, synth, neon, sunset',
            'colors': ((35, 15, 45), (15, 8, 25), (192, 132, 252), 'aesthetic')
        },
    ]

    for p in posters_data:
        cat = cat_map[p['category']]
        poster, created = Poster.objects.get_or_create(
            title=p['title'],
            defaults={
                'category': cat,
                'base_price': p['base_price'],
                'description': p['description'],
                'stock': p['stock'],
                'rating': p['rating'],
                'is_featured': p['is_featured'],
                'is_trending': p['is_trending'],
                'is_bestseller': p['is_bestseller'],
                'tags': p['tags'],
            }
        )
        if not poster.main_image:
            art_file = generate_poster_artwork(
                p['title'], p['category'],
                p['colors'][0], p['colors'][1], p['colors'][2],
                p['colors'][3]
            )
            poster.main_image.save(f"poster_{poster.slug}.jpg", art_file, save=True)

        # Add sample reviews
        if created and demo_user:
            Review.objects.get_or_create(
                poster=poster,
                user=demo_user,
                defaults={
                    'rating': random.choice([5, 5, 4]),
                    'review_text': f"Absolutely in love with this '{poster.title}' poster! The matte paper quality and depth of colors exceeded my expectations. Arrived in sturdy packaging with zero creases.",
                    'is_verified_purchase': True
                }
            )

    print(f"  ✓ Created {len(posters_data)} Sample Posters with High-Res Artworks and Reviews")

    # 6. Coupons
    coupons_data = [
        {'code': 'POSTER10', 'discount_type': 'PERCENT', 'discount_value': Decimal('10.00'), 'min_order_amount': Decimal('0.00'), 'max_discount_amount': Decimal('300.00'), 'active': True},
        {'code': 'SAVE100', 'discount_type': 'FIXED', 'discount_value': Decimal('100.00'), 'min_order_amount': Decimal('499.00'), 'max_discount_amount': None, 'active': True},
        {'code': 'WELCOME50', 'discount_type': 'FIXED', 'discount_value': Decimal('50.00'), 'min_order_amount': Decimal('299.00'), 'max_discount_amount': None, 'active': True},
        {'code': 'FESTIVE20', 'discount_type': 'PERCENT', 'discount_value': Decimal('20.00'), 'min_order_amount': Decimal('799.00'), 'max_discount_amount': Decimal('500.00'), 'active': True},
    ]
    for c in coupons_data:
        Coupon.objects.update_or_create(code=c['code'], defaults=c)
    print("  ✓ Created Coupons (POSTER10, SAVE100, WELCOME50, FESTIVE20)")

    print("\n🎉 PosterKart Database Seeding Complete!")
    print("Superuser: admin / admin123")
    print("Demo Customer: rahul / rahul123")


if __name__ == '__main__':
    seed_database()
