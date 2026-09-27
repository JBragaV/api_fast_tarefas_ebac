from app.database.models.tarefa import Tarefa


def test_representacao_usuario():
    tarefa = Tarefa(
        id=1, nome="Estudar", descricao="Estudar muito mesmo", concluida=False
    )

    assert repr(tarefa) == ("id: 1 -- Titulo: Estudar -- Concluida: False")
