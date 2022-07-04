from .models import VK, Person

def main():
    p = Person.objects.all()
    print(p)
    user_id = VK.objects.filter(user_id='123')
    print(user_id)


if __name__ == '__main__':
    main()