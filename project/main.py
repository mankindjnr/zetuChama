from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .database import get_manager, get_member, get_chamas_by_manager, get_all_chamas, get_tables
from .models import Chamas
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from . import db

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
  id_value = request.args.get('id')
  username = request.args.get('username')
  return render_template('home.html', id=id_value, name=username)

@main.route('/about', methods=['GET'])
def about():
  return render_template('about.html')

@main.route("/view")
def views():
  chama_name = request.args.get('name')
  id_value = request.args.get('id')
  manager = request.args.get('manager')

  query = text(f"SELECT * FROM {chama_name}")
  result = db.session.execute(query)

  column_names = result.keys()
  table_list = []

  for row in result:
    row_dict = {}

    for column_name, value in zip(column_names, row):
      row_dict[column_name] = value

    table_list.append(row_dict)

  table_data = table_list

  return render_template("view.html", table=table_data, name=chama_name, manager=manager, id=id_value)



@main.route("/deposit", methods=['POST'])
def deposit():
  sumof = float(request.form['amount'])
  chama_name = request.form['chama_name']
  id_val = int(request.form['id'])


  #updating the money column
  query = text(f"UPDATE {chama_name} SET sumof = sumof + :sumof WHERE member_id = :id_val")

  db.session.execute(query, {"sumof": sumof, "id_val": id_val})
  db.session.commit()

  return redirect(url_for('main.views', name=chama_name, id=id_val))

@main.route('/chamas')
def chamas():
  all_chamas = get_all_chamas()
  id_value = request.args.get('id')
  username = request.args.get('username')
  return render_template('chamas.html', chamas=all_chamas, id=id_value, name=username)

@main.route('/more')
def more():
  chama_name = request.args.get('name')
  id_value = request.args.get('member_id')
  manager = request.args.get('manager')
  chamas = get_chamas_by_manager(manager)

  # Get the chama that matches the chama_name
  matching_chama = None
  for chama in chamas:
    if chama.get('chama_name') == chama_name:
      matching_chama = chama
      break
  
  return render_template('more_chama.html', member_id=id_value, chama_name=chama_name, manager=manager, chama=matching_chama)

@main.route("/manager/<user_name>")
def manager_from_db(user_name):
  result = get_manager(user_name)
  chamas = get_chamas_by_manager(user_name)
  user_name = user_name

  if not result:
    return jsonify({"error": "Not found"}), 404

  return render_template("leader.html", result=result, user_name=user_name, chamas=chamas)


@main.route('/member/<mem_id>')
def member_from_db(mem_id):
  result = get_member(mem_id)
  all_chamas = get_all_chamas()

  if not result:
    return jsonify({"error": "Not found"}), 404
  
  tables = get_tables(mem_id)

  if not tables:
    mychamas = None
  else:
    mychamas = [d for d in all_chamas if d['chama_name'] in tables]

 
  return render_template("member.html", chamas=chamas, result=result, mychamas=mychamas)


@main.route('/add_chama', methods=['POST'])
def add_chama():
    chama_name = (request.form['chama_name']).replace(' ','_')
    requirements = request.form['requirements']
    description = request.form['description']
    summary = request.form['summary']
    manager = request.form['username']

    new_chama = Chamas(
        chama_name=chama_name,
        requirements=requirements,
        description=description,
        summary=summary,
        manager=manager  # Assign the currently logged in user as the manager
    )
    
    db.session.add(new_chama)
    db.session.commit()

    # Create a new table in the database with the chama_name as the table name
    table_name = chama_name.replace(' ', '_')

    query = text(f"CREATE TABLE {table_name} (member_id INT, name VARCHAR(255), sumof INT)")
    connection = db.engine.connect()
    connection.execute(query)
    connection.close()

    return redirect(url_for('main.manager_from_db', user_name=manager))


@main.route('/edit_chama', methods=['GET'])
def edit_chama():
  manager = request.args.get('manager')
  chama_name = request.args.get('chama_name')
  chamas = get_chamas_by_manager(manager)

  # Get the chama that matches the chama_name
  matching_chama = None
  for chama in chamas:
    if chama.get('chama_name') == chama_name:
      matching_chama = chama
      break

  print(matching_chama)


  return render_template("edit_chama.html", chama_name=chama_name, manager=manager, chama=matching_chama)


@main.route('/update_chama', methods=['POST'])
def update_chama():
  manager = request.form['username']
  chama_name = request.form['chama_name']
  requirements = request.form['requirements']
  description = request.form['description']
  summary = request.form['summary']

  query = text(f"UPDATE chamas SET requirements = :requirements, description = :description, summary = :summary WHERE chama_name = :chama_name")

  db.session.execute(query, {"requirements": requirements, "description": description, "summary": summary, "chama_name": chama_name})
  db.session.commit()

  return redirect(url_for('main.manager_from_db', user_name=manager))

@main.route('/join_chama', methods=['GET'])
def join_chama():
  id_value = request.args.get('id')
  chama_name = request.args.get('name')
  chamaname = chama_name.strip().replace(' ', '_')
  return render_template("join-chama.html", id=id_value, name=chamaname)

@main.route('/add_member_to_chama', methods=['POST'])
def add_member_to_chama():
  member_id = request.form['member_id']
  name = request.form['name']
  sumof = 0
  chama_name = (request.form['chama_name']).replace(' ','_')

  query = text(f"INSERT INTO {chama_name} (member_id, name, sumof) VALUES (:member_id, :name, :sumof)")
  db.session.execute(query, {"member_id": member_id, "name": name, "sumof": sumof})
  db.session.commit()

  return redirect(url_for('main.chamas', id=member_id))



@main.route('/newchama')
@login_required
def newchama():
  username = request.args.get('username')
  return render_template('create_chama.html', user_name=username)


