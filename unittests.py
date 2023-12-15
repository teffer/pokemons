import unittest
from app import app
from contextlib import contextmanager
from flask import template_rendered

@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_battle_route(self):
        with self.app as client:
            with client.session_transaction() as session:
                session['round_number'] = 1
                session['player_pokemon'] = 1
                session['computer_pokemon'] = 5
                session['player_health'] = 100
                session['computer_health'] = 90
                session['player_damage'] = 100
                session['computer_damage'] = 150
                session['player_def'] = 0
                session['computer_def'] = 0

            player_choice = 5  # Добавлен параметр для передачи в тест
            with captured_templates(app) as templates:
                response = client.post('/battle', data={'player_choice': player_choice})
                template, context = templates[0]

                self.assertEqual(template.name, 'pokemon.html')
                self.assertIn('name', context)
                self.assertIn('health', context)

                # Добавлены проверки передаваемых параметров
                self.assertEqual(context['player_choice'], player_choice)
                self.assertEqual(context['player_attack'], 100)  # Пример, ожидаемое значение
                self.assertEqual(context['computer_attack'], 150)  # Пример, ожидаемое значение
                self.assertTrue(90 <= context['player_health'] <= 100 or context['player_health'] == -50)
                self.assertTrue(80 <= context['computer_health'] <= 90 or context['computer_health'] == -10)
    def test_qbattle_route(self):
        with self.app as client:
            with client.session_transaction() as session:
                session['round_number'] = 1
                session['player_pokemon'] = 1
                session['computer_pokemon'] = 2
                session['player_health'] = 100
                session['computer_health'] = 90
                session['player_damage'] = 200
                session['computer_damage'] = 150
                session['player_def'] = 0
                session['computer_def'] = 0

            with captured_templates(app) as templates:
                response = client.post('/qbattle')

                template, context = templates[0]

                self.assertEqual(template.name, 'pokemon.html')
                self.assertIn('name', context)
                self.assertIn('health', context)
                self.assertEqual(context['player_attack'], 200)  # Пример, ожидаемое значение
                self.assertEqual(context['computer_attack'], 150)  # Пример, ожидаемое значение
                self.assertTrue(90 <= context['player_health'] <= 100 or context['player_health'] == -50)
                self.assertTrue(80 <= context['computer_health'] <= 90 or context['computer_health'] == -110)

if __name__ == '__main__':
    unittest.main()
