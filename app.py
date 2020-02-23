from ariadne import QueryType, graphql_sync, make_executable_schema, ObjectType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify


studentID = 1
classID = 1

DB = {
    "students": [],
    "classes": [],
}

type_defs = """
    type Query {
        hello: String!
        getStudent(id: ID!): Student
        getClass(id: ID!): CClass
    }

    type Mutation {
        createStudent(name: String!): Student!
        createClass(name: String!): CClass!
        addStudentToClass(sID: ID!, cID: ID!): CClass
    }

    type Student {
        id: ID!
        name: String!
    }

    type CClass {
        id: ID!
        name: String!
        students: [Student]
    }

"""

query = QueryType()
mutation = MutationType()
student = ObjectType('Student')
cclass = ObjectType('CClass')

@query.field("hello")
def resolve_hello(_, info):
    request = info.context
    user_agent = request.headers.get("User-Agent", "Guest")
    return "Hello, %s!" % user_agent

@mutation.field('createStudent')
def createStudent(_, info, name):
    global studentID
    # request = info.context
    currentID = studentID
    DB['students'].append({
        'id': currentID,
        'name': name
    })
    studentID += 1
    return DB['students'][currentID-1]

@query.field('getStudent')
def getStudent(_, info, id):
    id = int(id)
    if(id >= studentID or id <= 0):
        return None
    return DB['students'][id-1]
    # for student in DB['students']:
    #     if student['id'] == id:
    #         return student

@mutation.field('createClass')
def createClass(_, info, name):
    global classID
    currentID = classID
    DB['classes'].append({
        'id': currentID,
        'name': name,
        'students': []
    })
    classID += 1
    return DB['classes'][currentID-1]

@query.field('getClass')
def getClass(_, info, id):
    id = int(id)
    if(id >= classID or id <= 0):
        return None
    return DB['classes'][id-1]

@mutation.field('addStudentToClass')
def addStudentToClass(_, info, sID, cID):
    sID = int(sID)
    cID = int(cID)
    if cID >= classID or cID <= 0:
        return None
    if sID >= studentID or sID <= 0:
        return None
    if not studentAlreadyInClass(sID, cID):
        DB['classes'][cID-1]['students'].append(
            DB['students'][sID-1]
        )
    return DB['classes'][cID-1]
    
def studentAlreadyInClass(sID, cID):
    students = DB['classes'][cID-1]['students']
    for student in students:
        if student['id'] == sID:
            return True
    return False


schema = make_executable_schema(type_defs, [query, mutation, student,cclass])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)