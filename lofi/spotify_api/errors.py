class PlaylistAlreadyExistsError(Exception):
    def __init__(self, user_id: str, name: str, playlist_id: str) -> None:
        self.user_id = user_id
        self.name = name
        self.playlist_id = playlist_id
