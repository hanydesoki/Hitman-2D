from hitman_2d import LevelCreator, Game


EDIT_LEVEL: bool =  True
LEVEL_PATH: str = "Levels/level_1.json"
ASSET_PATH: str = "Assets"

if __name__ == "__main__":
    if EDIT_LEVEL:
        level_creator: LevelCreator = LevelCreator(
            level_path=LEVEL_PATH,
            asset_path=ASSET_PATH
        )
        level_creator.run()
    else:
        game: Game = Game(
            level_path=LEVEL_PATH,
            asset_path=ASSET_PATH
        )
        
        game.run()
        
    
    