from app.db import User, Board

async def create_dummy_user(create_num):
    try:
        for i in range(create_num):
            print('i: ', i)
            data = {
                "email": f"email-{i}@test.com",
                "username": f"user-{i}",
                "password": f"1q2w3e4r!@#"
            }
            await User(**data).save()
    except Exception as e:
        print(e)
        return False
    return True

async def create_dummy_board(create_num):
    try:
        user_list = await User.objects.all()
        for i, user in enumerate(user_list):
            data = {
                "title": f"title-{i}",
                "content": f"content-{i}",
                "writer": user
            }
            await Board(**data).save()
    except Exception as e:
        print(e)
        return False
    return True
