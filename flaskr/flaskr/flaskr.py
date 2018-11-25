# Application Setup Code

import os
import json
import time
import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from datetime import date
from datetime import datetime

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file, flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY = 'development key',     # keeps client-side sessions secure with key
    USERNAME = 'admin',
    PASSWORD = 'default',
    USER_APP_NAME = "Blood Bank",
    USER_ENABLE_EMAIL = True,        # Enable email authentication
    USER_ENABLE_USERNAME = False,    # Disable username authentication
    USER_EMAIL_SENDER_NAME = "Blood Bank",
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
))

# define environment variable FLASKR_SETTINGS that points to a config file to be loaded
# silent tells Flask to not complain if no such environment key is set
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

usr = ''
role = ''

#allows for easy connectsion to the specified database
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

#initializes the database
def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#registers a new command with the flask script to run the database
@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Show tuples
@app.route('/',  methods=['GET', 'POST'])
def show_links():
    if request.method == 'POST':
        db = get_db()
        if (request.form.get('action', None) == "Show Doctors"):
            cur = db.execute('select * from doctor')
            doctors = cur.fetchall()
            flash('inside show doctors')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', doctors=doctors, chosen="doctors")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', doctors=doctors, chosen="doctors")
            else:
                return render_template('show_entries_all.html', doctors=doctors, chosen="doctors")
        elif (request.form.get('action', None) == "Show Doctors taking care of patients..."):
            cur = db.execute(
                'SELECT D.d_Fname, D.d_lname, P.p_fname, P.p_lname\
                FROM    doctor AS D, patients AS P, doctor_take_care_of AS DC \
                WHERE   D.d_id = DC.doctor_id AND DC.patient_id = P.p_id \
                ORDER BY D.d_fname')
            doctorsTakesCareOf = cur.fetchall()
            flash('inside show doctors taking care of')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', doctorsTakesCareOf=doctorsTakesCareOf, chosen="doctorsTakesCareOf")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', doctorsTakesCareOf=doctorsTakesCareOf, chosen="doctorsTakesCareOf")
            else:
                return render_template('show_entries_all.html', doctorsTakesCareOf=doctorsTakesCareOf, chosen="doctorsTakesCareOf")
        elif (request.form.get('action', None) == "Show Doctors Assisted by which Nurses"):
            cur = db.execute(
                'SELECT D.d_fname, D.d_lname, N.n_fname, N.n_lname\
                FROM    doctor AS D, nurse AS N, assists AS A \
                WHERE   D.d_id = A.doctor_id AND A.nurse_id = N.n_id \
                ORDER BY D.d_fname')
            doctorsAssistedBy = cur.fetchall()
            flash('inside show doctors being by assisted by which nurses')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', doctorsAssistedBy=doctorsAssistedBy, chosen="doctorsAssistedBy")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', doctorsAssistedBy=doctorsAssistedBy, chosen="doctorsAssistedBy")
            else:
                return render_template('show_entries_all.html', doctorsAssistedBy=doctorsAssistedBy, chosen="doctorsAssistedBy")
        elif (request.form.get('action', None) == "Show Patients"):
            cur = db.execute('select * from patients')
            patients = cur.fetchall()
            flash('inside show patients')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', patients=patients, chosen="patients")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', patients=patients, chosen="patients")
            else:
                return render_template('show_entries_all.html', patients=patients, chosen="patients")
        elif (request.form.get('action', None) == "Show Patients Receiving Blood from which Blood Bank"):
            global role
            if (role == "admin" or role == "head nurse"):
                cur = db.execute(
                    'SELECT P.p_fname, P.p_lname, BB.bb_name, R.received_date, R.blood_type, R.received_amt, R.pack_cnt\
                    FROM    patients AS P, receives_blood AS R, blood_bank AS BB \
                    WHERE   P.p_id = R.patient_id AND R.blood_bank_id = BB.bb_id \
                    ORDER BY P.p_fname')
                patientsReceiveBlood = cur.fetchall()
                flash('inside show patients receiving blood from which blood bank')
                if (role == "admin"):
                    return render_template('show_entries_admin.html', patientsReceiveBlood=patientsReceiveBlood, chosen="patientsReceiveBlood")
                else:
                    return render_template('show_entries_nurse.html', patientsReceiveBlood=patientsReceiveBlood, chosen="patientsReceiveBlood")
        elif (request.form.get('action', None) == "Show Patients Who Needs Blood"):
            cur = db.execute(
                'SELECT P.p_fname, P.p_lname, P.blood_type\
                FROM    patients AS P\
                WHERE   NOT EXISTS (\
                        SELECT  *\
                        FROM    receives_blood AS RB\
                        WHERE   RB.patient_id = P.p_id)')
            patientsWhoNeedBlood = cur.fetchall()
            flash('inside show patients who need blood')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', patientsWhoNeedBlood=patientsWhoNeedBlood, chosen="patientsWhoNeedBlood")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', patientsWhoNeedBlood=patientsWhoNeedBlood, chosen="patientsWhoNeedBlood")
            else:
                return render_template('show_entries_all.html', patientsWhoNeedBlood=patientsWhoNeedBlood, chosen="patientsWhoNeedBlood")
        elif (request.form.get('action', None) == "Show Donors"):
            cur = db.execute('select * from donor')
            donors = cur.fetchall()
            flash('inside show donors')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', donors=donors, chosen="donors")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', donors=donors, chosen="donors")
            else:
                return render_template('show_entries_all.html', donors=donors, chosen="donors")
        elif (request.form.get('action', None) == "Show Donor File"):
            cur = db.execute('select * from donor_file')
            donorFiles = cur.fetchall()
            flash('inside show donor file')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', donorFiles=donorFiles, chosen="donorFile")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', donorFiles=donorFiles, chosen="donorFile")
            else:
                return render_template('show_entries_all.html', donorFiles=donorFiles, chosen="donorFile")
        elif (request.form.get('action', None) == "Show Blood Banks"):
            global role
            if (role == "admin" or role == "head nurse"):
                cur = db.execute('select * from blood_bank')
                bloodBanks = cur.fetchall()
                flash('inside show blood banks')
                if (role == "admin"):
                    return render_template('show_entries_admin.html', bloodBanks=bloodBanks, chosen="bloodBank")
                else:
                    return render_template('show_entries_nurse.html', bloodBanks=bloodBanks, chosen="bloodBank")
        elif (request.form.get('action', None) == "Show Blood Transferred"):
            global role
            if (role == "admin" or role == "head nurse"):
                cur = db.execute('select * from transfer_blood')
                bloodsTransferred = cur.fetchall()
                flash('inside show blood transferred')
                if (role == "admin"):
                    return render_template('show_entries_admin.html', bloodsTransferred=bloodsTransferred, chosen="bloodsTransferred")
                else:
                    return render_template('show_entries_nurse.html', bloodsTransferred=bloodsTransferred, chosen="bloodsTransferred")
        elif (request.form.get('action', None) == "Show Blood Bank Inventory"):
            global role
            if (role == "admin" or role == "head nurse"):
                cur = db.execute(
                    'SELECT BB.bb_name, B.b_type, B.blood_amt, B.num_available\
                    FROM    bloods AS B, blood_bank AS BB, has_blood AS HB\
                    WHERE   BB.bb_id = HB.blood_bank_id AND HB.blood_bank_ref_id = B.blood_bank_ref_id')
                bloods = cur.fetchall()
                flash('inside show blood bank inventory')
                if (role == "admin"):
                    return render_template('show_entries_admin.html', bloods=bloods, chosen="bloods")
                else:
                    return render_template('show_entries_nurse.html', bloods=bloods, chosen="bloods")
        elif (request.form.get('action', None) == "Show Nurses"):
            cur = db.execute('select * from nurse')
            nurses = cur.fetchall()
            flash('inside show nurses')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', nurses=nurses, chosen="nurses")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', nurses=nurses, chosen="nurses")
            else:
                return render_template('show_entries_all.html', nurses=nurses, chosen="nurses")
        elif (request.form.get('action', None) == "Show Nurses Taking Care of Which Patients..."):
            cur = db.execute(
                'SELECT N.n_fname, N.n_lname, P.p_fname, P.p_lname\
                FROM    nurse AS N, patients AS P, nurse_take_care_of AS NC\
                WHERE   N.n_id = NC.nurse_id AND NC.patient_id = P.p_id\
                ORDER BY N.n_fname')
            nursesTakingCareOf = cur.fetchall()
            flash('inside show nurses taking care of')
            global role
            if (role == "admin"):
                return render_template('show_entries_admin.html', nursesTakingCareOf=nursesTakingCareOf, chosen="nursesTakingCareOf")
            elif (role == "head nurse"):
                return render_template('show_entries_nurse.html', nursesTakingCareOf=nursesTakingCareOf, chosen="nursesTakingCareOf")
            else:
                return render_template('show_entries_all.html', nursesTakingCareOf=nursesTakingCareOf, chosen="nursesTakingCareOf")
        elif (request.form.get('action', None) == "Show Nurses with Supervisor"):
            global role
            if (role == "admin" or role == "head nurse"):
                cur = db.execute(
                    'select * from supervise Order By super_fname')
                supervisedNurses = cur.fetchall()
                flash('inside show nurses supervising...')
                if (role == "admin"):
                    return render_template('show_entries_admin.html', supervisedNurses=supervisedNurses, chosen="supervisedNurses")
                else:
                    return render_template('show_entries_nurse.html', supervisedNurses=supervisedNurses, chosen="supervisedNurses")
        elif (request.form.get('action', None) == "Show Accounts"):
            global role
            if (role == "admin"):
                cur = db.execute('select * from accounts')
                accounts = cur.fetchall()
                flash('inside show accounts')
                return render_template('show_entries_admin.html', accounts=accounts, chosen="accounts")
            else:
                flash('unauthorized')
    global role
    if (role == "admin"):
        return render_template('show_entries_admin.html')
    elif (role == "head nurse"):
        return render_template('show_entries_nurse.html')
    else:
        return render_template('show_entries_all.html')

# Add tuple form
@app.route('/add', methods=['POST'])
def add_form():
    if not session.get('logged_in'):
        abort(401)
    """use question marks to prevent app from SQL injection"""
    """takes data extracted from form and insert into table"""
    db = get_db()
    # Patient Forms
    if (request.form.get('addForm', None) == "Add Patient"):
        db.execute('insert into patients (p_id, p_fname, p_lname, blood_type) values (?, ?, ?, ?)',
        [request.form['p_id'], request.form['p_fname'], request.form['p_lname'], request.form['blood_type']])
        flash('Added Patient')
    elif (request.form.get('addForm', None) == "Add Donor"):
        db.execute('insert into donor (d_id, d_fname, d_lname) values (?, ?, ?)',
        [request.form['d_id'], request.form['d_fname'], request.form['d_lname']])
        flash('Added Donor')
    elif (request.form.get('addForm', None) == "Add Doctor"):
        db.execute('insert into doctor (d_id, d_fname, d_lname) values (?, ?, ?)',
        [request.form['d_id'], request.form['d_fname'], request.form['d_lname']])
        flash('Added Doctor')
        db.commit()
    elif (request.form.get('addForm', None) == "Add Blood Bank"):
        db.execute('insert into blood_bank (bb_name, bb_id, bb_location) values (?, ?, ?)',
        [request.form['bb_name'], request.form['bb_id'], request.form['bb_location']])
        flash('Added Blood Bank')
        db.commit()
    elif (request.form.get('addForm', None) == "Add Doctor-Patient Relation"):
        db.execute('insert into doctor_take_care_of (doctor_id, patient_id) values (?, ?)',
        [request.form['doctor_id'], request.form['patient_id']])
        flash('Added Doctor-Patient Relation')
        db.commit()
    elif (request.form.get('addForm', None) == "Add Doctor-Nurse Relation"):
        db.execute('insert into assists (doctor_id, nurse_id) values (?, ?)',
        [request.form['doctor_id'], request.form['nurse_id']])
        flash('Added Doctor-Nurse Relation')
        db.commit()
    elif (request.form.get('addForm', None) == "Get Blood from Donor"):
        d_fname = request.form['donor_fname']
        d_lname = request.form['donor_lname']
        condition = request.form['condition']
        blood_amt = request.form['blood_amt']
        bb_name = request.form['bb_name']
        # check if it has been at least 60 days since donor donated
        today = date.today().strftime('%Y-%m-%d')
        date_last_donated = ''
        cur = db.execute('select * from donor_file')
        donor_files = cur.fetchall()
        for i in donor_files:
            if (i[1] == d_fname and i[2] == d_lname):
                date_last_donated = i[8]
        FMT = '%Y-%m-%d'
        print(date_last_donated)
        print(today)
        dt_obj1 = datetime.strptime(today, FMT)
        dt_obj2 = datetime.strptime(date_last_donated, FMT)
        tdelta = datetime.strptime(today, FMT) - datetime.strptime(date_last_donated, FMT)
        tdelta = abs((dt_obj1 - dt_obj2).days)
        print(tdelta)
        if (tdelta >= 60):
            flash(d_fname + ' can donate')
        else:
            flash(d_fname + ' cannot donate')
        # update donor file
    elif (request.form.get('addForm', None) == "Add Blood Bank"):
        db.execute('insert into blood_bank (bb_id, bb_name, bb_location) values (?, ?, ?)',
        [request.form['bb_id'], request.form['bb_name'], request.form['bb_location']])
        flash('Added Blood Bank')
    elif (request.form.get('addForm', None) == "Get Blood Packs for Patient"):
        cur = db.execute('select * from bloods')
        bloods = cur.fetchall()
        cur = db.execute('select * from has_blood')
        has_bloods = cur.fetchall()
        cur = db.execute('select * from patients')
        patients = cur.fetchall()
        hasBlood = False
        p_fname = request.form['patient_fname']
        p_lname = request.form['patient_lname']
        blood_bank_id_br = ''
        # create variables for storing data to
        patient_id = ''                                         # patient_id
        blood_bank_id_bb = ''                                   # blood_bank_id
        today = date.today().strftime('%Y-%m-%d')               # received_date
        blood_type = request.form['blood_type']                 # blood_type
        blood_pack_cnt = int(request.form['blood_pack_cnt'])    # pack_cnt
        received_amt = float(blood_pack_cnt) * 501.98           # received_amt
        # data to change bloods table
        blood_amt = ''
        num_available = ''
        # get first blood bank that has enough blood for patient
        for i in bloods:
            if (i[1] == blood_type and i[3] > blood_pack_cnt):
                hasBlood = True
                blood_bank_id_br = i[0]    # br...
        if (hasBlood == False):
            flash('All Blood Banks are out of Patient\'s Blood Type')
        else:
            # get blood_bank_id (bb...)
            for i in has_bloods:
                if (blood_bank_id_br == i[1]):
                    blood_bank_id_bb = i[0]
            # get patient id
            for i in patients:
                if (i[1] == p_fname and i[2] == p_lname):
                    patient_id = i[0]
            # insert blood given to patient into receives_blood table
            db.execute(
                'INSERT INTO receives_blood (patient_id, blood_bank_id, received_date, blood_type, received_amt, pack_cnt) values (?, ?, ?, ?, ?, ?)', [patient_id, blood_bank_id_bb, today, blood_type, received_amt, blood_pack_cnt])
            # get difference values after patient receives blood
            for i in bloods:
                if (i[0] == blood_bank_id_br and i[1] == blood_type):
                    blood_amt = i[2] - received_amt
                    num_available = i[3] - blood_pack_cnt
                    if (100 >= num_available):
                        flash('Running Low in ' + blood_type + ' emailing willing donors...')
            # subtract blood from blood inventory
            db.execute(
                'UPDATE bloods\
                SET     blood_amt=?, num_available=?\
                WHERE   blood_bank_ref_id=? AND b_type=?', [blood_amt, num_available, blood_bank_id_br, blood_type])
            flash('The Blood Packs are on Its Way')
    db.commit()
    global role
    if (role == "admin"):
        return render_template('show_entries_admin.html')
    elif (role == "head nurse"):
        return render_template('show_entries_nurse.html')
    else:
        return render_template('show_entries_all.html')

# Delete tuple
@app.route('/delete', methods=['POST'])
def delete_data():
    db = get_db()
    if (request.form.get('action', None) == "Delete Patient"):
        flash('Data deleted. DB committed successfully.' + request.form['p_id'])
        db.execute('delete from patients where p_id=? AND p_fname=? AND p_lname=? AND blood_type=?', [request.form['p_id'], request.form['p_fname'], request.form['p_lname'], request.form['blood_type']])
        db.commit()
    elif (request.form.get('action', None) == "Delete Doctor"):
        flash('Data deleted. DB committed successfully.' + request.form['d_id'])
        db.execute('delete from doctor where d_id=? AND d_fname=? AND d_lname=?', [request.form['d_id'], request.form['d_fname'], request.form['d_lname']])
        db.commit()
    elif (request.form.get('action', None) == "Delete Donor"):
        flash('Data deleted. DB committed successfully.' + request.form['d_id'])
        db.execute('delete from donor where d_id=? AND d_fname=? AND d_lname=?', [request.form['d_id'], request.form['d_fname'], request.form['d_lname']])
        db.commit()
    elif (request.form.get('action', None) == "Delete Blood Bank"):
        flash('Data deleted. DB committed successfully.' + request.form['bb_id'])
        db.execute('delete from blood_bank where bb_name=? AND bb_id=? AND bb_location=?', [request.form['bb_name'], request.form['bb_id'], request.form['bb_location']])
        db.commit()
    elif (request.form.get('action', None) == "Delete Doctor-Patient Relation"):
        flash('Data deleted. DB committed successfully.' + request.form['doctor_id'])
        db.execute('delete from doctor_take_care_of where doctor_id=? AND patient_id=?', [request.form['doctor_id'], request.form['patient_id']])
        db.commit()
    elif (request.form.get('action', None) == "Delete Doctor-Nurse Relation"):
        flash('Data deleted. DB committed successfully.' + request.form['doctor_id'])
        db.execute('delete from assists where doctor_id=? AND nurse_id=?', [request.form['doctor_id'], request.form['nurse_id']])
        db.commit()
    global role
    if (role == "admin"):
        return render_template('show_entries_all.html')
    elif (role == "head nurse"):
        return render_template('show_entries_nurse.html')
    else:
        return render_template('show_entries_all.html')

# Edit tuple
@app.route('/changeData', methods=['GET', 'POST'])
def change_data():
    db = get_db()
    # Patient Forms
    if (request.form.get('action', None) == "Change Patient's Name"):
        db.execute('update patients set p_fname=?, p_lname=? where p_id=?', [request.form['p_fNewName'], request.form['p_lNewName'], request.form['p_id']])
        flash('Changed Patient\'s Name')
    elif (request.form.get('action', None) == "Change Patient's Blood Type"):
        db.execute('update patients set blood_type=? where p_id=?',
            [request.form['blood_type'], request.form['pB_id']])
        flash('Changed Patient\'s Blood Type')
    elif (request.form.get('action', None) == "Change Doctors Name"):
        db.execute('update doctor set d_fname=?, d_lname=? where d_id=?',
            [request.form['d_fname'], request.form['d_lname'], request.form['d_id']])
        flash('Changed Doctors\'s Name')
        db.commit()
    elif (request.form.get('action', None) == "Change Donors Name"):
        db.execute('update donor set d_fname=?, d_lname=? where d_id=?',
            [request.form['d_fname'], request.form['d_lname'], request.form['d_id']])
        flash('Changed Donors\'s Name')
        db.commit()
    elif (request.form.get('action', None) == "Change Blood Bank Name"):
        db.execute('update blood_bank set bb_name=?, bb_location=? where bb_id=?',
            [request.form['bb_name'], request.form['bb_location'], request.form['bb_id']])
        flash('Changed Blood Bank\'s Name')
        db.commit()
    elif (request.form.get('action', None) == "Change Doctor-Patient Relation"):
        db.execute('update doctor_take_care_of set patient_id=? where doctor_id=?',
            [request.form['doctor_id'], request.form['patient_id']])
        flash('Changed Doctor-Patient\'s Relation')
        db.commit()
    # Transfer Blood Form
    elif (request.form.get('action', None) == "Transfer Blood"):
        cur = db.execute('select * from bloods')
        bloods = cur.fetchall()
        cur = db.execute('select * from blood_bank')
        blood_banks = cur.fetchall()
        cur = db.execute('select * from has_blood')
        has_bloods = cur.fetchall()
        found = False
        tooMuch = False
        blood_pack_cnt_from = 0
        blood_amt_from = 0.0
        blood_pack_cnt_to = 0
        blood_amt_to = 0.0
        blood_from = ''
        blood_to = ''
        blood_from_bb = ''                                  # transferred_from
        blood_to_bb = ''                                    # transferred_to
        from_blood_bank = request.form['transferred_from']  # from_blood_bank
        to_blood_bank = request.form['transferred_to']      # to_blood_bank
        match1 = False
        match2 = False
        blood_type = request.form['blood_type']             # blood_type
        blood_pack_cnt = request.form['blood_pack_cnt']     # blood_pack_cnt
        blood_amt = float(blood_pack_cnt) * 501.98          # blood_amt
        today = date.today().strftime('%Y-%m-%d')           # transfer_date
        # get IDs (bb...) of referenced blood banks
        for i in blood_banks:
            if (match1 and match2):
                found = True
                break
            else:
                if (i[1] == from_blood_bank):
                    match1 = True
                    blood_from = i[1]
                    blood_from_bb = i[1]
                elif (i[1] == to_blood_bank):
                    match2 = True
                    blood_to = i[1]
                    blood_to_bb = i[1]
        if (found == False):
            flash('Blood Bank Name Not Found')
        else:
            # get IDs (br...) of dependent bloods
            for i in has_bloods:
                if (i[0] == blood_from):
                    blood_from = i[1]
                elif (i[0] == blood_to):
                    blood_to = i[1]
            # find match, for blood bank from
            for i in bloods:
                if (i[0] == blood_from and i[1] == blood_type):
                    if (blood_pack_cnt > i[3]):
                        tooMuch = True
                    else:
                        blood_pack_cnt_from = i[3] - blood_pack_cnt
                        blood_amt_from = blood_pack_cnt_from * 501.98
            if (tooMuch):
                flash('Too Much Blood Being Transferred')
            else:
                # find match, for blood bank to
                for i in bloods:
                    if (i[0] == blood_to and i[1] == blood_type):
                        blood_pack_cnt_to = i[3] + blood_pack_cnt
                        blood_amt_to = blood_pack_cnt_to * 501.98

                # update bloods table on transfer from
                db.execute(
                    'UPDATE bloods \
                    SET     blood_amt=?, num_available=?\
                    WHERE   blood_bank_ref_id=? AND b_type=?', [blood_amt_from, blood_pack_cnt_from, blood_from, blood_type])
                # update bloods table on transfer to
                db.execute(
                    'UPDATE bloods \
                    SET     blood_amt=?, num_available=?\
                    WHERE   blood_bank_ref_id=? AND b_type=?', [blood_amt_to, blood_pack_cnt_to, blood_to, blood_type])
                # insert into transfer_blood table
                db.execute(
                    'INSERT INTO transfer_blood (transferred_from, from_blood_bank, transferred_to, to_blood_bank, blood_type, blood_amt, blood_pack_cnt, transfer_date) values(?, ?, ?, ?, ?, ?, ?, ?)', [blood_from_bb, from_blood_bank, blood_to_bb, to_blood_bank, blood_type, blood_amt, blood_pack_cnt, today])
                flash('Transfer Complete')
    db.commit()
    global role
    if (role == "admin" or role == "head nurse"):
        return render_template('show_entries_admin.html')
    else:
        return render_template('show_entries_nurse.html')

#logging the user in
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select * from accounts')
        accounts = cur.fetchall()
        usrPasCor = False
        for i in accounts:
            if (i[1] == request.form['username']):
                global role
                role = i[3]
                bc = Bcrypt(app)
                pw_hash = bc.generate_password_hash(request.form['password'])
                if (bc.check_password_hash(pw_hash, i[2])):
                    usrPasCor = True
                    flash(pw_hash)
                break
        if usrPasCor == True:
            global usr
            usr = request.form['username']
            session['logged_in'] = True
            flash('You were logged in as a(n) ' + role)
            return redirect(url_for('show_links'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error = error)

#logging the user out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('you were logged out')
    return redirect(url_for('login'))

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)