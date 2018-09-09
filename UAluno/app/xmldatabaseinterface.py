from app import BaseXClient
import xml.dom.minidom
from lxml import etree
from django.conf import settings

# Check if database exists
def database_exists(dbname):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        # create empty database
        db_content = session.execute("xquery doc('"+dbname+"')")

    except Exception as e:
        # If this exception occurs, database does not exist
        return False

    finally:
        if session:
            session.close()

    return True

# Function to create database, with input file of database
def create_database(dbname, infile_name, xml_schema):
    doc = xml.dom.minidom.parse(infile_name)
    content = doc.toxml()

    return create_databasefromstring(dbname, content, xml_schema)

# Function to create database, with input file of database
def create_databasefromstring(dbname, content, xml_schema):

    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        parser = etree.XMLParser(encoding='utf-8')
        tree = etree.fromstring(content.encode('utf-8'), parser)

    except Exception as e:
        print(repr(e))
        raise e

    try:
        # Validate with xml schema
        with open(xml_schema) as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            if not xmlschema.validate(tree):
                return False
    except:
        raise FileNotFoundError("Could not find schema")

    try:
        # Create db and add content
        session.create(dbname, content)

    except Exception as e:
        print(repr(e))
        raise e


    finally:
        if session:
            session.close()

    return True

# Drop dname database
def drop_database(dbname):

    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        drop_query = "drop db "+ dbname
        session.execute(drop_query)

    except Exception as e:
        print(repr(e))
        raise e


    finally:
        if session:
            session.close()

# Returns the entire database
def getAllDatabase(db, schema_file):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        # run query on database
        db_content = session.execute("xquery doc('"+db+"')")

    except Exception as e:
        raise Exception("Database not found")

    try:
        xml_schema = schema_file
        # Validate with xml schema
        with open(xml_schema) as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            parser = etree.XMLParser(encoding='utf-8')
            tree = etree.fromstring(db_content, parser=parser)

            if not xmlschema.validate(tree):
                raise Exception("Could not validate the schema on the database")
    except:
        raise FileNotFoundError("Could not find the schema")

    finally:
        if session:
            session.close()

    return db_content

# Get database of chat
def get_chat_database():
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        # run query on database
        db_content = session.execute("xquery doc('uachat')")

    except Exception as e:
        raise Exception("Chat database not found")

    try:
        xml_schema = settings.XML_FILES + "/chat.xsd"
        # Validate with xml schema
        with open(xml_schema) as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            parser = etree.XMLParser(encoding='utf-8')
            tree = etree.fromstring(db_content, parser=parser)

            if not xmlschema.validate(tree):
                raise Exception("Could not validate the schema on the database")
    except:
        raise FileNotFoundError("Could not find the chat schema")

    finally:
        if session:
            session.close()

    return tree

# Insert user message into chat
def insertMessage(id, name, timestamp, message):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    try:

        # create insert query
        node = '<message id="' + str(id) + '" timestamp="' + str(timestamp) + '" name="' + str(name) + '">' + str(
            message) + '</message>'
        query = session.query('let $messages:=doc("uachat")/chat return insert node ' + node + ' into doc("uachat")/chat')

        # Execute query
        query.execute()
        query.close()

    except Exception as e:
        print(repr(e))
        # Message was not inserted
        return False

    finally:
        if session:
            session.close()
    return True

# Insert user course
def insertCourse(id, name, ects, area, year, semester, grade):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    try:
        # Check if student already exists
        student_exists = session.execute("xquery for $student in doc('gradesdatabase')/students/student where $student/@id=\""+str(id)+"\" return $student")
        if student_exists:
            # Check if course already registered
            course_exists = session.execute("xquery for $student in doc('gradesdatabase')/students/student where $student/@id=\""+str(id)+"\" return $student/course/@name=\""+str(name)+'"')

            if course_exists == 'false':
                # Create new node
                node = '<course name="' + str(name) + '" ects="' + str(ects) + '" area="' + str(area) + '" year="' + str(year) + '" semester="' + str(semester) + '"><grade>' + str(grade) + '</grade></course>'
                # Insert new course
                session.execute('xquery for $student in doc("gradesdatabase")/students/student where $student/@id="'+str(id)+'" return insert node '+node+' into $student')
            else:
                return False
        else:
            node = '<student id="'+str(id)+'"><course name="'+str(name)+'" ects="'+str(ects)+'"' \
            ' area="'+str(area)+'" year="'+str(year)+'" semester="'+str(semester)+'"><grade>'+str(grade)+'</grade></course></student>'

            query = session.query('insert node ' + node + ' into doc("gradesdatabase")/students')

            # Execute query
            query.execute()
            query.close()

    except Exception as e:
        print(repr(e))
        return False
    finally:
        if session:
            session.close()

    return True

# Delete user course
def deleteCourse(id, name):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
    try:
        # Check if student already exists
        student_exists = session.execute("xquery for $student in doc('gradesdatabase')/students/student where $student/@id=\"" + str(id) + "\" return $student")
        if student_exists:
            # Check if course already registered
            course_exists = session.execute("xquery for $student in doc('gradesdatabase')/students/student where $student/@id=\"" + str(id) + "\" return $student/course/@name=\"" + str(name) + '"')

            if course_exists == 'true':
                # Delete node
                query = session.query('let $courses := for $student in doc("gradesdatabase")/students/student where $student/@id=\"' + str(id) + '" return $student/course ' \
                              'let $course := for $course in $courses where $course/@name="' + str(name) + '" return $course return delete node $course')

                # Execute query
                query.execute()
                query.close()
            else:
                return False
        else:
            return False

    except Exception as e:
        print(repr(e))
        return False
    finally:
        if session:
            session.close()

    return True

# Get all courses with grades from a student
def getAllCoursesFromStudent(student_id):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        # run query on database
        db_content = session.execute("xquery for $student in doc('gradesdatabase')/students/student where $student/@id=\""+str(student_id)+"\" return $student")

    except Exception as e:
        raise Exception

    finally:
        if session:
            session.close()

    if(not db_content):
        return None
    else:
        # Create parser
        parser = etree.XMLParser(encoding='utf-8')
        # Parse courses from xml string
        courses = etree.fromstring(db_content, parser=parser)

        return courses

# Get all categories of news
def getAllNewsCategories():
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        cath = []
        # run query on database
        query = session.query("for $name in collection('departments')/departamentos//item/nome/text() return $name")
        for tc, item in query.iter():
            cath += [item]

    except Exception as e:
        raise Exception

    finally:
        if session:
            session.close()

    return cath

# Get ID of category by name
def getCategoryIdByName(name):
    session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')

    try:
        # run query on database
        id = session.execute("xquery for $item in collection('departments')/departamentos//item where $item/nome='"+name+"' return $item/guid/text()")

    except Exception as e:
        raise Exception

    finally:
        if session:
            session.close()

    return id

# Updates the database with new content
def updateDatabase(db, xml_schema, newcontent):
    drop_database(db)
    return create_databasefromstring(db, newcontent, xml_schema)

# Create databases if they do not exist
if ( not database_exists("gradesdatabase") ):
    create = create_database("gradesdatabase", settings.XML_FILES + "/gradesdatabase.xml", settings.XML_FILES + "/grades.xsd")
    if (not create):
        raise NotImplementedError("Schema is not validating the grades xml file")

if ( not database_exists("uachat") ):
    create = create_database("uachat", settings.XML_FILES + "/chatdatabase.xml", settings.XML_FILES + "/chat.xsd")
    if(not create):
        raise NotImplementedError("Schema is not validating the chat xml file")

if ( not database_exists("departments") ):
    create = create_database("departments", settings.XML_FILES + "/departmentsdatabase.xml",
                                settings.XML_FILES + "/departments.xsd")
    if (not create):
        raise NotImplementedError("Schema is not validating the departments xml file")

# Create backup databases
if ( not database_exists("weather") ):
    create = create_database("weather", settings.XML_FILES + "/backup_rss/weather.xml",
                                settings.XML_FILES + "/weather.xsd")
    if (not create):
        raise NotImplementedError("Schema is not validating the weather xml file")

if ( not database_exists("ementas") ):
    create = create_database("ementas",
                            settings.XML_FILES + "/backup_rss/ementas.xml",
                            settings.XML_FILES + "/ementas.xsd")
    if (not create):
        raise NotImplementedError("Schema is not validating the ementas xml file")

if ( not database_exists("news") ):
    create = create_database("news",
                            settings.XML_FILES + "/backup_rss/news.xml",
                            settings.XML_FILES + "/news.xsd")
    if (not create):
        raise NotImplementedError("Schema is not validating the news xml file")
