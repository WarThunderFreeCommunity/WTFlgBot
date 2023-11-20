import ast
import unittest
from io import StringIO

from services.eval_expressions import eval_expr, eval_


class TestCalculator(unittest.TestCase):

    def test_eval_expr(self):
        self.assertEqual(eval_expr('2 + 2 * 2'), 6)
        self.assertEqual(eval_expr('(2 + 2) * 2'), 8)
        self.assertEqual(eval_expr('10 * 10'), 100)
        self.assertEqual(eval_expr('100 / 10'), 10.0)
        self.assertEqual(eval_expr('100 // 10'), 10)
        self.assertEqual(eval_expr('2 ** 3'), 8)
        self.assertEqual(eval_expr('55'), 55)
        self.assertEqual(eval_expr('-55'), -55)
        self.assertEqual(eval_expr('2^6'), 4)
        self.assertEqual(eval_expr('2**6'), 64)
        self.assertEqual(eval_expr('1 + 2*3**(4^5) / (6 + -7)'), -5.0)

    def test_eval_number(self):
        # Проверка, что функция правильно обрабатывает числа
        self.assertEqual(eval_(ast.Num(42)), 42)
        self.assertEqual(eval_(ast.Num(-10)), -10)

    def test_eval_binop(self):
        # Проверка, что функция правильно обрабатывает бинарные операции
        node = ast.BinOp(left=ast.Num(5), op=ast.Add(), right=ast.Num(3))
        self.assertEqual(eval_(node), 8)

        node = ast.BinOp(left=ast.Num(10), op=ast.Mult(), right=ast.Num(2))
        self.assertEqual(eval_(node), 20)

    def test_eval_unaryop(self):
        # Проверка, что функция правильно обрабатывает унарные операции
        node = ast.UnaryOp(op=ast.USub(), operand=ast.Num(7))
        self.assertEqual(eval_(node), -7)

        node = ast.UnaryOp(op=ast.USub(), operand=ast.Num(-3))
        self.assertEqual(eval_(node), 3)

    def test_eval_invalid_input(self):
        # Проверка, что функция вызывает исключение TypeError для неподдерживаемых типов узлов
        with self.assertRaises(TypeError):
            eval_(ast.Name(id='x', ctx=ast.Load()))
        

async def run_tests(**kwargs):
    print(info_str := f"```AST TEST STARTED, kwargs:\n {kwargs}\n```")
    output_buffer = StringIO()

    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    test_runner = unittest.TextTestRunner(stream=output_buffer)
    test_result = test_runner.run(test_suite)
    
    if kwargs.get("info"): info_str = info_str[:-3] + f"\n{output_buffer.getvalue()}```"

    return test_result, info_str

if __name__ == '__main__':
    unittest.main()
