import pytest
from pydantic import ValidationError

from app.database.schemas.usuario_schema import UsuarioInput, UsuarioUpdate


@pytest.fixture
def dados_usuario():
    return {
        "nome": "NUNUELA CAIADO",
        "email": "nunulinda@email.com.br",
        "username": "nunuelacaiado",
        "password1": "Senha123",
        "password2": "Senha123",
    }


@pytest.mark.parametrize("schema", [UsuarioInput, UsuarioUpdate])
def test_dados_validos_e_senhas_excluidas(schema, dados_usuario):
    usuario = schema.model_validate(dados_usuario)

    assert usuario.nome == dados_usuario["nome"]
    assert usuario.email == dados_usuario["email"]
    assert usuario.username == dados_usuario["username"]
    assert usuario.password1.get_secret_value() == "Senha123"
    assert usuario.password2.get_secret_value() == "Senha123"

    dados_serializados = usuario.model_dump()

    assert "password1" not in dados_serializados
    assert "password2" not in dados_serializados


@pytest.mark.parametrize("schema", [UsuarioInput, UsuarioUpdate])
def test_remove_espacos_email_e_username(schema, dados_usuario):
    dados_usuario["email"] = "  nunulinda@email.com.br  "
    dados_usuario["username"] = "  nunuela  "

    usuario = schema.model_validate(dados_usuario)

    assert usuario.email == "nunulinda@email.com.br"
    assert usuario.username == "nunuela"


@pytest.mark.parametrize("schema", [UsuarioInput, UsuarioUpdate])
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("email", " " * 15, "O E-mail deve ser preenchido"),
        ("username", " " * 5, "O username é obrigatório"),
    ],
)
def test_rejeita_campos_apenas_com_espacos(
    dados_usuario, campo, valor, mensagem, schema
):
    dados_usuario[campo] = valor

    with pytest.raises(ValidationError, match=mensagem):
        schema.model_validate(dados_usuario)


@pytest.mark.parametrize("schema", [UsuarioInput, UsuarioUpdate])
@pytest.mark.parametrize(
    ("senha", "mensagem"),
    [
        ("senha123", "A senha deve conter ao menos uma letra maiúscula"),
        ("Senhaabc", "A senha deve conter ao menos um número"),
    ],
)
def test_rejeita_senha_fraca(mensagem, senha, schema, dados_usuario):
    dados_usuario["password1"] = senha
    dados_usuario["password2"] = senha

    with pytest.raises(ValidationError, match=mensagem):
        schema.model_validate(dados_usuario)


@pytest.mark.parametrize("schema", [UsuarioInput, UsuarioUpdate])
def test_rejeita_senhas_diferentes(schema, dados_usuario):
    dados_usuario["password2"] = "senhadiferente"

    with pytest.raises(ValidationError, match="As senhas não coincidem"):
        schema.model_validate(dados_usuario)


@pytest.mark.parametrize("informar_none", [False, True])
def test_gera_username_quando_ausente_ou_none(dados_usuario, informar_none):
    dados_usuario.pop("username")

    if informar_none:
        dados_usuario["username"] = None

    usuario = UsuarioInput.model_validate(dados_usuario)

    assert usuario.username == "nunuela_caiado"


def test_username_gerado_limitado_a_15_caracteres(dados_usuario):
    dados_usuario["nome"] = "MARIA EDUARDA DE SOUZA"
    dados_usuario["username"] = None

    usuario = UsuarioInput.model_validate(dados_usuario)

    assert usuario.username == "maria_eduarda_d"
    assert len(usuario.username) == 15


def test_rejeita_nome_e_username_none(dados_usuario):
    dados_usuario["nome"] = None
    dados_usuario["username"] = None

    with pytest.raises(
        ValidationError,
        match="É necessário informar o nome ou o username",
    ):
        UsuarioInput.model_validate(dados_usuario)


def test_update_aceita_campos_explicitamente_none():
    usuario = UsuarioUpdate(
        nome=None,
        email=None,
        username=None,
        password1=None,
        password2=None,
    )

    assert usuario.nome is None
    assert usuario.email is None
    assert usuario.username is None
    assert usuario.password1 is None
    assert usuario.password2 is None


def test_update_permite_alterar_nome_sem_enviar_senhas():
    usuario = UsuarioUpdate(nome="MANUELA CAIADO")
    assert usuario.nome == "MANUELA CAIADO"
    assert usuario.password1 is None
    assert usuario.password2 is None
    assert usuario.model_fields_set == {"nome"}


@pytest.mark.parametrize("campo", ["password1", "password2"])
def test_update_exige_as_duas_senhas(campo):
    dados = {campo: "NovaSenha123"}

    with pytest.raises(
        ValidationError,
        match="Informe password1 e password2 para alterar a senha",
    ):
        UsuarioUpdate.model_validate(dados)
