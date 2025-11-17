import client.src.config as cfg

def test_config_values():
    assert cfg.SERVER_IP == '127.0.0.1'
    assert isinstance(cfg.SERVER_PORT, int)
