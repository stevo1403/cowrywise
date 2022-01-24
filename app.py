import uuid
import time
import json
from datetime import datetime

from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
app = Flask(__name__)

engine = create_engine("sqlite:///id_store.db")
Session = sessionmaker(bind=engine)

class TaskID(Base):
    __tablename__ = 'task_ids'
    #primary key for the table
    id = Column(name='id', type_=Integer, primary_key=True)
    #timestamp in which the uuid was generated
    t_timestamp = Column(String(50), nullable=False)
    #32-bytes long UUIDv4
    t_uuid = Column(String(50), nullable=False)
    #raw epoch timestamp
    r_timestamp = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<TaskID(t_uuid='{self.t_uuid}' t_timestamp='{self.t_timestamp} r_timestamp='{self.r_timestamp}')>"

#Base.metadata.drop_all(engine, Base.metadata.tables.values(), checkfirst=True)
Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)

@app.route("/ids", methods=['GET'])
def get_ids():
    with Session() as session:
        
        t_uuid = uuid.uuid4().hex
        dt = datetime.now()
        r_timestamp = int(dt.timestamp())
        t_timestamp = dt.strftime(f"%Y-%m-%d %I:%M:%S.%f")

        task = TaskID(t_timestamp=t_timestamp, t_uuid=t_uuid, r_timestamp=r_timestamp)
        session.add(task)
        session.flush()
        session.commit()

        result = session.query(TaskID).order_by(TaskID.t_timestamp.desc()).all()

        data = {}
        for item in result:
            data[item.t_timestamp] =  item.t_uuid
        
        j_data = json.dumps(data, indent=2)
        response = app.make_response(j_data)
        return response

if __name__ == '__main__':
    #start the development server on port 5000.
    app.run(host='localhost', port='5000', debug=False)

