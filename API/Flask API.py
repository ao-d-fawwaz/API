from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
import json
from sqlalchemy import text
# from werkzeug.security import check_password_hash
import mysql.connector
import uuid
import hashlib
import csv
from io import StringIO
from datetime import datetime, timedelta
from flask import send_file

app = Flask(__name__)


# Configure the MySQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://AdibDzakwanF:Adibdf@AdibDzakwanF.mysql.pythonanywhere-services.com/AdibDzakwanF$klinik'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Pasien(db.Model):
    ID_Pasien = db.Column(db.Integer, primary_key=True)
    Nama = db.Column(db.String(50))
    Alamat = db.Column(db.String(100))
    Tanggal_Lahir = db.Column(db.Date)
    Jenis_Kelamin = db.Column(db.String(10))
    password = db.Column(db.String(50))
    Email = db.Column(db.String(50))

class Dokter(db.Model):
    ID_Dokter = db.Column(db.Integer, primary_key=True)
    Nama = db.Column(db.String(50))
    Spesialisasi = db.Column(db.String(50))
    Password = db.Column(db.String(50))
class DetailBerobat(db.Model):
    ID_Detail = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Pasien = db.Column(db.Integer, db.ForeignKey('pasien.ID_Pasien'))
    ID_Dokter = db.Column(db.Integer, db.ForeignKey('dokter.ID_Dokter'))
    Tanggal_Berobat = db.Column(db.Date)
    Keluhan = db.Column(db.String(255))
    Diagnosis = db.Column(db.String(255))
    Resep = db.Column(db.String(255))
    Status = db.Column(db.String(255))
    reservasi = db.Column(db.String(255))
class Admin(db.Model):
    ID_Admin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nama = db.Column(db.String(50))
    Password = db.Column(db.String(50))

# Membuat database tables
db.create_all()
# Add login functionality for Admin
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = json.loads(request.data)
        admin = Admin.query.filter_by(Nama=data['Nama']).first()

        if admin and admin.Password == data['Password']:
            response = {
                'code': '200',
                'status': 'sukses',
                'message': 'Admin login successful'
            }
            return response, 200
        else:
            response = {
                'code': '401',
                'status': 'gagal',
                'message': 'Invalid credentials'
            }
            return response, 401
    except Exception as e:
        response = {
            'code': '500',
            'status': 'gagal',
            'message': f'Error: {str(e)}'
        }
        return response, 500
# Add login functionality for Pasien
@app.route('/api/pasien/login', methods=['POST'])
def pasien_login():
    try:
        data = json.loads(request.data)
        pasien = Pasien.query.filter_by(Email=data['Email']).first()

        if pasien and pasien.password == data['Password']:
            response = {
                'code': '200',
                'status': 'sukses',
                'message': 'Pasien login successful',
                'ID_Pasien':pasien.ID_Pasien
            }
            return response, 200
        else:
            response = {
                'code': '401',
                'status': 'gagal',
                'message': 'Invalid credentials'
            }
            return response, 401
    except Exception as e:
        response = {
            'code': '500',
            'status': 'gagal',
            'message': f'Error: {str(e)}'
        }
        return response, 500
# Add login functionality for Dokter
@app.route('/api/dokter/login', methods=['POST'])
def dokter_login():
    try:
        data = json.loads(request.data)
        dokter = Dokter.query.filter_by(Nama=data['Nama']).first()

        if dokter and dokter.Password == data['Password']:
            return {'message': 'Dokter login successful'}, 200
        else:
            return {'error': 'Invalid credentials'}, 401
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/detail_berobat_with_number', methods=['GET'])
def get_detail_berobat_with_number():
    try:
        # Execute raw SQL query
        sql_query = text("""
            SELECT
                (@no:=@no+1) AS nomor,
                ID_Pasien,
                ID_Dokter,
                Tanggal_Berobat,
                Keluhan,
                Diagnosis,
                Resep,
                Status,
                reservasi
            FROM
                (SELECT
                    ID_Pasien,
                    ID_Dokter,
                    Tanggal_Berobat,
                    Keluhan,
                    Diagnosis,
                    Resep,
                    Status,
                    reservasi
                FROM detail_berobat
                WHERE DATE(Tanggal_Berobat) = CURDATE() -- Only for the current day
                ORDER BY Tanggal_Berobat ASC) AS ranked,
                (SELECT @no:= 0) AS no;
        """)
        query_result = db.engine.execute(sql_query)

        result = []
        for row in query_result:
            result.append({
                'nomor': row.nomor,
                'ID_Pasien': row.ID_Pasien,
                'ID_Dokter': row.ID_Dokter,
                'Tanggal_Berobat': row.Tanggal_Berobat.strftime('%Y-%m-%d %H:%M:%S'),
                'Keluhan': row.Keluhan,
                'Diagnosis': row.Diagnosis,
                'Resep': row.Resep,
                'Status': row.Status,
                'reservasi': row.reservasi
            })

        return jsonify(result)

    except Exception as e:
        return {'error': str(e)}, 500
# Create new Admin
def create_admin(data):
    try:
        new_admin = Admin(
            ID_Admin=data['ID_Admin'],
            Nama=data['Nama'],
            Password=data['Password']
        )
        db.session.add(new_admin)
        db.session.commit()
        return {'message': 'Admin created successfully'}, 201
    except Exception as e:
        return {'error': str(e)}, 500

# Get all Admin
def get_all_admin():
    admin_list = Admin.query.all()
    result = []
    for admin in admin_list:
        result.append({
            'ID_Admin': admin.ID_Admin,
            'Nama': admin.Nama,
            'Password': admin.Password
        })
    return result

# Get Admin by ID
def get_admin_by_id(admin_id):
    admin = Admin.query.get(admin_id)
    if admin:
        return {
            'ID_Admin': admin.ID_Admin,
            'Nama': admin.Nama,
            'Password': admin.Password
        }
    else:
        return {'error': 'Admin not found'}, 404

# Update Admin
def update_admin(admin_id, data):
    try:
        admin = Admin.query.get(admin_id)
        if admin:
            admin.Nama = data['Nama']
            admin.Password = data['Password']
            db.session.commit()
            return {'message': 'Admin updated successfully'}, 200
        else:
            return {'error': 'Admin not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

# Delete Admin by ID
def delete_admin(admin_id):
    try:
        admin = Admin.query.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return {'message': 'Admin deleted successfully'}, 200
        else:
            return {'error': 'Admin not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

#  new Detail_Berobat
def create_detail_berobat(data):
    try:
        new_detail_berobat = DetailBerobat(
            ID_Detail=data['ID_Detail'],
            ID_Pasien=data['ID_Pasien'],
            ID_Dokter=data['ID_Dokter'],
            Tanggal_Berobat=datetime.strptime(data['Tanggal_Berobat'], '%Y-%m-%d %H:%M:%S'),  # Removed .date()
            Keluhan=data['Keluhan'],
            Diagnosis=data['Diagnosis'],
            Resep=data['Resep'],
            Status=data['Status'],
            reservasi=data['reservasi']
        )
        db.session.add(new_detail_berobat)
        db.session.commit()
        response = {
                'code': '200',
                'status': 'sukses',
                'message': 'Detail Berobat Created Successful'
            }
        return response
    except Exception as e:
        response = {
                'code': '500',
                'status': 'gagal',
                'message': 'your error = '+str(e)
            }
        return response

# Get all Detail_Berobat
def get_all_detail_berobat_data():
    detail_berobat_list = DetailBerobat.query.all()
    result = []
    for detail_berobat in detail_berobat_list:
        result.append({
            'ID_Detail': detail_berobat.ID_Detail,
            'ID_Pasien': detail_berobat.ID_Pasien,
            'ID_Dokter': detail_berobat.ID_Dokter,
            'Tanggal_Berobat': detail_berobat.Tanggal_Berobat.strftime('%Y-%m-%d %H:%M:%S'),
            'Keluhan': detail_berobat.Keluhan,
            'Diagnosis': detail_berobat.Diagnosis,
            'Resep': detail_berobat.Resep,
            'Status':detail_berobat.Status,
            'reservasi':detail_berobat.reservasi
        })
    return result

# Get Detail_Berobat by ID
def get_detail_berobat_data_by_id(detail_id):
    detail_berobat = DetailBerobat.query.get(detail_id)
    if detail_berobat:
        return {
            'ID_Detail': detail_berobat.ID_Detail,
            'ID_Pasien': detail_berobat.ID_Pasien,
            'ID_Dokter': detail_berobat.ID_Dokter,
            'Tanggal_Berobat': detail_berobat.Tanggal_Berobat.strftime('%Y-%m-%d %H:%M:%S'),
            'Keluhan': detail_berobat.Keluhan,
            'Diagnosis': detail_berobat.Diagnosis,
            'Resep': detail_berobat.Resep,
            'Status':detail_berobat.Status,
            'reservasi':detail_berobat.reservasi
        }
    else:
        return {'error': 'Detail Berobat not found'}, 404

# Update Detail_Berobat
def update_detail_berobat_data(detail_id, data):
    try:
        detail_berobat = DetailBerobat.query.get(detail_id)
        if detail_berobat:
            detail_berobat.ID_Pasien = data['ID_Pasien']
            detail_berobat.ID_Dokter = data['ID_Dokter']
            detail_berobat.Tanggal_Berobat = datetime.strptime(data['Tanggal_Berobat'], '%Y-%m-%d %H:%M:%S').date()
            detail_berobat.Keluhan = data['Keluhan']
            detail_berobat.Diagnosis = data['Diagnosis']
            detail_berobat.Resep = data['Resep']
            detail_berobat.Status=data['Status']
            detail_berobat.reservasi=data['reservasi']
            db.session.commit()
            return {'message': 'Detail Berobat updated successfully'}, 200
        else:
            return {'error': 'Detail Berobat not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

# Delete by id
def delete_detail_berobat_data(detail_id):
    try:
        detail_berobat = DetailBerobat.query.get(detail_id)
        if detail_berobat:
            db.session.delete(detail_berobat)
            db.session.commit()
            return {'message': 'Detail Berobat deleted successfully'}, 200
        else:
            return {'error': 'Detail Berobat not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500
# DOKTER
def create_dokter(data):
    try:
        new_dokter = Dokter(
            ID_Dokter=data['ID_Dokter'],
            Nama=data['Nama'],
            Spesialisasi=data['Spesialisasi'],
            Password=data['Password']  # Fix the semicolon to equal sign here
        )
        db.session.add(new_dokter)
        db.session.commit()
        return {'message': 'Dokter created successfully'}, 201
    except Exception as e:
        return {'error': str(e)}, 500

# Get all Dokter
def get_all_dokter():
    dokter_list = Dokter.query.all()
    result = []
    for dokter in dokter_list:
        result.append({
            'ID_Dokter': dokter.ID_Dokter,
            'Nama': dokter.Nama,
            'Spesialisasi':dokter.Spesialisasi,
            'Password':dokter.Password
        })
    return result

# Get Dokter by ID
def get_dokter_by_id(dokter_id):
    dokter = Dokter.query.get(dokter_id)
    if dokter:
        return {
            'ID_Dokter': dokter.ID_Dokter,
            'Nama': dokter.Nama,
            'Spesialisasi':dokter.Spesialisasi,
            'Password': dokter.Password
        }
    else:
        return {'error': 'Dokter not found'}, 404

# Update Dokter
def update_dokter(dokter_id, data):
    try:
        dokter = Dokter.query.get(dokter_id)
        if dokter:
            dokter.Nama = data['Nama']
            dokter.Alamat = data['Alamat']
            dokter.Spesialisasi=data['Spesialisasi']
            dokter.Password=data['Password']
            db.session.commit()
            return {'message': 'Dokter updated successfully'}, 200
        else:
            return {'error': 'Dokter not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

# Delete Dokter by ID
def delete_dokter(dokter_id):
    dokter = Dokter.query.get(dokter_id)
    if dokter:
        db.session.delete(dokter)
        db.session.commit()



# PASIEN
# Create new Pasien
def create_pasien(data):
    try:
        new_pasien = Pasien(
            ID_Pasien=data['ID_Pasien'],
            Nama=data['Nama'],
            Alamat=data['Alamat'],
            Tanggal_Lahir=datetime.strptime(data['Tanggal_Lahir'], '%Y-%m-%d').date(),
            Jenis_Kelamin=data['Jenis_Kelamin'],
            password=data['Password'],  # Include the password field
            Email=data['Email']  # Include the Email field
        )
        db.session.add(new_pasien)
        db.session.commit()
        response = {
            'code': '201',
            'status': 'sukses',
            'message': 'Pasien created successfully.'
        }
        # return response, 201
        return response
    except Exception as e:
        response = {
            'code': '500',
            'status': 'gagal',
            'message': f'Error: {str(e)}'
        }
        return response
        # return response, 500



# Get all Pasien
def get_all_pasien():
    pasien_list = Pasien.query.all()
    result = []
    for pasien in pasien_list:
        result.append({
            'ID_Pasien': pasien.ID_Pasien,
            'Nama': pasien.Nama,
            'Alamat': pasien.Alamat,
            'Tanggal_Lahir': pasien.Tanggal_Lahir.strftime('%Y-%m-%d'),
            'Jenis_Kelamin': pasien.Jenis_Kelamin,
            'Password': pasien.password,  # Include the password field
            'Email': pasien.Email  # Include the Email field
        })
    return result

# Get Pasien by ID
def get_pasien_by_id(pasien_id):
    pasien = Pasien.query.get(pasien_id)
    if pasien:
        return {
            'ID_Pasien': pasien.ID_Pasien,
            'Nama': pasien.Nama,
            'Alamat': pasien.Alamat,
            'Tanggal_Lahir': pasien.Tanggal_Lahir.strftime('%Y-%m-%d'),
            'Jenis_Kelamin': pasien.Jenis_Kelamin,
            'Password': pasien.password,  # Include the password field
            'Email': pasien.Email  # Include the Email field
        }
    else:
        response = {
            'code': '500',
            'status': 'gagal',
            'message': 'Pasien not found'
        }
        return response, 404


# Update Pasien
def update_pasien(pasien_id, data):
    try:
        pasien = Pasien.query.get(pasien_id)
        if pasien:
            pasien.Nama = data['Nama']
            pasien.Alamat = data['Alamat']
            pasien.Tanggal_Lahir = datetime.strptime(data['Tanggal_Lahir'], '%Y-%m-%d').date()
            pasien.Jenis_Kelamin = data['Jenis_Kelamin']
            pasien.password = data['Password']  # Update the password field
            pasien.Email = data['Email']  # Update the Email field
            db.session.commit()
            return {'message': 'Pasien updated successfully'}, 200
        else:
            return {'error': 'Pasien not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500


# Delete Pasien by ID
def delete_pasien(pasien_id):
    try:
        pasien = Pasien.query.get(pasien_id)
        if pasien:
            db.session.delete(pasien)
            db.session.commit()
            return {'message': 'Pasien deleted successfully'}, 200
        else:
            return {'error': 'Pasien not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500
@app.route('/api/lupa_password', methods=['POST'])
def lupa_password():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check if the email exists in the Pasien table
        pasien = Pasien.query.filter_by(Email=email).first()

        if pasien:
            # Check if the new password matches the confirmation password
            if new_password == confirm_password:
                # Update the password for the user with the provided email
                pasien.password = new_password
                db.session.commit()

                response = {
                    'code': '200',
                    'status': 'sukses',
                    'message': 'Password updated successfully'
                }
                return response, 200
            else:
                response = {
                    'code': '400',
                    'status': 'gagal',
                    'message': 'New password and confirmation password do not match'
                }
                return response, 400
        else:
            response = {
                'code': '404',
                'status': 'gagal',
                'message': 'Email not found'
            }
            return response, 404

    except Exception as e:
        response = {
            'code': '500',
            'status': 'gagal',
            'message': f'Error: {str(e)}'
        }
        return response, 500
# Routes Admin
@app.route('/api/admin', methods=['POST'])
def add_admin():
    data = json.loads(request.data)
    return jsonify(create_admin(data))

@app.route('/api/admin', methods=['GET'])
def get_all_admin_route():
    return jsonify(get_all_admin())

@app.route('/api/admin/<int:admin_id>', methods=['GET'])
def get_admin_route(admin_id):
    return jsonify(get_admin_by_id(admin_id))

@app.route('/api/admin/<int:admin_id>', methods=['PUT'])
def update_admin_route(admin_id):
    data = json.loads(request.data)
    return jsonify(update_admin(admin_id, data))

@app.route('/api/admin/<int:admin_id>', methods=['DELETE'])
def delete_admin_route(admin_id):
    return jsonify(delete_admin(admin_id))


# Routes Detail
# Add a new endpoint for creating a detail berobat
# @app.route('/api/input_detail_berobat', methods=['POST'])
# def add_detail_berobat_2():
#     try:

#         data = json.loads(request.data)
#         # Set other fields to None if not provided
#         unique_id = str(uuid.uuid4())
#         hashed_id = hashlib.md5(unique_id.encode()).hexdigest()
#         data['ID_Detail']=hashed_id
#         data['ID_Pasien'] = data.get('ID_Pasien')
#         data['ID_Dokter'] = data.get('ID_Dokter')
#         data['Tanggal_Berobat'] = data.get('Tanggal_Berobat', None)
#         data['Keluhan'] = data.get('Keluhan', None)
#         data['Diagnosis'] = data.get('Diagnosis',None)
#         data['Resep'] = data.get('Resep',None)
#         data['Status'] = data.get('Status',None)
#         data['reservasi'] = data.get('reservasi', None)

#         # Create a new detail berobat
#         response = create_detail_berobat(data)
#         return jsonify(response)

#     except Exception as e:
#         response = {
#             'code': '500',
#             'status': 'gagal',
#             'message': f'Error: {str(e)}'
#         }
#         return jsonify(response), 500
@app.route('/api/detail_berobat', methods=['POST'])
def add_detail_berobat():
    data = json.loads(request.data)
    combined_data = f"{data['Tanggal_Berobat']}_{data['ID_Dokter']}_{data['ID_Pasien']}"
    hashed_id = hashlib.md5(combined_data.encode()).hexdigest()
    data['ID_Detail']=hashed_id
    data['ID_Pasien'] = data.get('ID_Pasien')
    data['ID_Dokter'] = data.get('ID_Dokter')
    data['Tanggal_Berobat'] = data.get('Tanggal_Berobat', None)
    data['Keluhan'] = data.get('Keluhan', None)
    data['Diagnosis'] = data.get('Diagnosis',None)
    data['Resep'] = data.get('Resep',None)
    data['Status'] = data.get('Status',None)
    data['reservasi'] = data.get('reservasi', None)
    return jsonify(create_detail_berobat(data))

@app.route('/api/detail_berobat', methods=['GET'])
def get_all_detail_berobat():
    return jsonify(get_all_detail_berobat_data())

@app.route('/api/detail_berobat/<int:detail_id>', methods=['GET'])
def get_detail_berobat_by_id(detail_id):
    return jsonify(get_detail_berobat_data_by_id(detail_id))

@app.route('/api/detail_berobat/<int:detail_id>', methods=['PUT'])
def update_detail_berobat(detail_id):
    data = json.loads(request.data)
    return jsonify(update_detail_berobat_data(detail_id, data))

@app.route('/api/detail_berobat/<int:detail_id>', methods=['DELETE'])
def delete_detail_berobat(detail_id):
    return jsonify(delete_detail_berobat_data(detail_id))
# Routes Dokter
@app.route('/api/dokter', methods=['POST'])
def add_dokter():
    data = json.loads(request.data)
    return jsonify(create_dokter(data))

@app.route('/api/dokter', methods=['GET'])
def get_all_dokter_route():
    return jsonify(get_all_dokter())

@app.route('/api/dokter/<int:dokter_id>', methods=['GET'])
def get_dokter_route(dokter_id):
    return jsonify(get_dokter_by_id(dokter_id))

@app.route('/api/dokter/<int:dokter_id>', methods=['PUT'])
def update_dokter_route(dokter_id):
    data = json.loads(request.data)
    return jsonify(update_dokter(dokter_id, data))

@app.route('/api/dokter_delete/<int:dokter_id>', methods=['GET'])
def delete_dokter_route(dokter_id):
    return jsonify(delete_dokter(dokter_id))

@app.route('/api/info_pemesanan', methods=['POST'])
def get_info_pemesanan():
    try:
        data = json.loads(request.data)
        id_pasien = data.get('ID_Pasien')

        # Get the current date in the 'Y-m-d' format
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Fetch the appointment details for the specified patient on the current date
        sql_query = text("""
            SELECT
                pasien.Nama AS PasienNama,
                dokter.Nama AS DokterNama,
                detail_berobat.Tanggal_Berobat,
                detail_berobat.Keluhan,
                detail_berobat.Diagnosis,
                detail_berobat.Resep,
                detail_berobat.Status,
                detail_berobat.reservasi
            FROM
                pasien
            JOIN detail_berobat ON pasien.ID_Pasien = detail_berobat.ID_Pasien
            JOIN dokter ON detail_berobat.ID_Dokter = dokter.ID_Dokter
            WHERE
                pasien.ID_Pasien = :id_pasien
                AND DATE(detail_berobat.Tanggal_Berobat) = :current_date
        """)

        query_result = db.engine.execute(sql_query, id_pasien=id_pasien, current_date=current_date)

        result = []
        for row in query_result:
            result.append({
                'PasienNama': row.PasienNama,
                'DokterNama': row.DokterNama,
                'Tanggal_Berobat': row.Tanggal_Berobat.strftime('%Y-%m-%d %H:%M:%S'),
                'Keluhan': row.Keluhan,
                'Diagnosis': row.Diagnosis,
                'Resep': row.Resep,
                'Status': row.Status,
                'reservasi': row.reservasi
            })

        return jsonify(result)

    except Exception as e:
        return {'error': str(e)}, 500

def archive_data(start_date, end_date):
    # Construct the raw SQL query to select and delete data within the specified date range
    sql_query = text("SELECT * FROM detail_berobat WHERE Status='Archived' and Tanggal_Berobat BETWEEN :start_date AND :end_date ")
    params = {'start_date': start_date, 'end_date': end_date}

    # Execute the raw SQL query
    result = db.engine.execute(sql_query, **params)

    # Fetch the results
    rows = result.fetchall()
    print(rows)
    # Export the data to CSV
    csv_file_path = 'archived_data.csv'
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(result.keys())  # Write header
        csv_writer.writerows(rows)          # Write data

    # Construct the raw SQL query to delete data within the specified date range
    delete_query = text("DELETE FROM detail_berobat WHERE Status='Archived' AND Tanggal_Berobat BETWEEN :start_date AND :end_date ")

    # Execute the raw SQL query to delete the data
    db.engine.execute(delete_query, **params)

    return csv_file_path

@app.route('/arsip_tujuan', methods=['POST'])
def arsip_tujuan():
    try:
        # Parse input JSON data
        data = request.get_json()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        # Convert input date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Archive data, export to CSV, and delete from the database
        csv_file_path = archive_data(start_date, end_date)

        return jsonify({"message": "Data archived successfully", "csv_file_path": csv_file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pasien', methods=['POST'])
def add_pasien():
    data = json.loads(request.data)

    unique_id = str(uuid.uuid4())

    # Hash the UUID using MD5 (you can choose a different hash algorithm if needed)
    hashed_id = hashlib.md5(unique_id.encode()).hexdigest()
    data['ID_Pasien'] = hashed_id
    data['Password']=data.get('password',None)
    return jsonify(create_pasien(data))
@app.route('/api/pasien2', methods=['POST'])
def add_pasien2():
    data = json.loads(request.data)
    return jsonify(create_pasien(data))

@app.route('/api/pasien', methods=['GET'])
def get_all_pasien_route():
    return jsonify(get_all_pasien())

@app.route('/api/pasien/<int:pasien_id>', methods=['GET'])
def get_pasien_route(pasien_id):
    return jsonify(get_pasien_by_id(pasien_id))

@app.route('/api/pasien/<int:pasien_id>', methods=['PUT'])
def update_pasien_route(pasien_id):
    data = json.loads(request.data)
    return jsonify(update_pasien(pasien_id, data))

@app.route('/api/pasien_delete/<int:pasien_id>', methods=['GET'])
def delete_pasien_route(pasien_id):
    return jsonify(delete_pasien(pasien_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
