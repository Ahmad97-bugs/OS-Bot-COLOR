import random
import time


def main():
    elemental = ['Air', 'Water', 'Earth', 'Fire']
    catalytic = ['Mind', 'Body', 'Chaos', 'Cosmic', 'Nature', 'Law', 'Death', 'Blood']
    priority = ['Blood', 'Fire', 'Earth', 'Death', 'Law', 'Nature', 'Cosmic', 'Chaos', 'Body', 'Water', 'Air', 'Mind']
    total_elemental = 0
    total_catalytic = 0

    for i in range(0, 50000):
        elemental_index = random.randint(0, 3)
        catalytic_index = random.randint(0, 7)
        chosen_elemental = elemental[elemental_index]
        chosen_catalytic = catalytic[catalytic_index]
        if priority.index(chosen_catalytic) > priority.index(chosen_elemental):
            total_catalytic += 1
        else:
            total_elemental += 1
    print(f'Total elemental points: {total_elemental}')
    print(f'Total catalytic points: {total_catalytic}')


if __name__ == "__main__":
    # main()
    overload_timer = time.time() + 300
    while True:
        time.sleep(5)
        if abs(time.time() - overload_timer) < 5:
            continue
        print('Still time')
