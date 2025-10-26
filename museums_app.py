from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import mysql.connector
from mysql.connector import Error
from config import Config
from forms import ArtistForm, ArtworkForm, MuseumForm, CollectionForm, SQLQueryForm
import csv
import io

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def normalize_url(url):
    """Add https:// if missing from URL"""
    if not url:
        return None
    url = url.strip()
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# ========= Test Route =============
@app.route('/test')
def test():
    return "<h1>Hello World!</h1><p>If you see this, Flask is working!</p>"




# ============= HOME ROUTE =============
@app.route('/')
def index():
    """Homepage with dashboard statistics"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('index.html', stats={})
    
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    stats = {}
    try:
        cursor.execute("SELECT COUNT(*) as count FROM artists")
        stats['artists'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM artworks")
        stats['artworks'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM museums")
        stats['museums'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM collections")
        stats['collections'] = cursor.fetchone()['count']
        
        # Get recent artworks with artist names
        cursor.execute("""
            SELECT a.title, a.image_url, ar.name as artist_name, a.creation_date
            FROM artworks a
            LEFT JOIN artists ar ON a.artist_id = ar.id
            ORDER BY a.created_at DESC
            LIMIT 6
        """)
        stats['recent_artworks'] = cursor.fetchall()
        
    except Error as e:
        print(f"Error fetching stats: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return render_template('index.html', stats=stats)

# ============= ARTISTS ROUTES =============
@app.route('/artists')
def artists():
    """List all artists"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('artists.html', artists=[])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM artists 
        ORDER BY name
    """)
    artists_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('artists.html', artists=artists_list)

@app.route('/artists/create', methods=['GET', 'POST'])
def create_artist():
    """Create new artist"""
    form = ArtistForm()
    
    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('artists'))
        
        cursor = conn.cursor()
        
        # Normalize URLs
        website = normalize_url(form.website.data)
        image_url = normalize_url(form.image_url.data)
        
        try:
            cursor.execute("""
                INSERT INTO artists 
                (name, birth_date, death_date, is_living, birth_place, death_place, 
                 nationality, art_movement, primary_medium, bio, website, image_url, instagram)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.name.data,
                form.birth_date.data,
                form.death_date.data,
                form.is_living.data,
                form.birth_place.data,
                form.death_place.data,
                form.nationality.data,
                form.art_movement.data or None,
                form.primary_medium.data or None,
                form.bio.data,
                website,
                image_url,
                form.instagram.data
            ))
            conn.commit()
            flash(f'Artist "{form.name.data}" created successfully!', 'success')
            return redirect(url_for('artists'))
        except Error as e:
            flash(f'Error creating artist: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('artist_form.html', form=form, title='Create Artist')

@app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
def edit_artist(artist_id):
    """Edit existing artist"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('artists'))
    
    cursor = conn.cursor(dictionary=True)
    
    # Get existing artist data
    cursor.execute("SELECT * FROM artists WHERE id = %s", (artist_id,))
    artist = cursor.fetchone()
    
    if not artist:
        flash('Artist not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('artists'))
    
    form = ArtistForm(data=artist)
    
    if form.validate_on_submit():
        website = normalize_url(form.website.data)
        image_url = normalize_url(form.image_url.data)
        
        try:
            cursor.execute("""
                UPDATE artists 
                SET name=%s, birth_date=%s, death_date=%s, is_living=%s, 
                    birth_place=%s, death_place=%s, nationality=%s, art_movement=%s, 
                    primary_medium=%s, bio=%s, website=%s, image_url=%s, instagram=%s
                WHERE id=%s
            """, (
                form.name.data, form.birth_date.data, form.death_date.data,
                form.is_living.data, form.birth_place.data, form.death_place.data,
                form.nationality.data, form.art_movement.data or None,
                form.primary_medium.data or None, form.bio.data,
                website, image_url, form.instagram.data, artist_id
            ))
            conn.commit()
            flash(f'Artist "{form.name.data}" updated successfully!', 'success')
            return redirect(url_for('artists'))
        except Error as e:
            flash(f'Error updating artist: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('artist_form.html', form=form, title='Edit Artist', artist=artist)

@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    """Delete artist"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('artists'))
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM artists WHERE id = %s", (artist_id,))
        conn.commit()
        flash('Artist deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting artist: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('artists'))

# ============= ARTWORKS ROUTES =============
@app.route('/artworks')
def artworks():
    """List all artworks"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('artworks.html', artworks=[])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, ar.name as artist_name
        FROM artworks a
        LEFT JOIN artists ar ON a.artist_id = ar.id
        ORDER BY a.title
    """)
    artworks_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('artworks.html', artworks=artworks_list)

@app.route('/artworks/create', methods=['GET', 'POST'])
def create_artwork():
    """Create new artwork"""
    form = ArtworkForm()
    
    # Populate artist dropdown
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM artists ORDER BY name")
        artists = cursor.fetchall()
        form.artist_id.choices = [(0, 'Select Artist')] + [(a['id'], a['name']) for a in artists]
        cursor.close()
    
    if form.validate_on_submit():
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('artworks'))
        
        cursor = conn.cursor()
        image_url = normalize_url(form.image_url.data)
        
        try:
            cursor.execute("""
                INSERT INTO artworks 
                (title, artist_id, medium, art_movement, subject, creation_date,
                 dimension_H, dimension_W, dimension_D, dimension_unit, weight, weight_unit,
                 estimated_value, description, image_url, is_signed, signature_location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.title.data, form.artist_id.data, form.medium.data,
                form.art_movement.data or None, form.subject.data or None,
                form.creation_date.data, form.dimension_H.data, form.dimension_W.data,
                form.dimension_D.data, form.dimension_unit.data, form.weight.data,
                form.weight_unit.data, form.estimated_value.data, form.description.data,
                image_url, form.is_signed.data, form.signature_location.data
            ))
            conn.commit()
            flash(f'Artwork "{form.title.data}" created successfully!', 'success')
            return redirect(url_for('artworks'))
        except Error as e:
            flash(f'Error creating artwork: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    if conn:
        conn.close()
    
    return render_template('artwork_form.html', form=form, title='Create Artwork')

@app.route('/artworks/<int:artwork_id>/delete', methods=['POST'])
def delete_artwork(artwork_id):
    """Delete artwork"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('artworks'))
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM artworks WHERE id = %s", (artwork_id,))
        conn.commit()
        flash('Artwork deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting artwork: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('artworks'))

@app.route('/artworks/<int:artwork_id>/edit', methods=['GET', 'POST'])
def edit_artwork(artwork_id):
    """Edit existing artwork"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('artworks'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM artworks WHERE id = %s", (artwork_id,))
    artwork = cursor.fetchone()
    
    if not artwork:
        flash('Artwork not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('artworks'))
    
    form = ArtworkForm(data=artwork)
    
    # Populate artist dropdown
    cursor.execute("SELECT id, name FROM artists ORDER BY name")
    artists = cursor.fetchall()
    form.artist_id.choices = [(a['id'], a['name']) for a in artists]
    
    if form.validate_on_submit():
        image_url = normalize_url(form.image_url.data)
        
        try:
            cursor.execute("""
                UPDATE artworks 
                SET title=%s, artist_id=%s, medium=%s, art_movement=%s, subject=%s,
                    creation_date=%s, dimension_H=%s, dimension_W=%s, dimension_D=%s,
                    dimension_unit=%s, weight=%s, weight_unit=%s, estimated_value=%s,
                    description=%s, image_url=%s, is_signed=%s, signature_location=%s
                WHERE id=%s
            """, (
                form.title.data, form.artist_id.data, form.medium.data,
                form.art_movement.data or None, form.subject.data or None,
                form.creation_date.data, form.dimension_H.data, form.dimension_W.data,
                form.dimension_D.data, form.dimension_unit.data, form.weight.data,
                form.weight_unit.data, form.estimated_value.data, form.description.data,
                image_url, form.is_signed.data, form.signature_location.data, artwork_id
            ))
            conn.commit()
            flash(f'Artwork "{form.title.data}" updated successfully!', 'success')
            return redirect(url_for('artworks'))
        except Error as e:
            flash(f'Error updating artwork: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('artwork_form.html', form=form, title='Edit Artwork', artwork=artwork)

# ============= MUSEUMS ROUTES =============
@app.route('/museums')
def museums():
    """List all museums"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('museums.html', museums=[])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM museums ORDER BY name")
    museums_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('museums.html', museums=museums_list)

@app.route('/museums/create', methods=['GET', 'POST'])
def create_museum():
    """Create new museum"""
    form = MuseumForm()
    
    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('museums'))
        
        cursor = conn.cursor()
        website = normalize_url(form.website.data)
        
        try:
            cursor.execute("""
                INSERT INTO museums 
                (name, museum_type, address, city, state_province, country, postal_code,
                 established_date, website, phone, email, description, annual_visitors, admission_fee)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.name.data, form.museum_type.data or None, form.address.data,
                form.city.data, form.state_province.data, form.country.data,
                form.postal_code.data, form.established_date.data, website,
                form.phone.data, form.email.data, form.description.data,
                form.annual_visitors.data, form.admission_fee.data
            ))
            conn.commit()
            flash(f'Museum "{form.name.data}" created successfully!', 'success')
            return redirect(url_for('museums'))
        except Error as e:
            flash(f'Error creating museum: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('museum_form.html', form=form, title='Create Museum')

@app.route('/museums/<int:museum_id>/edit', methods=['GET', 'POST'])
def edit_museum(museum_id):
    """Edit existing museum"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('museums'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM museums WHERE id = %s", (museum_id,))
    museum = cursor.fetchone()
    
    if not museum:
        flash('Museum not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('museums'))
    
    form = MuseumForm(data=museum)
    
    if form.validate_on_submit():
        website = normalize_url(form.website.data)
        
        try:
            cursor.execute("""
                UPDATE museums 
                SET name=%s, museum_type=%s, address=%s, city=%s, state_province=%s,
                    country=%s, postal_code=%s, established_date=%s, website=%s,
                    phone=%s, email=%s, description=%s, annual_visitors=%s, admission_fee=%s
                WHERE id=%s
            """, (
                form.name.data, form.museum_type.data or None, form.address.data,
                form.city.data, form.state_province.data, form.country.data,
                form.postal_code.data, form.established_date.data, website,
                form.phone.data, form.email.data, form.description.data,
                form.annual_visitors.data, form.admission_fee.data, museum_id
            ))
            conn.commit()
            flash(f'Museum "{form.name.data}" updated successfully!', 'success')
            return redirect(url_for('museums'))
        except Error as e:
            flash(f'Error updating museum: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('museum_form.html', form=form, title='Edit Museum', museum=museum)

@app.route('/museums/<int:museum_id>/delete', methods=['POST'])
def delete_museum(museum_id):
    """Delete museum"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('museums'))
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM museums WHERE id = %s", (museum_id,))
        conn.commit()
        flash('Museum deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting museum: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('museums'))

# ============= COLLECTIONS ROUTES =============
@app.route('/collections')
def collections():
    """List all collections"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('collections.html', collections=[])
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, m.name as museum_name, a.title as artwork_title, 
               ar.name as artist_name
        FROM collections c
        LEFT JOIN museums m ON c.museum_id = m.id
        LEFT JOIN artworks a ON c.artwork_id = a.id
        LEFT JOIN artists ar ON a.artist_id = ar.id
        ORDER BY c.id DESC
    """)
    collections_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('collections.html', collections=collections_list)

@app.route('/collections/create', methods=['GET', 'POST'])
def create_collection():
    """Create new collection entry"""
    form = CollectionForm()
    
    # Populate dropdowns
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name FROM museums ORDER BY name")
        museums = cursor.fetchall()
        form.museum_id.choices = [(0, 'Select Museum')] + [(m['id'], m['name']) for m in museums]
        
        cursor.execute("SELECT id, title FROM artworks ORDER BY title")
        artworks = cursor.fetchall()
        form.artwork_id.choices = [(0, 'Select Artwork')] + [(a['id'], a['title']) for a in artworks]
        
        cursor.close()
    
    if form.validate_on_submit():
        if not conn:
            flash('Database connection error', 'error')
            return redirect(url_for('collections'))
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO collections 
                (museum_id, artwork_id, accession_number, acquisition_date, acquisition_method,
                 acquisition_cost, acquisition_details, donor_name, status, gallery_location,
                 on_display, current_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form.museum_id.data, form.artwork_id.data, form.accession_number.data,
                form.acquisition_date.data, form.acquisition_method.data,
                form.acquisition_cost.data, form.acquisition_details.data,
                form.donor_name.data, form.status.data, form.gallery_location.data,
                form.on_display.data, form.current_value.data
            ))
            conn.commit()
            flash('Collection entry created successfully!', 'success')
            return redirect(url_for('collections'))
        except Error as e:
            flash(f'Error creating collection entry: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    if conn:
        conn.close()
    
    return render_template('collection_form.html', form=form, title='Add to Collection')

@app.route('/collections/<int:collection_id>/edit', methods=['GET', 'POST'])
def edit_collection(collection_id):
    """Edit collection entry"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('collections'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM collections WHERE id = %s", (collection_id,))
    collection = cursor.fetchone()
    
    if not collection:
        flash('Collection entry not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('collections'))
    
    form = CollectionForm(data=collection)
    
    # Populate dropdowns
    cursor.execute("SELECT id, name FROM museums ORDER BY name")
    museums = cursor.fetchall()
    form.museum_id.choices = [(m['id'], m['name']) for m in museums]
    
    cursor.execute("SELECT id, title FROM artworks ORDER BY title")
    artworks = cursor.fetchall()
    form.artwork_id.choices = [(a['id'], a['title']) for a in artworks]
    
    if form.validate_on_submit():
        try:
            cursor.execute("""
                UPDATE collections 
                SET museum_id=%s, artwork_id=%s, accession_number=%s, acquisition_date=%s,
                    acquisition_method=%s, acquisition_cost=%s, acquisition_details=%s,
                    donor_name=%s, status=%s, gallery_location=%s, on_display=%s, current_value=%s
                WHERE id=%s
            """, (
                form.museum_id.data, form.artwork_id.data, form.accession_number.data,
                form.acquisition_date.data, form.acquisition_method.data,
                form.acquisition_cost.data, form.acquisition_details.data,
                form.donor_name.data, form.status.data, form.gallery_location.data,
                form.on_display.data, form.current_value.data, collection_id
            ))
            conn.commit()
            flash('Collection entry updated successfully!', 'success')
            return redirect(url_for('collections'))
        except Error as e:
            flash(f'Error updating collection entry: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('collection_form.html', form=form, title='Edit Collection Entry', collection=collection)

@app.route('/collections/<int:collection_id>/delete', methods=['POST'])
def delete_collection(collection_id):
    """Delete collection entry"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('collections'))
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM collections WHERE id = %s", (collection_id,))
        conn.commit()
        flash('Collection entry deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting collection entry: {e}', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('collections'))

# ============= SQL PLAYGROUND =============
@app.route('/sql-playground', methods=['GET', 'POST'])
def sql_playground():
    """Interactive SQL query builder"""
    form = SQLQueryForm()
    results = None
    generated_sql = None
    
    if form.validate_on_submit():
        # Build SQL query
        columns = form.columns.data.strip()
        table = form.table.data
        where = form.where_clause.data.strip()
        order = form.order_by.data.strip()
        limit = form.limit.data or 50
        
        # Build query
        query = f"SELECT {columns} FROM {table}"
        
        if where:
            query += f" WHERE {where}"
        if order:
            query += f" ORDER BY {order}"
        query += f" LIMIT {limit}"
        
        generated_sql = query
        
        # Execute query
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                flash(f'Query returned {len(results)} results', 'success')
            except Error as e:
                flash(f'SQL Error: {e}', 'error')
            finally:
                cursor.close()
                conn.close()
    
    return render_template('sql_playground.html', form=form, results=results, sql=generated_sql)

# ============= EXPORT =============
@app.route('/export/<table_name>')
def export_csv(table_name):
    """Export table data as CSV"""
    allowed_tables = ['artists', 'artworks', 'museums', 'collections']
    
    if table_name not in allowed_tables:
        flash('Invalid table name', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        flash('No data to export', 'error')
        return redirect(url_for(table_name))
    
    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    
    # Convert to bytes
    output.seek(0)
    
    cursor.close()
    conn.close()
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{table_name}_export.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
