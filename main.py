from sqlalchemy import create_engine, Column, Integer, Text, UniqueConstraint, CheckConstraint, MetaData, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import json


with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.loads(config_file.read())

if config['DEBUG']:
    engine = create_engine('sqlite:///project.db', echo=True)
else:
    db_user = config['db_user']
    db_password = config['db_password']
    db_host = config['db_host']
    db_port = config['db_port']
    db_name = config['db_name']

    engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}", echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class CustomerInfo(Base):
    __tablename__ = 'customer_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(150), nullable=False, unique=True)
    tc = Column(String(11), nullable=False, unique=True)
    gender = Column(Integer)
    age = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('age > 18', name='check_age'),
        # CheckConstraint('age > 18', name='check_age'),
        UniqueConstraint('email', name='uq_email'),
        UniqueConstraint('phone', name='uq_phone'),
    )


class CustomerSurveyQuestions(Base):
    __tablename__ = 'customer_survey_questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text(), nullable=False)
    answers = relationship("CustomerSurveyAnswers", back_populates="question")


class CustomerSurveyAnswers(Base):
    __tablename__ = 'customer_survey_answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(Text(), nullable=False)
    question_id = Column(Integer, ForeignKey('customer_survey_questions.id'))
    question = relationship("CustomerSurveyQuestions", back_populates="answers")


class SurveyCollector(Base):
    __tablename__ = 'survey_collector'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer_info.id'))  # Buraya doğru ForeignKey tanımını ekleyin
    survey_question_id = Column(Integer, ForeignKey('customer_survey_questions.id'))
    survey_answers_id = Column(Integer, ForeignKey('customer_survey_answers.id'))


def write_database():
    Base.metadata.create_all(engine)


def create_questions():
    with open('questions', 'r', encoding='utf-8') as questions_file:
        questions = [
            CustomerSurveyQuestions(question=question) for question in questions_file.read().split('\n')
        ]
    session.add_all(questions)
    session.commit()


def add_user():
    customer = CustomerInfo(
        name=input('name : '),
        password=input('password : '),
        email=input('email : '),
        phone=input('phone : '),
        tc=input('tc : '),
        gender=1 if input('gender E/K : ').lower() == 'e' else 0,
        age=int(input('age : ')),
    )
    session.add(customer)
    session.commit()


def answer_questions():
        user_id = input('customer id (int) : ')
        for question in session.query(CustomerSurveyQuestions).all():
            print(f"Soru: {question.question}")
            answer_text = input("Cevabınız: ")

            # Yeni cevap oluşturun ve kaydedin
            answer = CustomerSurveyAnswers(answer=answer_text, question=question)
            session.add(answer)
            session.commit()

            # Anket bilgilerini toplandığı tabloya ekleyin
            survey_collector = SurveyCollector(
                customer_id=user_id,
                survey_question_id=question.id,
                survey_answers_id=answer.id  # Burada answer.id'yi kullanamazsınız
            )
            session.add(survey_collector)
            session.commit()


try:
    while True:
        select = input("""
        1. Write DB
        2. Create Questions
        2. Answer Questions
        4. Add New User
        5.E Exit
        >>> : """)
        if select == '1':
            write_database()
        elif select == '2':
            create_questions()
        elif select == '3':
            answer_questions()
        elif select == '4':
            add_user()
        else:
            break

except Exception as exception:
    print('error alındı log.txt')
    with open('log.txt', 'a+', encoding='utf-8') as log:
        log.write(str(exception))
finally:
    session.close()


