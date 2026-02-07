import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from typing import Optional

cli = typer.Typer()

@cli.command()
def initialize():
    """
    Docstring for initialize
    """
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")


if __name__ == "__main__":
    cli()


@cli.command()
def get_user(username:str = typer.Argument(..., help="The username of the user to retrieve")):
    """
    Docstring for get_user
    
    :param username: Description
    :type username: str
    """

    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)


@cli.command()
def get_all_users():
    """
    Docstring for get_all_users
    """

    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str = typer.Argument(..., help="The username of the user whose email is to be changed"), 
                 new_email:str = typer.Argument(..., help="The new email address")
                 ):
    """
    Docstring for change_email
    
    :param username: Description
    :type username: str
    :param new_email: Description
    :type new_email: str
    """

    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str = typer.Argument(..., help="The username of the new user"), 
                email:str = typer.Argument(..., help="The email of the new user"), 
                password: str = typer.Argument(..., help="The password of the new user")
                ):
    """
    Docstring for create_user
    
    :param username: Description
    :type username: str
    :param email: Description
    :type email: str
    :param password: Description
    :type password: str
    """

    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user 

@cli.command()
def delete_user(username: str = typer.Argument(..., help="The username of the user to delete")):
    """
    Docstring for delete_user
    
    :param username: Description
    :type username: str
    """

    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command()
def findUser(username: Optional[str] = typer.Argument(None, help="The username to search for"),
              email: Optional[str] = typer.Argument(None, help="The email to search for")):
    """
    Docstring for findUser
    
    :param username: Description
    :type username: Optional[str]
    :param email: Description
    :type email: Optional[str]
    """

    with get_session() as db:
        query = select(User)  

        if username and email:
            query = query.where(
            (User.username.contains(username)) |
            (User.email.contains(email))
            )

        elif username:
            query = query.where(User.username.contains(username))
        elif email:
            query = query.where(User.email.contains(email))
        users = db.exec(query).all()

        if not users:
            print("No users found..")
        else:
            for user in users:
                print(user)

@cli.command()
def listNUsers(limit: Optional[int] = typer.Argument(10, help="The number of users to list"),
                offset: Optional[int] = typer.Argument(0, help="The offset to start listing users from")):
    """
    Docstring for listNUsers
    
    :param limit: Description
    :type limit: Optional[int]
    :param offset: Description
    :type offset: Optional[int]
    """

    with get_session() as db:
        users = db.exec(select(User).limit(limit).offset(offset)).all()
        if not users:
            print("No users found..")
        else:
            for user in users:
                print(user)

