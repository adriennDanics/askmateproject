import time
import connection
import user_handling

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def display_time(act_time):
    """
    :param act_time as a float: the UNIX timestamp
    :returns date as a string: 'yyyy.mm.dd hh:mm'
    """
    act_time = time.localtime(act_time)
    year = str(act_time.tm_year)
    month = str(act_time.tm_mon)
    month = '0' + month if len(month) < 2 else month
    day = str(act_time.tm_mday)
    day = '0' + day if len(day) < 2 else day
    hour = str(act_time.tm_hour)
    hour = '0' + hour if len(hour) < 2 else hour
    minute = str(act_time.tm_min)
    minute = '0' + minute if len(minute) < 2 else minute
    date = ".".join([year, month, day])
    hour_minute = ":".join([hour, minute])
    result = " ".join([date, hour_minute])
    return result


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def display_unix_time():
    """
    :returns UNIX timestamp of current time as a float
    """
    return time.time()


@connection.connection_handler
def get_all_tags(cursor):
    """
    :param:  -
    :return: Return a disctionary with the following keys: name, id, count_tag
    """
    cursor.execute("""SELECT name, id, COUNT(id) AS count_tag 
                      FROM tag
                      JOIN question_tag ON tag.id = question_tag.tag_id
                      GROUP BY id
                      ORDER BY count_tag DESC
                      LIMIT 7 """)
    return cursor.fetchall()


@connection.connection_handler
def get_tags_by_question_id(cursor, question_id):
    cursor.execute("""SELECT name FROM tag 
                      INNER JOIN question_tag ON question_tag.tag_id=tag.id 
                      WHERE question_id=%(q_id)s;""",
                   {'q_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def add_new_tag(cursor, tag_name):
    cursor.execute("""INSERT INTO tag (name) 
                      VALUES (%(name)s);""", {'name': tag_name})
    cursor.execute("""SELECT id FROM tag
                      WHERE name = %(t_name)s;""", {'t_name': tag_name})
    return cursor.fetchone()


@connection.connection_handler
def create_question_tag_relation(cursor, question_id, tag_id):
    cursor.execute("""
                    SELECT * FROM question_tag
                    WHERE question_id=%(qid)s
                    AND
                    tag_id=%(tid)s;
                    """, {'qid': question_id, 'tid': tag_id})
    if not cursor.fetchone():
        cursor.execute("""INSERT INTO question_tag (question_id, tag_id)
                          VALUES (%(q_id)s, %(t_id)s);""",
                       {'q_id': question_id, 't_id': tag_id})


@connection.connection_handler
def add_tag_to_question(cursor, question_id, tag_name):
    cursor.execute("""SELECT id FROM tag
                      WHERE name = %(t_name)s;""",
                   {'t_name': tag_name})
    result = cursor.fetchone()
    if result:
        create_question_tag_relation(question_id, result['id'])
    else:
        tag_id = add_new_tag(tag_name)['id']
        create_question_tag_relation(question_id, tag_id)


@connection.connection_handler
def remove_tag_from_question(cursor, tag_name, question_id):
    cursor.execute("""
                    SELECT id FROM tag
                    WHERE name = %(t_name)s;
                    """,
                   {'t_name': tag_name})
    result = cursor.fetchone()
    tag_id = result['id']
    cursor.execute("""
                    DELETE FROM question_tag
                    WHERE question_id=%(q_id)s
                    AND
                    tag_id=%(tag_id)s;
                    """,
                   {'q_id': question_id, 'tag_id': tag_id})


@connection.connection_handler
def delete_answer(cursor, answer_id):
    user_handling.delete_comment_by_answer(answer_id)
    cursor.execute("""
                    DELETE FROM answer
                    WHERE id = %(answer_id)s;
                  """, {'answer_id': answer_id})


@connection.connection_handler
def delete_question_and_answers(cursor, question_id):
    user_handling.delete_answer_comment_by_question_id(question_id)
    user_handling.delete_comment_by_question(question_id)
    cursor.execute("""
                    DELETE FROM answer
                    WHERE question_id=%(qid)s;
                    """, {'qid': question_id})
    cursor.execute("""
                    DELETE FROM question_tag
                    WHERE question_id=%(question_id)s;
                    """, {'question_id': question_id})
    cursor.execute("""
                    DELETE FROM question
                    WHERE id=%(qid)s;
                    """, {'qid': question_id})


@connection.connection_handler
def show_comment_question(cursor, question_id):
    cursor.execute("""SELECT id, message FROM comment WHERE question_id = %(q_id)s;""",
                   {'q_id': question_id})
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def add_comment_to_question(cursor, new_comment):
    cursor.execute("""INSERT INTO comment(question_id, message, submission_time, user_id) VALUES 
                      (%(question_id)s, %(message)s, %(submission_time)s, %(user_id)s);""", new_comment)


@connection.connection_handler
def show_comment_answer(cursor, answer_id):
    cursor.execute("""SELECT * FROM comment WHERE answer_id = %(a_id)s;""",
                   {'a_id': answer_id})
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def add_comment_to_answer(cursor, new_comment):
    cursor.execute("""INSERT INTO comment(answer_id, message, submission_time, user_id) VALUES 
                      (%(answer_id)s, %(message)s, %(submission_time)s, %(user_id)s);""", new_comment)
