from way.game import Game

def main() -> None:
    game = Game(800, 600, "The Way Out", debug=True)
    game.run()

if __name__ == "__main__":
    main()
