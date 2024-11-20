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
        prompt = """Сгенерируй короткое дружеское сообщение поддержки.

        Стиль общения:
        - Лёгкая подколка друга к подруге
        - С налётом самоуверенности и дружеского стёба
        - Мы давно знакомы, можем позволить себе подшучивать
        - Искреннее, но без слащавости

        Важно:
        - Обращение только в начале (Кам или Мила)
        - Говорить уверенно, но без конкретных обещаний
        - Никаких отсылок к конкретным делам из прошлого
        - Избегать клише про "всё наладится/будет хорошо"
        - Сохранять лёгкую самоиронию
        - Тон поддерживающий, но с элементами здорового троллинга

        Формат:
        - 2-3 коротких предложения
        - Разговорный стиль, будто переписка в мессенджере
        - Можно использовать современный сленг, но умеренно"""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.9,
            system="Ты близкий друг, общаешься в лёгком, чуть самоуверенном стиле. Любишь пошутить, но знаешь меру. Используешь современный разговорный язык.",
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
        print(f"Error generating message: {str(e)}")
        return jsonify({
            'message': 'Эй, ну ты чего раскисла? Давай включай свой режим вредины - он у тебя всегда лучше всего работает! А я тут подежурю рядом, вдруг понадобится профессиональный советчик по плохим идеям.'
        })