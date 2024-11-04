from flask import Blueprint, render_template, jsonify
from flask_login import login_required
import anthropic

support_blueprint = Blueprint('support', __name__)

client = anthropic.Anthropic()


@support_blueprint.route('/mi_support')
@login_required
def support_page():
    return render_template('mi_support.html')


@support_blueprint.route('/mi_support/generate', methods=['POST'])
@login_required
def generate_support():
    try:
        prompt = """Сгенерируй искреннее сообщение поддержки для подруги в сложный период. 

        Важно:
        - Её зовут Камилла, любит Мила, но можно клички: Кам, Копилка, Мила, Миллениал, МиллЛось, Милен
        - Без излишней слащавости и пафоса
        - От мужского лица Влада
        - Я ей не брат)
        - Она любит меня шутя подбешивать или троллить, и я тоже
        - С юмором и издевками, немного высокомерно, но по доброму
        - Практично и по-дружески
        - Без конкретных примеров прошлого, ведь ты не знаешь о ней особо ничего))
        - С конкретной надеждой на будущее
        - С акцентом на силу и опыт человека
        - Кратко, 2-3 предложения
        - Используй не более 1-2 вариантов её имени-прозвищ в обращении, а то выглядит странно
        - Генерируй реально разные варианты каждый раз, это многоразовый запрос. Используй какой-то сид рандома

        Пиши простым разговорным языком, как близкий друг."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.7,
            system="Ты близкий друг, который общается просто и искренне, без лишнего пафоса. Ты знаешь цену простым словам поддержки. Отдавай только один вариант за раз",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        support_text = message.content[0].text

        return jsonify({'message': support_text})

    except Exception as e:
        print(f"Error generating message: {str(e)}")  # Для отладки
        return jsonify({
            'message': 'Знаю, сейчас тяжело. Но ты уже проходила через сложные времена и всегда находила выход. Просто помни - это состояние временное, оно пройдет. А я рядом, если нужно поговорить или просто помолчать вместе.'
        })
