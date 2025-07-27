from libphext import cli

def test_main_output(capfd):
    cli.main()
    out, _ = capfd.readouterr()
    assert "hello world" in out