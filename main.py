from hitman_2d import LevelCreator


if __name__ == "__main__":
    level_creator: LevelCreator = LevelCreator(
        level_path="Levels/level_1.json",
        asset_path="Assets"
    )
    
    level_creator.run()