from sqlmodel import create_engine,SQLModel,Session


DATABASE_URL = f"mysql+pymysql://root:{'ZYQ5241@@'}@9.134.130.69:3306/test"

#engine = create_engine(DATABASE_URL, echo=True, future=True)
engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    result = session.exec("SELECT id,fieldKey from config")
    print(result.one())
