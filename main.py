from hitman_2d import LevelCreator, Game


EDIT_LEVEL: bool = False


if __name__ == "__main__":
    if EDIT_LEVEL:
        level_creator: LevelCreator = LevelCreator(
            level_path="Levels/level_1.json",
            asset_path="Assets"
        )
        level_creator.run()
    else:
        game: Game = Game(
            level_path="Levels/level_1.json",
            asset_path="Assets"
        )
        game.run()
        
    
    