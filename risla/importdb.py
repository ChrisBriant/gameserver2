import pandas as pd
from .models import Person
from datetime import datetime
from .models import Person

#Import from CSV into database
def importdb(wipe=False):
    if wipe:
        people = Person.objects.all()
        for person in people:
            person.delete()

    import_data = pd.read_csv('../people.csv',error_bad_lines=False)
    for i in range(len(import_data)):
    #for i in range(10):
        try:
            birthyear = int(import_data.loc[i,'birthyear'])
        except Exception as e:
            birthyear = None
        try:
            birthdate = datetime.strptime(str(import_data.loc[i,'birthdate']), '%Y-%m-%d')
        except Exception as e:
            birthdate = None
        try:
            deathdate = datetime.strptime(str(import_data.loc[i,'deathdate']), '%Y-%m-%d')
        except Exception as e:
            deathdate = None
        try:
            age = int(import_data.loc[i,'age'])
        except Exception as e:
            age = None

        try:
            Person.objects.create(
                slug = import_data.loc[i,'slug'],
                name = import_data.loc[i,'name'],
                occupation = import_data.loc[i,'occupation'],
                bplace_country = import_data.loc[i,'bplace_country'],
                birthdate = birthdate,
                birthyear = birthyear,
                dplace_name = import_data.loc[i,'dplace_name'],
                dplace_country =  import_data.loc[i,'dplace_country'],
                deathdate = deathdate,
                age = age
            )
        except Exception as e:
            print('error')
