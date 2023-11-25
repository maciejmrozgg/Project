from flask import Flask, render_template, redirect, url_for, request, abort, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'MVCProject'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    numberOfLogins = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '%r: %r: %r: %r' % (self.email, self.password, self.firstName, self.lastName, self.numberOfLogins)

class Mushroom(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imgURL = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    kingdom = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    family = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '%r: %r' % (self.name, self.kingdom)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    log = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if password == user.password:
                try:
                    session['login'] = email
                    user.numberOfLogins+=1
                    db.session.merge(user)
                    db.session.commit()
                    return redirect(url_for('home'))
                except:
                    log = 'Wrong email or password'
    return render_template('login.html', log=log)

@app.route('/register', methods = ['GET','POST'])
def register():
    log = ''
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        try:
            new = User(email=email, password=password, firstName=firstName, lastName=lastName)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            log = 'Register error!'
            db.session.rollback()
    return render_template('register.html', log=log)

@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    user = User.query.filter_by(email=session['login']).first()
    return render_template('profile.html', user=user)

@app.route('/editProfile', methods = ['GET','POST'])
def editProfile():
    log = ''
    userToEdit = User.query.filter_by(email=session['login']).first()
    if userToEdit is None:
        abort(404)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        
        try:
            userToEdit.email = email
            userToEdit.password = password
            userToEdit.firstName = firstName
            userToEdit.lastName = lastName
            
            db.session.merge(userToEdit)
            db.session.commit()
            return redirect(url_for('profile'))
        except:
            log = 'Edit error!'
            db.session.rollback()
    return render_template('editProfile.html', user=userToEdit, log=log)

@app.route('/deleteProfile')
def deleteProfile():
    userToDelete = User.query.filter_by(email=session['login']).first()
    if userToDelete is None:
        abort(404)
    db.session.delete(userToDelete)
    db.session.commit()
    session.pop('login', None)
    return redirect(url_for('home'))

@app.route('/topUsers')
def topUsers():
    users = User.query.order_by(User.numberOfLogins.desc()).limit(3).all()
    return render_template('topUsers.html', users=users)

@app.route('/mushrooms')
def mushrooms():
    mushrooms=Mushroom.query.all()
    return render_template('mushrooms.html', mushrooms=mushrooms)

@app.route('/mushroomsadd', methods = ['GET','POST'])
def addMushroom():
    if(session['login'] == "admin@test.pl"):
        if request.method =='POST':
            imgURL = request.form['imgURL']
            name = request.form['name']
            kingdom = request.form['kingdom']
            color = request.form['color']
            family = request.form['family']
            species = request.form['species']
            
            try:
                new = Mushroom(imgURL = imgURL, name = name, kingdom=kingdom, color=color, family=family, species=species)
                db.session.add(new)
                db.session.commit()
                return redirect(url_for('mushrooms'))
            except:
                db.session.rollback()
        return render_template('addMushroom.html')
    else:
        return redirect(url_for('home'))

@app.route('/mushroom/details/<int:id>')
def mushroom(id):
    mushroom = Mushroom.query.get(id)
    return render_template('mushroomdetails.html', mushroom=mushroom)

@app.route('/mushroomsedit/<int:id>', methods = ['GET','POST'])
def editMushroom(id):
    if(session['login'] == "admin@test.pl"):
        mushroomToEdit = Mushroom.query.get(id)
        if mushroomToEdit is None:
            abort(404)
        if request.method == 'POST':
            imgURL = request.form['imgURL']
            name = request.form['name']
            kingdom = request.form['kingdom']
            color = request.form['color']
            family = request.form['family']
            species = request.form['species']
            
            try:
                mushroomToEdit.imgURL = imgURL
                mushroomToEdit.name = name
                mushroomToEdit.kingdom = kingdom
                mushroomToEdit.color = color
                mushroomToEdit.family = family
                mushroomToEdit.species = species
                
                db.session.merge(mushroomToEdit)
                db.session.commit()
                return redirect(url_for('mushrooms'))
            except:
                db.session.rollback()
        return render_template('editMushroom.html', mushroom=mushroomToEdit)
    else:
        return redirect(url_for('home'))

@app.route('/mushroomdelete/<int:id>')
def deleteMushroom(id):
    if(session['login'] == "admin@test.pl"):
        mushroomToDelete = Mushroom.query.get(id)
        if mushroomToDelete is None:
            abort(404)
        db.session.delete(mushroomToDelete)
        db.session.commit()
        return redirect(url_for('mushrooms'))
    else:
        return redirect(url_for('home'))

db.drop_all()
db.create_all()

admin = User(email = "admin@test.pl", password = "admin", firstName = "admin", lastName = "admin")
db.session.add(admin)

mushroom1 = Mushroom(imgURL = 'https://www.tapeciarnia.pl/tapety/normalne/tapeta-trzy-borowiki-szlachetne.jpg', name = 'borowik szlachetny' , kingdom = 'grzyby', color = 'brazowy', family = 'borowikowate', species = 'borowik szlachetny')
mushroom2 = Mushroom(imgURL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Cantharellus_cibarius_20090717-02.jpg/240px-Cantharellus_cibarius_20090717-02.jpg', name = 'pieprznik jadalny' , kingdom = 'grzyby', color = 'zolty', family = 'kolczakowate', species = 'pieprznik jadalny')
mushroom3 = Mushroom(imgURL = 'https://ocdn.eu/pulscms-transforms/1/Lqbk9kpTURBXy81NTk2NmQwOTQzNzE0OGE4Y2E2ZjE0ZmMyYTI5MzRlMi5qcGeRlQLNAfQAwsOBoTAB', name = 'podgrzyb brunatny' , kingdom = 'grzyby', color = 'brazowy', family = 'borowikowate', species = 'podgrzyb brunatny')
mushroom4 = Mushroom(imgURL = 'https://upload.wikimedia.org/wikipedia/commons/4/44/Leccinum_scabrum_G3.1.jpg', name = 'kozlarz babka' , kingdom = 'grzyby', color = 'brazowy', family = 'borowikowate', species = 'kozlarz babka')
mushroom5 = Mushroom(imgURL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Leccinum_aurantiacum_G4.JPG/1280px-Leccinum_aurantiacum_G4.JPG', name = 'kozlarz czerwony' , kingdom = 'grzyby', color = 'pomaranczowy', family = 'borowikowate', species = 'kozlarz czerwony')
mushroom6 = Mushroom(imgURL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Macrolepiota-procera.jpg/800px-Macrolepiota-procera.jpg', name = 'czubajka kania' , kingdom = 'grzyby', color = 'bialy', family = 'pieczarkowate', species = 'czubajka kania')
mushroom7 = Mushroom(imgURL = 'https://ogrodnik24.pl/userdata/public/gfx/43953.jpg', name = 'maslak zwyczajny' , kingdom = 'grzyby', color = 'brazowy', family = 'maslakowate', species = 'maslak zwyczajny')
mushroom8 = Mushroom(imgURL = 'https://zasoby.ekologia.pl/artykulyNew/25862/xxl/shutterstock-158119619_800x600.jpg', name = 'Agaricus-pieczarka', kingdom = 'grzyby', color = 'biały', family = 'pieczarkowate', species = 'pieczarka')
db.session.add(mushroom1)
db.session.add(mushroom2)
db.session.add(mushroom3)
db.session.add(mushroom4)
db.session.add(mushroom5)
db.session.add(mushroom6)
db.session.add(mushroom7)
db.session.add(mushroom8)
db.session.commit()