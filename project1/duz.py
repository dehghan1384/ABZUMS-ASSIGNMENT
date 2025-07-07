
board = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
player = False
end = False
player_name = 1
while True :
#پرینت وضعیت
    print(f'{board[0]} | {board[1]} | {board[2]}')
    print(f'{board[3]} | {board[4]} | {board[5]}')
    print(f'{board[6]} | {board[7]} | {board[8]}')
    print("\n \n")
#تعویض کاربر
    player = not player
    if player:
        player_name = 1
    else :
        player_name = 2
    #گرفتن ورودی
    movment=input(f"*** player {player_name} enter your move \n" )

#بررسی وضعیت ورودی 
    if not ('0'<=movment<='8') :
        print('**** wrong number ****')
        player = not player
        continue
    # ورودی صحیح داده شد
    movment = int(movment)   
    
    if board[movment] == "x" or board[movment] == "o" :
        print('****this cell is taken*****')
        player = not player
        continue
 
#اعمال حرکت 
    if player :
        board[movment] = 'x'
    else :
        board[movment] = "o"
#بررسی برد و باخت
    for i in range (0,3) :
        if board[3*i] == board[3*i+1] == board[3*i+2]:
            print(f'player{player_name},you won!!!')
            end = True
        if board[i] == board[i+3] == board[i+6]:
            print(f'player{player_name},you won!!!')
            end = True

    if (board[0] == board[4] == board[8]) or (board[2] == board[4] == board[6]) :
        print(f'player{player_name},you won!!!')
        end = True

    if not end :
        end = True
        for i in range(0,9) :
            if '1'<=board [i]<='8' :
                end = False
                break
        if end :
            print('that is a tie')

#بررسی اتمام بازی
    if end :
        break


