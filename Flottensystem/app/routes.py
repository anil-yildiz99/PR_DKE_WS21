from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, RegistrationFormZugpersonal, EmptyForm, EditProfileForm, \
    EditProfileFormZugpersonal, TriebwagenForm, PersonenwagenForm, EditTriebwagenForm, EditPersonenwagenForm, \
    ZugForm, EditZugForm
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator, Wagen, Triebwagen, Personenwagen, \
    Zug


@app.route('/')
@app.route('/Startseite')
def home():
    if current_user.is_authenticated:   # Falls der Benutzer schon angemeldet ist, wird dieser in die jeweilige Seite weitergeleitet
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            next_page = url_for('home_admin')
        else:
            next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('home.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Admin')
@login_required
def home_admin():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird kontrolliert, ob der angemeldete Benutzer kein Administrator ist. Ist dies der Fall, wird dieser in die Personalseite weitergeleitet (wo man auch keine Administratorrechte hat)
        flash('Sie müssen als Administrator angemeldet sein, um in die Administrator-Startseite zu gelangen!')  # Anschließend wird diese Meldung mitgegeben, um den Benutzer darüber zu informieren, warum dieser nicht auf diese Webseite zugreifen kann
        return redirect(url_for('home_personal'))
    return render_template('home_administrator.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Personal')
@login_required
def home_personal():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None: # Falls es sich beim angemeldet User um einen Administrator handelt, wird dieser in die Administrator-Startseite weitergeleitet
        flash('Sie sind als Administrator angemeldet!')
        return redirect(url_for('home_admin'))
    return render_template('home_personal.html', title='Startseite - Flotteninformationssystem')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:   # Ist der Nutzer schon angemeldet, dann hat dieser keinen Zugriff auf die Login-Webseite und wird entsprechend weitergeleitet
        if Administrator.query.filter(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            return redirect(url_for('home_admin'))
        else:
            return redirect(url_for('home_personal'))
    form = LoginForm()
    if form.validate_on_submit():   # Drückt man beim Login auf den Submit-Button, dann ist diese Bedingung True
        user = Mitarbeiter.query.filter_by(email=form.email.data).first()   # Es wird über die gesamte Mitarbeitertabelle hinweg die eingegebene Email Adresse gesucht
        if user is None or not user.check_password(form.passwort.data): # Falls kein User unter der angegebenen Email Adresse gefunden wurde oder das Passwort vom User falsch eingegeben wurde, dann wird die folgende Fehlermeldung ausgegeben und der Benutzer muss sich nochmal anmelden
            flash('Email bzw. Passwort ungültig!')
            return redirect(url_for('login'))
        login_user(user, remember=form.angemeldet_bleiben.data) # Das Login wird durchgeführt und es wird sich auch gemerkt, ob die Checkbox "angemeldet_bleiben" angekreuzt worden ist
        next_page = request.args.get('next')    # Wurde ein Benutzer von einer anderen Seite in das Login weitergeleitet, so wird diese vorherige Seite (auf die man zugreifen wollte) in next_page gespeichert
        if not next_page or url_parse(next_page).netloc != '':
            if Administrator.query.filter_by(mitarbeiterNr=user.mitarbeiterNr).first() is not None:
                next_page = url_for('home_admin')
            else:
                next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('login.html', title='Anmelden', form=form)

    
@app.route('/logout')
def logout():
    logout_user()   # Hier wird der User ausgeloggt und in die Startseite weitergeleitet
    return redirect(url_for('home'))


@app.route('/register')
@login_required
def register():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird überprüft, ob ein Administrator auf diese Webseite zugreift. ist dies nicht der Fall, wird der User in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    return render_template('register.html', title='Benutzer erstellen')


@app.route('/registerUser/<name>', methods=['GET', 'POST'])
@login_required
def registerUser(name):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird überprüft, ob ein Administrator auf diese Webseite zugreift. ist dies nicht der Fall, wird der User in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    if name == 'Zugpersonal':   # Es wird überprüft, ob im übergebenen Parameter 'name' 'Zugpersonal' eingetragen ist. Ist dies der Fall wird ein Formular für das Zugpersonal verwendet der eine kleine Abweichung im Unterschied zu den anderen Mitarbeitern enthält
        form = RegistrationFormZugpersonal()
        ''' Als nächstes werden die Zugnummern dynamisch dem SelectField "zugNr" übergeben. Auch der User sieht bei der Beschriftung die Zugnummer
            (rechter Ausruck von (z.nr, z.nr)). Hier wird dem User bewusst nicht der Name des Zuges (also (z.nr, z.name)) angezeigt, da Zugnamen 
            redundant sein können und der User somit nicht wissen kann, welches Feld im SelectField nun das gewünschte ist. Als Beispiel kann man
            den Zugnamen Railjet nehmen: Es gibt Railjet Züge mit unterschiedlichen Zugnummern (z.B.: RJX 368, RJX 660, usw.). Jedoch haben all
            diese Zugnummern den gleichen Zugnamen, nämlich "Railjet". Würde man somit dem User beim SelectField den Zugnamen anzeigen (also indem 
            man in der nachfolgenden Zeile (z.nr, z.name) eingibt), dann würde nur "Railjet" stehen und der User wüsste dadurch nicht, welches sein 
            gewünschter Zug ist. '''
        form.zugNr.choices = [(z.nr, z.nr) for z in Zug.query.all()]
    else:   # Ist im Parameter 'name' nicht 'Zugpersonal' eingetragen, so wird das andere Formular für die Registrierung eines Users verwendet
    	form = RegistrationForm()
    if form.validate_on_submit():
        if name == 'Administrator':
            user = Administrator(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        elif name == 'Wartungspersonal':
            user = Wartungspersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        elif name == 'Zugpersonal':
            user = Zugpersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data, berufsbezeichnung=form.berufsbezeichnung.data, zugNr=form.zugNr.data)
        user.set_password(form.passwort.data)
        db.session.add(user)
        db.session.commit() # Hier werden die Daten persistiert
        flash('Benutzer wurde erfolgreich erstellt!')
        return redirect(url_for('register'))
    return render_template('register_user.html', title=name + ' erstellen', form=form, typ=name)


@app.route('/User_bearbeiten')
@login_required
def updateUser():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wartungspersonal = Wartungspersonal.query.all()
    zugpersonal = Zugpersonal.query.all()
    form = EmptyForm()
    return render_template('user.html', wartungspersonal=wartungspersonal, zugpersonal=zugpersonal, form=form)  # Wartungs- und Zugpersonal werden auch übergeben, um diese nachfolgend auf der Webseite darzustellen
    
    
@app.route('/User_bearbeiten/<mitarbeiterNr>', methods=['GET', 'POST'])
@login_required
def editUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
    if user is None:    # Wird unter der übergebenen Mitarbeiternummer kein User gefunden, so wird der Benutzer darüber informiert
        flash('Es wurde kein Mitarbeiter unter der Mitarbeiternummer {} gefunden!'.format(mitarbeiterNr))
        return redirect(url_for('updateUser'))
    elif type(user) == Administrator and user.mitarbeiterNr != current_user.mitarbeiterNr:  # Hier wird verhindert, dass die Daten eines anderen Administrators geändert werden
        flash('Sie dürfen die Daten eines anderen Administrators nicht bearbeiten!')
        return redirect(url_for('updateUser'))
    elif type(user) == Zugpersonal:
        typ = 'Zugpersonal'
        form = EditProfileFormZugpersonal(user.mitarbeiterNr, user.svnr, user.email)
        form.zugNr.choices = [(z.nr, z.nr) for z in Zug.query.all()]
    else:
        typ = 'Wartungspersonal'
        form = EditProfileForm(user.mitarbeiterNr, user.svnr, user.email)
    if form.validate_on_submit():
        user.mitarbeiterNr = form.mitarbeiterNr.data
        user.svnr = form.svnr.data
        user.vorname = form.vorname.data
        user.nachname = form.nachname.data
        user.email = form.email.data
        if typ == 'Zugpersonal':
            user.berufsbezeichnung = form.berufsbezeichnung.data
            user.zugNr = form.zugNr.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateUser'))
    elif request.method == 'GET':   # Ist die Abfragemethode 'GET', dann wird das Formular mit den Daten des jeweiligen Mitarbeiters angezeigt
        form.mitarbeiterNr.data = user.mitarbeiterNr
        form.svnr.data = user.svnr
        form.vorname.data = user.vorname
        form.nachname.data = user.nachname
        form.email.data = user.email
        if typ == 'Zugpersonal':
            form.berufsbezeichnung.data = user.berufsbezeichnung
            form.zugNr.data = user.zugNr
    return render_template('edit_user.html', form=form, typ=typ)

@app.route('/User_löschen/<mitarbeiterNr>', methods=['POST'])
@login_required
def deleteUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer löschen zu können!')
        return redirect(url_for('home_personal'))
    form=EmptyForm()
    if form.validate_on_submit():
        mitarbeiter = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
        if mitarbeiter is None: # Wird der Mitarbeiter nicht gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen eines nicht vorhandenen Mitarbeiters nicht möglich')
            return redirect(url_for('updateUser'))
        db.session.delete(mitarbeiter)
        db.session.commit()
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None: # Es wird hier kontrolliert ob der Administrator sich selbst gelöscht hat
            flash('Löschen des Mitarbeiters {} {} mit der Mitarbeiternummer {} wurde erfolgreich durchgeführt'.format(mitarbeiter.vorname, mitarbeiter.nachname, mitarbeiterNr))
            return redirect(url_for('updateUser'))
        else:
            flash('Sie haben Ihr Profil erfolgreich gelöscht!')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('updateUser'))


@app.route('/Profil', methods=['GET', 'POST'])
@login_required
def profile():  # Bei der Änderung eines Profils wird zwischen einem Administrator und den anderen Personalarten unterschieden. Ein Administrator kann die eigenen Daten verändern, während normales Personal nur Leserechte hat
    user = Mitarbeiter.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first()
    if type(user) == Administrator:
        typ = 'Administrator'
        form = EditProfileForm(user.mitarbeiterNr, user.svnr, user.email)
        form2 = EmptyForm()
    elif type(user) == Wartungspersonal:
        typ = 'Wartungspersonal'
    else:
        typ = 'Zugpersonal'
        
    if type(user) == Administrator and form.validate_on_submit():
        user.mitarbeiterNr = form.mitarbeiterNr.data
        user.svnr = form.svnr.data
        user.vorname = form.vorname.data
        user.nachname = form.nachname.data
        user.email = form.email.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('home_admin'))
        
    if type(user) == Administrator and request.method == 'GET':
        form.mitarbeiterNr.data = user.mitarbeiterNr
        form.svnr.data = user.svnr
        form.vorname.data = user.vorname
        form.nachname.data = user.nachname
        form.email.data = user.email
        
    if type(user) == Administrator:
        return render_template('profile.html', form=form, form2=form2, typ=typ)
    else:
        return render_template('profile.html', typ=typ)


@app.route('/Wagen_erstellen')
@login_required
def waggon():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Waggon erstellen zu können!')
        return redirect(url_for('home_personal'))
    return render_template('wagen.html', title='Wagen erstellen')


@app.route('/Wagen_erstellen/<typ>', methods=['GET', 'POST'])
@login_required
def createWaggon(typ):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Waggon erstellen zu können!')
        return redirect(url_for('home_personal'))
    if typ == 'Triebwagen': # Für die unterschiedlichen Typen des Waggons werden unterschiedliche Formulare verwendet
        form = TriebwagenForm()
    else:
        form = PersonenwagenForm()
    if form.validate_on_submit():
        if typ == 'Triebwagen':
            wagen = Triebwagen(nr=form.nr.data, spurweite=form.spurweite.data, maxZugkraft=form.maxZugkraft.data)
        elif typ == 'Personenwagen':
            wagen = Personenwagen(nr=form.nr.data, spurweite=form.spurweite.data, sitzanzahl=form.sitzanzahl.data, maximalgewicht=form.maximalgewicht.data)
        db.session.add(wagen)
        db.session.commit()
        flash(typ + ' wurde erfolgreich erstellt!')
        return redirect(url_for('waggon'))
    return render_template('create_waggon.html', title=typ + ' erstellen', form=form, typ=typ)

@app.route('/Wagen_bearbeiten')
@login_required
def updateWaggon():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    triebwagen = Triebwagen.query.all()
    personenwagen = Personenwagen.query.all()
    form = EmptyForm()
    return render_template('edit_wagen_overview.html', triebwagen=triebwagen, personenwagen=personenwagen, form=form)

@app.route('/Wagen_bearbeiten/<nr>', methods=['GET', 'POST'])
@login_required
def editWaggon(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen bestehenden Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wagen = Wagen.query.filter_by(nr=nr).first()
    if wagen is None:    # Wird unter der übergebenen Wagennummer kein Waggon gefunden, so wird der Benutzer darüber informiert
        flash('Es wurde kein Waggon unter der Wagennummer {} gefunden!'.format(nr))
        return redirect(url_for('updateWaggon'))
    elif type(wagen) == Triebwagen:
        typ = 'Triebwagen'
        form = EditTriebwagenForm(wagen.nr)
    else:
        typ = 'Personenwagen'
        form = EditPersonenwagenForm(wagen.nr)
    if form.validate_on_submit():
        wagen.nr = form.nr.data
        wagen.spurweite = form.spurweite.data
        if type(wagen) == Triebwagen:
            wagen.maxZugkraft = form.maxZugkraft.data
        else:
            wagen.sitzanzahl = form.sitzanzahl.data
            wagen.maximalgewicht = form.maximalgewicht.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateWaggon'))
    elif request.method == 'GET':   # Ist die Abfragemethode 'GET', dann wird das Formular mit den Daten des jeweiligen Waggons angezeigt
        form.nr.data = wagen.nr
        form.spurweite.data = wagen.spurweite
        if type(wagen) == Triebwagen:
            form.maxZugkraft.data = wagen.maxZugkraft
        else:
            form.sitzanzahl.data = wagen.sitzanzahl
            form.maximalgewicht.data = wagen.maximalgewicht
    return render_template('edit_wagen.html', form=form, typ=typ)

@app.route('/Wagen_löschen/<nr>', methods=['POST'])
@login_required
def deleteWaggon(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Waggon löschen zu können!')
        return redirect(url_for('home_personal'))
    form = EmptyForm()
    if form.validate_on_submit():
        wagen = Wagen.query.filter_by(nr=nr).first()
        if wagen is None: # Wird kein Wagggon gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen eines nicht vorhandenen Waggons nicht möglich')
            return redirect(url_for('updateWaggon'))
        db.session.delete(wagen)
        db.session.commit()
        flash('Löschen des Waggons mit der Wagennummer {} wurde erfolgreich durchgeführt'.format(nr))
        return redirect(url_for('updateWaggon'))
    else:
        return redirect(url_for('updateWaggon'))


@app.route('/Zug_erstellen', methods=['GET', 'POST'])
@login_required
def createTrain():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug erstellen zu können!')
        return redirect(url_for('home_personal'))
    form = ZugForm()
    if form.validate_on_submit():
        zug = Zug(nr=form.nr.data, name=form.name.data)
        db.session.add(zug)
        db.session.commit()
        flash('Zug wurde erfolgreich erstellt!')
        return redirect(url_for('createTrain'))
    return render_template('create_zug.html', form=form)

@app.route('/Zug_bearbeiten')
@login_required
def updateTrain():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    zug = Zug.query.all()
    form = EmptyForm()
    return render_template('edit_zug_overview.html', zug=zug, form=form)

@app.route('/Zug_bearbeiten/<nr>', methods=['GET', 'POST'])
@login_required
def editTrain(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen bestehenden Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    zug = Zug.query.filter_by(nr=nr).first()
    if zug is None:
        flash('Es wurde kein Zug unter der Zugnummer {} gefunden!'.format(nr))
        return redirect(url_for('updateTrain'))
    form = EditZugForm(zug.nr)
    if form.validate_on_submit():
        zug.nr = form.nr.data
        zug.name = form.name.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateTrain'))
    elif request.method == 'GET':
        form.nr.data = zug.nr
        form.name.data = zug.name
    return render_template('edit_zug.html', form=form)

@app.route('/Zug_löschen/<nr>', methods=['POST'])
@login_required
def deleteTrain(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug löschen zu können!')
        return redirect(url_for('home_personal'))
    form = EmptyForm()
    if form.validate_on_submit():
        zug = Zug.query.filter_by(nr=nr).first()
        if zug is None: # Wird kein Zug gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen eines nicht vorhandenen Zuges nicht möglich')
            return redirect(url_for('updateTrain'))
        db.session.delete(zug)
        db.session.commit()
        flash('Löschen des Zuges mit der Zugnummer {} wurde erfolgreich durchgeführt'.format(nr))
        return redirect(url_for('updateTrain'))
    else:
        return redirect(url_for('updateTrain'))


@app.route('/Zugübersicht')
@login_required
def trainOverview():
    zug = Zug.query.order_by('name').all()
    return render_template('zug_overview.html', zug=zug)

@app.route('/Waggonübersicht')
@login_required
def waggonOverview():
    triebwagen = Triebwagen.query.all()
    personenwagen = Personenwagen.query.all()
    return render_template('wagen_overview.html', triebwagen=triebwagen, personenwagen=personenwagen)
