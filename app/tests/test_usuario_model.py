from app.database.models.usuario import Usuario


def test_representacao_usuario():
    usuario = Usuario(
        id=1,
        nome="Nuneula",
        email="nunuela@nunu.com.br",
        username="nununu",
        hashed_password="115a1s6d5a5s4",
    )

    assert repr(usuario) == ("id: 1 -- username: nununu -- E-mail: nunuela@nunu.com.br")
