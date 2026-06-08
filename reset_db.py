import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app import app, db
from models import User, Property, PropertyImage, SavedSearch, SearchAlert

def seed():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        # Add Admin User
        print("Adding admin user...")
        admin = User(full_name='Admin User', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit() # Commit to get admin ID

        # Sample Properties with Multiple Images
        samples = [
            {
                'title': 'Luxury Villa in New Capital',
                'price': '12,500,000 EGP',
                'location': '30.0125, 31.7513',
                'city': 'New Administrative Capital',
                'listing_type': 'buy',
                'images': [
                    'https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&q=80&w=800',
                    'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&q=80&w=800'
                ],
                'description': 'A stunning 5-bedroom villa with a private pool and spacious garden in the New Administrative Capital.',
                'lat': 30.0125, 'lng': 31.7513,
                'area': '450 sqm', 'bedrooms': 5, 'bathrooms': 4,
                'contact_phone': '+20 100 123 4567',
                'tags': ['pool', 'private garden', 'smart home']
            },
            {
                'title': 'Modern Apartment in El Shorouk',
                'price': '45,000 EGP / Month',
                'location': '30.1415, 31.6288',
                'city': 'El Shorouk',
                'listing_type': 'rent',
                'images': [
                    'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=800',
                    'https://images.unsplash.com/photo-1560448204-61dc36dc98c8?auto=format&fit=crop&q=80&w=800'
                ],
                'description': 'Elegant 3-bedroom apartment with a view. Perfect for families looking for a quiet life in El Shorouk.',
                'lat': 30.1415, 'lng': 31.6288,
                'area': '180 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 111 987 6543',
                'tags': ['air conditioner', 'parking']
            },
            {
                'title': 'Family House in Badr City',
                'price': '8,200,000 EGP',
                'location': '30.1348, 31.7392',
                'city': 'Badr',
                'listing_type': 'buy',
                'images': [
                    'https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?auto=format&fit=crop&q=80&w=800',
                    'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&q=80&w=800'
                ],
                'description': 'Spacious family home in Badr City with a large garden and modern finishes.',
                'lat': 30.1348, 'lng': 31.7392,
                'area': '320 sqm', 'bedrooms': 4, 'bathrooms': 3,
                'contact_phone': '+20 122 345 6789',
                'tags': ['private garden', 'parking']
            },
            {
                'title': 'Stylish Studio in Nasr City',
                'price': '25,000 EGP / Month',
                'location': '30.0571, 31.3415',
                'city': 'Nasr City',
                'listing_type': 'rent',
                'images': [
                    'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800',
                    'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&q=80&w=800'
                ],
                'description': 'Newly renovated studio apartment in the heart of Nasr City. Ideal for young professionals.',
                'lat': 30.0571, 'lng': 31.3415,
                'area': '55 sqm', 'bedrooms': 1, 'bathrooms': 1,
                'contact_phone': '+20 106 555 4444',
                'tags': ['smart home', 'air conditioner']
            },
            {
                'title': 'High-Rise Condo in New Capital',
                'price': '6,500,000 EGP',
                'location': '30.0145, 31.7525',
                'city': 'New Administrative Capital',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&q=80&w=800'],
                'description': 'Modern condo with a view of the Iconic Tower.',
                'lat': 30.0145, 'lng': 31.7525,
                'area': '180 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 100 111 2222',
                'tags': ['parking', 'air conditioner']
            },
            {
                'title': 'Penthouse in El Shorouk',
                'price': '4,200,000 EGP',
                'location': '30.1450, 31.6350',
                'city': 'El Shorouk',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1512914890251-2f96a9b0bbe2?auto=format&fit=crop&q=80&w=800'],
                'description': 'Spacious penthouse with a private roof garden.',
                'lat': 30.1450, 'lng': 31.6350,
                'area': '250 sqm', 'bedrooms': 4, 'bathrooms': 3,
                'contact_phone': '+20 101 222 3333',
                'tags': ['private garden', 'parking']
            },
            {
                'title': 'Budget Apartment in Badr',
                'price': '1,800,000 EGP',
                'location': '30.1360, 31.7420',
                'city': 'Badr',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1515263487990-61b07816b324?auto=format&fit=crop&q=80&w=800'],
                'description': 'Affordable 2-bedroom apartment near the city center.',
                'lat': 30.1360, 'lng': 31.7420,
                'area': '110 sqm', 'bedrooms': 2, 'bathrooms': 1,
                'contact_phone': '+20 102 333 4444',
                'tags': ['parking']
            },
            
            {
                'title': 'Executive Suite in New Capital',
                'price': '80,000 EGP / Month',
                'location': '30.0160, 31.7565',
                'city': 'New Administrative Capital',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800'],
                'description': 'Luxury suite for executives in the financial district.',
                'lat': 30.0160, 'lng': 31.7565,
                'area': '150 sqm', 'bedrooms': 2, 'bathrooms': 2,
                'contact_phone': '+20 104 555 6666',
                'tags': ['smart home', 'parking']
            },
            {
                'title': 'Duplex Garden in Shorouk',
                'price': '5,800,000 EGP',
                'location': '30.1420, 31.6250',
                'city': 'El Shorouk',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&q=80&w=800'],
                'description': 'Charming duplex with a large private garden.',
                'lat': 30.1420, 'lng': 31.6250,
                'area': '240 sqm', 'bedrooms': 3, 'bathrooms': 3,
                'contact_phone': '+20 105 666 7777',
                'tags': ['private garden', 'parking']
            },
            {
                'title': 'Studio in Badr City',
                'price': '8,000 EGP / Month',
                'location': '30.1340, 31.7380',
                'city': 'Badr',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1536376074432-bf1581456a7d?auto=format&fit=crop&q=80&w=800'],
                'description': 'Cozy studio for students or young workers.',
                'lat': 30.1340, 'lng': 31.7380,
                'area': '50 sqm', 'bedrooms': 1, 'bathrooms': 1,
                'contact_phone': '+20 106 777 8888',
                'tags': ['air conditioner']
            },
            {
                'title': 'Ground Luxury in Nasr City',
                'price': '12,000,000 EGP',
                'location': '30.0550, 31.3380',
                'city': 'Nasr City',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=800'],
                'description': 'Ultra-luxury ground floor apartment with private entrance.',
                'lat': 30.0550, 'lng': 31.3380,
                'area': '300 sqm', 'bedrooms': 4, 'bathrooms': 4,
                'contact_phone': '+20 107 888 9999',
                'tags': ['private garden', 'parking', 'smart home']
            },
            {
                'title': 'Townhouse in New Capital',
                'price': '9,500,000 EGP',
                'location': '30.0130, 31.7540',
                'city': 'New Administrative Capital',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&q=80&w=800'],
                'description': 'Modern townhouse in a prime residential compound.',
                'lat': 30.0130, 'lng': 31.7540,
                'area': '320 sqm', 'bedrooms': 4, 'bathrooms': 4,
                'contact_phone': '+20 108 999 0000',
                'tags': ['parking', 'pool']
            },
            {
                'title': 'Cozy Flat in Shorouk',
                'price': '15,000 EGP / Month',
                'location': '30.1390, 31.6210',
                'city': 'El Shorouk',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800'],
                'description': 'Sunny apartment in a quiet neighborhood of Shorouk.',
                'lat': 30.1390, 'lng': 31.6210,
                'area': '140 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 109 000 1111',
                'tags': ['parking', 'air conditioner']
            },
            {
                'title': 'Large Villa in Badr',
                'price': '6,200,000 EGP',
                'location': '30.1385, 31.7490',
                'city': 'Badr',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=800'],
                'description': 'Spacious villa for large families with a big yard.',
                'lat': 30.1385, 'lng': 31.7490,
                'area': '400 sqm', 'bedrooms': 5, 'bathrooms': 4,
                'contact_phone': '+20 110 111 2222',
                'tags': ['private garden', 'parking']
            },
            {
                'title': 'Modern Studio in Nasr City',
                'price': '15,000 EGP / Month',
                'location': '30.0585, 31.3450',
                'city': 'Nasr City',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1560448204-61dc36dc98c8?auto=format&fit=crop&q=80&w=800'],
                'description': 'Fully renovated studio for young professionals.',
                'lat': 30.0585, 'lng': 31.3450,
                'area': '70 sqm', 'bedrooms': 1, 'bathrooms': 1,
                'contact_phone': '+20 111 222 3333',
                'tags': ['air conditioner', 'parking']
            },
            {
                'title': 'Villa Oasis in New Capital',
                'price': '18,000,000 EGP',
                'location': '30.0110, 31.7580',
                'city': 'New Administrative Capital',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&q=80&w=800'],
                'description': 'Exclusive villa with high-end finishes and pool.',
                'lat': 30.0110, 'lng': 31.7580,
                'area': '550 sqm', 'bedrooms': 6, 'bathrooms': 5,
                'contact_phone': '+20 112 333 4444',
                'tags': ['pool', 'smart home', 'private garden']
            },
            {
                'title': 'Apartment for Rent in Shorouk',
                'price': '22,000 EGP / Month',
                'location': '30.1435, 31.6310',
                'city': 'El Shorouk',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=800'],
                'description': 'Modern flat in a premium Shorouk compound.',
                'lat': 30.1435, 'lng': 31.6310,
                'area': '160 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 113 444 5555',
                'tags': ['parking', 'air conditioner']
            },
            {
                'title': 'Eco-House in Badr',
                'price': '3,500,000 EGP',
                'location': '30.1320, 31.7350',
                'city': 'Badr',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&q=80&w=800'],
                'description': 'Eco-friendly house with solar energy.',
                'lat': 30.1320, 'lng': 31.7350,
                'area': '200 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 114 555 6666',
                'tags': ['private garden']
            },
            {
                'title': 'Office Studio in Nasr City',
                'price': '10,000 EGP / Month',
                'location': '30.0610, 31.3480',
                'city': 'Nasr City',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800'],
                'description': 'Small studio perfect for a small business office.',
                'lat': 30.0610, 'lng': 31.3480,
                'area': '45 sqm', 'bedrooms': 0, 'bathrooms': 1,
                'contact_phone': '+20 115 666 7777',
                'tags': ['parking']
            },
            {
                'title': 'Luxury Flat in New Capital',
                'price': '7,200,000 EGP',
                'location': '30.0155, 31.7590',
                'city': 'New Administrative Capital',
                'listing_type': 'buy',
                'images': ['https://images.unsplash.com/photo-1560448204-61dc36dc98c8?auto=format&fit=crop&q=80&w=800'],
                'description': 'Spacious 3-bedroom flat in the R7 district.',
                'lat': 30.0155, 'lng': 31.7590,
                'area': '210 sqm', 'bedrooms': 3, 'bathrooms': 3,
                'contact_phone': '+20 116 777 8888',
                'tags': ['parking', 'air conditioner']
            },
            {
                'title': 'Rental Villa in Shorouk',
                'price': '65,000 EGP / Month',
                'location': '30.1460, 31.6400',
                'city': 'El Shorouk',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&q=80&w=800'],
                'description': 'Beautiful villa for rent in Shorouk, fully furnished.',
                'lat': 30.1460, 'lng': 31.6400,
                'area': '380 sqm', 'bedrooms': 4, 'bathrooms': 4,
                'contact_phone': '+20 117 888 9999',
                'tags': ['pool', 'private garden']
            },
            {
                'title': 'Apartment near Badr University',
                'price': '10,000 EGP / Month',
                'location': '30.1375, 31.7460',
                'city': 'Badr',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&q=80&w=800'],
                'description': 'Ideal for students, twin apartment with high capacity.',
                'lat': 30.1375, 'lng': 31.7460,
                'area': '130 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 118 999 0000',
                'tags': ['parking']
            },
            {
                'title': 'Sunny Flat in Nasr City',
                'price': '28,000 EGP / Month',
                'location': '30.0630, 31.3550',
                'city': 'Nasr City',
                'listing_type': 'rent',
                'images': ['https://images.unsplash.com/photo-1493666438817-866a91353ca9?auto=format&fit=crop&q=80&w=800'],
                'description': 'Well-lit apartment in a high-floor corner building.',
                'lat': 30.0630, 'lng': 31.3550,
                'area': '170 sqm', 'bedrooms': 3, 'bathrooms': 2,
                'contact_phone': '+20 119 000 1111',
                'tags': ['air conditioner', 'parking']
            }
        ]

        print("Seeding properties...")
        for s in samples:
            p = Property(
                title=s['title'],
                price=s['price'],
                location=s['location'],
                listing_type=s['listing_type'],
                description=s['description'],
                lat=s['lat'],
                lng=s['lng'],
                area=s['area'],
                bedrooms=s['bedrooms'],
                bathrooms=s['bathrooms'],
                image_url=s['images'][0],
                owner_id=admin.id,
                status='approved',
                contact_email=admin.email,
                contact_phone=s.get('contact_phone'),
                city=s.get('city'),
                year_built=s.get('year_built', 2023),
                tags=s.get('tags', [])
            )
            db.session.add(p)
            db.session.flush() # Get ID for images

            for img_url in s['images']:
                pi = PropertyImage(property_id=p.id, image_url=img_url)
                db.session.add(pi)

        db.session.commit()

        # Add Sample Profile Data for Admin
        print("Adding sample profile data for admin...")
        # Save first two properties
        all_props = Property.query.limit(2).all()
        for p in all_props:
            admin.saved_list.append(p)
        
        # Add Saved Searches
        s1 = SavedSearch(user_id=admin.id, name='Downtown Lofts', filters={'city': 'New Cairo', 'type': 'buy', 'min_price': 5000000})
        s2 = SavedSearch(user_id=admin.id, name='Marin Retreats', filters={'city': 'North Coast', 'type': 'rent'})
        db.session.add_all([s1, s2])

        # Add Search Alerts
        a1 = SearchAlert(user_id=admin.id, name='Downtown Condos < $900k', criteria='2+ Beds • Downtown, SoMa • New Listings Only', frequency='instant')
        a2 = SearchAlert(user_id=admin.id, name='Marin County Homes', criteria='3+ Beds • Mill Valley, Tiburon • Price Drops', frequency='daily')
        db.session.add_all([a1, a2])

        db.session.commit()
        print("Database reset and seeded successfully!")

if __name__ == '__main__':
    seed()
