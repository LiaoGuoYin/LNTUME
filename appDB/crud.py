import datetime
from functools import wraps

from sqlalchemy.orm import Session

from app import schemas, exceptions
from appDB import models


def update_user(user: schemas.User, session: Session) -> models.User:
    new_user = models.User(**user.dict())
    new_user.lastUpdatedAt = datetime.datetime.now()
    session.merge(new_user)
    session.commit()
    return new_user


def update_info(user_info: schemas.UserInfo, session: Session) -> models.UserInfo:
    new_user_info = models.UserInfo(**user_info.dict())
    session.merge(new_user_info)
    session.commit()
    return new_user_info


def update_course_table(course_table_list: [schemas.CourseTable], session: Session):
    for course in course_table_list:
        new_course = models.CourseTable(**course.dict())
        session.merge(new_course)
    session.commit()


def update_grade_list(user: schemas.User, grade_list: [schemas.Grade], session: Session):
    for grade in grade_list:
        new_grade = models.Grade(username=user.username, **grade.dict())
        session.merge(new_grade)
    session.commit()


def update_gpa(user: schemas.User, grade_gpa: schemas.GPA, session: Session) -> models.GPA:
    new_gpa = models.GPA(username=user.username, **grade_gpa.dict())
    session.merge(new_gpa)
    session.commit()
    return new_gpa


def update_aipao_order(student: schemas.AiPaoUser, session: Session) -> models.AiPaoOrder:
    new_user = models.AiPaoOrder(**student.dict(exclude={'token'}))
    session.merge(new_user)
    session.commit()
    return new_user


# Login Decorator Function
def server_user_valid_required(function_to_wrap):
    @wraps(function_to_wrap)
    def wrap(request_user: schemas.User, session: Session, *args, **kwargs):
        server_user = session.query(models.User).filter_by(username=request_user.username).first()
        if not server_user:
            # Check user server account validation
            raise exceptions.FormException(F"离线模式: {request_user.username} 用户无效，请稍后再试，可能是未曾登录过 LNTUHelper")
        else:
            if request_user.password != server_user.password:
                raise exceptions.FormException(F"离线模式: {request_user.username} 用户名或密码错误")
            else:
                # Authenticated successfully
                return function_to_wrap(request_user, session, *args, **kwargs)

    return wrap


@server_user_valid_required
def retrieve_user_info(request_user: schemas.User, session: Session) -> dict:
    return dict(session.query(models.UserInfo).filter_by(username=request_user.username).first().__dict__)


@server_user_valid_required
def retrieve_user_grade(request_user: schemas.User, session: Session) -> list:
    grade_list = session.query(models.Grade).filter_by(username=request_user.username).all()
    return list(grade_list)


@server_user_valid_required
def retrieve_user_gpa(request_user: schemas.User, session: Session) -> dict:
    return dict(session.query(models.GPA).filter_by(username=request_user.username).first().__dict__)

# TODO
# @server_user_valid_required
# def retrieve_user_course_table(request_user: schemas.User, session: Session) -> dict:
#     return dict(session.query(models.CourseTable).filter_by(username=request_user.username).first().__dict__)
