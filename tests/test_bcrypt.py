import os

import mock

import pytest

import six

import bcrypt


def test_raise_implicit_compile():
    with pytest.raises(RuntimeError):
        bcrypt._compile_module()


def test_gensalt_basic(monkeypatch):
    urandom = mock.Mock(return_value=b"0000000000000000")
    monkeypatch.setattr(os, "urandom", urandom)
    assert bcrypt.gensalt() == b"$2a$12$KB.uKB.uKB.uKB.uKB.uK."


@pytest.mark.parametrize(("rounds", "expected"), [
    (4, b"$2a$04$KB.uKB.uKB.uKB.uKB.uK."),
    (5, b"$2a$05$KB.uKB.uKB.uKB.uKB.uK."),
    (6, b"$2a$06$KB.uKB.uKB.uKB.uKB.uK."),
    (7, b"$2a$07$KB.uKB.uKB.uKB.uKB.uK."),
    (8, b"$2a$08$KB.uKB.uKB.uKB.uKB.uK."),
    (9, b"$2a$09$KB.uKB.uKB.uKB.uKB.uK."),
    (10, b"$2a$10$KB.uKB.uKB.uKB.uKB.uK."),
    (11, b"$2a$11$KB.uKB.uKB.uKB.uKB.uK."),
    (12, b"$2a$12$KB.uKB.uKB.uKB.uKB.uK."),
    (13, b"$2a$13$KB.uKB.uKB.uKB.uKB.uK."),
    (14, b"$2a$14$KB.uKB.uKB.uKB.uKB.uK."),
    (15, b"$2a$15$KB.uKB.uKB.uKB.uKB.uK."),
    (16, b"$2a$16$KB.uKB.uKB.uKB.uKB.uK."),
    (17, b"$2a$17$KB.uKB.uKB.uKB.uKB.uK."),
    (18, b"$2a$18$KB.uKB.uKB.uKB.uKB.uK."),
    (19, b"$2a$19$KB.uKB.uKB.uKB.uKB.uK."),
    (20, b"$2a$20$KB.uKB.uKB.uKB.uKB.uK."),
    (21, b"$2a$21$KB.uKB.uKB.uKB.uKB.uK."),
    (22, b"$2a$22$KB.uKB.uKB.uKB.uKB.uK."),
    (23, b"$2a$23$KB.uKB.uKB.uKB.uKB.uK."),
    (24, b"$2a$24$KB.uKB.uKB.uKB.uKB.uK."),
])
def test_gensalt_rounds_valid(rounds, expected, monkeypatch):
    urandom = mock.Mock(return_value=b"0000000000000000")
    monkeypatch.setattr(os, "urandom", urandom)
    assert bcrypt.gensalt(rounds) == expected


@pytest.mark.parametrize("rounds", list(range(1, 4)))
def test_gensalt_rounds_invalid(rounds, monkeypatch):
    urandom = mock.Mock(return_value=b"0000000000000000")
    monkeypatch.setattr(os, "urandom", urandom)

    with pytest.raises(ValueError):
        bcrypt.gensalt(rounds)


@pytest.mark.parametrize(("password", "salt", "expected"), [
    (
        b"Kk4DQuMMfZL9o",
        b"$2a$04$cVWp4XaNU8a4v1uMRum2SO",
        b"$2a$04$cVWp4XaNU8a4v1uMRum2SO026BWLIoQMD/TXg5uZV.0P.uO8m3YEm",
    ),
    (
        b"9IeRXmnGxMYbs",
        b"$2a$04$pQ7gRO7e6wx/936oXhNjrO",
        b"$2a$04$pQ7gRO7e6wx/936oXhNjrOUNOHL1D0h1N2IDbJZYs.1ppzSof6SPy",
    ),
    (
        b"xVQVbwa1S0M8r",
        b"$2a$04$SQe9knOzepOVKoYXo9xTte",
        b"$2a$04$SQe9knOzepOVKoYXo9xTteNYr6MBwVz4tpriJVe3PNgYufGIsgKcW",
    ),
    (
        b"Zfgr26LWd22Za",
        b"$2a$04$eH8zX.q5Q.j2hO1NkVYJQO",
        b"$2a$04$eH8zX.q5Q.j2hO1NkVYJQOM6KxntS/ow3.YzVmFrE4t//CoF4fvne",
    ),
    (
        b"Tg4daC27epFBE",
        b"$2a$04$ahiTdwRXpUG2JLRcIznxc.",
        b"$2a$04$ahiTdwRXpUG2JLRcIznxc.s1.ydaPGD372bsGs8NqyYjLY1inG5n2",
    ),
    (
        b"xhQPMmwh5ALzW",
        b"$2a$04$nQn78dV0hGHf5wUBe0zOFu",
        b"$2a$04$nQn78dV0hGHf5wUBe0zOFu8n07ZbWWOKoGasZKRspZxtt.vBRNMIy",
    ),
    (
        b"59je8h5Gj71tg",
        b"$2a$04$cvXudZ5ugTg95W.rOjMITu",
        b"$2a$04$cvXudZ5ugTg95W.rOjMITuM1jC0piCl3zF5cmGhzCibHZrNHkmckG",
    ),
    (
        b"wT4fHJa2N9WSW",
        b"$2a$04$YYjtiq4Uh88yUsExO0RNTu",
        b"$2a$04$YYjtiq4Uh88yUsExO0RNTuEJ.tZlsONac16A8OcLHleWFjVawfGvO",
    ),
    (
        b"uSgFRnQdOgm4S",
        b"$2a$04$WLTjgY/pZSyqX/fbMbJzf.",
        b"$2a$04$WLTjgY/pZSyqX/fbMbJzf.qxCeTMQOzgL.CimRjMHtMxd/VGKojMu",
    ),
    (
        b"tEPtJZXur16Vg",
        b"$2a$04$2moPs/x/wnCfeQ5pCheMcu",
        b"$2a$04$2moPs/x/wnCfeQ5pCheMcuSJQ/KYjOZG780UjA/SiR.KsYWNrC7SG",
    ),
    (
        b"vvho8C6nlVf9K",
        b"$2a$04$HrEYC/AQ2HS77G78cQDZQ.",
        b"$2a$04$HrEYC/AQ2HS77G78cQDZQ.r44WGcruKw03KHlnp71yVQEwpsi3xl2",
    ),
    (
        b"5auCCY9by0Ruf",
        b"$2a$04$vVYgSTfB8KVbmhbZE/k3R.",
        b"$2a$04$vVYgSTfB8KVbmhbZE/k3R.ux9A0lJUM4CZwCkHI9fifke2.rTF7MG",
    ),
    (
        b"GtTkR6qn2QOZW",
        b"$2a$04$JfoNrR8.doieoI8..F.C1O",
        b"$2a$04$JfoNrR8.doieoI8..F.C1OQgwE3uTeuardy6lw0AjALUzOARoyf2m",
    ),
    (
        b"zKo8vdFSnjX0f",
        b"$2a$04$HP3I0PUs7KBEzMBNFw7o3O",
        b"$2a$04$HP3I0PUs7KBEzMBNFw7o3O7f/uxaZU7aaDot1quHMgB2yrwBXsgyy",
    ),
    (
        b"I9VfYlacJiwiK",
        b"$2a$04$xnFVhJsTzsFBTeP3PpgbMe",
        b"$2a$04$xnFVhJsTzsFBTeP3PpgbMeMREb6rdKV9faW54Sx.yg9plf4jY8qT6",
    ),
    (
        b"VFPO7YXnHQbQO",
        b"$2a$04$WQp9.igoLqVr6Qk70mz6xu",
        b"$2a$04$WQp9.igoLqVr6Qk70mz6xuRxE0RttVXXdukpR9N54x17ecad34ZF6",
    ),
    (
        b"VDx5BdxfxstYk",
        b"$2a$04$xgZtlonpAHSU/njOCdKztO",
        b"$2a$04$xgZtlonpAHSU/njOCdKztOPuPFzCNVpB4LGicO4/OGgHv.uKHkwsS",
    ),
    (
        b"dEe6XfVGrrfSH",
        b"$2a$04$2Siw3Nv3Q/gTOIPetAyPr.",
        b"$2a$04$2Siw3Nv3Q/gTOIPetAyPr.GNj3aO0lb1E5E9UumYGKjP9BYqlNWJe",
    ),
    (
        b"cTT0EAFdwJiLn",
        b"$2a$04$7/Qj7Kd8BcSahPO4khB8me",
        b"$2a$04$7/Qj7Kd8BcSahPO4khB8me4ssDJCW3r4OGYqPF87jxtrSyPj5cS5m",
    ),
    (
        b"J8eHUDuxBB520",
        b"$2a$04$VvlCUKbTMjaxaYJ.k5juoe",
        b"$2a$04$VvlCUKbTMjaxaYJ.k5juoecpG/7IzcH1AkmqKi.lIZMVIOLClWAk.",
    ),
])
def test_hashpw_new(password, salt, expected):
    assert bcrypt.hashpw(password, salt) == expected


@pytest.mark.parametrize(("password", "hashed"), [
    (
        b"Kk4DQuMMfZL9o",
        b"$2a$04$cVWp4XaNU8a4v1uMRum2SO026BWLIoQMD/TXg5uZV.0P.uO8m3YEm",
    ),
    (
        b"9IeRXmnGxMYbs",
        b"$2a$04$pQ7gRO7e6wx/936oXhNjrOUNOHL1D0h1N2IDbJZYs.1ppzSof6SPy",
    ),
    (
        b"xVQVbwa1S0M8r",
        b"$2a$04$SQe9knOzepOVKoYXo9xTteNYr6MBwVz4tpriJVe3PNgYufGIsgKcW",
    ),
    (
        b"Zfgr26LWd22Za",
        b"$2a$04$eH8zX.q5Q.j2hO1NkVYJQOM6KxntS/ow3.YzVmFrE4t//CoF4fvne",
    ),
    (
        b"Tg4daC27epFBE",
        b"$2a$04$ahiTdwRXpUG2JLRcIznxc.s1.ydaPGD372bsGs8NqyYjLY1inG5n2",
    ),
    (
        b"xhQPMmwh5ALzW",
        b"$2a$04$nQn78dV0hGHf5wUBe0zOFu8n07ZbWWOKoGasZKRspZxtt.vBRNMIy",
    ),
    (
        b"59je8h5Gj71tg",
        b"$2a$04$cvXudZ5ugTg95W.rOjMITuM1jC0piCl3zF5cmGhzCibHZrNHkmckG",
    ),
    (
        b"wT4fHJa2N9WSW",
        b"$2a$04$YYjtiq4Uh88yUsExO0RNTuEJ.tZlsONac16A8OcLHleWFjVawfGvO",
    ),
    (
        b"uSgFRnQdOgm4S",
        b"$2a$04$WLTjgY/pZSyqX/fbMbJzf.qxCeTMQOzgL.CimRjMHtMxd/VGKojMu",
    ),
    (
        b"tEPtJZXur16Vg",
        b"$2a$04$2moPs/x/wnCfeQ5pCheMcuSJQ/KYjOZG780UjA/SiR.KsYWNrC7SG",
    ),
    (
        b"vvho8C6nlVf9K",
        b"$2a$04$HrEYC/AQ2HS77G78cQDZQ.r44WGcruKw03KHlnp71yVQEwpsi3xl2",
    ),
    (
        b"5auCCY9by0Ruf",
        b"$2a$04$vVYgSTfB8KVbmhbZE/k3R.ux9A0lJUM4CZwCkHI9fifke2.rTF7MG",
    ),
    (
        b"GtTkR6qn2QOZW",
        b"$2a$04$JfoNrR8.doieoI8..F.C1OQgwE3uTeuardy6lw0AjALUzOARoyf2m",
    ),
    (
        b"zKo8vdFSnjX0f",
        b"$2a$04$HP3I0PUs7KBEzMBNFw7o3O7f/uxaZU7aaDot1quHMgB2yrwBXsgyy",
    ),
    (
        b"I9VfYlacJiwiK",
        b"$2a$04$xnFVhJsTzsFBTeP3PpgbMeMREb6rdKV9faW54Sx.yg9plf4jY8qT6",
    ),
    (
        b"VFPO7YXnHQbQO",
        b"$2a$04$WQp9.igoLqVr6Qk70mz6xuRxE0RttVXXdukpR9N54x17ecad34ZF6",
    ),
    (
        b"VDx5BdxfxstYk",
        b"$2a$04$xgZtlonpAHSU/njOCdKztOPuPFzCNVpB4LGicO4/OGgHv.uKHkwsS",
    ),
    (
        b"dEe6XfVGrrfSH",
        b"$2a$04$2Siw3Nv3Q/gTOIPetAyPr.GNj3aO0lb1E5E9UumYGKjP9BYqlNWJe",
    ),
    (
        b"cTT0EAFdwJiLn",
        b"$2a$04$7/Qj7Kd8BcSahPO4khB8me4ssDJCW3r4OGYqPF87jxtrSyPj5cS5m",
    ),
    (
        b"J8eHUDuxBB520",
        b"$2a$04$VvlCUKbTMjaxaYJ.k5juoecpG/7IzcH1AkmqKi.lIZMVIOLClWAk.",
    ),
])
def test_hashpw_existing(password, hashed):
    assert bcrypt.hashpw(password, hashed) == hashed


def test_hashpw_invalid():
    with pytest.raises(ValueError):
        bcrypt.hashpw(b"password", b"$2z$04$cVWp4XaNU8a4v1uMRum2SO")


def test_hashpw_str_password():
    with pytest.raises(TypeError):
        bcrypt.hashpw(
            six.text_type("password"),
            b"$2a$04$cVWp4XaNU8a4v1uMRum2SO",
        )


def test_hashpw_str_salt():
    with pytest.raises(TypeError):
        bcrypt.hashpw(
            b"password",
            six.text_type("$2a$04$cVWp4XaNU8a4v1uMRum2SO"),
        )
