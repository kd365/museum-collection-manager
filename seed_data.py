"""Seed the database with sample museum data and an admin account."""

from datetime import date
from museums_app import create_app
from extensions import db
from models import User, Artist, Artwork, Museum, Collection


def seed():
    app = create_app('development')

    with app.app_context():
        # Clear existing data
        Collection.query.delete()
        Artwork.query.delete()
        Artist.query.delete()
        Museum.query.delete()
        User.query.delete()
        db.session.commit()

        # Admin account
        admin = User(username='admin', email='admin@museumcollection.com', is_admin=True)
        admin.set_password('Admin123!')
        db.session.add(admin)

        # --- Artists ---
        artists = [
            Artist(
                name='Vincent van Gogh',
                birth_date=date(1853, 3, 30), death_date=date(1890, 7, 29),
                is_living=False, birth_place='Zundert, Netherlands',
                death_place='Auvers-sur-Oise, France', nationality='Dutch',
                art_movement='Post-Impressionism', primary_medium='Painting',
                bio='Dutch Post-Impressionist painter who posthumously became one of the most famous and influential figures in Western art history.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project.jpg/800px-Vincent_van_Gogh_-_Self-Portrait_-_Google_Art_Project.jpg',
            ),
            Artist(
                name='Claude Monet',
                birth_date=date(1840, 11, 14), death_date=date(1926, 12, 5),
                is_living=False, birth_place='Paris, France',
                death_place='Giverny, France', nationality='French',
                art_movement='Impressionism', primary_medium='Painting',
                bio='French Impressionist painter and founder of the Impressionist movement, known for his landscapes and water lily series.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Claude_Monet_1899_Nadar_crop.jpg/800px-Claude_Monet_1899_Nadar_crop.jpg',
            ),
            Artist(
                name='Frida Kahlo',
                birth_date=date(1907, 7, 6), death_date=date(1954, 7, 13),
                is_living=False, birth_place='Coyoacan, Mexico',
                death_place='Coyoacan, Mexico', nationality='Mexican',
                art_movement='Surrealism', primary_medium='Painting',
                bio='Mexican artist known for her self-portraits and works inspired by nature and Mexican folk art, blending realism with fantasy.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg/800px-Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg',
            ),
            Artist(
                name='Leonardo da Vinci',
                birth_date=date(1452, 4, 15), death_date=date(1519, 5, 2),
                is_living=False, birth_place='Vinci, Italy',
                death_place='Amboise, France', nationality='Italian',
                art_movement='Renaissance', primary_medium='Painting',
                bio='Italian polymath of the High Renaissance, regarded as one of the greatest painters of all time and possibly the most diversely talented person ever.',
            ),
            Artist(
                name='Yayoi Kusama',
                birth_date=date(1929, 3, 22),
                is_living=True, birth_place='Matsumoto, Japan',
                nationality='Japanese',
                art_movement='Contemporary', primary_medium='Installation',
                bio='Japanese contemporary artist who works primarily in sculpture and installation art, known for her polka dots and infinity rooms.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Yayoi_Kusama_cropped_2_Yayoi_Kusama_201611.jpg/800px-Yayoi_Kusama_cropped_2_Yayoi_Kusama_201611.jpg',
            ),
            Artist(
                name='Georgia O\'Keeffe',
                birth_date=date(1887, 11, 15), death_date=date(1986, 3, 6),
                is_living=False, birth_place='Sun Prairie, Wisconsin',
                death_place='Santa Fe, New Mexico', nationality='American',
                art_movement='Modern', primary_medium='Painting',
                bio='American modernist artist known for her paintings of enlarged flowers, New York skyscrapers, and New Mexico landscapes.',
            ),
        ]
        db.session.add_all(artists)
        db.session.flush()

        # --- Artworks ---
        artworks = [
            Artwork(
                title='The Starry Night',
                artist_id=artists[0].id, medium='Oil on canvas',
                art_movement='Post-Impressionism', subject='Landscape',
                creation_date=date(1889, 6, 1),
                dimension_H=73.7, dimension_W=92.1, dimension_unit='cm',
                estimated_value=100000000,
                description='Depicts the view from his asylum room at Saint-Remy-de-Provence with an idealized village and dramatic swirling night sky.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
                is_signed=False,
            ),
            Artwork(
                title='Sunflowers',
                artist_id=artists[0].id, medium='Oil on canvas',
                art_movement='Post-Impressionism', subject='Still Life',
                creation_date=date(1888, 8, 1),
                dimension_H=92.1, dimension_W=73, dimension_unit='cm',
                estimated_value=39000000,
                description='Part of a series of paintings depicting sunflowers in various stages, created to decorate the room of Paul Gauguin in Arles.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Vincent_Willem_van_Gogh_127.jpg/800px-Vincent_Willem_van_Gogh_127.jpg',
                is_signed=True, signature_location='Lower left',
            ),
            Artwork(
                title='Water Lilies',
                artist_id=artists[1].id, medium='Oil on canvas',
                art_movement='Impressionism', subject='Landscape',
                creation_date=date(1906, 1, 1),
                dimension_H=89.9, dimension_W=94.1, dimension_unit='cm',
                estimated_value=80000000,
                description='Part of approximately 250 oil paintings depicting the water lily pond at his home in Giverny.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg/1280px-Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg',
                is_signed=True, signature_location='Lower right',
            ),
            Artwork(
                title='Impression, Sunrise',
                artist_id=artists[1].id, medium='Oil on canvas',
                art_movement='Impressionism', subject='Landscape',
                creation_date=date(1872, 11, 13),
                dimension_H=48, dimension_W=63, dimension_unit='cm',
                estimated_value=30000000,
                description='The painting that gave the Impressionist movement its name, depicting the port of Le Havre at sunrise.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Monet_-_Impression%2C_Sunrise.jpg/1280px-Monet_-_Impression%2C_Sunrise.jpg',
                is_signed=True, signature_location='Lower left',
            ),
            Artwork(
                title='The Two Fridas',
                artist_id=artists[2].id, medium='Oil on canvas',
                art_movement='Surrealism', subject='Portrait',
                creation_date=date(1939, 1, 1),
                dimension_H=173.5, dimension_W=173, dimension_unit='cm',
                estimated_value=30000000,
                description='Double self-portrait showing two versions of Kahlo seated side by side, their hearts exposed and connected by a vein.',
                image_url='https://upload.wikimedia.org/wikipedia/en/thumb/2/22/Frida_Kahlo_-_The_Two_Fridas.jpg/800px-Frida_Kahlo_-_The_Two_Fridas.jpg',
                is_signed=True, signature_location='Lower right',
            ),
            Artwork(
                title='Self-Portrait with Thorn Necklace',
                artist_id=artists[2].id, medium='Oil on canvas',
                art_movement='Surrealism', subject='Portrait',
                creation_date=date(1940, 1, 1),
                dimension_H=63.5, dimension_W=49.5, dimension_unit='cm',
                estimated_value=25000000,
                description='One of Kahlo\'s most recognized works, featuring her with a thorn necklace, a hummingbird, a black cat, and a monkey.',
                is_signed=True, signature_location='Lower center',
            ),
            Artwork(
                title='Mona Lisa',
                artist_id=artists[3].id, medium='Oil on poplar panel',
                art_movement='Renaissance', subject='Portrait',
                creation_date=date(1503, 1, 1),
                dimension_H=77, dimension_W=53, dimension_unit='cm',
                description='Half-length portrait of a woman by Leonardo da Vinci, considered the most famous painting in the world.',
                image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg',
                is_signed=False,
            ),
            Artwork(
                title='Infinity Mirrored Room',
                artist_id=artists[4].id, medium='Mixed Media',
                art_movement='Contemporary', subject='Abstract',
                creation_date=date(2013, 1, 1),
                description='An immersive installation featuring mirrors and LED lights creating the illusion of infinite space.',
                is_signed=False,
            ),
            Artwork(
                title='Jimson Weed/White Flower No. 1',
                artist_id=artists[5].id, medium='Oil on canvas',
                art_movement='Modern', subject='Still Life',
                creation_date=date(1932, 1, 1),
                dimension_H=121.9, dimension_W=101.6, dimension_unit='cm',
                estimated_value=44400000,
                description='A monumental close-up of a white jimson weed flower, exemplifying O\'Keeffe\'s signature style of magnified floral forms.',
                is_signed=False,
            ),
        ]
        db.session.add_all(artworks)
        db.session.flush()

        # --- Museums ---
        museums = [
            Museum(
                name='Museum of Modern Art (MoMA)',
                museum_type='Modern Art', city='New York City',
                state_province='New York', country='United States',
                address='11 W 53rd St', postal_code='10019',
                established_date=date(1929, 11, 7),
                website='https://www.moma.org', phone='+1-212-708-9400',
                description='One of the largest and most influential museums of modern art in the world.',
                annual_visitors=2800000, admission_fee=25.00,
            ),
            Museum(
                name='Musee d\'Orsay',
                museum_type='Art', city='Paris',
                country='France', postal_code='75007',
                address='1 Rue de la Legion d\'Honneur',
                established_date=date(1986, 12, 1),
                website='https://www.musee-orsay.fr',
                description='Houses the largest collection of Impressionist and Post-Impressionist masterpieces in the world.',
                annual_visitors=3600000, admission_fee=16.00,
            ),
            Museum(
                name='Museo Frida Kahlo',
                museum_type='Art', city='Mexico City',
                country='Mexico', postal_code='04000',
                address='Londres 247, Del Carmen, Coyoacan',
                established_date=date(1958, 1, 1),
                website='https://www.museofridakahlo.org.mx',
                description='Also known as the Blue House, it is the birthplace and former residence of Mexican artist Frida Kahlo.',
                annual_visitors=500000, admission_fee=11.00,
            ),
            Museum(
                name='The Louvre',
                museum_type='Art', city='Paris',
                country='France', postal_code='75001',
                address='Rue de Rivoli',
                established_date=date(1793, 8, 10),
                website='https://www.louvre.fr',
                description='The world\'s largest art museum and a historic monument in Paris, home to thousands of works including the Mona Lisa.',
                annual_visitors=7800000, admission_fee=17.00,
            ),
        ]
        db.session.add_all(museums)
        db.session.flush()

        # --- Collections (assign artworks to museums) ---
        collections = [
            Collection(museum_id=museums[0].id, artwork_id=artworks[0].id,
                       accession_number='MoMA.472.1941', acquisition_method='Purchase',
                       acquisition_date=date(1941, 1, 1), status='Active',
                       gallery_location='Gallery 5, Floor 5', on_display=True),
            Collection(museum_id=museums[0].id, artwork_id=artworks[7].id,
                       accession_number='MoMA.2013.001', acquisition_method='Commission',
                       acquisition_date=date(2013, 1, 1), status='Active',
                       gallery_location='Special Exhibition Hall', on_display=True),
            Collection(museum_id=museums[0].id, artwork_id=artworks[8].id,
                       accession_number='MoMA.1994.032', acquisition_method='Purchase',
                       acquisition_date=date(1994, 11, 1), status='Active',
                       gallery_location='Gallery 4, Floor 5', on_display=True),
            Collection(museum_id=museums[1].id, artwork_id=artworks[2].id,
                       accession_number='RF.1981.40', acquisition_method='Donation',
                       acquisition_date=date(1981, 1, 1), status='Active',
                       gallery_location='Impressionism Gallery', on_display=True),
            Collection(museum_id=museums[1].id, artwork_id=artworks[3].id,
                       accession_number='RF.1952.15', acquisition_method='Purchase',
                       acquisition_date=date(1952, 1, 1), status='Active',
                       gallery_location='Impressionism Gallery', on_display=True),
            Collection(museum_id=museums[1].id, artwork_id=artworks[1].id,
                       accession_number='RF.1987.12', acquisition_method='Purchase',
                       acquisition_date=date(1987, 3, 30), status='Active',
                       gallery_location='Post-Impressionism Wing', on_display=True),
            Collection(museum_id=museums[2].id, artwork_id=artworks[4].id,
                       accession_number='FK.1958.001', acquisition_method='Bequest',
                       acquisition_date=date(1958, 1, 1), status='Active',
                       gallery_location='Main Gallery', on_display=True),
            Collection(museum_id=museums[2].id, artwork_id=artworks[5].id,
                       accession_number='FK.1958.015', acquisition_method='Bequest',
                       acquisition_date=date(1958, 1, 1), status='Active',
                       gallery_location='Second Floor Gallery', on_display=True),
            Collection(museum_id=museums[3].id, artwork_id=artworks[6].id,
                       accession_number='INV.779', acquisition_method='Transfer',
                       acquisition_date=date(1797, 1, 1), status='Active',
                       gallery_location='Salle des Etats, Floor 1', on_display=True),
        ]
        db.session.add_all(collections)
        db.session.commit()

        print(f"Seeded: {len(artists)} artists, {len(artworks)} artworks, "
              f"{len(museums)} museums, {len(collections)} collection entries")
        print(f"Admin account: admin@museumcollection.com / Admin123!")


if __name__ == '__main__':
    seed()
