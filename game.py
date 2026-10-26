class Esm_famil_player_game:
    def start(self):
        players = list()
        number_of_players = int(input("How many number_of_players want to play? "))
        if number_of_players > 0:
            for i in range(number_of_players):
                name_of_player = input("What is your name?: ")
                print(f"Welcome to game {name_of_player} !!")
                players.append(name_of_player)  
            page = []
            list_of_objects = []
            dict_of_objects = dict()
            items = input("What is your item: ").split()
            same_word = input("What is the same word? ")
            if len(same_word) == 1:
                for i in range(len(players)):
                    for item in items:
                        answer_part = input(f"What is your answer for {item} {players[i]}: ")
                        if answer_part[0] == same_word[0]:
                            part = {item : answer_part}
                            list_of_objects.append(part)
                            print(list_of_objects)
                            
                        else:
                            print("Your answer isn't correct !!")
                            break            
                    else:
                        print("error")
                        print("The game can't number the same word.")  

        elif number_of_players <= 0:
                print("The game can't numbered the number_of_players.")


game = Esm_famil_player_game()
game.start()