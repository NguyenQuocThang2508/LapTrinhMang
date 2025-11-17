import server.src.config as cfg

def test_server_config():
    assert cfg.SERVER_PORT == 5000
    assert cfg.MAX_PLAYERS >= 1
