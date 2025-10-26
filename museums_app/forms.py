from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, DecimalField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional, URL, Length, NumberRange

class ArtistForm(FlaskForm):
    name = StringField('Artist Name', validators=[DataRequired(), Length(max=200)])
    birth_date = DateField('Birth Date', validators=[Optional()], format='%Y-%m-%d')
    death_date = DateField('Death Date', validators=[Optional()], format='%Y-%m-%d')
    is_living = BooleanField('Currently Living')
    birth_place = StringField('Birth Place', validators=[Optional(), Length(max=100)])
    death_place = StringField('Death Place', validators=[Optional(), Length(max=100)])
    nationality = StringField('Nationality', validators=[Optional(), Length(max=100)])
    
    art_movement = SelectField('Art Movement', choices=[
        ('', 'Select Movement'),
        ('Renaissance', 'Renaissance'),
        ('Baroque', 'Baroque'),
        ('Rococo', 'Rococo'),
        ('Neoclassicism', 'Neoclassicism'),
        ('Romanticism', 'Romanticism'),
        ('Realism', 'Realism'),
        ('Impressionism', 'Impressionism'),
        ('Post-Impressionism', 'Post-Impressionism'),
        ('Expressionism', 'Expressionism'),
        ('Cubism', 'Cubism'),
        ('Surrealism', 'Surrealism'),
        ('Abstract Expressionism', 'Abstract Expressionism'),
        ('Pop Art', 'Pop Art'),
        ('Minimalism', 'Minimalism'),
        ('Contemporary', 'Contemporary'),
        ('Modern', 'Modern'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    primary_medium = SelectField('Primary Medium', choices=[
        ('', 'Select Medium'),
        ('Painting', 'Painting'),
        ('Sculpture', 'Sculpture'),
        ('Drawing', 'Drawing'),
        ('Printmaking', 'Printmaking'),
        ('Photography', 'Photography'),
        ('Mixed Media', 'Mixed Media'),
        ('Digital Art', 'Digital Art'),
        ('Installation', 'Installation'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    bio = TextAreaField('Biography', validators=[Optional()])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=255)])
    image_url = StringField('Portrait URL', validators=[Optional(), URL(), Length(max=255)])
    instagram = StringField('Instagram Handle', validators=[Optional(), Length(max=100)])

class ArtworkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    artist_id = SelectField('Artist', coerce=int, validators=[DataRequired()])
    medium = StringField('Medium', validators=[Optional(), Length(max=100)])
    
    art_movement = SelectField('Art Movement', choices=[
        ('', 'Select Movement'),
        ('Renaissance', 'Renaissance'),
        ('Baroque', 'Baroque'),
        ('Impressionism', 'Impressionism'),
        ('Post-Impressionism', 'Post-Impressionism'),
        ('Contemporary', 'Contemporary'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    subject = SelectField('Subject', choices=[
        ('', 'Select Subject'),
        ('Portrait', 'Portrait'),
        ('Landscape', 'Landscape'),
        ('Still Life', 'Still Life'),
        ('Abstract', 'Abstract'),
        ('Religious', 'Religious'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    creation_date = DateField('Creation Date', validators=[Optional()], format='%Y-%m-%d')
    
    dimension_H = DecimalField('Height', validators=[Optional(), NumberRange(min=0)], places=2)
    dimension_W = DecimalField('Width', validators=[Optional(), NumberRange(min=0)], places=2)
    dimension_D = DecimalField('Depth', validators=[Optional(), NumberRange(min=0)], places=2)
    
    dimension_unit = SelectField('Unit', choices=[
        ('inches', 'Inches'),
        ('cm', 'Centimeters'),
        ('meters', 'Meters'),
        ('feet', 'Feet')
    ], default='inches')
    
    weight = DecimalField('Weight', validators=[Optional(), NumberRange(min=0)], places=2)
    weight_unit = SelectField('Weight Unit', choices=[
        ('lbs', 'Pounds'),
        ('kg', 'Kilograms'),
        ('grams', 'Grams')
    ], default='lbs')
    
    estimated_value = DecimalField('Estimated Value ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional(), URL(), Length(max=255)])
    is_signed = BooleanField('Signed')
    signature_location = StringField('Signature Location', validators=[Optional(), Length(max=100)])

class MuseumForm(FlaskForm):
    name = StringField('Museum Name', validators=[DataRequired(), Length(max=100)])
    
    museum_type = SelectField('Type', choices=[
        ('', 'Select Type'),
        ('Art', 'Art Museum'),
        ('History', 'History Museum'),
        ('Science', 'Science Museum'),
        ('Natural History', 'Natural History Museum'),
        ('Modern Art', 'Modern Art Museum'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state_province = StringField('State/Province', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    
    established_date = DateField('Established Date', validators=[Optional()], format='%Y-%m-%d')
    website = StringField('Website', validators=[Optional(), URL(), Length(max=200)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    
    annual_visitors = IntegerField('Annual Visitors', validators=[Optional(), NumberRange(min=0)])
    admission_fee = DecimalField('Admission Fee ($)', validators=[Optional(), NumberRange(min=0)], places=2)

class CollectionForm(FlaskForm):
    museum_id = SelectField('Museum', coerce=int, validators=[DataRequired()])
    artwork_id = SelectField('Artwork', coerce=int, validators=[DataRequired()])
    accession_number = StringField('Accession Number', validators=[Optional(), Length(max=50)])
    
    acquisition_date = DateField('Acquisition Date', validators=[Optional()], format='%Y-%m-%d')
    
    acquisition_method = SelectField('Acquisition Method', choices=[
        ('Purchase', 'Purchase'),
        ('Donation', 'Donation'),
        ('Bequest', 'Bequest'),
        ('Exchange', 'Exchange'),
        ('Commission', 'Commission'),
        ('Transfer', 'Transfer')
    ], validators=[DataRequired()])
    
    acquisition_cost = DecimalField('Acquisition Cost ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    acquisition_details = TextAreaField('Acquisition Details', validators=[Optional()])
    donor_name = StringField('Donor Name', validators=[Optional(), Length(max=200)])
    
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('On Loan', 'On Loan'),
        ('In Conservation', 'In Conservation'),
        ('Storage', 'Storage'),
        ('Deaccessioned', 'Deaccessioned')
    ], default='Active')
    
    gallery_location = StringField('Gallery Location', validators=[Optional(), Length(max=100)])
    on_display = BooleanField('Currently on Display', default=False)
    
    current_value = DecimalField('Current Value ($)', validators=[Optional(), NumberRange(min=0)], places=2)

class SQLQueryForm(FlaskForm):
    table = SelectField('Table', choices=[
        ('artists', 'Artists'),
        ('artworks', 'Artworks'),
        ('museums', 'Museums'),
        ('collections', 'Collections')
    ], validators=[DataRequired()])
    
    columns = StringField('Columns (comma-separated, or * for all)', 
                         default='*', 
                         validators=[DataRequired()])
    
    where_clause = StringField('WHERE condition (optional)', validators=[Optional()])
    order_by = StringField('ORDER BY (optional)', validators=[Optional()])
    limit = IntegerField('LIMIT', default=50, validators=[Optional(), NumberRange(min=1, max=1000)])
