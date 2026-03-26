"""
Generate a 500-product catalog for ShopMuse.
Run from project root: python scripts/generate_catalog.py
"""

import json
import random
import hashlib

random.seed(42)  # Reproducible

# ── Product templates per category ──

CATEGORIES = {
    "t-shirt": {
        "prefix": "TS",
        "templates": [
            ("Classic {color} Crew Neck T-Shirt", "{material} crew neck tee. Soft, breathable, and perfect for {use_case} wear.", ["crew neck", "classic"]),
            ("{color} Performance Dry-Fit T-Shirt", "Moisture-wicking {material} tee designed for intense workouts. Lightweight with mesh ventilation.", ["performance", "dry-fit", "workout"]),
            ("{color} V-Neck T-Shirt {fit}", "{fit} V-neck tee in {color}. Made from a {material} blend for extra softness.", ["v-neck", "soft"]),
            ("Graphic Print {theme} T-Shirt", "{material} tee featuring a minimalist {theme} graphic. Great for {use_case}.", ["graphic", "print"]),
            ("Oversized {color} Wash T-Shirt", "Relaxed oversized fit with a faded vintage wash effect in {color}. Drop shoulders for streetwear look.", ["oversized", "vintage", "streetwear"]),
            ("{color} Polo T-Shirt {fit}", "Classic polo with ribbed collar and two-button placket in {color}. Perfect for smart casual.", ["polo", "collar", "smart casual"]),
            ("{color} Long Sleeve Thermal", "Waffle-knit thermal long sleeve in {color}. Ideal for layering in cooler weather.", ["long sleeve", "thermal", "layering"]),
            ("Cropped {color} Ribbed Tee", "Fitted cropped tee with ribbed texture in {color}. Pairs perfectly with high-waisted bottoms.", ["cropped", "ribbed", "fitted"]),
            ("{color} Compression Training Tee", "Second-skin compression tee in {color} for high-intensity training. UV protection and antimicrobial.", ["compression", "training", "UV protection"]),
            ("{color} Linen Blend Summer Tee", "Lightweight {material} blend tee in {color}. Naturally breathable for hot summer days.", ["linen", "summer", "breathable"]),
            ("Tie-Dye {color} Festival Tee", "Hand-dyed spiral tie-dye tee in {color} tones. Loose fit for maximum comfort.", ["tie-dye", "festival", "hand-dyed"]),
            ("{color} Henley Button Tee", "Three-button henley tee in {color} with a relaxed fit. A step up from a basic tee.", ["henley", "button", "relaxed"]),
            ("Eco-Friendly {color} Bamboo Tee", "Sustainably made from bamboo fiber in {color}. Hypoallergenic, soft, and eco-conscious.", ["bamboo", "eco-friendly", "sustainable"]),
        ],
        "price_range": (18.99, 54.99),
        "materials": ["100% cotton", "cotton-polyester blend", "organic cotton", "bamboo fiber", "cotton-modal blend", "recycled polyester", "merino wool blend", "linen-cotton blend"],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
    },
    "shoes": {
        "prefix": "SH",
        "templates": [
            ("Classic {color} Leather Sneakers", "Clean minimalist {color} leather sneakers with cushioned insole. Versatile for any outfit.", ["leather", "sneakers", "minimalist"]),
            ("{color} Running Performance Shoes", "Lightweight running shoes in {color} with responsive foam cushioning and breathable mesh upper.", ["running", "performance", "cushioned"]),
            ("{color} Chelsea Boots", "Classic Chelsea boots in {color} {material} with elastic side panels and pull tab.", ["chelsea", "boots", "elegant"]),
            ("{color} High-Top Canvas Sneakers", "Retro high-top canvas sneakers in {color} with vulcanized rubber sole. A streetwear staple.", ["high-top", "canvas", "retro"]),
            ("{color} Trail Hiking Boots", "Waterproof hiking boots in {color} with Vibram outsole and ankle support. Built for rugged terrain.", ["hiking", "waterproof", "trail"]),
            ("{color} Slip-On Loafers", "Italian-style {material} loafers in {color} with hand-stitched moccasin toe.", ["loafers", "slip-on", "italian"]),
            ("{color} Platform Sneakers", "Trendy platform sneakers in {color} with chunky sole for a bold statement.", ["platform", "chunky", "trendy"]),
            ("{color} Sandals Cork Footbed", "Comfortable sandals in {color} with molded cork footbed and adjustable straps.", ["sandals", "cork", "comfortable"]),
            ("{color} Oxford Dress Shoes", "Polished {material} Oxford shoes in {color} with Goodyear welt construction.", ["oxford", "dress", "polished"]),
            ("{color} Knit Slip-On Runners", "Ultra-light knit slip-on shoes in {color}. Seamless comfort with no-lace design.", ["knit", "slip-on", "ultra-light"]),
            ("{color} Desert Boots Suede", "Classic crepe-sole desert boots in {color} suede. Heritage silhouette for smart casual.", ["desert boots", "suede", "heritage"]),
            ("{color} Basketball Shoes", "Professional-grade basketball shoes in {color} with zoom air cushioning and herringbone traction.", ["basketball", "high-performance", "ankle support"]),
        ],
        "price_range": (39.99, 219.99),
        "materials": ["full-grain leather", "suede", "canvas", "mesh", "synthetic leather", "knit fabric", "nubuck", "patent leather"],
        "sizes": ["US 6", "US 7", "US 8", "US 9", "US 10", "US 11", "US 12", "US 13"],
    },
    "bag": {
        "prefix": "BG",
        "templates": [
            ("{color} Canvas Tote Bag", "Large canvas tote in {color} with reinforced handles and interior pocket. Perfect for daily errands.", ["canvas", "tote", "practical"]),
            ("{color} Leather Messenger Bag", "Full-grain {material} messenger bag in {color} with adjustable strap. Fits 15-inch laptop.", ["leather", "messenger", "laptop"]),
            ("{color} Minimalist Backpack", "Sleek minimalist backpack in {color} with padded laptop compartment and water-resistant fabric.", ["backpack", "minimalist", "water-resistant"]),
            ("{color} Hiking Daypack 30L", "Durable 30L hiking daypack in {color} with hydration sleeve and rain cover.", ["hiking", "daypack", "durable"]),
            ("{color} Crossbody Sling Bag", "Compact crossbody sling in {color} with anti-theft zippered compartment. Great for travel.", ["crossbody", "sling", "anti-theft"]),
            ("{color} Quilted Handbag", "Quilted {material} handbag in {color} with chain strap and gold-tone hardware.", ["quilted", "handbag", "chain"]),
            ("{color} Gym Duffle Bag", "Spacious duffle in {color} with shoe compartment, wet pocket, and shoulder strap.", ["gym", "duffle", "shoe compartment"]),
            ("{color} Tech Commuter Backpack", "Expandable commuter backpack in {color} with USB port and TSA-friendly laptop sleeve.", ["tech", "commuter", "USB"]),
            ("{color} Weekender Travel Bag", "Stylish weekender in {color} {material} with trolley sleeve. Carry-on approved.", ["weekender", "travel", "carry-on"]),
            ("{color} Camera Bag Padded", "Padded camera bag in {color} with customizable dividers and weather-sealed zippers.", ["camera", "padded", "photography"]),
            ("{color} Clutch Purse", "Slim {material} clutch in {color} with detachable wrist strap. Elegant for evening.", ["clutch", "slim", "evening"]),
            ("{color} Roll-Top Waterproof Pack", "Waterproof roll-top backpack in {color} from recycled materials. 25L for any adventure.", ["roll-top", "waterproof", "eco-friendly"]),
        ],
        "price_range": (24.99, 229.99),
        "materials": ["canvas", "full-grain leather", "nylon", "recycled polyester", "vegan leather", "waxed cotton", "ballistic nylon", "genuine leather"],
        "sizes": ["One Size"],
    },
    "jacket": {
        "prefix": "JK",
        "templates": [
            ("Classic {color} Denim Jacket", "Timeless {color} denim jacket with button closure and chest pockets. A wardrobe essential.", ["denim", "classic", "essential"]),
            ("{color} Leather Biker Jacket", "Genuine {material} biker jacket in {color} with asymmetrical zip and quilted shoulders.", ["leather", "biker", "rebel"]),
            ("{color} Puffer Jacket Insulated", "Warm insulated puffer in {color} with DWR coating and packable design.", ["puffer", "insulated", "packable"]),
            ("{color} Slim Fit Blazer", "Tailored slim-fit blazer in {color}. Perfect for business meetings and smart occasions.", ["blazer", "slim fit", "tailored"]),
            ("{color} Windbreaker", "Ultra-light windbreaker in {color} with reflective details and zip pockets.", ["windbreaker", "ultralight", "reflective"]),
            ("{color} Sherpa Fleece Jacket", "Cozy sherpa fleece in {color} with deep pockets and zip front. Perfect for campfire nights.", ["sherpa", "fleece", "cozy"]),
            ("{color} Trench Coat", "Double-breasted trench coat in {color} with belt and storm flap. Timeless sophistication.", ["trench", "double-breasted", "sophisticated"]),
            ("{color} Bomber Jacket Satin", "Classic satin bomber in {color} with ribbed cuffs and collar. Streetwear icon.", ["bomber", "satin", "streetwear"]),
            ("{color} Rain Shell Jacket", "Fully seam-sealed rain shell in {color} with hood and ventilation zips.", ["rain", "shell", "seam-sealed"]),
            ("{color} Wool Overcoat", "Full-length {material} overcoat in {color} with notch lapels. Executive elegance.", ["wool", "overcoat", "executive"]),
            ("{color} Down Parka Long", "Long down parka in {color} with fur-trimmed hood. Rated to -30F.", ["parka", "down", "extreme cold"]),
            ("{color} Softshell Hiking Jacket", "Stretchy softshell in {color} with wind resistance and DWR finish. Ideal for active hiking.", ["softshell", "hiking", "stretchy"]),
        ],
        "price_range": (49.99, 299.99),
        "materials": ["denim", "genuine leather", "nylon", "wool blend", "polyester", "Gore-Tex", "softshell", "waxed cotton"],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
    },
    "pants": {
        "prefix": "PT",
        "templates": [
            ("Classic {color} Straight-Leg Jeans", "Mid-rise straight-leg jeans in {color} wash. Comfortable stretch {material} for all-day wear.", ["jeans", "straight-leg", "stretch"]),
            ("{color} Slim Fit Chinos", "Slim fit chinos in {color} with slight stretch. Smart enough for office, casual for weekends.", ["chinos", "slim fit", "versatile"]),
            ("{color} Jogger Sweatpants", "Tapered joggers in {color} with elastic cuffs and drawstring waist. Ultra-soft fleece.", ["joggers", "sweatpants", "comfortable"]),
            ("{color} Cargo Pants Relaxed", "Relaxed fit cargo pants in {color} with six pockets. Utility meets style.", ["cargo", "relaxed", "utility"]),
            ("{color} Athletic Training Pants", "Lightweight training pants in {color} with side zip pockets and moisture-wicking {material}.", ["athletic", "training", "moisture-wicking"]),
            ("{color} Wide Leg Trousers", "Flowing wide-leg pants in {color} with high waist and pleated front. Chic and sophisticated.", ["wide leg", "high-waisted", "chic"]),
            ("{color} Skinny Jeans", "Super skinny jeans in {color} with stretch. A versatile wardrobe staple.", ["skinny", "jeans", "staple"]),
            ("{color} Linen Summer Pants", "Relaxed {material} pants in {color} with drawstring waist. Lightweight for hot days.", ["linen", "summer", "drawstring"]),
            ("{color} Tailored Dress Trousers", "Sharp tailored trousers in {color} with pressed crease. Office-ready elegance.", ["tailored", "dress", "formal"]),
            ("{color} Corduroy Pants", "Straight-fit corduroy in {color} with soft wale texture. Retro charm meets modern comfort.", ["corduroy", "retro", "textured"]),
            ("{color} Yoga Leggings High-Rise", "Buttery-soft high-rise yoga leggings in {color} with four-way stretch and hidden pocket.", ["yoga", "leggings", "high-rise"]),
            ("{color} Hiking Convertible Pants", "Zip-off convertible pants in {color} that transform into shorts. Quick-dry with UPF 50+.", ["hiking", "convertible", "quick-dry"]),
            ("{color} Compression Running Tights", "Compression tights in {color} for running with reflective details and calf support.", ["compression", "running", "reflective"]),
        ],
        "price_range": (27.99, 99.99),
        "materials": ["stretch denim", "cotton twill", "fleece", "ripstop nylon", "technical fabric", "linen", "wool blend", "compression fabric"],
        "sizes": ["XS", "S", "M", "L", "XL", "28W", "30W", "32W", "34W", "36W"],
    },
    "accessories": {
        "prefix": "AC",
        "templates": [
            ("Classic {color} Aviator Sunglasses", "Iconic aviator sunglasses with polarized lenses and {color} metal frame. UV400 protection.", ["aviator", "sunglasses", "polarized"]),
            ("{color} Leather Belt", "Full-grain {material} belt in {color} with brushed nickel buckle. A timeless essential.", ["belt", "leather", "essential"]),
            ("{color} Wool Beanie", "Soft merino wool beanie in {color} with ribbed knit texture. Keeps you warm in style.", ["beanie", "wool", "warm"]),
            ("{color} Silk Scarf", "Luxurious silk scarf with {theme} print in {color}. Versatile as headband or neck tie.", ["silk", "scarf", "luxury"]),
            ("{color} Sport Watch Digital", "Rugged digital sport watch in {color} with stopwatch and 100m water resistance.", ["watch", "digital", "sport"]),
            ("{color} Canvas Bucket Hat", "Trendy cotton canvas bucket hat in {color} with wide brim for sun protection.", ["bucket hat", "canvas", "sun protection"]),
            ("{color} Minimalist Wallet", "Slim bifold wallet in {color} {material} with RFID blocking. Fits 8 cards.", ["wallet", "slim", "RFID"]),
            ("{color} Hoop Earrings", "18k gold-plated hoop earrings in {color} tone. Lightweight and hypoallergenic.", ["earrings", "hoops", "hypoallergenic"]),
            ("{color} Cashmere Gloves", "Pure cashmere gloves in {color} with touch-screen compatible fingertips.", ["gloves", "cashmere", "touch screen"]),
            ("{color} Fedora Hat", "Classic wool fedora in {color} with grosgrain ribbon band. Sophisticated headwear.", ["fedora", "wool", "sophisticated"]),
            ("{color} Chain Necklace", "Minimal sterling silver chain necklace in {color} tone with adjustable length.", ["necklace", "silver", "minimal"]),
            ("{color} Crossbody Phone Bag", "Compact {material} phone bag in {color} with card slots and adjustable strap.", ["phone bag", "compact", "crossbody"]),
        ],
        "price_range": (14.99, 89.99),
        "materials": ["genuine leather", "stainless steel", "merino wool", "silk", "cashmere", "canvas", "vegan leather", "sterling silver"],
        "sizes": ["One Size"],
    },
}

COLORS = [
    "white", "black", "navy", "charcoal", "olive", "burgundy", "cream", "sand",
    "forest green", "royal blue", "rust", "camel", "slate gray", "blush pink",
    "deep purple", "midnight blue", "terracotta", "sage green", "stone", "coral",
    "light blue", "dark brown", "heather gray", "neon yellow", "dusty rose",
    "teal", "ivory", "taupe", "burnt orange", "steel blue",
]

STYLES = ["casual", "sporty", "formal", "smart casual", "streetwear", "outdoor", "trendy", "minimalist"]
USE_CASES = ["everyday", "sports", "office", "outdoor", "summer", "winter", "formal", "travel", "festival", "lounge"]
GENDERS = ["men", "women", "unisex"]
THEMES = ["mountain", "geometric", "abstract", "floral", "tropical", "urban", "wave", "sunset"]
FITS = ["slim fit", "relaxed fit", "regular fit", "oversized"]

BRANDS = [
    "BasicThreads", "AthletePro", "UrbanEdge", "ParisBasics", "TrailBlaze",
    "RetroVibe", "GentleWear", "FestivalGear", "WarmLayer", "ChicBasics",
    "RunFast", "StreetBold", "SummerEase", "CoastLife", "WeatherGuard",
    "EcoThread", "LuxeCraft", "TechPack", "TravelSmart", "SunShade",
    "NordStitch", "PeakForm", "VelvetLine", "IronThread", "CraftHouse",
]

# Unsplash image IDs for each category
IMAGES = {
    "t-shirt": [
        "photo-1521572163474-6864f9cf17ab", "photo-1583743814966-8936f5b7be1a",
        "photo-1618354691373-d851c5c3a990", "photo-1554568218-0f1715e72254",
        "photo-1576566588028-4147f3842f27", "photo-1618354691438-25bc04584c23",
        "photo-1586790170083-2f9ceadc732d", "photo-1562157873-818bc0726f68",
        "photo-1596755094514-f87e34085b2c", "photo-1594938298603-c8148c4dae35",
        "photo-1581655353564-df123a1eb820", "photo-1622445275576-721325763afe",
        "photo-1529374255404-311a2a4f1fd9",
    ],
    "shoes": [
        "photo-1549298916-b41d501d3772", "photo-1542291026-7eec264c27ff",
        "photo-1638247025967-b4e38f787b76", "photo-1607522370275-f14206abe5d3",
        "photo-1520219306100-ec4afeeefe58", "photo-1614252234498-1ab7ec142705",
        "photo-1595950653106-6c9ebd614d3a", "photo-1603487742131-4160ec999306",
        "photo-1556906781-9a412961c28c", "photo-1560343090-f0409e92791a",
        "photo-1491553895911-0055eca6402d", "photo-1525966222134-fcfa99b8ae77",
        "photo-1543163521-1bf539c55dd2",
    ],
    "bag": [
        "photo-1544816155-12df9643f363", "photo-1553062407-98eeb64c6a62",
        "photo-1622560480605-d83c853bc5c3", "photo-1548036328-c9fa89d128fa",
        "photo-1584917865442-de89df76afd3", "photo-1590874103328-eac38a683ce7",
        "photo-1594223274512-ad4803739b7c", "photo-1556656793-08538906a9f8",
    ],
    "jacket": [
        "photo-1576995853123-5a10305d93c0", "photo-1551028719-00167b16eac5",
        "photo-1544923246-77307dd270b1", "photo-1591047139829-d91aecb6caea",
        "photo-1495105787522-5334e3ffa0ef",
    ],
    "pants": [
        "photo-1542272454315-4c01d7abdf4a", "photo-1473966968600-fa801b869a1a",
        "photo-1552902865-b72c031ac5ea", "photo-1517438476312-10d79c077509",
        "photo-1594633312681-425c7b97ccd1", "photo-1541099649105-f69ad21f3246",
        "photo-1506629082955-511b1aa562c8",
    ],
    "accessories": [
        "photo-1511499767150-a48a237f0083", "photo-1576871337622-98d48d1cf531",
        "photo-1524592094714-0f0654e20314", "photo-1535632066927-ab7c9ab60908",
        "photo-1601924994987-69e26d50dc26",
    ],
}


def generate_product(category: str, index: int) -> dict:
    cat_config = CATEGORIES[category]
    template = random.choice(cat_config["templates"])
    title_tpl, desc_tpl, base_tags = template

    color = random.choice(COLORS)
    material = random.choice(cat_config["materials"])
    style = random.choice(STYLES)
    use_case = random.choice(USE_CASES)
    gender = random.choice(GENDERS)
    brand = random.choice(BRANDS)
    theme = random.choice(THEMES)
    fit = random.choice(FITS)

    title = title_tpl.format(color=color.title(), theme=theme, fit=fit.title(), material=material)
    desc = desc_tpl.format(color=color, material=material, use_case=use_case, theme=theme, fit=fit)

    lo, hi = cat_config["price_range"]
    price = round(random.uniform(lo, hi), 2)
    # Make price end in .99 or .49
    price = round(int(price) + random.choice([0.49, 0.99]), 2)

    rating = round(random.uniform(3.5, 5.0), 1)
    review_count = random.randint(5, 2000)
    discount = random.choice([0, 0, 0, 0, 0, 10, 15, 20, 25, 30])  # Most items no discount
    in_stock = random.random() > 0.08  # 8% out of stock

    images = IMAGES[category]
    image_id = images[index % len(images)]

    product_id = f"{cat_config['prefix']}{index + 1:03d}"
    tags = list(set(base_tags + [color, style, use_case, material.split()[0].lower()]))

    return {
        "id": product_id,
        "title": title,
        "category": category,
        "description": desc,
        "tags": tags[:8],
        "price": price,
        "color": color,
        "style": style,
        "use_case": use_case,
        "gender": gender,
        "rating": rating,
        "brand": brand,
        "image_url": f"https://images.unsplash.com/{image_id}?w=400",
        "material": material,
        "sizes": cat_config["sizes"] if category != "bag" and category != "accessories" else ["One Size"],
        "in_stock": in_stock,
        "review_count": review_count,
        "discount_pct": discount,
    }


def main():
    products = []
    # Distribution: more t-shirts and pants (popular categories)
    distribution = {
        "t-shirt": 100,
        "shoes": 90,
        "pants": 100,
        "jacket": 80,
        "bag": 70,
        "accessories": 60,
    }

    for category, count in distribution.items():
        for i in range(count):
            products.append(generate_product(category, i))

    random.shuffle(products)
    total = len(products)
    print(f"Generated {total} products")

    # Stats
    cats = {}
    for p in products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    for c, n in sorted(cats.items()):
        prices = [p["price"] for p in products if p["category"] == c]
        print(f"  {c}: {n} items (${min(prices):.2f} - ${max(prices):.2f})")

    out_of_stock = sum(1 for p in products if not p["in_stock"])
    discounted = sum(1 for p in products if p["discount_pct"] > 0)
    print(f"  Out of stock: {out_of_stock}")
    print(f"  On sale: {discounted}")

    output_path = "backend/data/catalog.json"
    with open(output_path, "w") as f:
        json.dump(products, f, indent=2)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
