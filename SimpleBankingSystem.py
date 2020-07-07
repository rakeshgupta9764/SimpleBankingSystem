import sys
import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS card;')
query = 'CREATE TABLE card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)'
cur.execute(query)
conn.commit()

class CreditCard:
    
# the card length is 16 digits and pin length is 4 digits
# the card number has to be in accordance with the Luhn's algorithm, see wikipedia: https://en.wikipedia.org/wiki/Luhn_algorithm
    def __init__(self):
        random.seed()
        self.balance = 0
        check_exists = True
        while check_exists:
            self.card_num = '400000' + f'{random.randint(0, 999999999):09}'
            length = len(self.card_num)
            sum = 0
            is_Second = True
            for i in range(length - 1, -1, -1):
                digit = self.card_num[i]
                digit = int(digit)
                if is_Second:
                    digit *= 2
                is_Second = not is_Second
                sum += digit // 10 + digit % 10

            check_digit = str((sum * 9) % 10)
            self.card_num += check_digit
            query = 'SELECT number from card WHERE number = "' + self.card_num + '";'
            cur.execute(query)
            if not cur.fetchone():
                check_exists = False

        self.pin = f'{random.randint(0, 9999):04}'
        query = 'INSERT INTO card(number, pin, balance) VALUES(?, ?, ?)'
        cur.execute(query, [self.card_num, self.pin, self.balance])
        conn.commit()

def check_luhn(number):
    length = len(number)
    sum = 0
    is_Second = True
    for i in range(length - 2, -1, -1):
        digit = int(number[i])
        if is_Second:
            digit *= 2
        is_Second = not is_Second
        sum += digit // 10 + digit % 10
      
    check_digit = str((sum * 9) % 10)
    return check_digit == number[-1]

while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    choice = int(input())
    if choice == 0:
        print()
        print("Bye!")
        conn.close()
        sys.exit(0)
    elif choice == 1:
        card = CreditCard()
        print('Your card has been created')
        print('Your card number:')
        print(card.card_num)
        print('Your card PIN:')
        print(card.pin)
        print()
    elif choice == 2:
        print()
        print('Enter your card number:')
        card_input = input()
        print('Enter your PIN:')
        pin_input = input()
        query = "SELECT pin, balance from card WHERE number = '" + card_input + "';"
        cur.execute(query)
        result = cur.fetchone()
        # print(result)
        if result is not None and result[0] == pin_input:
            print()
            print('You have successfully logged in!')
            while True:
                print()
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfer')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                login_input = int(input())
                if login_input == 1:
                    print()
                    print('Balance: {}'.format(result[1]))
                elif login_input == 2:
                    print()
                    print('Enter income:')
                    income_to_add = int(input())
                    cur.execute('UPDATE card SET balance = balance + ' + str(income_to_add) + ' WHERE number = "' + card_input + '";')
                    conn.commit()
                    print('Income was added!')
                elif login_input == 3:
                    print()
                    print('Transfer')
                    print('Enter card number:')
                    dest_card = input()
                    if check_luhn(dest_card):
                        result = cur.execute('SELECT number FROM card WHERE number = "' + dest_card + '";')
                        dest_card_num = result.fetchone()
                        if dest_card_num is not None:
                            print('Enter how much money you want to transfer:')
                            amount = int(input())
                            result = cur.execute('SELECT balance FROM card where number = "' + card_input + '";')
                            src_balance = result.fetchone()[0]
                            if amount <= src_balance:
                                cur.execute('UPDATE card SET balance = balance +' + str(amount) + ' WHERE number = "' + dest_card_num[0] + '";')
                                conn.commit()
                                cur.execute('UPDATE card SET balance = balance -' + str(amount) + ' WHERE number = "' + card_input + '";')
                                conn.commit()
                                print('Success!')
                            else:
                                print('Not enough money!')
                        else:
                            print('Such a card does not exist.')
                    else:
                        print('Probably you made mistake in the card number. Please try again!')
                elif login_input == 4:
                    cur.execute('DELETE FROM card WHERE number = "' + card_input + '";')
                    conn.commit()
                    print()
                    print('The account has been closed')
                elif login_input == 5:
                    break
                elif login_input == 0:
                    print()
                    print('Bye!')
                    conn.close()
                    sys.exit(0)
        else:
            print('Wrong card number or PIN!')
            print()
