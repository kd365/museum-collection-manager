import logging
import csv
import io
import re
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, send_file, jsonify, abort)
from flask_login import login_user, logout_user, login_required, current_user
from config import config
from extensions import db, migrate, login_manager
from forms import (ArtistForm, ArtworkForm, MuseumForm, CollectionForm,
                   SQLQueryForm, LoginForm, RegistrationForm)

logger = logging.getLogger(__name__)


def admin_required(f):
    """Decorator that requires the user to be logged in AND an admin."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required for this action.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        import os
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    logging.getLogger('ai_service').addHandler(handler)

    # Import models so they're registered with SQLAlchemy
    from models import User, Artist, Artwork, Museum, Collection

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Create tables on first run
    with app.app_context():
        db.create_all()

    # --- Helpers ---

    def normalize_url(url):
        if not url:
            return None
        url = url.strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    # --- Auth Routes ---

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered.', 'error')
                return render_template('register.html', form=form)
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already taken.', 'error')
                return render_template('register.html', form=form)
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            logger.info(f"New user registered: {form.username.data}")
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'Welcome back, {user.username}!', 'success')
                logger.info(f"User logged in: {user.username}")
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            flash('Invalid email or password.', 'error')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logger.info(f"User logged out: {current_user.username}")
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    # --- Home ---

    @app.route('/')
    def index():
        stats = {
            'artists': Artist.query.count(),
            'artworks': Artwork.query.count(),
            'museums': Museum.query.count(),
            'collections': Collection.query.count(),
            'recent_artworks': (
                Artwork.query
                .outerjoin(Artist)
                .order_by(Artwork.created_at.desc())
                .limit(6)
                .all()
            )
        }
        return render_template('index.html', stats=stats)

    # --- Artists ---

    @app.route('/artists')
    def artists():
        page = request.args.get('page', 1, type=int)
        pagination = Artist.query.order_by(Artist.name).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        return render_template('artists.html', pagination=pagination)

    @app.route('/artists/create', methods=['GET', 'POST'])
    @admin_required
    def create_artist():
        form = ArtistForm()
        if form.validate_on_submit():
            artist = Artist(
                name=form.name.data,
                birth_date=form.birth_date.data,
                death_date=form.death_date.data,
                is_living=form.is_living.data,
                birth_place=form.birth_place.data,
                death_place=form.death_place.data,
                nationality=form.nationality.data,
                art_movement=form.art_movement.data or None,
                primary_medium=form.primary_medium.data or None,
                bio=form.bio.data,
                website=normalize_url(form.website.data),
                image_url=normalize_url(form.image_url.data),
                instagram=form.instagram.data,
            )
            db.session.add(artist)
            db.session.commit()
            flash(f'Artist "{artist.name}" created successfully!', 'success')
            logger.info(f"Artist created: {artist.name} (id={artist.id})")
            return redirect(url_for('artists'))
        return render_template('artist_form.html', form=form, title='Create Artist')

    @app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_artist(artist_id):
        artist = db.session.get(Artist, artist_id)
        if not artist:
            flash('Artist not found', 'error')
            return redirect(url_for('artists'))
        form = ArtistForm(obj=artist)
        if form.validate_on_submit():
            form.populate_obj(artist)
            artist.website = normalize_url(artist.website)
            artist.image_url = normalize_url(artist.image_url)
            artist.art_movement = artist.art_movement or None
            artist.primary_medium = artist.primary_medium or None
            db.session.commit()
            flash(f'Artist "{artist.name}" updated successfully!', 'success')
            return redirect(url_for('artists'))
        return render_template('artist_form.html', form=form, title='Edit Artist', artist=artist)

    @app.route('/artists/<int:artist_id>/delete', methods=['POST'])
    @admin_required
    def delete_artist(artist_id):
        artist = db.session.get(Artist, artist_id)
        if artist:
            db.session.delete(artist)
            db.session.commit()
            flash('Artist deleted successfully!', 'success')
            logger.info(f"Artist deleted: id={artist_id}")
        return redirect(url_for('artists'))

    # --- Artworks ---

    @app.route('/artworks')
    def artworks():
        page = request.args.get('page', 1, type=int)
        pagination = (
            Artwork.query
            .outerjoin(Artist)
            .order_by(Artwork.title)
            .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        )
        return render_template('artworks.html', pagination=pagination)

    @app.route('/artworks/create', methods=['GET', 'POST'])
    @admin_required
    def create_artwork():
        form = ArtworkForm()
        form.artist_id.choices = [(0, 'Select Artist')] + [
            (a.id, a.name) for a in Artist.query.order_by(Artist.name).all()
        ]
        if form.validate_on_submit():
            artwork = Artwork(
                title=form.title.data,
                artist_id=form.artist_id.data,
                medium=form.medium.data,
                art_movement=form.art_movement.data or None,
                subject=form.subject.data or None,
                creation_date=form.creation_date.data,
                dimension_H=form.dimension_H.data,
                dimension_W=form.dimension_W.data,
                dimension_D=form.dimension_D.data,
                dimension_unit=form.dimension_unit.data,
                weight=form.weight.data,
                weight_unit=form.weight_unit.data,
                estimated_value=form.estimated_value.data,
                description=form.description.data,
                image_url=normalize_url(form.image_url.data),
                is_signed=form.is_signed.data,
                signature_location=form.signature_location.data,
            )
            db.session.add(artwork)
            db.session.commit()
            flash(f'Artwork "{artwork.title}" created successfully!', 'success')
            logger.info(f"Artwork created: {artwork.title} (id={artwork.id})")
            return redirect(url_for('artworks'))
        return render_template('artwork_form.html', form=form, title='Create Artwork')

    @app.route('/artworks/<int:artwork_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_artwork(artwork_id):
        artwork = db.session.get(Artwork, artwork_id)
        if not artwork:
            flash('Artwork not found', 'error')
            return redirect(url_for('artworks'))
        form = ArtworkForm(obj=artwork)
        form.artist_id.choices = [
            (a.id, a.name) for a in Artist.query.order_by(Artist.name).all()
        ]
        if form.validate_on_submit():
            form.populate_obj(artwork)
            artwork.image_url = normalize_url(artwork.image_url)
            artwork.art_movement = artwork.art_movement or None
            artwork.subject = artwork.subject or None
            db.session.commit()
            flash(f'Artwork "{artwork.title}" updated successfully!', 'success')
            return redirect(url_for('artworks'))
        return render_template('artwork_form.html', form=form, title='Edit Artwork', artwork=artwork)

    @app.route('/artworks/<int:artwork_id>/delete', methods=['POST'])
    @admin_required
    def delete_artwork(artwork_id):
        artwork = db.session.get(Artwork, artwork_id)
        if artwork:
            db.session.delete(artwork)
            db.session.commit()
            flash('Artwork deleted successfully!', 'success')
            logger.info(f"Artwork deleted: id={artwork_id}")
        return redirect(url_for('artworks'))

    @app.route('/artworks/<int:artwork_id>/generate-description', methods=['POST'])
    @admin_required
    def generate_artwork_description(artwork_id):
        from ai_service import generate_artwork_description as gen_desc
        artwork = db.session.get(Artwork, artwork_id)
        if not artwork:
            return jsonify({'error': 'Artwork not found'}), 404
        description = gen_desc(artwork)
        if description:
            artwork.ai_description = description
            db.session.commit()
            flash('AI description generated!', 'success')
            logger.info(f"AI description generated for artwork id={artwork_id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'description': description})
        else:
            flash('Failed to generate description. Check AWS credentials.', 'error')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Generation failed'}), 500
        return redirect(url_for('artworks'))

    # --- Museums ---

    @app.route('/museums')
    def museums():
        page = request.args.get('page', 1, type=int)
        pagination = Museum.query.order_by(Museum.name).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        return render_template('museums.html', pagination=pagination)

    @app.route('/museums/create', methods=['GET', 'POST'])
    @admin_required
    def create_museum():
        form = MuseumForm()
        if form.validate_on_submit():
            museum = Museum(
                name=form.name.data,
                museum_type=form.museum_type.data or None,
                address=form.address.data,
                city=form.city.data,
                state_province=form.state_province.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                established_date=form.established_date.data,
                website=normalize_url(form.website.data),
                phone=form.phone.data,
                email=form.email.data,
                description=form.description.data,
                annual_visitors=form.annual_visitors.data,
                admission_fee=form.admission_fee.data,
            )
            db.session.add(museum)
            db.session.commit()
            flash(f'Museum "{museum.name}" created successfully!', 'success')
            logger.info(f"Museum created: {museum.name} (id={museum.id})")
            return redirect(url_for('museums'))
        return render_template('museum_form.html', form=form, title='Create Museum')

    @app.route('/museums/<int:museum_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_museum(museum_id):
        museum = db.session.get(Museum, museum_id)
        if not museum:
            flash('Museum not found', 'error')
            return redirect(url_for('museums'))
        form = MuseumForm(obj=museum)
        if form.validate_on_submit():
            form.populate_obj(museum)
            museum.website = normalize_url(museum.website)
            museum.museum_type = museum.museum_type or None
            db.session.commit()
            flash(f'Museum "{museum.name}" updated successfully!', 'success')
            return redirect(url_for('museums'))
        return render_template('museum_form.html', form=form, title='Edit Museum', museum=museum)

    @app.route('/museums/<int:museum_id>/delete', methods=['POST'])
    @admin_required
    def delete_museum(museum_id):
        museum = db.session.get(Museum, museum_id)
        if museum:
            db.session.delete(museum)
            db.session.commit()
            flash('Museum deleted successfully!', 'success')
            logger.info(f"Museum deleted: id={museum_id}")
        return redirect(url_for('museums'))

    # --- Collections ---

    @app.route('/collections')
    def collections():
        page = request.args.get('page', 1, type=int)
        pagination = (
            Collection.query
            .join(Museum)
            .join(Artwork)
            .outerjoin(Artist, Artwork.artist_id == Artist.id)
            .order_by(Collection.id.desc())
            .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
        )
        return render_template('collections.html', pagination=pagination)

    @app.route('/collections/create', methods=['GET', 'POST'])
    @admin_required
    def create_collection():
        form = CollectionForm()
        form.museum_id.choices = [(0, 'Select Museum')] + [
            (m.id, m.name) for m in Museum.query.order_by(Museum.name).all()
        ]
        form.artwork_id.choices = [(0, 'Select Artwork')] + [
            (a.id, a.title) for a in Artwork.query.order_by(Artwork.title).all()
        ]
        if form.validate_on_submit():
            collection = Collection(
                museum_id=form.museum_id.data,
                artwork_id=form.artwork_id.data,
                accession_number=form.accession_number.data,
                acquisition_date=form.acquisition_date.data,
                acquisition_method=form.acquisition_method.data,
                acquisition_cost=form.acquisition_cost.data,
                acquisition_details=form.acquisition_details.data,
                donor_name=form.donor_name.data,
                status=form.status.data,
                gallery_location=form.gallery_location.data,
                on_display=form.on_display.data,
                current_value=form.current_value.data,
            )
            db.session.add(collection)
            db.session.commit()
            flash('Collection entry created successfully!', 'success')

            # Auto-generate collection description if museum has 5+ artworks
            museum = db.session.get(Museum, form.museum_id.data)
            if museum:
                artwork_count = Collection.query.filter_by(museum_id=museum.id).count()
                if artwork_count >= 5 and not museum.ai_collection_description:
                    from ai_service import generate_collection_description
                    museum_artworks = [
                        c.artwork for c in
                        Collection.query.filter_by(museum_id=museum.id).all()
                    ]
                    desc = generate_collection_description(museum, museum_artworks)
                    if desc:
                        museum.ai_collection_description = desc
                        db.session.commit()
                        flash('AI collection description auto-generated!', 'success')

            return redirect(url_for('collections'))
        return render_template('collection_form.html', form=form, title='Add to Collection')

    @app.route('/collections/<int:collection_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_collection(collection_id):
        collection = db.session.get(Collection, collection_id)
        if not collection:
            flash('Collection entry not found', 'error')
            return redirect(url_for('collections'))
        form = CollectionForm(obj=collection)
        form.museum_id.choices = [
            (m.id, m.name) for m in Museum.query.order_by(Museum.name).all()
        ]
        form.artwork_id.choices = [
            (a.id, a.title) for a in Artwork.query.order_by(Artwork.title).all()
        ]
        if form.validate_on_submit():
            form.populate_obj(collection)
            db.session.commit()
            flash('Collection entry updated successfully!', 'success')
            return redirect(url_for('collections'))
        return render_template('collection_form.html', form=form,
                             title='Edit Collection Entry', collection=collection)

    @app.route('/collections/<int:collection_id>/delete', methods=['POST'])
    @admin_required
    def delete_collection(collection_id):
        collection = db.session.get(Collection, collection_id)
        if collection:
            db.session.delete(collection)
            db.session.commit()
            flash('Collection entry deleted successfully!', 'success')
        return redirect(url_for('collections'))

    # --- SQL Playground (secured) ---

    ALLOWED_TABLES = {'artists', 'artworks', 'museums', 'collections'}
    ALLOWED_OPERATORS = {'=', '!=', '>', '<', '>=', '<=', 'LIKE'}
    COLUMN_PATTERN = re.compile(r'^[a-zA-Z_*]+$')

    @app.route('/sql-playground', methods=['GET', 'POST'])
    @login_required
    def sql_playground():
        form = SQLQueryForm()
        results = None
        generated_sql = None

        if form.validate_on_submit():
            table = form.table.data
            columns = form.columns.data.strip()

            # Validate table
            if table not in ALLOWED_TABLES:
                flash('Invalid table name', 'error')
                return render_template('sql_playground.html', form=form)

            # Validate columns
            col_list = [c.strip() for c in columns.split(',')]
            if not all(COLUMN_PATTERN.match(c) for c in col_list):
                flash('Invalid column names. Use only letters, underscores, or *.', 'error')
                return render_template('sql_playground.html', form=form)

            # Build parameterized query
            query = f"SELECT {columns} FROM {table}"
            params = []

            where_col = form.where_column.data
            where_op = form.where_operator.data
            where_val = form.where_value.data

            if where_col and where_op and where_val is not None:
                if not COLUMN_PATTERN.match(where_col):
                    flash(f'Invalid WHERE column: {where_col}', 'error')
                    return render_template('sql_playground.html', form=form)
                if where_op not in ALLOWED_OPERATORS:
                    flash(f'Invalid operator: {where_op}', 'error')
                    return render_template('sql_playground.html', form=form)
                query += f" WHERE {where_col} {where_op} :val"
                params.append(where_val)

            order = form.order_by.data.strip() if form.order_by.data else ''
            if order and re.match(r'^[a-zA-Z_]+(\s+(ASC|DESC))?$', order, re.IGNORECASE):
                query += f" ORDER BY {order}"

            limit = form.limit.data or 50
            query += f" LIMIT {limit}"

            generated_sql = query.replace(':val', repr(where_val)) if params else query

            try:
                if params:
                    result = db.session.execute(
                        db.text(query),
                        {'val': params[0]}
                    )
                else:
                    result = db.session.execute(db.text(query))
                results = [dict(row._mapping) for row in result]
                flash(f'Query returned {len(results)} results', 'success')
            except Exception as e:
                flash(f'SQL Error: {e}', 'error')
                logger.warning(f"SQL Playground error: {e}")

        return render_template('sql_playground.html', form=form,
                             results=results, sql=generated_sql)

    # --- API: table columns for SQL Playground ---

    @app.route('/api/table-columns/<table_name>')
    @login_required
    def table_columns(table_name):
        model_map = {
            'artists': Artist, 'artworks': Artwork,
            'museums': Museum, 'collections': Collection
        }
        model = model_map.get(table_name)
        if not model:
            return jsonify([])
        columns = [c.name for c in model.__table__.columns]
        return jsonify(columns)

    # --- Export ---

    @app.route('/export/<table_name>')
    @login_required
    def export_csv(table_name):
        if table_name not in ALLOWED_TABLES:
            flash('Invalid table name', 'error')
            return redirect(url_for('index'))

        model_map = {
            'artists': Artist, 'artworks': Artwork,
            'museums': Museum, 'collections': Collection
        }
        model = model_map[table_name]
        rows = model.query.all()

        if not rows:
            flash('No data to export', 'error')
            return redirect(url_for(table_name))

        # Get column names from model
        col_names = [c.name for c in model.__table__.columns]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=col_names)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: getattr(row, c) for c in col_names})

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_export.csv'
        )

    # --- Test ---

    @app.route('/test')
    def test():
        return "<h1>Hello World!</h1><p>Flask is working!</p>"

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5001, debug=True)
