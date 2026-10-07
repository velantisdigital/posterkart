import os
import re
import shutil
from decimal import Decimal
from PIL import Image

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify

from store.models import Category, Poster


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# Curated high-precision metadata for recognized designs in the project
CURATED_POSTER_METADATA = {
    "'game zone poster' poster, picture, metal print, paint by stonebridgeart _ displate.jpg": {
        "title": "Game Zone Neon Gaming Poster",
        "category": "Gaming",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "gaming, neon, game zone, arcade, gamer, controller, wall art, room decor",
        "description": "Vibrant neon Game Zone art poster designed for gaming setups, streamer rooms, and entertainment lounges. Printed on museum-grade 300 GSM archival matte art paper."
    },
    "45387908741001767.jpg": {
        "title": "Dodge Challenger SRT Hellcat Poster",
        "category": "Cars & Bikes",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "cars, dodge, srt, hellcat, muscle car, yellow, automotive, speed, supercar",
        "description": "Bold and sleek Dodge Challenger SRT Hellcat illustration against a vivid yellow backdrop. High-contrast automotive artwork engineered for car enthusiasts and studio garages."
    },
    "anbe sivam⚛️ #anbesivam #anbesivammovie….jpg": {
        "title": "Anbe Sivam Classic Cinema Poster",
        "category": "Movies",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("5.0"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "movies, anbe sivam, kamal haasan, madhavan, cult classic, kollywood, cinema, classic film",
        "description": "Tribute artwork celebrating the timeless cult classic Anbe Sivam. Rich storytelling art piece on heavyweight 300 GSM matte paper for cinema lovers."
    },
    "anirudh ravichander.jpg": {
        "title": "Anirudh Ravichander Musical Maestro Poster",
        "category": "Music",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "music, anirudh ravichander, composer, rockstar, concert, artist, live tour",
        "description": "High-energy concert and portrait art poster celebrating musical powerhouse Anirudh Ravichander. Perfect for music studios, bedroom walls, and audiophile corners."
    },
    "classic 1969 mustang – timeless american muscle car.jpg": {
        "title": "Classic 1969 Mustang Muscle Car Poster",
        "category": "Cars & Bikes",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": True,
        "is_trending": False,
        "is_bestseller": True,
        "tags": "cars, mustang, ford mustang, 1969, american muscle, vintage cars, automotive, classic",
        "description": "The timeless 1969 Ford Mustang captured in classic automotive aesthetic. Museum-grade fine art giclée print with archival fade-resistant pigment inks."
    },
    "hiphop tamizha poster.jpg": {
        "title": "HipHop Tamizha Musical Icon Poster",
        "category": "Music",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "music, hiphop tamizha, adhi, indie music, hip hop, artist, concert, independent music",
        "description": "Iconic portrait artwork of HipHop Tamizha Adhi. Dynamic urban styling printed with sharp detail on 300 GSM heavyweight art paper."
    },
    "mankatha 4k wallpaper.jpg": {
        "title": "Mankatha Action Cinema Poster",
        "category": "Movies",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "movies, mankatha, ajith kumar, thala, kollywood, action, heist, cinema tribute",
        "description": "Stylish high-octane Mankatha cinema tribute poster featuring Ajith Kumar. Crisp detail and dramatic tone for Indian cinema collections."
    },
    "orange cat playing valorant.jpg": {
        "title": "Orange Cat Playing Valorant Poster",
        "category": "Gaming",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "gaming, cat, orange cat, valorant, funny, cute, esports, pc gaming, cozy",
        "description": "Whimsical and endearing art print of an orange tabby cat immersed in a Valorant match. High-definition vibrant art print for cozy desk and gaming setups."
    },
    "royal enfield gt-650.jpg": {
        "title": "Royal Enfield Continental GT 650 Poster",
        "category": "Cars & Bikes",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "bikes, royal enfield, continental gt 650, cafe racer, motorcycle, automotive, twin cylinder",
        "description": "Handcrafted cafe racer aesthetic featuring the Royal Enfield Continental GT 650. Premium matte finish highlighting chrome detailing and twin-cylinder heritage."
    },
    "this is a vintage-style decorative poster featuring a towering, snow-capped mountain peak _.jpg": {
        "title": "Vintage Alpine Mountain Peak Poster",
        "category": "Nature",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": True,
        "is_trending": False,
        "is_bestseller": False,
        "tags": "nature, mountain, alpine, peak, snow, vintage travel, landscape, scandinavian, travel poster",
        "description": "Nostalgic vintage travel artwork portraying majestic snow-covered alpine mountain peaks. Serene earthy tones ideal for minimalist and nature-inspired spaces."
    },
    "_ the legend, m s dhoni 🔥✨!!  •follow for more….jpg": {
        "title": "MS Dhoni The Legend Cricket Poster",
        "category": "Sports",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("5.0"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "sports, ms dhoni, cricket, captain cool, csk, india, legends, thala, world cup",
        "description": "Commemorative fine art tribute to India's legendary captain MS Dhoni. Captures unforgettable championship glory on museum-quality 300 GSM matte art paper."
    },
    "_make abstract poster art featuring oversized ochre suns and.jpg": {
        "title": "Ochre Sun Abstract Geometric Poster",
        "category": "Minimalist",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.7"),
        "is_featured": False,
        "is_trending": False,
        "is_bestseller": False,
        "tags": "minimalist, abstract, ochre sun, geometric, modern art, scandinavian, aesthetic, boho",
        "description": "Modern Scandinavian abstract art print featuring an oversized ochre sun and organic forms. Warm minimalist palette designed for contemporary living rooms."
    },
    "_with great power comes a new era_ 🕷️_the spider….jpg": {
        "title": "Spider-Man With Great Power Poster",
        "category": "Movies",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "movies, spiderman, marvel, with great power, superhero, comics, cinema, peter parker",
        "description": "Iconic Spider-Man cinematic art poster portraying the legendary superhero mantle. Deep rich blacks and vivid suit textures on 300 GSM archival stock."
    },
    "all is well when you're  happy 😊.jpg": {
        "title": "All Is Well When You're Happy Quote Poster",
        "category": "Quotes",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": False,
        "is_bestseller": False,
        "tags": "quotes, motivational, happiness, typography, positive vibes, wall quote, mindfulness",
        "description": "Uplifting typography quote poster spreading positive mindfulness and cheer. Clean layout suitable for bedrooms, offices, and creative workstations."
    },
    "anime one piece.jpg": {
        "title": "One Piece Anime Art Poster",
        "category": "Anime",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("5.0"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "anime, one piece, luffy, straw hat, shonen, manga, anime art, grand line",
        "description": "Epic One Piece anime art poster celebrating the grand adventure across the seas. Vivid colors and crisp lines printed on premium matte art paper."
    },
    "don't let idiots ruin your day, vintage typography poster stock illustration.jpg": {
        "title": "Don't Let Idiots Ruin Your Day Quote Poster",
        "category": "Quotes",
        "base_price": Decimal("299.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "quotes, humor, typography, vintage, funny quotes, motivational, office decor",
        "description": "Witty vintage-style typography art reminding you to protect your peace. Printed with distressed retro lettering on museum-grade heavyweight matte paper."
    },
    "images (1).png": {
        "title": "Coastal Sunset Beach Paradise Poster",
        "category": "Nature",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "nature, coastal, beach, ocean, sunset, cliff, sea, scenic landscape, paradise",
        "description": "Breathtaking golden-hour panoramic view of an untouched coastal cove and turquoise ocean waters. Vivid natural lighting that brings warmth to any room."
    },
    "images.png": {
        "title": "Bauhaus Exhibition 1923 Geometric Poster",
        "category": "Minimalist",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": False,
        "is_bestseller": True,
        "tags": "minimalist, bauhaus, 1923, exhibition, geometric, vintage design, modern art, typography",
        "description": "Authentic reissue artwork of the historic 1923 Bauhaus Weimar Exhibition. Iconic primary colors and isometric cube geometry for design aficionados."
    },
    "ok kanmani poster.jpg": {
        "title": "OK Kanmani Romantic Cinema Poster",
        "category": "Movies",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "movies, ok kanmani, mani ratnam, dulquer salmaan, nithya menen, romance, cinema, kollywood",
        "description": "Warm and intimate movie poster artwork commemorating Mani Ratnam's modern romance classic OK Kanmani. Rich cinematic visuals on 300 GSM paper."
    },
    "pexels-photo-34115440.png": {
        "title": "Desert Oasis Sand Dunes Art Poster",
        "category": "Nature",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.8"),
        "is_featured": False,
        "is_trending": False,
        "is_bestseller": False,
        "tags": "nature, desert dunes, oasis, sand, minimalist nature, aerial photography, landscape",
        "description": "Sculptural white sand dunes curving gracefully around a pristine freshwater lagoon. Harmonious blend of earth tones and crystal clear waters."
    },
    "ronaldooo.jpg": {
        "title": "Cristiano Ronaldo CR7 Football Legend Poster",
        "category": "Sports",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("5.0"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "sports, ronaldo, cr7, football, soccer, real madrid, portugal, goat, stadium",
        "description": "Dynamic athletic tribute to football icon Cristiano Ronaldo. Powerful stance and stadium lighting captured on archival gallery paper."
    },
    "vadachennai.jpg": {
        "title": "Vada Chennai Cult Cinema Poster",
        "category": "Movies",
        "base_price": Decimal("329.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": False,
        "tags": "movies, vada chennai, dhanush, vetrimaaran, cult cinema, gangster, kollywood, cinema",
        "description": "Raw, gritty, and atmospheric artwork inspired by Vetrimaaran's acclaimed crime epic Vada Chennai. Premium contrast and detailing for film buffs."
    },
    "vaporwave-sunset-synth-city-horizon-v0-pce596hztst71.png": {
        "title": "Vaporwave Synth City Horizon Poster",
        "category": "Aesthetic",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("4.9"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "aesthetic, vaporwave, synthwave, retro 80s, neon sunset, cyber city, lo-fi, cyberpunk",
        "description": "Nostalgic 80s synthwave dreamscape with glowing neon skyline, grid horizon, and giant magenta setting sun. Ideal for retro-futuristic decor."
    },
    "𓂃 ࣪˖ ִֶ ★ ainaarlaith.jpg": {
        "title": "Itachi Uchiha Anime Art Poster",
        "category": "Anime",
        "base_price": Decimal("349.00"),
        "stock": 20,
        "rating": Decimal("5.0"),
        "is_featured": True,
        "is_trending": True,
        "is_bestseller": True,
        "tags": "anime, naruto, itachi uchiha, sharingan, akatsuki, tokyo, manga art, japanese anime",
        "description": "Striking dark aesthetic artwork of Itachi Uchiha with glowing Sharingan and bold typography. Printed on heavyweight 300 GSM archival matte paper."
    }
}

DEFAULT_CATEGORY_ICONS = {
    'Movies': 'bi-film',
    'Anime': 'bi-stars',
    'Cars & Bikes': 'bi-speedometer2',
    'Gaming': 'bi-controller',
    'Quotes': 'bi-chat-quote',
    'Sports': 'bi-trophy',
    'Nature': 'bi-tree',
    'Music': 'bi-music-note-beamed',
    'Minimalist': 'bi-square',
    'Aesthetic': 'bi-palette',
}


def clean_filename_to_title(filename):
    """Automatically convert an arbitrary filename to a clean human-readable title."""
    name, _ = os.path.splitext(filename)
    # Remove hashtags and trailing characters
    name = re.sub(r'#\w+', '', name)
    # Remove emojis and non-ascii decorative symbols
    name = re.sub(r'[^\w\s\-\'\".,]', ' ', name)
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Remove excessive numbers
    name = re.sub(r'\b\d{6,}\b', '', name)
    # Remove common filler phrases
    name = re.sub(r'\b(displate|metal print|stock illustration|wallpaper|4k)\b', '', name, flags=re.IGNORECASE)
    # Clean whitespace
    name = ' '.join(name.split())
    if len(name) < 3:
        return "Premium Wall Art Poster"
    # Title case words
    return name.title()


def detect_category_from_text(text):
    """Determine best category matching filename or keywords."""
    t = text.lower()
    if any(k in t for k in ['anime', 'manga', 'naruto', 'one piece', 'itachi', 'ghibli', 'luffy']):
        return 'Anime'
    if any(k in t for k in ['car', 'bike', 'mustang', 'dodge', 'enfield', 'gt-650', 'gt 650', 'racing', 'porsche', 'f1']):
        return 'Cars & Bikes'
    if any(k in t for k in ['game', 'gaming', 'valorant', 'arcade', 'controller', 'quest']):
        return 'Gaming'
    if any(k in t for k in ['quote', 'happy', 'idiots', 'typography', 'inspire', 'text']):
        return 'Quotes'
    if any(k in t for k in ['sport', 'dhoni', 'ronaldo', 'cricket', 'football', 'soccer', 'trophy']):
        return 'Sports'
    if any(k in t for k in ['nature', 'mountain', 'peak', 'beach', 'sunset', 'oasis', 'dunes', 'tree', 'landscape']):
        return 'Nature'
    if any(k in t for k in ['music', 'anirudh', 'hiphop', 'song', 'jazz', 'vinyl', 'band']):
        return 'Music'
    if any(k in t for k in ['bauhaus', 'minimal', 'ochre sun', 'geometric', 'scandinavian']):
        return 'Minimalist'
    if any(k in t for k in ['vaporwave', 'synth', 'aesthetic', 'neon', 'cyber', 'retro']):
        return 'Aesthetic'
    if any(k in t for k in ['movie', 'cinema', 'sivam', 'mankatha', 'vadachennai', 'spider', 'kanmani', 'batman', 'interstellar']):
        return 'Movies'
    return 'Minimalist'


class Command(BaseCommand):
    help = "Scan design folder (desingtemp / designtemp), import poster designs to media/posters, and create products in database."

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            default='',
            help='Explicit source folder path. If not provided, will scan desingtemp/ and designtemp/.'
        )
        parser.add_argument(
            '--keep-samples-active',
            action='store_true',
            help='Do not prioritize imported posters over demo samples.'
        )

    def handle(self, *args, **options):
        # 1. Locate source folder
        base_dir = settings.BASE_DIR
        candidate_dirs = []
        if options['source_dir']:
            candidate_dirs.append(options['source_dir'])
        else:
            candidate_dirs.extend([
                os.path.join(base_dir, 'desingtemp'),
                os.path.join(base_dir, 'designtemp'),
            ])

        source_dir = None
        for cd in candidate_dirs:
            if os.path.isdir(cd):
                source_dir = cd
                break

        if not source_dir:
            self.stderr.write(self.style.ERROR(
                f"Source directory not found. Checked: {', '.join(candidate_dirs)}"
            ))
            return

        self.stdout.write(self.style.NOTICE(f"Scanning poster designs from: {source_dir}"))

        # 2. Prepare media destination directory: media/posters/
        posters_media_dir = os.path.join(settings.MEDIA_ROOT, 'posters')
        os.makedirs(posters_media_dir, exist_ok=True)

        # 3. Scan for supported image files
        all_entries = os.listdir(source_dir)
        found_images = []
        unsupported_files = []

        for entry in all_entries:
            full_path = os.path.join(source_dir, entry)
            if not os.path.isfile(full_path):
                continue
            ext = os.path.splitext(entry)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                found_images.append(entry)
            else:
                unsupported_files.append(entry)

        found_count = len(found_images)
        imported_count = 0
        created_count = 0
        skipped_count = 0
        errors_count = 0

        # 4. Process each image
        for filename in sorted(found_images):
            src_file_path = os.path.join(source_dir, filename)
            ext = os.path.splitext(filename)[1].lower()

            try:
                # Validate image integrity with PIL without altering original
                with Image.open(src_file_path) as img:
                    img.verify()

                # Determine metadata: check curated lookup first, else fallback algorithm
                key = filename.strip().lower()
                meta = CURATED_POSTER_METADATA.get(key)
                if not meta:
                    # Clean title
                    title = clean_filename_to_title(filename)
                    cat_name = detect_category_from_text(f"{filename} {title}")
                    meta = {
                        "title": title,
                        "category": cat_name,
                        "base_price": Decimal("299.00"),
                        "stock": 20,
                        "rating": Decimal("4.8"),
                        "is_featured": False,
                        "is_trending": False,
                        "is_bestseller": False,
                        "tags": f"{cat_name.lower()}, wall art, poster, premium print",
                        "description": f"Archival quality {title} printed on museum-grade 300 GSM matte art paper with fade-resistant pigment inks."
                    }

                title = meta["title"]
                cat_name = meta["category"]
                base_price = meta.get("base_price", Decimal("299.00"))
                stock = meta.get("stock", 20)
                rating = meta.get("rating", Decimal("4.8"))
                is_featured = meta.get("is_featured", False)
                is_trending = meta.get("is_trending", False)
                is_bestseller = meta.get("is_bestseller", False)
                tags = meta.get("tags", "")
                description = meta.get("description", "")

                # Duplicate protection check: by source_filename or slug
                clean_slug_base = slugify(title)
                existing_poster = Poster.objects.filter(source_filename=filename).first()
                if not existing_poster:
                    existing_poster = Poster.objects.filter(slug=clean_slug_base).first()

                if existing_poster:
                    # Poster already exists: ensure fields are updated without duplication
                    existing_poster.source_filename = filename
                    existing_poster.stock = stock
                    existing_poster.save()
                    skipped_count += 1
                    safe_title = title.encode('ascii', 'replace').decode('ascii')
                    self.stdout.write(f"  - Skipped duplicate: {safe_title} (ID #{existing_poster.id})")
                    continue

                # Prepare destination file in media/posters/
                # Generate safe destination filename
                safe_stem = slugify(title)
                dst_filename = f"{safe_stem}{ext}"
                dst_full_path = os.path.join(posters_media_dir, dst_filename)

                # Avoid file collision
                counter = 1
                while os.path.exists(dst_full_path):
                    dst_filename = f"{safe_stem}-{counter}{ext}"
                    dst_full_path = os.path.join(posters_media_dir, dst_filename)
                    counter += 1

                # Copy original file to media without altering/modifying the original
                shutil.copy2(src_file_path, dst_full_path)
                imported_count += 1

                # Ensure Category exists
                cat, _ = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={
                        'description': f"Curated collection of {cat_name} posters and art prints.",
                        'icon': DEFAULT_CATEGORY_ICONS.get(cat_name, 'bi-tags')
                    }
                )

                # Create Poster record
                poster = Poster(
                    title=title,
                    slug=clean_slug_base,
                    description=description,
                    category=cat,
                    main_image=f"posters/{dst_filename}",
                    base_price=base_price,
                    stock=stock,
                    rating=rating,
                    is_featured=is_featured,
                    is_trending=is_trending,
                    is_bestseller=is_bestseller,
                    tags=tags,
                    source_filename=filename
                )
                poster.save()
                created_count += 1
                safe_title = title.encode('ascii', 'replace').decode('ascii')
                self.stdout.write(self.style.SUCCESS(f"  + Created: '{safe_title}' in [{cat.name}] (Rs. {base_price})"))

            except Exception as e:
                errors_count += 1
                safe_fn = filename.encode('ascii', 'replace').decode('ascii')
                self.stderr.write(self.style.ERROR(f"  ! Error processing '{safe_fn}': {e}"))

        # 5. Sample products prioritization
        if not options.get('keep_samples_active') and created_count + skipped_count > 0:
            # Set sample demo posters (which have no source_filename) to unfeatured/untrending
            # so that user's actual designs occupy Trending, Featured, and Hero spotlights
            Poster.objects.filter(source_filename='').update(
                is_featured=False,
                is_trending=False,
                is_bestseller=False
            )
            self.stdout.write(self.style.SUCCESS("  [OK] Prioritized real poster designs on Homepage & spotlights"))

        # 6. Print summary
        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(f"Found: {found_count} images")
        self.stdout.write(f"Imported: {imported_count}")
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Skipped duplicates: {skipped_count}")
        self.stdout.write(f"Errors: {errors_count}")
        if unsupported_files:
            self.stdout.write(f"Unsupported files ({len(unsupported_files)}): {', '.join(unsupported_files)}")
        else:
            self.stdout.write("Unsupported files: 0")
        self.stdout.write("=" * 40 + "\n")
