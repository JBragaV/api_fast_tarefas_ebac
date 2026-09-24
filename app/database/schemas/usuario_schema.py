from pydantic import Field, SecretStr, field_validator, model_validator

from .base_schema import Base


class UsuarioBase(Base):
    nome: str | None = Field(
        min_length=10,
        max_length=25,
        examples=["Trujilo Vila Carvalho"],
        description="Nome do usuário",
    )

    email: str = Field(
        min_length=15,
        max_length=50,
        examples=["example@email.com.br"],
        description="Email do usuário para realizar o login",
    )
    username: str | None = Field(
        default=None,
        min_length=5,
        max_length=15,
        examples=["username_exemplo"],
        description="Username escolhido pelo usuário",
    )

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("O E-mail deve ser preenchido")
        return valor

    @field_validator("username")
    @classmethod
    def validar_username(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("O username é obrigatório")

        return valor

    @model_validator(mode="after")
    def preencher_username_padrao(self):
        if self.username is None:
            if self.nome is None:
                raise ValueError("É necessário informar o nome ou o username")
            username_padrao = self.nome.lower().replace(" ", "_")
            self.username = username_padrao[:15]
        return self


class UsuarioInput(UsuarioBase):
    password1: SecretStr = Field(min_length=8, max_length=64, exclude=True)
    password2: SecretStr = Field(min_length=8, max_length=64, exclude=True)

    @field_validator("password1")
    @classmethod
    def validar_forca_password(cls, valor: SecretStr) -> SecretStr:
        senha = valor.get_secret_value()
        if not any(c.isupper() for c in senha):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula")
        if not any(c.isdigit() for c in senha):
            raise ValueError("A senha deve conter ao menos um número")
        return valor

    @model_validator(mode="after")
    def validar_senhas_iguais(self):
        if self.password1 != self.password2:
            raise ValueError("As senhas não coincidem")
        return self


class UsuarioResposta(UsuarioBase):
    id: int = Field(description="Identificador único do usuário.")


class ListaUsuarioResposta(Base):
    page: int
    limit: int
    tamanho: int
    usuarios: list[UsuarioResposta]


class UsuarioUpdate(Base):
    nome: str | None = Field(default=None, min_length=10, max_length=25)
    email: str | None = Field(default=None, min_length=15, max_length=50)
    username: str | None = Field(default=None, min_length=5, max_length=15)
    password1: SecretStr | None = Field(
        default=None, min_length=8, max_length=64, exclude=True
    )
    password2: SecretStr | None = Field(
        default=None, min_length=8, max_length=64, exclude=True
    )

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("O E-mail deve ser preenchido")
        return valor

    @field_validator("username")
    @classmethod
    def validar_username(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("O username é obrigatório")
        return valor

    @field_validator("password1")
    @classmethod
    def validar_forca_password(cls, valor: SecretStr | None) -> SecretStr | None:
        if valor is None:
            return valor
        senha = valor.get_secret_value()
        if not any(c.isupper() for c in senha):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula")
        if not any(c.isdigit() for c in senha):
            raise ValueError("A senha deve conter ao menos um número")
        return valor

    @model_validator(mode="after")
    def validar_senhas_iguais(self):
        # só exige coerência SE o usuário decidiu mexer na senha
        if self.password1 is not None or self.password2 is not None:
            if self.password1 is None or self.password2 is None:
                raise ValueError("Informe password1 e password2 para alterar a senha")
            if self.password1 != self.password2:
                raise ValueError("As senhas não coincidem")
        return self
