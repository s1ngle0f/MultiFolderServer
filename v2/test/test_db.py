from v2.server.models import *

with db:
    # db.create_tables([User, Directory, File])
    # path = 'C:\\Users\\zubko\\Desktop\\DATA\\zubkov\\new.txt'
    # print(os.path.getmtime(path)) # 1672440980.775274
    # print(os.path.getmtime('C:\\Users\\zubko\\Desktop\\DATA\\zubkov\\creating_files\\change.txt')) #
    # User.create(login='admin', password='admin')
    # user_id = User.select().where(User.login == "admin")[0].id
    # Directory.create(name='txts', user_id=user_id)
    # directory_id = Directory.select().where(Directory.name == "txts")[0].id
    # with open(path, 'rb') as f:
    #     File.create(directory_id=directory_id, name=f.name, path=path, timestamp=os.path.getmtime(path), size=os.path.getsize(path), data=f.read())

    # files = File.select().join(Directory)
    # for file in files:
    #     print(file.id, file.directory_id.name, file.name, file.path, file.timestamp, file.size, file.data)
    #     timestamp = time.mktime(datetime.datetime.strptime(str(file.timestamp), "%Y-%m-%d %H:%M:%S").timetuple())
    #     print(timestamp)
    #     print(round(1672440979.775274) < round(timestamp))
        # with open('C:\\Users\\zubko\\Desktop\\DATA\\zubkov\\creating_files\\' + os.path.basename(file.name), 'a+') as f:
        #     f.write(file.data)
    dir = Directory.select().where((Directory.name == "ЗубковМБП") & (Directory.user_id == 1)).first()
    print(dir.id)