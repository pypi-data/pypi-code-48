# __main__.py


from random_generator import RandomGen

def main():
    random_generator = RandomGen()
    random_number = random_generator.next_num()
    print(random_number)

if __name__ == "__main__":
    main()
